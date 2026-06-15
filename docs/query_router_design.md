# Query Router — Design Document

## How it works

`_route_query(query, mode)` runs once per request before any ES call. It inspects
the raw query string and returns a 2-tuple `(route, variant)`. The `search()`
handler then branches on `route`.

Each request passes through a spam check first, then the router. Rules are applied **in strict priority order** — earlier rules always win:

```
query string
    │
    ├─ spam / junk? (URL, phone number, repeated chars, long token, high symbol density)
    │       → 400 "invalid query"  (logged as spam_rejected)
    │
    ├─ contains any Arabic Unicode character?
    │       → route: lexical  │  variant: arabic
    │         (takes priority over quotes so quoted Arabic still searches full corpus)
    │
    ├─ starts and ends with " " (≥3 chars)?
    │       → route: lexical  │  variant: —  (query_string handles phrase natively)
    │
    ├─ ends with a number /(^|\s)\d+[a-z]?\s*$/ (text + number, or bare number)?
    │       → route: lexical  │  variant: reference
    │
    ├─ contains AND / OR / NOT (uppercase)?
    │       → route: lexical  │  variant: —  (standard BM25)
    │
    └─ otherwise (passthrough to ?mode=)
            → route: lexical   │  variant: —  (default, or ?mode=lexical)
              route: semantic  │  variant: —  (if ?mode=semantic)
```

### Detection code

```python
_ARABIC_RE = re.compile(r'[؀-ۿ]')
_REF_RE    = re.compile(r'(^|\s)\d+[a-z]?\s*$', re.IGNORECASE)
_BOOL_RE   = re.compile(r'\b(AND|OR|NOT)\b')

def _route_query(query, mode):
    q = query.strip()
    if _ARABIC_RE.search(q):
        return "lexical", "arabic"
    if len(q) >= 3 and q[0] == '"' and q[-1] == '"':
        return "lexical", None
    if _REF_RE.search(q):
        return "lexical", "reference"
    if _BOOL_RE.search(q):
        return "lexical", None
    return mode, None
```

Returns a 2-tuple `(route, variant)`. Priority is absolute — earlier rules always win
and all four force `route: lexical` regardless of `?mode=`.

The reference rule now catches bare numbers too — `5`, `42`, `bukhari 1`, `abu dawud 200`,
`ibn majah 12` all match. A bare number has no semantic content worth embedding; a
collection+number query empirically returns 0/9 correct from semantic search.

The boolean rule catches uppercase `AND`/`OR`/`NOT` — ES `query_string` operators that
semantic search ignores entirely (it just embeds the words and discards the logic).

---

## Spam / junk filter

`_is_spam(query)` runs before `_route_query`. Queries that match return `400 "invalid query"` and are logged as `spam_rejected` — they never hit ES.

| Pattern | Regex / rule | Examples caught |
|---------|-------------|-----------------|
| URL | `https?://`, `www.`, `\.[a-z]{3,4}(/\|$)` | `http://example.com`, `visit islam.com` |
| Phone number | `^[+0-9 ()\-]{7,}$` | `+1 (555) 867-5309`, `+44 20 7946 0000` |
| Repeated chars | `(.)\1{4,}` (same char 5+ times) | `aaaaaaaa`, `11111111`, `;;;;;;;;` |
| Long single token | `\S{40,}` (40+ non-space chars) | random hash strings, packed URLs |
| High symbol density | >40% of non-space chars are non-alphanumeric | `!@#$%^&*()`, `{{{{{{{{` |

Patterns are derived from zero-result query analysis (`search_queries.12may26.sql`).
Arabic letters count as alphabetic (`.isalpha()` is Unicode-aware), so diacriticised
Arabic is not penalised by the symbol-density check.

---

## Quoted queries — forced lexical, `query_string` handles phrase

**Triggered by:** Query wrapped in double quotes of at least 3 characters total:
`"actions are by intention"`.

**What changes:** The route is forced to `lexical` (semantic is skipped). The query
string is passed **unchanged** — quotes and all — to the standard `query_string` ES
query. ES natively interprets quoted tokens as phrase queries, so `"actions are by
intention"` already means "these words in order" inside `query_string`. No separate
`match_phrase` handler or stripped-quote logic is needed.

The Arabic rule has higher priority: `"صلاة الليل"` (quoted Arabic) still routes to
`lexical_arabic` so the full corpus is searched without the `hadithText` exists filter.

