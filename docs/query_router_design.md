# Query Router — Design Document

## How it works

`_route_query(query, mode)` runs once per request before any ES call. It inspects
the raw query string and returns a 3-tuple `(route, variant, extra)`. The `search()`
handler then branches on `route`.

Rules are applied **in strict priority order** — earlier rules always win:

```
query string
    │
    ├─ starts and ends with " " (≥3 chars)?
    │       → route: lexical  │  variant: phrase
    │
    ├─ contains any Arabic Unicode character?
    │       → route: lexical  │  variant: arabic
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
    if len(q) >= 3 and q[0] == '"' and q[-1] == '"':
        return "lexical", "phrase", {"phrase_text": q[1:-1]}
    if _ARABIC_RE.search(q):
        return "lexical", "arabic", {}
    if _REF_RE.search(q):
        return "lexical", "reference", {}
    if _BOOL_RE.search(q):
        return "lexical", None, {}
    return mode, None, {}
```

Priority is absolute. All four rules force `route: lexical` regardless of `?mode=`.

The reference rule now catches bare numbers too — `5`, `42`, `bukhari 1`, `abu dawud 200`,
`ibn majah 12` all match. A bare number has no semantic content worth embedding; a
collection+number query empirically returns 0/9 correct from semantic search.

The boolean rule catches uppercase `AND`/`OR`/`NOT` — ES `query_string` operators that
semantic search ignores entirely (it just embeds the words and discards the logic).

---

## Route: `lexical` / variant `phrase`

**Triggered by:** Query wrapped in double quotes: `"actions are by intention"`.

**ES query:** `match_phrase` on both `hadithText` and `arabicText` (minimum one
must match), wrapped in `function_score` for collection boosts. Requires all
tokens to appear in order with no gaps.

Example for query `"actions are by intention"` on `/english/search`:

```json
GET /english-mxbai/_search
{
  "query": {
    "function_score": {
      "query": {
        "bool": {
          "filter": [{"exists": {"field": "hadithText"}}],
          "should": [
            {"match_phrase": {"hadithText": "actions are by intention"}},
            {"match_phrase": {"arabicText": "actions are by intention"}}
          ],
          "minimum_should_match": 1
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

**Why override mode:** A quoted query is an explicit user signal that word order
matters. Running it through a semantic model would ignore that signal and return
"similar" hadiths rather than exact-phrase matches.

**Response `_meta`:** `{"route": "lexical_phrase"}`

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
GET /english-mxbai/_search
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
GET /english-mxbai/_search
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
of the four override rules (phrase, Arabic, number, boolean — those always force lexical).

**ES query:** `semantic` query on the `semantic_text` field, which calls the
configured inference endpoint (Ollama → mxbai-embed-large) at query time.

Example for query `comparing yourself to others` with `?mode=semantic` on `/english/search`:

```json
GET /english-mxbai/_search
{
  "query": {
    "bool": {
      "filter": [{"exists": {"field": "hadithText"}}],
      "must": [
        {"semantic": {"field": "semantic_text", "query": "comparing yourself to others"}}
      ]
    }
  }
}
```

The `semantic` query type is handled by the ES inference plugin — it embeds the
query string at search time using the same model used at index time
(mxbai-embed-large via Ollama). No client-side embedding needed.

**Response `_meta`:** `{"route": "semantic"}`

---

## `_meta.route` field

Every response includes `_meta.route`. Values:

| Value | Path |
|-------|------|
| `lexical_phrase` | `match_phrase` on quoted query |
| `lexical_arabic` | cross-fields BM25, full corpus (Arabic variant) |
| `lexical_reference` | cross-fields BM25, English docs (number queries: `bukhari 1`, `42`, etc. — forced off semantic) |
| `lexical` | cross-fields BM25, English docs (standard path, includes boolean-forced queries) |
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
