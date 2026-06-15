# Query Router — Design Document

> **Status: observational.** The router classifies queries but does **not** change
> which Elasticsearch path a request takes. Production `search()` routes purely on
> `?mode=`. The router's decision is only *recorded* — in the `routing_decision`
> column of shadow-sampling metrics, and (with `ROUTER_LOG=true`) in a
> `router_decision` access-log line. The per-route Elasticsearch behaviour described
> below is the **intended** behaviour for when the rules are eventually wired into the
> served path; it does not run today. The one exception is the spam filter, which
> *does* gate production (returns 400 before any ES call).
>
> Code: `query_router.py`. Tests: `tests/test_query_router.py` (pure unit tests).

## How it works

**`query_router.py` is the source of truth for the rules.** Read it rather than a prose
restatement here, which would only drift. In particular:

- **`route_query(query, mode)`** — the full rule list and their strict priority order
  live in its docstring. Returns a `(route, variant)` tuple.
- **`routing_decision(query, mode)`** — collapses that tuple into the single label that
  gets recorded: `lexical`, `lexical_arabic`, `lexical_reference`, or `semantic`.
- **`is_spam(query)`** — the junk patterns, each regex commented inline.

The first four rules would force `lexical` regardless of `?mode=` (the "overridden" case
in `ROUTER_LOG` — recorded, not yet served). The rest of this document covers what the
code *doesn't* say on its own: why each rule exists, the Elasticsearch behaviour each
label is meant to map to, and the known gaps.

---

## Spam / junk filter (gates production)

`is_spam(query)` runs before everything else. Matching queries return
`400 "invalid query"` and are logged as `spam_rejected` — they never hit ES. This is
the only classifier that currently changes the served response. The patterns (each
commented in the code) cover URLs, phone numbers, repeated characters, long single
tokens, WhatsApp business spam, and high symbol density. Examples of what each catches:

| Pattern | Examples caught |
|---------|-----------------|
| URL | `http://example.com`, `visit buyfc26coins.com now` |
| Phone number | `+1 (555) 867-5309`, `+44 20 7946 0000` |
| Repeated chars | `aaaaaaaa`, `11111111`, `;;;;;;;;` |
| Long single token | random hash strings, packed URLs |
| WhatsApp business spam | `WA 0852 2611 9277 Pasang Interior...` |
| High symbol density | `!@#$%^&*()`, `{{{{{{{{` |

Patterns are derived from zero-result query analysis (`search_queries.12may26.sql`).
Arabic letters count as alphabetic (`.isalpha()` is Unicode-aware), so diacriticised
Arabic is not penalised by the symbol-density check.

---

## The labels, and what each route would do

The sections below describe the **intended** Elasticsearch behaviour each label
stands for once routing is wired into the served path. Today only the label is
recorded; the served query is whatever `?mode=` selects.

### `lexical` — quoted queries (forced lexical, `query_string` handles phrase)

**Triggered by:** Query wrapped in double quotes of at least 3 characters total:
`"actions are by intention"`.

**Intended behaviour:** Route forced to `lexical` (semantic skipped). The query
string is passed **unchanged** — quotes and all — to the standard `query_string` ES
query. ES natively interprets quoted tokens as phrase queries, so `"actions are by
intention"` already means "these words in order" inside `query_string`. No separate
`match_phrase` handler or stripped-quote logic is needed.

The Arabic rule has higher priority: `"صلاة الليل"` (quoted Arabic) is labelled
`lexical_arabic` so the full corpus would be searched without the `hadithText` exists
filter.

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

**Stop words and position gaps:** Omitting a stop word from the quoted phrase shifts the
positional constraint, finding a different (smaller) set of documents:

```
"prayer at night"  →  94 hits  (gap at position 1 where "at" was)
"prayer night"     →  28 hits  (prayer and night must be adjacent)
```

### `lexical_arabic`

**Triggered by:** Query contains any character in the Arabic Unicode block
(`U+0600–U+06FF`). A single Arabic character is enough — even a mixed query
like `aisha عائشة` is labelled here.

**Intended behaviour:** Same `function_score` + `cross_fields` structure as standard
BM25, across `["hadithNumber^2", "hadithText", "arabicText", "collection^2"]` with
`type: cross_fields`. ES uses each field's mapped analyzer automatically —
`arabicText` is mapped with `custom_arabic`, so Arabic tokens get correct
morphological analysis without explicit annotation.

**Key difference from standard BM25:** The Arabic route would omit the `hadithText`
exists filter, searching the full corpus — Arabic-only docs (`lang:ar`) have
`arabicText` but no `hadithText`, so that filter would exclude them.

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

**Why BM25 over an Arabic semantic model:** Arabic semantic models (multilingual-e5,
arabic-openai) live in separate indexes and require a separate embed call. BM25
on a well-configured Arabic analyser is fast, exact, and covers morphological
variants well enough for Arabic text search. Multilingual semantic search is
planned as a parallel comparison path, not a replacement.

