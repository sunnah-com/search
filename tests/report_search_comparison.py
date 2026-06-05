"""
Search comparison report.

Sections:
  1. Routing verification — route taken per query + lang distribution
  2. BM25 hadithText vs englishMatn — top 10 per query, grade details
  3. Arabic queries — arabicText BM25, lang distribution, variant spellings

Designed to run inside the search container (access to ES + Flask):
    docker cp tests/report_search_comparison.py search-web-1:/tmp/report_search_comparison.py
    docker exec search-web-1 python3 /tmp/report_search_comparison.py \
        > "test results & reports/search_comparison.md"

Or from host if FLASK_BASE env is set:
    TEST_BASE=http://localhost:5001 python3 tests/report_search_comparison.py
"""

import json, os, re, urllib.request, urllib.parse
from datetime import date
from elasticsearch import Elasticsearch

FLASK = os.environ.get("FLASK_BASE", "http://localhost:5000")
ES    = Elasticsearch(
    os.environ.get("ES_HOST", "http://elasticsearch:9200"),
    basic_auth=("elastic", os.environ.get("ELASTIC_PASSWORD", "123")),
    request_timeout=30,
)
INDEX = "english-mxbai"

CHAIN_FILTER = {"bool": {"must_not": {"term": {"isChainRef": True}}}}

# ── Queries ────────────────────────────────────────────────────────────────────
ENGLISH_QUERIES = [
    ("comparing yourself to others",   False),   # (query, is_phrase)
    ("aisha",                          False),
    ('"actions are by intention"',     True),    # quoted → phrase route
    ("actions are by intention",       False),   # same, unquoted
    ("how to make wudu",               False),
    ("ramadan",                        False),
    ("music",                          False),
]

ARABIC_QUERIES = [
    "الرحمن",
    "الرحمان",
    "الرحمٰن",
    "الرحمن قد اشتق من الرحم",
]

CAUTION_GRADES = {"Da'if", "Maudu'"}


# ── Helpers ────────────────────────────────────────────────────────────────────
def flask_get(path, **params):
    qs = urllib.parse.urlencode(params, doseq=True)
    url = f"{FLASK}{path}?{qs}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e), "_meta": {}}


