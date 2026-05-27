"""
Batch search across all semantic models + lexical — production approach (size=100, HNSW).
Outputs: batch_results.csv and batch_report.md in /code/ inside the container.

WHY run inside the container:
    ES is not exposed to the host. It only resolves at http://elasticsearch:9200
    from within the Docker network (search-web-1 is on that network).

STEP 1 — copy the script into the container:
    docker cp search/batch_search.py search-web-1:/code/batch_search.py

STEP 2 — run it:
    docker exec search-web-1 python3 /code/batch_search.py

STEP 3 — copy results back to your local machine:
    docker cp search-web-1:/code/batch_results.csv search/batch_results.csv
    docker cp search-web-1:/code/batch_report.md   search/batch_report.md

One-liner (copy in, run, copy results out):
    docker cp search/batch_search.py search-web-1:/code/batch_search.py && \
    docker exec search-web-1 python3 /code/batch_search.py && \
    docker cp search-web-1:/code/batch_results.csv search/batch_results.csv && \
    docker cp search-web-1:/code/batch_report.md search/batch_report.md

To add/remove queries: edit QUERIES below.
To change how many results are fetched per model per query: edit SIZE.
To change how many are shown in the markdown report: edit REPORT_TOP_N.

NOTE: always include commas between query strings — Python silently concatenates
adjacent string literals without a comma, producing wrong queries with no error.
"""
import csv
import os
import re
import textwrap
from datetime import date
from elasticsearch import Elasticsearch, BadRequestError

ES_HOST = os.environ.get("ES_HOST", "http://elasticsearch:9200")
ES_PASS = os.environ.get("ELASTIC_PASSWORD", "123")
ES = Elasticsearch(ES_HOST, basic_auth=("elastic", ES_PASS))

LEXICAL_INDEX = "english-lexical"

LEXICAL_FIELDS = ["hadithNumber^2", "hadithText", "arabicText", "collection^2"]

COLLECTION_BOOSTS = [
    ("bukhari", 5.0), ("muslim", 4.8), ("nasai", 3.5), ("abudawud", 3.0),
    ("tirmidhi", 2.5), ("ibnmajah", 2.0), ("malik", 2.5), ("ahmad", 2.5),
    ("darimi", 2.0), ("mishkat", 2.5), ("nawawi40", 3.3), ("riyadussalihin", 2.5),
]

SEMANTIC_INDEXES = {
    "openai-small-en":    "english-openai-small-1779045411",
    #"openai-small-multi": "multilingual-openai-small-1779017104",
    "nomic":              "english-nomic-1779026769",
    "mxbai":              "english-mxbai-1779026713",
}

QUERIES = [
    "comparing yourself to others",
    "aisha six years",
    "music",
    "actions are by intentions",
    "ramadan",
    "jesus",
    "sex",
    "marriage",
    "masturbation",
    "racism",
    "polygamy",
    "pork",
    "dance"
,]

SIZE = 100   # fetch this many; report shows top 10 per model per query
REPORT_TOP_N = 10

OUT_DIR = "/code"
CSV_PATH = os.path.join(OUT_DIR, "batch_results.csv")
MD_PATH  = os.path.join(OUT_DIR, "batch_report.md")


def lexical_search(query, size=SIZE):
    def _build(query_type):
        inner = {"query": query, "fields": LEXICAL_FIELDS}
        if query_type == "query_string":
            inner["type"] = "cross_fields"
        return {
            "function_score": {
                "query": {"bool": {"must": [{query_type: inner}]}},
                "functions": [
                    {"filter": {"term": {"collection": name}}, "weight": w}
                    for name, w in COLLECTION_BOOSTS
                ],
                "score_mode": "sum",
                "boost_mode": "sum",
            }
        }

    kwargs = dict(
        index=LEXICAL_INDEX,
        size=size,
        track_total_hits=True,
        _source=["hadithText", "collection", "hadithNumber", "urn"],
    )
    try:
        res = ES.search(query=_build("query_string"), **kwargs)
    except BadRequestError:
        res = ES.search(query=_build("simple_query_string"), **kwargs)
    return res["hits"]["hits"], res["hits"]["total"]["value"]


def semantic_search(index, query, size=SIZE):
    res = ES.search(
        index=index,
        query={"semantic": {"field": "semantic_text", "query": query}},
        size=size,
        track_total_hits=True,
        _source=["hadithText", "collection", "hadithNumber", "urn"],
    )
    return res["hits"]["hits"], res["hits"]["total"]["value"]


def query_anchor(query):
    s = f'query: "{query}"'
    s = s.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    return s


def snippet(text, width=160):
    if not text:
        return ""
    return textwrap.shorten(text.replace("\n", " ").strip(), width=width, placeholder="…")


def run():
    csv_rows = []
    md_sections = []

    all_models = {"lexical": None, **SEMANTIC_INDEXES}

    md_sections.append(f"# Batch Search Report")
    md_sections.append(f"**Date:** {date.today()}  ")
    md_sections.append(f"**Models:** {', '.join(all_models)}  ")
    md_sections.append(f"**Method:** lexical = BM25 + collection boosts; semantic = HNSW `size={SIZE}`  ")
    md_sections.append(f"**Queries:** {len(QUERIES)}, report shows top {REPORT_TOP_N} per model")
    md_sections.append("")

    # Table of contents
    md_sections.append("## Queries")
    for query in QUERIES:
        md_sections.append(f"- [{query}](#{query_anchor(query)})")
    md_sections.append("")

    for query in QUERIES:
        print(f"\nQuery: {query!r}")
        md_sections.append(f"---\n\n## Query: \"{query}\"\n")

        for model_name, index in all_models.items():
            print(f"  [{model_name}] ...", end=" ", flush=True)
            try:
                if model_name == "lexical":
                    hits, total = lexical_search(query, size=SIZE)
                else:
                    hits, total = semantic_search(index, query, size=SIZE)
                print(f"{len(hits)} hits (total: {total})")
            except Exception as e:
                print(f"ERROR: {e}")
                md_sections.append(f"### {model_name}\n\n_Error: {e}_\n")
                continue

            md_sections.append(f"### {model_name} — {total} total hits\n")

            for rank, h in enumerate(hits[:REPORT_TOP_N], 1):
                src = h["_source"]
                score = round(h["_score"], 4)
                collection = src.get("collection", "")
                hadith_num = src.get("hadithNumber", "")
                text = src.get("hadithText", "")
                urn = src.get("urn", "")

                csv_rows.append({
                    "query":        query,
                    "model":        model_name,
                    "rank":         rank,
                    "collection":   collection,
                    "hadithNumber": hadith_num,
                    "urn":          urn,
                    "score":        score,
                    "text_snippet": snippet(text, width=500),
                })

                md_sections.append(f"**#{rank}** — {collection} {hadith_num} · score: {score}")
                md_sections.append(f"> {snippet(text, width=600)}\n")

            md_sections.append("")

    # Write CSV
    fieldnames = ["query", "model", "rank", "collection", "hadithNumber", "urn", "score", "text_snippet"]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"\nCSV  → {CSV_PATH}")

    # Write markdown
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_sections) + "\n")
    print(f"MD   → {MD_PATH}")
    print(f"Rows: {len(csv_rows)} ({len(QUERIES)} queries × {len(all_models)} models × up to {REPORT_TOP_N})")


if __name__ == "__main__":
    run()
