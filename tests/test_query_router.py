"""
Query router integration tests — runs against the live Flask API on localhost:5001.

Tests three routes:
  1. Phrase search     — "prayer at night" (quoted)
  2. Arabic BM25       — صلاة الليل
  3. Semantic/lexical  — normal English query, both modes

Also tests:
  - Route values in _meta.route on every path
  - Mode override priority (Arabic/phrase beat ?mode=semantic)
  - Arabic route searches full corpus (no language restriction)

Collection+number queries ("bukhari 1") are handled by the standard lexical
BM25 path — hadithNumber^2 and collection^2 boosts surface the correct hadith
naturally without a dedicated reference route.

Run from the host (Flask is exposed at localhost:5001):
    python3 tests/test_query_router.py

Or inside the container (Flask on localhost:5000):
    python3 /code/tests/test_query_router.py
"""

import json
import re
import sys
import urllib.request
import urllib.parse
import os

_ARABIC_RE = re.compile(r"[؀-ۿ]")

# ── Config ─────────────────────────────────────────────────────────────────────
BASE = os.environ.get("TEST_BASE", "http://localhost:5001")
LANG = "english"
# Which model to use for semantic smoke-tests. Defaults to mxbai (always indexed
# locally). Override with TEST_SEMANTIC_MODEL if testing a different model index.
SEMANTIC_MODEL = os.environ.get("TEST_SEMANTIC_MODEL", "mxbai")

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"


# ── Helpers ────────────────────────────────────────────────────────────────────
def get(path, **params):
    qs = urllib.parse.urlencode(params, doseq=True)
    url = f"{BASE}{path}?{qs}" if qs else f"{BASE}{path}"
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read())


def search(q, mode="lexical", **extra):
    return get(f"/{LANG}/search", q=q, mode=mode, **extra)


def hits(resp):
    return resp.get("hits", {}).get("hits", [])


def first_hit(resp):
    h = hits(resp)
    return h[0] if h else None


def source(hit):
    return hit.get("_source", {}) if hit else {}


def meta(resp):
    return resp.get("_meta", {})


# ── Test runner ────────────────────────────────────────────────────────────────
results = []

def check(name, condition, detail=""):
    ok = bool(condition)
    tag = PASS if ok else FAIL
    msg = f"  [{tag}] {name}"
    if detail:
        msg += f"  ({detail})"
    print(msg)
    results.append((name, ok))
    return ok


