"""
Clean vs Noisy mxbai vector comparison report.

Compares two semantic indexes built with the same model (mxbai-embed-large) but
different source text:

  noisy  — english-mxbai       — hadithText (full text including isnad prefix)
  clean  — english-mxbai-matn  — englishMatn (body only, isnad stripped)

For each priority query, shows:
  - Top-10 results from each index, rank by rank
  - Overlap between the two result sets
  - Hadiths that moved up/down significantly

Run inside the search container (ES not exposed to host):
    docker cp tests/report_clean_vs_noisy.py search-web-1:/tmp/report_clean_vs_noisy.py
    docker exec search-web-1 python3 /tmp/report_clean_vs_noisy.py \
        > "test results & reports/clean_vs_noisy_report.md"

Or from host (slower — goes through Flask semantic endpoint):
    TEST_BASE=http://localhost:5001 python3 tests/report_clean_vs_noisy.py \
        > "test results & reports/clean_vs_noisy_report.md"
"""

import os
import re
import textwrap
from datetime import date
from elasticsearch import Elasticsearch

ES_HOST = os.environ.get("ES_HOST", "http://elasticsearch:9200")
ES_PASS = os.environ.get("ELASTIC_PASSWORD", "123")
ES = Elasticsearch(ES_HOST, basic_auth=("elastic", ES_PASS))

NOISY_INDEX = "english-mxbai"
CLEAN_INDEX  = "english-mxbai-matn"

TOP_N = 10
SIZE  = 100  # fetch more than TOP_N for dedup, then trim

CHAIN_FILTER  = {"bool": {"must_not": {"term": {"isChainRef": True}}}}
EXISTS_FILTER = {"exists": {"field": "hadithText"}}

GOOD_GRADES = {"Sahih", "Hasan"}

# Priority queries — conceptual/topical, where semantic search should shine.
# These are the queries where isnad noise matters most (long narrator chains
# dilute the matn signal in the embedding).
QUERIES = [
    "comparing yourself to others",
    "actions are by intention",
    "prayer at night",
    "day of judgment",
    "gratitude and thankfulness",
    "backbiting and gossip",
    "the status of knowledge",
    "being kind to parents",
    "marriage and divorce",
    "the heart in Islam",
    "music",
    "how to make wudu",
    "fasting in ramadan",
    "giving charity",
]

COLLECTION_RANK = {
    "bukhari": 1, "muslim": 2, "forty": 3, "riyadussalihin": 4,
    "abudawud": 5, "tirmidhi": 6, "nasai": 7, "ibnmajah": 8,
    "malik": 9, "ahmad": 10, "mishkat": 11, "darimi": 12,
}


def sem_search(index, query, size=SIZE):
    try:
        res = ES.search(
            index=index,
            query={
                "bool": {
                    "must": [{"semantic": {"field": "semantic_text", "query": query}}],
                    "filter": [EXISTS_FILTER, CHAIN_FILTER],
                }
            },
            size=size,
            _source=["collection", "hadithNumber", "hadithText", "englishMatn",
                     "gradeNorm", "grade", "isChainRef", "lang"],
        )
        return res["hits"]["hits"]
    except Exception as e:
        return []


def excerpt(text, n=140):
    if not text:
        return "_[no text]_"
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()
    return t[:n] + ("…" if len(t) > n else "")


def grade_tag(src):
    gn = src.get("gradeNorm") or "Uncategorized"
    coll = src.get("collection", "")
    if coll in ("bukhari", "muslim"):
        return f"`Sahih` _(auto)_"
    flag = " ⚠️" if gn in ("Da'if", "Maudu'") else ""
    return f"`{gn}`{flag}"


def hit_id(hit):
    s = hit["_source"]
    return f"{s.get('collection','')}:{s.get('hadithNumber','')}"


def result_block(rank, hit):
    s = hit["_source"]
    score = hit.get("_score", 0)
    coll = s.get("collection", "?")
    num  = s.get("hadithNumber", "?")
    text = excerpt(s.get("hadithText") or "")
    matn = excerpt(s.get("englishMatn") or "", n=100)
    g    = grade_tag(s)
    return (
        f"{rank}. **{coll}:{num}**  {g}  score: `{score:.4f}`  \n"
        f"   {text}  \n"
        f"   _matn: {matn}_"
    )


