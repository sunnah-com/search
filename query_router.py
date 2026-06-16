"""Query classification: spam detection and route selection.

Route selection here is **observational** — `route_query` / `routing_decision`
classify an incoming query but do not, on their own, change which Elasticsearch
path the request takes. Production `search()` routes purely on `?mode=`; the
router's decision is only recorded (shadow-sampling `routing_decision` column and
the optional `ROUTER_LOG` access-log line) so the rules can be validated on real
traffic before they are wired into the served code path.

Spam detection (`is_spam`) is the one classifier that *does* gate production: a
match returns 400 before any ES call.

See docs/query_router_design.md.
"""

import re

from config import SearchMode

# ── Spam / junk-query detection ──────────────────────────────────────────────
# Patterns drawn from zero-result query analysis (search_queries.12may26.sql).
# \b (word boundary) instead of (/|$) catches TLDs mid-sentence: "visit buyfc26coins.com now"
_SPAM_URL_RE = re.compile(r"https?://|www\.|\.[a-z]{3,4}\b", re.IGNORECASE)
_SPAM_PHONE_RE = re.compile(r"^[+0-9 ()\-]{7,}$")
_SPAM_REPEAT_RE = re.compile(r"(.)\1{4,}")  # same char 5+ times in a row
_SPAM_LONGTOKEN_RE = re.compile(r"\S{40,}")  # unbroken 40-char run → no real query
# Indonesian WhatsApp business spam: "WA 0852 2611 9277 Pasang Interior..."
_SPAM_WA_RE = re.compile(r"\bWA\s+08")


def is_spam(query):
    """Return True if the query looks like spam/junk rather than a real search."""
    if not query:
        return False
    q = query.strip()
    if _SPAM_URL_RE.search(q):
        return True
    if _SPAM_PHONE_RE.match(q):
        return True
    if _SPAM_REPEAT_RE.search(q):
        return True
    if _SPAM_LONGTOKEN_RE.search(q):
        return True
    if _SPAM_WA_RE.search(q):
        return True
    # High special-character density: >40% of non-space chars are punctuation/symbols.
    # .isalpha() handles Arabic and other Unicode letters correctly.
    non_space = [c for c in q if not c.isspace()]
    if len(non_space) >= 8:
        special = sum(1 for c in non_space if not c.isalpha() and not c.isdigit())
        if special / len(non_space) > 0.4:
            return True
    return False


# ── Route classification ─────────────────────────────────────────────────────
_ARABIC_RE = re.compile(r"[؀-ۿ]")
# Ends with a number (with or without preceding text) — "bukhari 1", "abu dawud 200", "5", "42".
_REF_RE = re.compile(r"(^|\s)\d+[a-z]?\s*$", re.IGNORECASE)
# Explicit boolean operators in ES query_string syntax.
_BOOL_RE = re.compile(r"\b(AND|OR|NOT)\b")

# variant → routing_decision label for the lexical variants.
_VARIANT_LABEL = {
    "arabic": "lexical_arabic",
    "reference": "lexical_reference",
}


def route_query(query, mode):
    """Classify the query and return (route, variant) — the route the router
    *recommends*, independent of the requested ``mode``.

    route   — "lexical" | SearchMode.SEMANTIC
    variant — None | "arabic" | "reference"

    The recommendation does not consult ``mode``: this is observational, so the
    point is to record what the router would pick, not to echo what the caller
    asked for. (``mode`` is retained in the signature for call-site symmetry with
    the requested-mode logging.)

    Rules (applied in order — earlier rules always win):
      1. Any Arabic character → lexical arabic BM25, full corpus (takes priority over quotes
         so that quoted Arabic still searches the full corpus, not just English docs)
      2. Quoted (≥3 chars) → lexical BM25; query_string handles phrase matching natively
      3. Ends with a number (or IS a number) → lexical reference, forced off semantic
      4. Contains AND/OR/NOT → lexical BM25 (operator syntax, semantic ignores these)
      5. Otherwise → semantic (a plain natural-language query is what semantic is for)
    """
    q = (query or "").strip()

    if _ARABIC_RE.search(q):
        return "lexical", "arabic"

    if len(q) >= 3 and q[0] == '"' and q[-1] == '"':
        return "lexical", None

    if _REF_RE.search(q):
        return "lexical", "reference"

    if _BOOL_RE.search(q):
        return "lexical", None

    return SearchMode.SEMANTIC, None


def routing_decision(query, mode):
    """Single-string label for the route the router would choose, suitable for
    the `routing_decision` metrics column and the ROUTER_LOG line:

        "lexical_arabic" | "lexical_reference" | "semantic" | "lexical"
    """
    route, variant = route_query(query, mode)
    if variant in _VARIANT_LABEL:
        return _VARIANT_LABEL[variant]
    return "semantic" if route == SearchMode.SEMANTIC else "lexical"