**Why force lexical:** A quoted query is an explicit user signal that word order matters.
Sending it to a semantic model would ignore that signal and return thematically similar
hadiths rather than exact-phrase matches.

**How the analyzer affects phrase matching:**

`hadithText` uses the `synonym` analyzer. This runs on the quoted phrase at query time
exactly as it does for unquoted queries — stemming, stop word removal, and synonym
expansion all still apply. The phrase constraint is on the *analyzed* token positions,
not the raw words.

Example — `"actions are by intention"`:

```
analyze("actions are by intention") → action(pos 0)  intent(pos 3)
                                       ↑ stemmed       ↑ stemmed
                                       "are" → removed (pos 1 gap)
                                       "by"  → removed (pos 2 gap)
```

The phrase query looks for `action` at position *p* and `intent` at position *p+3*
(the gap where the two stop words were). The document "Actions are through intentions."
indexes `action(0) through(2) intent(3)`, which satisfies `action(0) … intent(3)` — so
it matches.

Synonym expansion also applies inside phrases:

```python
# All three return 94 identical hits on the live index:
"prayer at night"  →  94 hits   # prayer → [prayer, salah, salat, namaz, ...]
"salah at night"   →  94 hits   # same expanded token set
"namaz at night"   →  94 hits
```

This means a quoted search expresses "these *concepts* in this order" rather than
"these exact words in this order". Users who want truly literal matching would need a
`keyword` sub-field; that is not currently indexed.

**`query_string` quotes vs `match_phrase`:** Empirically identical — same hit count,
same scores, same ranking for all tested queries. Both go through the field analyzer;
`query_string` just supports multi-field and boolean operators around the quoted span.

**Stop words and position gaps:** Omitting a stop word from the quoted phrase shifts the
positional constraint, finding a different (smaller) set of documents:

```
"prayer at night"  →  94 hits  (gap at position 1 where "at" was)
"prayer night"     →  28 hits  (prayer and night must be adjacent)
```