def run():
    lines = []
    w = lines.append

    # ── Check both indexes are accessible ────────────────────────────────────
    try:
        noisy_info = ES.count(index=NOISY_INDEX)
        noisy_count = noisy_info["count"]
    except Exception as e:
        noisy_count = f"ERROR: {e}"

    try:
        clean_info = ES.count(index=CLEAN_INDEX)
        clean_count = clean_info["count"]
    except Exception as e:
        clean_count = f"ERROR: {e}"

    w("# Clean vs Noisy mxbai Vector Comparison")
    w("")
    w(f"**Date:** {date.today()}  ")
    w(f"**Model:** mxbai-embed-large (same model, different source text)  ")
    w(f"**Noisy index:** `{NOISY_INDEX}` — embeds `hadithText` (full text + isnad) — {noisy_count:,} docs  " if isinstance(noisy_count, int) else f"**Noisy index:** `{NOISY_INDEX}` — {noisy_count}  ")
    w(f"**Clean index:** `{CLEAN_INDEX}` — embeds `englishMatn` (body only, isnad stripped) — {clean_count:,} docs  " if isinstance(clean_count, int) else f"**Clean index:** `{CLEAN_INDEX}` — {clean_count}  ")
    w(f"**Filters:** isChainRef excluded, hadithText exists (English/bilingual only)  ")
    w(f"**Top N shown:** {TOP_N}  ")
    w("")

    if isinstance(clean_count, str):
        w(f"> ⚠️ Clean index not available: {clean_count}")
        w(f"> Build it first: `GET /index?password=...&targets=mxbai-matn&rebuild=true`")
        print("\n".join(lines))
        return

    # ── Per-query comparison ──────────────────────────────────────────────────
    summary_rows = []

    for query in QUERIES:
        w(f"\n---\n## `{query}`\n")

        noisy_hits = sem_search(NOISY_INDEX, query)[:TOP_N]
        clean_hits = sem_search(CLEAN_INDEX, query)[:TOP_N]

        noisy_ids = [hit_id(h) for h in noisy_hits]
        clean_ids = [hit_id(h) for h in clean_hits]

        overlap    = len(set(noisy_ids) & set(clean_ids))
        noisy_only = [hid for hid in noisy_ids if hid not in set(clean_ids)]
        clean_only = [hid for hid in clean_ids if hid not in set(noisy_ids)]

        noisy_good = sum(1 for h in noisy_hits
                         if h["_source"].get("gradeNorm") in GOOD_GRADES
                         or h["_source"].get("collection") in ("bukhari","muslim"))
        clean_good = sum(1 for h in clean_hits
                         if h["_source"].get("gradeNorm") in GOOD_GRADES
                         or h["_source"].get("collection") in ("bukhari","muslim"))

        w(f"**Overlap:** {overlap}/{TOP_N} hadiths appear in both top-{TOP_N}  ")
        w(f"**Noisy-only:** {', '.join(noisy_only) if noisy_only else '—'}  ")
        w(f"**Clean-only:** {', '.join(clean_only) if clean_only else '—'}  ")
        w(f"**Sahih/Hasan in top-{TOP_N}:** noisy={noisy_good}  clean={clean_good}  ")
        w("")

        w(f"### Noisy (`hadithText`)\n")
        if noisy_hits:
            for i, h in enumerate(noisy_hits, 1):
                marker = "🆕 " if hit_id(h) in set(clean_only) else ""
                w(result_block(f"{marker}{i}", h))
                w("")
        else:
            w("_No results_")

        w(f"### Clean (`englishMatn`)\n")
        if clean_hits:
            for i, h in enumerate(clean_hits, 1):
                marker = "🆕 " if hit_id(h) in set(noisy_only) else ""
                w(result_block(f"{marker}{i}", h))
                w("")
        else:
            w("_No results_")

        summary_rows.append((query, overlap, noisy_good, clean_good))

    # ── Summary table ─────────────────────────────────────────────────────────
    w(f"\n---\n## Summary\n")
    w(f"| Query | Overlap/{TOP_N} | Noisy Sahih/Hasan | Clean Sahih/Hasan | Winner |")
    w(f"|-------|--------------|-------------------|-------------------|--------|")
    for query, overlap, ng, cg in summary_rows:
        if cg > ng:
            winner = "clean ✅"
        elif ng > cg:
            winner = "noisy"
        else:
            winner = "tie"
        short_q = query[:40] + ("…" if len(query) > 40 else "")
        w(f"| `{short_q}` | {overlap} | {ng} | {cg} | {winner} |")

    w("")
    w("**Overlap** = hadiths appearing in both top-10 result sets.  ")
    w("Low overlap = the two indexes return substantially different results for the same query.  ")
    w("**Sahih/Hasan** = count of Sahih/Hasan-graded hadiths in top-10 (higher is better).  ")
    w("🆕 = hadith unique to this index (not in the other's top-10).  ")

    print("\n".join(lines))


if __name__ == "__main__":
    run()