def strip_html(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()


def excerpt(text, n=110):
    t = strip_html(text)
    return t[:n] + ("…" if len(t) > n else "") if t else "_[empty]_"


def grade_info(src):
    """Returns (gradeNorm, raw_grade_display, reason)."""
    gn   = src.get("gradeNorm") or "Uncategorized"
    raw  = src.get("grade") or ""
    coll = src.get("collection", "")

    if coll in ("bukhari", "muslim"):
        reason = f"{coll.title()} collection (auto-Sahih)"
    elif raw.startswith("[") or raw.startswith("{"):
        # JSON blob — extract inner grade string
        m = re.search(r'"grade"\s*:\s*"([^"]+)"', raw)
        inner = m.group(1) if m else raw[:40]
        reason = f"graded: {inner}"
    elif raw:
        cleaned = re.sub(r"\s*\([^)]+\)", "", raw).strip()
        reason  = f"graded: {cleaned}"
    else:
        reason = "no grade data"

    raw_display = raw[:60].replace("\n", " ") if raw else "—"
    return gn, raw_display, reason


def caution(gn):
    return " ⚠️" if gn in CAUTION_GRADES else ""


def result_line(rank, hit, show_lang=False):
    s   = hit["_source"]
    sc  = hit.get("_score", 0)
    gn, raw_g, reason = grade_info(s)
    coll = s.get("collection", "?")
    num  = s.get("hadithNumber", "?")
    lang = s.get("lang", "?")
    chain = " 🔗" if s.get("isChainRef") else ""
    text  = excerpt(s.get("hadithText") or s.get("arabicText") or "")
    lang_tag = f" `[{lang}]`" if show_lang else ""
    return (
        f"{rank}. **{coll}:{num}**{lang_tag}{chain}  "
        f"`{gn}`{caution(gn)} _(raw: {raw_g} | {reason})_  \n"
        f"   {text}  \n"
        f"   score: {sc:.3f}"
    )


def es_search(query_body, size=10, source_fields=None):
    kw = dict(index=INDEX, query=query_body, size=size,
              _source=source_fields or ["collection", "hadithNumber", "lang",
                                        "hadithText", "arabicText", "englishMatn",
                                        "grade", "gradeNorm", "isChainRef"])
    return ES.search(**kw)


def bm25_hadith(query, size=10):
    return es_search({
        "bool": {
            "must": [{"match": {"hadithText": query}}],
            "filter": [CHAIN_FILTER],
        }
    }, size=size)


def bm25_matn(query, size=10):
    return es_search({
        "bool": {
            "must": [{"match": {"englishMatn": query}}],
            "filter": [CHAIN_FILTER],
        }
    }, size=size)


def bm25_arabic(query, size=10):
    return es_search({
        "bool": {
            "must": [{"match": {"arabicText": {"query": query, "analyzer": "custom_arabic"}}}],
            "filter": [CHAIN_FILTER],
        }
    }, size=size)


def lang_dist(hits):
    en = sum(1 for h in hits if h["_source"].get("lang") == "en")
    ar = sum(1 for h in hits if h["_source"].get("lang") == "ar")
    return f"en:{en} ar:{ar}"


# ── Report builder ────────────────────────────────────────────────────────────
lines = []
w = lines.append


def section(title):
    w(f"\n---\n## {title}\n")


def subsection(title):
    w(f"\n### {title}\n")


def subsubsection(title):
    w(f"\n#### {title}\n")


# ── Header ────────────────────────────────────────────────────────────────────
w(f"# Search Comparison Report")
w(f"")
w(f"**Date:** {date.today()}  ")
w(f"**Index:** `{INDEX}` — English hadiths + bilingual pairs  ")
w(f"**isChainRef filter:** always applied (pure isnad chains excluded)  ")
w(f"**Grade flags:** ⚠️ = Da'if or Maudu' | 🔗 = isChainRef (would be excluded)  ")
w(f"**Grade reason:** auto-Sahih for Bukhari/Muslim; otherwise from raw grade field  ")
w(f"")

# ══════════════════════════════════════════════════════════════════
# PART 1: ROUTING VERIFICATION
# ══════════════════════════════════════════════════════════════════
section("Part 1 — Routing Verification")
w("Checks which route the query router selects for each query.")
w("English queries should only return `lang:en` docs; Arabic queries return all.")
w("")
w("| Query | Route | lang dist (top 10) | Correct? |")
w("|-------|-------|-------------------|---------|")

all_queries = [(q, False, "english") for q, _ in ENGLISH_QUERIES] + \
              [(q, False, "arabic")  for q in ARABIC_QUERIES]

for raw_q, _, expected_lang in all_queries:
    resp  = flask_get("/english/search", q=raw_q, mode="lexical")
    meta  = resp.get("_meta", {})
    route = meta.get("route", resp.get("error", "error")[:30])
    h     = resp.get("hits", {}).get("hits", [])
    dist  = lang_dist(h) if h else "no hits"
    # For English queries: expect no lang:ar hits; for Arabic: mixed OK
    en_count = sum(1 for x in h if x["_source"].get("lang") == "en")
    ar_count = sum(1 for x in h if x["_source"].get("lang") == "ar")
    if expected_lang == "english":
        ok = "✅" if ar_count == 0 else f"⚠️ {ar_count} ar docs leaked"
    else:
        ok = "✅" if len(h) > 0 else "❌ no hits"
    display_q = raw_q.replace("|", "\\|")
    w(f"| `{display_q}` | {route} | {dist} | {ok} |")

# ══════════════════════════════════════════════════════════════════
# PART 2: BM25 — hadithText vs englishMatn
# ══════════════════════════════════════════════════════════════════
section("Part 2 — BM25: hadithText vs englishMatn")
w("""**hadithText** = full hadith including isnad prefix ("Narrated X that Y said…").
**englishMatn** = body only, isnad stripped (cleaner signal, smaller vocab match).
""")

for raw_q, is_phrase in ENGLISH_QUERIES:
    q = raw_q.strip('"')   # strip quotes for BM25 (router handles phrase, we test BM25 directly)
    subsection(f"`{raw_q}`")

    # hadithText
    subsubsection("hadithText (BM25)")
    try:
        res = bm25_hadith(q)
        hits = res["hits"]["hits"]
        total = res["hits"]["total"]["value"]
        w(f"_{total:,} total matches_\n")
        if hits:
            for i, h in enumerate(hits, 1):
                w(result_line(i, h))
                w("")
        else:
            w("_No results_")
    except Exception as e:
        w(f"_Error: {e}_")

    # englishMatn
    subsubsection("englishMatn (BM25)")
    try:
        res = bm25_matn(q)
        hits = res["hits"]["hits"]
        total = res["hits"]["total"]["value"]
        w(f"_{total:,} total matches_\n")
        if hits:
            for i, h in enumerate(hits, 1):
                w(result_line(i, h))
                w("")
        else:
            w("_No results_")
    except Exception as e:
        w(f"_Error: {e}_")

# ══════════════════════════════════════════════════════════════════
# PART 3: ARABIC QUERIES
# ══════════════════════════════════════════════════════════════════
section("Part 3 — Arabic Queries")
w("""Arabic queries route to `lexical_arabic` (BM25 on arabicText with Arabic analyzer).
All docs — both Arabic-only and bilingual — are searched.
Results show `[lang]` tag so you can see the mix.
Note: الرحمن / الرحمان / الرحمٰن are spelling variants — differences reveal analyzer normalization.
""")

for aq in ARABIC_QUERIES:
    subsection(f"`{aq}`")
    try:
        res  = bm25_arabic(aq)
        hits = res["hits"]["hits"]
        total = res["hits"]["total"]["value"]
        w(f"_{total:,} total matches, lang dist: {lang_dist(hits)}_\n")
        if hits:
            for i, h in enumerate(hits, 1):
                w(result_line(i, h, show_lang=True))
                w("")
        else:
            w("_No results — analyzer may not normalize this variant_")
    except Exception as e:
        w(f"_Error: {e}_")

# ── Variant analysis ──────────────────────────────────────────────────────────
subsection("Arabic variant analysis")
w("Checking if the Arabic analyzer normalizes الرحمن / الرحمان / الرحمٰن to the same tokens:\n")

counts = {}
for aq in ["الرحمن", "الرحمان", "الرحمٰن", "الرحمن قد اشتق من الرحم"]:
    try:
        res = bm25_arabic(aq, size=1)
        counts[aq] = res["hits"]["total"]["value"]
    except Exception:
        counts[aq] = "error"

w("| Query | Total hits |")
w("|-------|-----------|")
for aq, c in counts.items():
    w(f"| `{aq}` | {c:,} |" if isinstance(c, int) else f"| `{aq}` | {c} |")

w("""
If الرحمن and الرحمان return the same count, the analyzer normalizes alef variants.
If الرحمٰن (with superscript alef) returns fewer, it may not be normalized.
""")

# ── Footer ────────────────────────────────────────────────────────────────────
section("Next: Semantic Model Comparison")
w("""Semantic models (small-model-eval index) require query embedding inside the container.
Run `small_model_comparison.py` to compare all 12 models × hadithText + englishMatn inputs.
Multilingual models (`multilingual-e5`, `english-openai-large`) will be a separate section.
""")

print("\n".join(lines))