def section(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ══════════════════════════════════════════════════════════════════
# 1. PHRASE SEARCH
# ══════════════════════════════════════════════════════════════════
section('1. Phrase search  ("quoted query")')

phrase_cases = [
    '"prayer at night"',
    '"Messenger of Allah"',
    '"Day of Judgement"',
    '"صلاة الليل"',        # quoted Arabic → phrase route (not arabic route)
]

for q in phrase_cases:
    try:
        resp = search(q)
        m = meta(resp)
        h = hits(resp)
        check(
            f'{q} → lexical/phrase route',
            m.get("route") == "lexical_phrase",
            f'route={m.get("route")}'
        )
        inner = q.strip('"')
        if h:
            if _ARABIC_RE.search(inner):
                # Arabic phrases: the custom_arabic analyzer normalizes diacritics
                # at query time, so stored text won't contain the raw substring.
                # Routing is verified above; just confirm results came back.
                check(
                    f'{q} → phrase route returned results',
                    len(h) > 0,
                    f'{len(h)} hits returned'
                )
            else:
                def phrase_in_hit(hit):
                    s = source(hit)
                    return (inner.lower() in s.get("hadithText", "").lower()
                            or inner.lower() in s.get("arabicText", "").lower())
                match_count = sum(phrase_in_hit(hit) for hit in h[:5])
                check(
                    f'{q} → ≥4/5 top hits contain phrase',
                    match_count >= 4,
                    f'{match_count}/5 hits match'
                )
    except Exception as e:
        check(f'{q} → no exception', False, str(e))


# ══════════════════════════════════════════════════════════════════
# 2. ARABIC BM25
# ══════════════════════════════════════════════════════════════════
section("2. Arabic text → BM25 on arabicText")

arabic_cases = [
    ("صلاة الليل", "night prayer"),
    ("الزكاة",     "zakat"),
    ("رمضان",      "ramadan"),
]

for arabic_q, hint in arabic_cases:
    try:
        resp = search(arabic_q)
        m = meta(resp)
        h = hits(resp)
        check(
            f'"{arabic_q}" ({hint}) → lexical/arabic route',
            m.get("route") == "lexical_arabic",
            f'route={m.get("route")}'
        )
        if h:
            check(
                f'"{arabic_q}" → hits have arabicText',
                bool(source(h[0]).get("arabicText")),
                f'first hit arabicText present: {bool(source(h[0]).get("arabicText"))}'
            )
    except Exception as e:
        check(f'"{arabic_q}" → no exception', False, str(e))


# ══════════════════════════════════════════════════════════════════
# 3. SEMANTIC vs LEXICAL PASSTHROUGH
# ══════════════════════════════════════════════════════════════════
section("3. Semantic / lexical mode passthrough")

query = "prayer during travel"

try:
    lex = search(query, mode="lexical")
    sem = search(query, mode="semantic", model=SEMANTIC_MODEL)
    lex_ids = [h["_id"] for h in hits(lex)[:10]]
    sem_ids = [h["_id"] for h in hits(sem)[:10]]
    check(
        "lexical and semantic return results",
        bool(lex_ids) and bool(sem_ids),
        f"lex={len(lex_ids)}, sem={len(sem_ids)}"
    )
    overlap = len(set(lex_ids) & set(sem_ids))
    check(
        "semantic and lexical top-10 are not identical (different ranking)",
        lex_ids != sem_ids,
        f"overlap={overlap}/10"
    )
except Exception as e:
    check("semantic/lexical passthrough → no exception", False, str(e))


# ══════════════════════════════════════════════════════════════════
# 4. COLLECTION+NUMBER QUERIES — handled by standard lexical BM25
# ══════════════════════════════════════════════════════════════════
section("4. Collection+number queries → lexical_reference (forced lexical, same BM25)")

# Any query ending with a number → forced lexical regardless of ?mode=.
# Includes multi-word collection names. BM25 unchanged; detection prevents semantic.
# Single-word collection names: BM25 matches the collection token directly,
# so rank-1 is reliable.
ref_cases_exact = [
    ("bukhari 1",       "bukhari",   "1"),
    ("bukhari 6594",    "bukhari",   "6594"),
    ("muslim 2363",     "muslim",    "2363"),
    ("nasai 3",         "nasai",     "3"),
    ("forty 1",         "forty",     "1"),
]

for query, expected_coll, expected_num in ref_cases_exact:
    try:
        resp = search(query)
        m = meta(resp)
        h = first_hit(resp)
        s = source(h)
        check(
            f'"{query}" → lexical_reference route',
            m.get("route") == "lexical_reference",
            f'route={m.get("route")}'
        )
        check(
            f'"{query}" → correct hadith at rank 1',
            s.get("collection") == expected_coll and
            str(s.get("hadithNumber")) == expected_num,
            f'got {s.get("collection")}:{s.get("hadithNumber")}'
        )
    except Exception as e:
        check(f'"{query}" → no exception', False, str(e))

# Multi-word collection names ("abu dawud", "ibn majah"): stored as compound tokens
# ("abudawud", "ibnmajah") so the query words don't match — rank-1 is unreliable.
# Route detection still works; rank fix requires synonyms on the collection field.
ref_cases_route_only = [
    "abu dawud 1",
    "ibn majah 1",
]

for query in ref_cases_route_only:
    try:
        resp = search(query)
        m = meta(resp)
        h = hits(resp)
        check(
            f'"{query}" → lexical_reference route',
            m.get("route") == "lexical_reference",
            f'route={m.get("route")}'
        )
        check(
            f'"{query}" → returns results',
            len(h) > 0,
            f'{len(h)} hits'
        )
    except Exception as e:
        check(f'"{query}" → no exception', False, str(e))

# Misspelled collection — still ends with a number so regex matches → lexical_reference.
# BM25 surfaces the right hadith anyway via hadithNumber^2 + collection^2 boosts.
for q in ["bukahri 1", "bukahri 7563"]:
    try:
        resp = search(q)
        m = meta(resp)
        h = hits(resp)
        check(
            f'"{q}" (misspelled) → lexical_reference (ends with number)',
            m.get("route") == "lexical_reference",
            f'route={m.get("route")}'
        )
        check(
            f'"{q}" (misspelled) → returns results',
            len(h) > 0,
            f'{len(h)} hits'
        )
    except Exception as e:
        check(f'"{q}" misspelled → no exception', False, str(e))

# Standalone numbers — no preceding text, still ends with a number → lexical_reference.
for q in ["5", "42", "1234"]:
    try:
        resp = search(q)
        m = meta(resp)
        check(
            f'"{q}" (standalone number) → lexical_reference',
            m.get("route") == "lexical_reference",
            f'route={m.get("route")}'
        )
    except Exception as e:
        check(f'"{q}" standalone number → no exception', False, str(e))


# ══════════════════════════════════════════════════════════════════
# 5. EXPLICIT ROUTE VALUES IN _meta
# ══════════════════════════════════════════════════════════════════
section("5. Explicit route values in _meta")

for q in ["prayer forgiveness", "comparing yourself to others", "aisha"]:
    try:
        resp = search(q, mode="lexical")
        m = meta(resp)
        check(
            f'"{q}" → route: lexical',
            m.get("route") == "lexical",
            f'route={m.get("route")}'
        )
    except Exception as e:
        check(f'"{q}" lexical route → no exception', False, str(e))

try:
    resp = search("prayer forgiveness", mode="semantic", model=SEMANTIC_MODEL)
    m = meta(resp)
    check(
        '"prayer forgiveness" mode=semantic → route: semantic',
        m.get("route") == "semantic",
        f'route={m.get("route")}'
    )
except Exception as e:
    check("semantic route → no exception", False, str(e))


# ══════════════════════════════════════════════════════════════════
# 6. MODE OVERRIDE PRIORITY
# ══════════════════════════════════════════════════════════════════
section("6. Mode override priority  (arabic/phrase beat mode param)")

try:
    resp = search("صلاة الليل", mode="semantic")
    m = meta(resp)
    check(
        'Arabic query + mode=semantic → lexical_arabic (not semantic)',
        m.get("route") == "lexical_arabic",
        f'route={m.get("route")}'
    )
except Exception as e:
    check("arabic overrides semantic → no exception", False, str(e))

try:
    resp = search('"actions are by intention"', mode="semantic")
    m = meta(resp)
    check(
        'quoted query + mode=semantic → lexical_phrase (not semantic)',
        m.get("route") == "lexical_phrase",
        f'route={m.get("route")}'
    )
except Exception as e:
    check("phrase overrides semantic → no exception", False, str(e))

try:
    resp = search("aisha عائشة", mode="lexical")
    m = meta(resp)
    check(
        '"aisha عائشة" (mixed) → lexical_arabic',
        m.get("route") == "lexical_arabic",
        f'route={m.get("route")}'
    )
except Exception as e:
    check("mixed arabic+english → no exception", False, str(e))

try:
    resp = search("و", mode="lexical")
    m = meta(resp)
    check(
        '"و" (single arabic char) → lexical_arabic',
        m.get("route") == "lexical_arabic",
        f'route={m.get("route")}'
    )
except Exception as e:
    check("single arabic char → no exception", False, str(e))

try:
    resp = search("bukhari 1", mode="semantic")
    m = meta(resp)
    check(
        '"bukhari 1" + mode=semantic → lexical_reference (not semantic)',
        m.get("route") == "lexical_reference",
        f'route={m.get("route")}'
    )
except Exception as e:
    check("reference overrides semantic → no exception", False, str(e))


# ══════════════════════════════════════════════════════════════════
# 7. BOOLEAN OPERATOR QUERIES — forced lexical
# ══════════════════════════════════════════════════════════════════
section("7. Boolean operators → lexical (AND/OR/NOT are BM25 syntax, not semantic)")

bool_cases = [
    "prayer AND night",
    "bukhari OR muslim",
    "prayer NOT shirk",
    "faith AND deeds AND paradise",
]

for q in bool_cases:
    try:
        # Test with mode=semantic — should still be forced to lexical
        resp = search(q, mode="semantic")
        m = meta(resp)
        check(
            f'"{q}" + mode=semantic → lexical (not semantic)',
            m.get("route") == "lexical",
            f'route={m.get("route")}'
        )
    except Exception as e:
        check(f'"{q}" boolean → no exception', False, str(e))


# ══════════════════════════════════════════════════════════════════
# 8. ARABIC ROUTE — no language filter applied
# ══════════════════════════════════════════════════════════════════
section("7. Arabic route — no language restriction (searches full index)")

try:
    resp = search("الصلاة")
    total_hits = resp.get("hits", {}).get("total", {}).get("value", 0)
    h = hits(resp)
    check(
        "Arabic query returns results",
        len(h) > 0,
        f"{len(h)} hits returned"
    )
    check(
        "Arabic query searches full corpus (>1000 total hits for 'الصلاة')",
        total_hits > 1000,
        f"total hits = {total_hits:,}"
    )
except Exception as e:
    check("arabic no-restriction → no exception", False, str(e))

try:
    resp = search("رمضان")
    h = hits(resp)
    collections_seen = {source(hit).get("collection") for hit in h if source(hit).get("collection")}
    check(
        "Arabic query hits multiple collections (no collection restriction)",
        len(collections_seen) >= 2,
        f"{len(collections_seen)} distinct collections in top {len(h)} hits: {sorted(collections_seen)}"
    )
except Exception as e:
    check("arabic multi-collection → no exception", False, str(e))


# ══════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════
print(f"\n{'═'*60}")
passed = sum(1 for _, ok in results if ok)
total  = len(results)
print(f"  {passed}/{total} checks passed")
if passed < total:
    print("\n  FAILED:")
    for name, ok in results:
        if not ok:
            print(f"    • {name}")
print(f"{'═'*60}\n")
sys.exit(0 if passed == total else 1)