**Response `_meta`:** `{"route": "lexical"}` (same as standard BM25 — no separate
`lexical_phrase` value; the phrase behaviour is entirely inside ES's `query_string`.)

---

## Route: `lexical` / variant `arabic`

**Triggered by:** Query contains any character in the Arabic Unicode block
(`U+0600–U+06FF`). A single Arabic character is enough — even a mixed query
like `aisha عائشة` routes here.

**ES query:** Same `function_score` + `cross_fields` structure as standard BM25.
`query_string` is used across `["hadithNumber^2", "hadithText", "arabicText",
"collection^2"]` with `type: cross_fields`. ES uses each field's mapped analyzer
automatically — `arabicText` is mapped with `custom_arabic`, so Arabic tokens get
correct morphological analysis without explicit annotation.

**Key difference from standard BM25:** The Arabic route omits the `hadithText` exists
filter that all other routes apply. Standard BM25 on `/english/search` adds
`{"exists": {"field": "hadithText"}}` to restrict to English/bilingual docs. The Arabic
route skips this, searching the full corpus — Arabic-only docs (`lang:ar`) have
`arabicText` but no `hadithText`, so the exists filter would exclude them.

Example for query `صلاة الليل` (no filter — full corpus):

```json
GET /english-<model>/_search
{
  "query": {
    "function_score": {
      "query": {
        "bool": {
          "must": [
            {"query_string": {
              "query": "صلاة الليل",
              "fields": ["hadithNumber^2", "hadithText", "arabicText", "collection^2"],
              "type": "cross_fields"
            }}
          ]
        }
      },
      "functions": [
        {"filter": {"term": {"collection": "bukhari"}},         "weight": 3.5},
        {"filter": {"term": {"collection": "muslim"}},          "weight": 3.5},
        {"filter": {"term": {"collection": "forty"}},           "weight": 3.3},
        {"filter": {"term": {"collection": "riyadussalihin"}},  "weight": 3.3}
      ],
      "score_mode": "sum",
      "boost_mode": "sum"
    }
  }
}
```

**Full-corpus scale:** `الصلاة` returns ~3,960 total hits across multiple collections
(Bukhari, Muslim, etc.) — confirming the exists filter is not applied. Standard BM25
on `/english/search` without the Arabic route would return 0 hits for Arabic-only docs.

**Why BM25 over an Arabic semantic model:** Arabic semantic models (multilingual-e5,
arabic-openai) live in separate indexes and require a separate embed call. BM25
on a well-configured Arabic analyser is fast, exact, and covers morphological
variants well enough for Arabic text search. Multilingual semantic search is
planned as a parallel comparison path, not a replacement.

**Arabic analyser normalisation:** Handles alef variants (`أ/إ/آ` → `ا`), tatweel,
hamza, taa marbuta. Does NOT normalise dagger alef (`الرحمٰن`) — known gap,
not yet addressed.

**Response `_meta`:** `{"route": "lexical_arabic"}`

---

## Route: `lexical` (standard BM25)

**Triggered by:** Any query that didn't match the four rules above.

**ES query:** Cross-field BM25 wrapped in `function_score` for collection boosts.
Tries `query_string` first (supports `AND`/`OR`/`-` operators); falls back to
`simple_query_string` if the query has syntax that `query_string` rejects.

Example for query `prayer at night` on `/english/search`:

```json
GET /english-<model>/_search
{
  "query": {
    "function_score": {
      "query": {
        "bool": {
          "filter": [{"exists": {"field": "hadithText"}}],
          "must": [
            {"query_string": {
              "query": "prayer at night",
              "fields": ["hadithNumber^2", "hadithText", "arabicText", "collection^2"],
              "type": "cross_fields"
            }}
          ]
        }
      },
      "functions": [
        {"filter": {"term": {"collection": "bukhari"}},         "weight": 3.5},
        {"filter": {"term": {"collection": "muslim"}},          "weight": 3.5},
        {"filter": {"term": {"collection": "forty"}},           "weight": 3.3},
        {"filter": {"term": {"collection": "riyadussalihin"}},  "weight": 3.3},
        {"filter": {"term": {"collection": "mishkat"}},         "weight": 2.5},
        {"filter": {"term": {"collection": "malik"}},           "weight": 2.5},
        {"filter": {"term": {"collection": "ahmad"}},           "weight": 2.5},
        {"filter": {"term": {"collection": "tirmidhi"}},        "weight": 2.5},
        {"filter": {"term": {"collection": "ibnmajah"}},        "weight": 2.0},
        {"filter": {"term": {"collection": "darimi"}},          "weight": 2.0}
      ],
      "score_mode": "sum",
      "boost_mode": "sum"
    }
  }
}
```

**query_string → simple_query_string fallback:** If the query contains syntax that
`query_string` rejects (unmatched `"`, stray `(`, reserved operators in unexpected
positions), ES returns a 400. The handler catches this and retries with
`simple_query_string`, which is lenient. The fallback is logged server-side but not
exposed in `_meta`.

**Collection boosts:** Bukhari and Muslim are weighted 3.5×, Nawawi 40 / Riyad
3.3×, Mishkat / Malik / Ahmad / Tirmidhi 2.5×, Ibn Majah / Darimi 2.0×. These
lift authoritative collections above identical term matches in weaker ones.

**Response `_meta`:** `{"route": "lexical"}`

---

## Route: `semantic`

**Triggered by:** `?mode=semantic` in the request, AND the query didn't match any
of the override rules (Arabic, quoted, number, boolean — those always force lexical).

**ES query:** `semantic` query on the `semantic_text` field, wrapped in the same
`function_score` collection boosts as the lexical routes. The inference endpoint
(Ollama on the host) embeds the query at search time — no client-side embedding needed.

Example for query `comparing yourself to others` with `?mode=semantic` on `/english/search`:

```json
GET /english-<model>/_search
{
  "query": {
    "function_score": {
      "query": {
        "bool": {
          "filter": [{"exists": {"field": "hadithText"}}],
          "must": [
            {"semantic": {"field": "semantic_text", "query": "comparing yourself to others"}}
          ]
        }
      },
      "functions": [
        {"filter": {"term": {"collection": "bukhari"}},        "weight": 5.0},
        {"filter": {"term": {"collection": "muslim"}},         "weight": 4.8},
        {"filter": {"term": {"collection": "nawawi40"}},       "weight": 3.3},
        {"filter": {"term": {"collection": "riyadussalihin"}}, "weight": 2.5}
      ],
      "score_mode": "sum",
      "boost_mode": "sum"
    }
  }
}
```

The `semantic` query type is handled by the ES inference plugin — it embeds the query
string at search time using the configured model via Ollama. When two results have
nearly equal cosine scores, the collection boost surfaces the more-authenticated one.

**Response `_meta`:** `{"route": "semantic"}`

---

## `_meta.route` field

Every response includes `_meta.route`. Values:

| Value | Path |
|-------|------|
| `lexical_arabic` | cross-fields BM25, full corpus (Arabic variant) |
| `lexical_reference` | cross-fields BM25, English docs (number queries: `bukhari 1`, `42`, etc. — forced off semantic) |
| `lexical` | cross-fields BM25, English docs (standard path — also covers quoted and boolean-forced queries) |
| `semantic` | Vector similarity via inference endpoint |

---

## Production rollout

The router is a pure code change — no index rebuild required. The `english-mxbai` index is unchanged.

**Recommended steps:**

1. Deploy with `ROUTER_LOG=true` in `.env`. Every request emits a structured log line:
   ```json
   {
     "message": "router_decision",
     "query": "صلاة الليل",
     "mode_requested": "semantic",
     "route": "lexical_arabic",
     "variant": "arabic",
     "overridden": true
   }
   ```

2. Review a day of real queries. Focus on:
   - `message: spam_rejected` — queries blocked before routing. Check the `query` field for false positives (e.g. a valid query that happened to match a spam pattern).
   - `overridden: true` — a rule (phrase/Arabic/number/boolean) blocked a `?mode=semantic` request. Investigate if English conceptual queries appear here unexpectedly.
   - `route: lexical_arabic` on queries that look English — a stray Arabic character in the input will trigger this.
   - `route: lexical_reference` — confirms number-ending and bare-number queries stayed off semantic.

3. If shadow sampling is enabled, `routing_decision` in `search_metrics` records the route for each sampled request alongside full result bodies.

4. Disable `ROUTER_LOG` once routing looks stable.

5. Rollback: redeploy previous image. Index is untouched; rollback is instant.

---

## Number queries and boolean operators (`lexical_reference` / `lexical`)

**Number queries** — `_REF_RE` catches any query that ends with a number, including bare numbers:
`bukhari 1`, `abu dawud 200`, `ibn majah 12`, `5`, `42`. All route to `lexical_reference`.

- Empirically: semantic returns 0/9 correct for collection+number queries in top 10.
- Bare numbers (`5`, `42`) have no semantic content — there is nothing meaningful to embed.
- `hadithNumber^2` and `collection^2` boosts reliably surface the correct hadith at rank 1
  without any term filter. Misspellings (`bukahri 1`) still end with a number, staying on
  lexical and returning sensible results via BM25.

```
"bukhari 1"    → rank 1: bukhari:1    ✓
"bukhari 6594" → rank 1: bukhari:6594 ✓
"muslim 2363"  → rank 1: muslim:2363  ✓
"bukahri 1"    → rank 1: bukhari:1    ✓  (misspelling tolerated via BM25)
```

The regex does **not** match number-first queries like `99 names` or `7 levels of hell` —
those end with a word, not a number, so they fall through to the default mode. This is
intentional: "last 10 nights" is a conceptual query that semantic handles better than
a reference lookup.

An earlier design used an exact `term` filter on `collection` + `hadithNumber`. It was removed because misspellings silently returned zero results.

**Boolean operators** — `_BOOL_RE` catches uppercase `AND`/`OR`/`NOT`. These are explicit
`query_string` syntax. Semantic search embeds the words as plain text and discards the logic
entirely — keeping these on BM25 ensures the operators actually work as intended.

---

## Known limitations

| Issue | Impact | Status |
|-------|--------|--------|
| Dagger alef (`الرحمٰن`) not normalised | 0 results for that spelling | Known gap, not addressed |
| Single Arabic character routes to Arabic path | `aisha عائشة` goes Arabic even though intent may be English | Acceptable — Arabic tokens dominate intent |
| `query_string` → `simple_query_string` fallback is silent | Client can't tell which was used | Logged server-side |
| Multi-word collection names with spaces | `abu dawud 1`, `ibn majah 1` end with a number so `_REF_RE` matches — they route `lexical_reference` correctly | No issue |
| Multi-word collection name synonyms not expanded at query time | Searching `abu dawud 3` retrieves the right hadith via `hadithNumber^2` boost, but `abu dawud` alone won't match the stored token `abudawud` | Requires (1) `synonym_graph` token filter in index settings, (2) a `search_analyzer` on the `collection` field using that filter, (3) collection name entries in `synonyms.txt`, and (4) a full reindex — not yet implemented |
| Quoted phrases expand synonyms and stem | `"prayer at night"` matches docs containing "salah at night" or "namaz at night" (94 hits each) — the `synonym` analyzer runs on the phrase at query time. Users expecting literal word matching won't get it. A `keyword` sub-field would be needed for truly literal phrases; not currently indexed. | By design — synonyms intentionally improve recall; document the behaviour for users |
