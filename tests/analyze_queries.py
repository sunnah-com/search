"""
Stream-parse search_queries.12may26.sql and report:
  - Top 100 multi-word queries (by total search frequency)
  - Top 100 multi-word zero-result queries (numResults = 0)

"Multi-word" = query contains at least one whitespace character (works for
English, Arabic, and any other script). Single-word queries are excluded.

Run from the repo root:
    python3 search/analyze_queries.py
"""
import re
import sys
from collections import Counter

SQL_PATH = "search_queries.12may26.sql"
TOP_N = 100

# Each data row looks like:
# (12345,'the query text','2024-01-01 00:00:00','1.2.3.4',7),
ROW_RE = re.compile(
    r"^\(\d+,'(.*?)','(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})','[^']+',(\d+)\),?$"
)

def normalize(q):
    return q.replace("''", "'").strip().lower()

def is_multiword(q):
    return len(q.split()) >= 2

all_queries   = Counter()
zero_result   = Counter()
total_rows    = 0
skipped_parse = 0

print(f"Streaming {SQL_PATH} …", flush=True)

with open(SQL_PATH, encoding="utf-8", errors="replace") as fh:
    for line in fh:
        if not line.startswith("("):
            continue
        m = ROW_RE.match(line.rstrip())
        if not m:
            skipped_parse += 1
            continue

        query      = normalize(m.group(1))
        num_results = int(m.group(3))
        total_rows += 1

        if total_rows % 5_000_000 == 0:
            print(f"  {total_rows:,} rows processed …", flush=True)

        if not is_multiword(query):
            continue

        all_queries[query] += 1
        if num_results == 0:
            zero_result[query] += 1

print(f"\nDone. {total_rows:,} total rows | {skipped_parse:,} unparseable lines\n")
print(f"Unique multi-word queries:              {len(all_queries):,}")
print(f"Unique multi-word zero-result queries:  {len(zero_result):,}")

def write_report(path, title, counter):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"| Rank | Count | Query |\n")
        f.write(f"|------|-------|-------|\n")
        for rank, (query, count) in enumerate(counter.most_common(TOP_N), 1):
            escaped = query.replace("|", "\\|")
            f.write(f"| {rank} | {count:,} | {escaped} |\n")
    print(f"Written: {path}")

write_report(
    "search/test results & reports/top100_multiword_queries.md",
    "Top 100 Multi-Word Search Queries",
    all_queries,
)
write_report(
    "search/test results & reports/top100_multiword_zero_results.md",
    "Top 100 Multi-Word Queries with Zero Results",
    zero_result,
)