**Arabic analyser normalisation:** Handles alef variants (`أ/إ/آ` → `ا`), tatweel,
hamza, taa marbuta. Does NOT normalise dagger alef (`الرحمٰن`) — known gap,
not yet addressed.

### `lexical_reference` and `lexical` (numbers and booleans)

**Number queries** — `_REF_RE` catches any query that ends with a number, including bare
numbers: `bukhari 1`, `abu dawud 200`, `ibn majah 12`, `5`, `42`. All labelled
`lexical_reference`.

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

An earlier design used an exact `term` filter on `collection` + `hadithNumber`. It was
removed because misspellings silently returned zero results.

**Boolean operators** — `_BOOL_RE` catches uppercase `AND`/`OR`/`NOT` (labelled `lexical`).
These are explicit `query_string` syntax. Semantic search embeds the words as plain text
and discards the logic entirely — keeping these on BM25 ensures the operators actually work.

### `lexical` (standard BM25) and `semantic`

These are the two paths production actually serves today, selected by `?mode=`.

Standard BM25 uses `query_string` first (supports `AND`/`OR`/`-` operators) and falls
back to `simple_query_string` if the query has syntax `query_string` rejects (unmatched
`"`, stray `(`, reserved operators). The fallback is logged server-side but not exposed
in `_meta`. Both lexical and semantic queries are wrapped in the same `function_score`
collection boosts.

**Collection boosts** (additive `boost_mode: sum`, applied to both lexical and semantic):

| Weight | Collections |
|---|---|
| 3.5 | Bukhari, Muslim |
| 3.3 | Nawawi 40, Riyadussalihin |
| 2.5 | Mishkat, Malik, Ahmad, Tirmidhi |
| 2.0 | Ibn Majah, Darimi |
| 1.0 | All others (baseline) |

When two results have nearly equal BM25 or cosine scores, the boost surfaces the
more-authenticated collection. Because it is additive, a highly-relevant weak-collection
hadith can still outrank a barely-relevant Bukhari hadith.

---

## `_meta.route` vs `routing_decision`

These are two different things — don't conflate them:

| Field | Where | Values today | Meaning |
|-------|-------|--------------|---------|
| `_meta.route` | every search response | `lexical`, `semantic` | the path **actually served** (mirrors `?mode=`) |
| `routing_decision` | `search_metrics` rows + `ROUTER_LOG` | `lexical`, `lexical_arabic`, `lexical_reference`, `semantic` | the route the classifier **would** pick (observational) |

`_meta.route` only carries `lexical` or `semantic` because the served path is mode-only.
The richer `lexical_arabic` / `lexical_reference` labels live in `routing_decision`, not
`_meta`, until routing is wired into the served path.

---

## Recording the decision

The router decision surfaces in two places, neither of which changes the response:

1. **Shadow-sampling metrics.** On sampled lexical-served queries (see the README
   "Shadow sampling" section), `routing_decision(query, mode)` is computed and written to
   the `routing_decision` column of `search_metrics` alongside the lexical and semantic
   result bodies. This lets sampled results be grouped and compared by query type.

2. **`ROUTER_LOG` access log.** Set `ROUTER_LOG=true` in `.env` to emit one structured
   line per request:
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
   `overridden: true` means a rule (Arabic/quoted/number/boolean) would force a lexical
   path when `?mode=semantic` was requested. Off by default; it adds access-log noise on
   busy servers.

When auditing real traffic, focus on:
- `spam_rejected` — queries blocked before classification; check `query` for false positives.
- `overridden: true` — investigate if English conceptual queries appear here unexpectedly.
- `lexical_arabic` on queries that look English — a stray Arabic character triggers it.
- `lexical_reference` — confirms number-ending and bare-number queries classify correctly.

Wiring the classification into the served path later is a pure code change — no index
rebuild required — and rollback is a redeploy of the previous image.

---

## Known limitations

| Issue | Impact | Status |
|-------|--------|--------|
| Routing not yet served | `routing_decision` is recorded but the served path is mode-only | By design — observational rollout |
| Dagger alef (`الرحمٰن`) not normalised | 0 results for that spelling (Arabic search) | Known gap, not addressed |
| Single Arabic character classifies as Arabic | `aisha عائشة` labelled `lexical_arabic` even though intent may be English | Acceptable — Arabic tokens dominate intent |
| `query_string` → `simple_query_string` fallback is silent | Client can't tell which was used | Logged server-side |
| Multi-word collection name synonyms not expanded at query time | `abu dawud 3` retrieves the right hadith via `hadithNumber^2` boost, but `abu dawud` alone won't match the stored token `abudawud` | Requires `synonym_graph` token filter, a `search_analyzer` on `collection`, `synonyms.txt` entries, and a full reindex — not yet implemented |
| Quoted phrases expand synonyms and stem | `"prayer at night"` matches docs containing "salah at night" (94 hits each) — the `synonym` analyzer runs on the phrase at query time. A `keyword` sub-field would be needed for truly literal phrases; not indexed. | By design — synonyms intentionally improve recall |
