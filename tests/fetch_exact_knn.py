"""
Fetch exact kNN results for all 4 models by:
1. Getting query embedding via ES inference API
2. Running knn query on inner dense_vector field (semantic_text.inference.chunks.embeddings)
   with num_candidates >= index doc count (forces exhaustive search)
"""
import urllib.request, urllib.parse, json, sys
from base64 import b64decode

ES = "http://elasticsearch:9200"
ES_AUTH = ("elastic", "123")
QUERY = "comparing yourself to others"
K = 10  # results to return

MODELS = {
    "openai-small-en": {
        "inference_id": "openai-text-embedding-3-small",
        "index": "english-openai-small-1779045411",
        "num_docs": 99956,
        "dims": 1536,
    },
    "openai-small-multi": {
        "inference_id": "openai-text-embedding-3-small",
        "index": "multilingual-openai-small-1779017104",
        "num_docs": 285236,
        "dims": 1536,
    },
    "nomic": {
        "inference_id": "nomic-embed-text",
        "index": "english-nomic-1779026769",
        "num_docs": 99956,
        "dims": 768,
    },
    "mxbai": {
        "inference_id": "mxbai-embed-large",
        "index": "english-mxbai-1779026713",
        "num_docs": 99956,
        "dims": 1024,
    },
}

import base64, urllib.error

def es_request(path, method="GET", body=None):
    url = ES + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    creds = base64.b64encode(b"elastic:123").decode()
    req.add_header("Authorization", f"Basic {creds}")
    if data:
        req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read())

def get_embedding(inference_id, text):
    r = es_request(f"/_inference/text_embedding/{inference_id}", "POST", {"input": text})
    return r["text_embedding"][0]["embedding"]

results = {}
for model_key, cfg in MODELS.items():
    print(f"\nModel: {model_key}", file=sys.stderr)
    print(f"  Getting embedding via {cfg['inference_id']} ...", file=sys.stderr)
    emb = get_embedding(cfg["inference_id"], QUERY)
    print(f"  Got {len(emb)}-dim embedding", file=sys.stderr)

    # Exact kNN: num_candidates >= num_docs forces exhaustive search
    num_candidates = cfg["num_docs"] + 1000
    print(f"  Running knn on {cfg['index']} (num_candidates={num_candidates}) ...", file=sys.stderr)

    body = {
        "size": K,
        "knn": {
            "field": "semantic_text.inference.chunks.embeddings",
            "query_vector": emb,
            "k": K,
            "num_candidates": num_candidates,
            "inner_hits": {"size": 1, "_source": False, "fields": []}
        },
        "_source": ["urn", "hadithText", "collection"],
    }

    try:
        r = es_request(f"/{cfg['index']}/_search", "POST", body)
        hits = r.get("hits", {}).get("hits", [])
        print(f"  Got {len(hits)} hits", file=sys.stderr)
        results[model_key] = [
            {
                "rank": i+1,
                "urn": h.get("_source", {}).get("urn", h.get("_id", "")),
                "score": round(h.get("_score", 0), 4),
                "text": h.get("_source", {}).get("hadithText", "")
            }
            for i, h in enumerate(hits)
        ]
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"  ERROR: {e.code} {err_body[:500]}", file=sys.stderr)
        results[model_key] = {"error": err_body[:300]}

with open("/tmp/exact_knn.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nDone — saved to /tmp/exact_knn.json", file=sys.stderr)
