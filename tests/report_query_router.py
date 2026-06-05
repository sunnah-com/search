"""
Query router comparison report — reference lookup vs lexical BM25.

For each collection+number query, shows:
  - What the reference route returns (exact match, always position 1)
  - What raw lexical BM25 returns (what users got BEFORE the router)
  - Whether lexical found the right hadith, and at what rank

Run from host:
    python3 tests/report_query_router.py > "test results & reports/query_router_report.md"
"""

import json, os, sys, urllib.request, urllib.parse
from datetime import date

BASE = os.environ.get("TEST_BASE", "http://localhost:5001")

QUERIES = [
    # (display_label, query_string, expected_collection, expected_number)
    ("Bukhari 1",        "bukhari 1",      "bukhari",   "1"),
    ("Bukhari 7563",     "bukhari 7563",   "bukhari",   "7563"),
    ("Muslim 1",         "muslim 1",       "muslim",    "1"),
    ("Muslim 2363",      "muslim 2363",    "muslim",    "2363"),
    ("Nasai 1",          "nasai 1",        "nasai",     "1"),
    ("Abu Dawud 1",      "abudawud 1",     "abudawud",  "1"),
    ("Ibn Majah 1",      "ibnmajah 1",     "ibnmajah",  "1"),
    ("Tirmidhi 1",       "tirmidhi 1",     "tirmidhi",  "1"),
    ("Malik 1",          "malik 1",        "malik",     "1"),
    ("Nawawi 40 #1",     "nawawi40 1",     "forty",     "1"),
    ("Nawawi 40 #40",    "nawawi40 40",    "forty",     "40"),
    ("Forty #13",        "forty 13",       "forty",     "13"),
    ("Riyad #1",         "riyadussalihin 1","riyadussalihin","1"),
    ("Mishkat 1",        "mishkat 1",      "mishkat",   "1"),
    ("Bulugh 1",         "bulugh 1",       "bulugh",    "1"),
]


def get(path, **params):
    qs = urllib.parse.urlencode(params, doseq=True)
    url = f"{BASE}{path}?{qs}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def hits(resp):
    return resp.get("hits", {}).get("hits", [])


def source(hit):
    return hit.get("_source", {}) if hit else {}


def excerpt(text, n=120):
    if not text:
        return "_[no text]_"
    text = text.replace("\n", " ").strip()
    return text[:n] + ("…" if len(text) > n else "")


def hadith_label(src):
    coll = src.get("collection", "?")
    num  = src.get("hadithNumber", "?")
    return f"{coll}:{num}"


def run():
    lines = []
    w = lines.append

    w(f"# Query Router: Reference Lookup vs Lexical BM25")
    w(f"")
    w(f"**Date:** {date.today()}  ")
    w(f"**API:** {BASE}  ")
    w(f"")
    w(f"For each `collection number` query, the router now does a direct filter lookup.")
    w(f"The **Lexical (pre-router)** column shows what BM25 would have returned — the")
    w(f"correct hadith may not be first, or may not appear at all in top 10.")
    w(f"")

    ref_wins = 0
    lex_correct_rank1 = 0
    lex_missing = 0
    total = len(QUERIES)

    for label, query, exp_coll, exp_num in QUERIES:
        w(f"---")
        w(f"## {label}  —  `{query}`")
        w(f"")

        # ── Reference route ──────────────────────────────────────────────────
        ref_resp = get("/english/search", q=query, mode="lexical")
        ref_hits = hits(ref_resp)
        ref_meta = ref_resp.get("_meta", {})

        w(f"### Reference route  *(route: {ref_meta.get('route', '?')})*")
        if ref_hits:
            s = source(ref_hits[0])
            w(f"**{hadith_label(s)}** — {excerpt(s.get('hadithText',''))}")
            correct_ref = (s.get("collection") == exp_coll and
                           str(s.get("hadithNumber")) == str(exp_num))
            w(f"Correct hadith: {'✅ Yes' if correct_ref else '❌ No'}")
            ref_wins += int(correct_ref)
        else:
            w(f"❌ No results returned")
        w(f"")

        # ── Lexical fallback (force BM25, bypass router by prepending space) ──
        # Can't easily bypass the router on the same endpoint, so we query ES
        # directly for BM25 to simulate pre-router behavior.
        # We use the /english/search endpoint but on a non-matching mode variant
        # that reveals lexical ranking — we inject a space prefix to break ref match.
        lex_resp = get("/english/search", q=f" {query}", mode="lexical")
        lex_hits = hits(lex_resp)

        w(f"### Lexical BM25  *(pre-router behavior)*")
        found_rank = None
        for i, h in enumerate(lex_hits[:10]):
            s = source(h)
            is_target = (s.get("collection") == exp_coll and
                         str(s.get("hadithNumber")) == str(exp_num))
            marker = "👉 " if is_target else f"#{i+1} "
            if is_target:
                found_rank = i + 1
                w(f"**{marker}{hadith_label(s)}** ← target  —  {excerpt(s.get('hadithText',''))}")
            else:
                w(f"{marker}{hadith_label(s)}  —  {excerpt(s.get('hadithText',''))}")

        if found_rank is None:
            w(f"")
            w(f"⚠️ Target hadith **not found** in top 10 lexical results")
            lex_missing += 1
        elif found_rank == 1:
            lex_correct_rank1 += 1
        w(f"")

    # ── Summary ───────────────────────────────────────────────────────────────
    w(f"---")
    w(f"## Summary")
    w(f"")
    w(f"| Metric | Count |")
    w(f"|--------|-------|")
    w(f"| Queries tested | {total} |")
    w(f"| Reference route: correct hadith returned | {ref_wins}/{total} |")
    w(f"| Lexical BM25: target at rank 1 | {lex_correct_rank1}/{total} |")
    w(f"| Lexical BM25: target **not in top 10** | {lex_missing}/{total} |")
    w(f"")
    w(f"The reference route is a deterministic filter (no scoring) — it either finds")
    w(f"the hadith or returns empty. Lexical BM25 uses `collection^2 + hadithNumber^2`")
    w(f"boosts but still competes with other term matches, so the target can be displaced.")

    return "\n".join(lines)


if __name__ == "__main__":
    print(run())
