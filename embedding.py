"""Index-time remote embedding via HuggingFace Dedicated Endpoints (TEI).

When a model has a `remote_inference` config (see config._build_remote_inference),
the indexer pre-computes vectors here and ships them inline in the bulk payload,
so ES's semantic_text skips its own inference call. Query-time embedding always
goes through the ES inference endpoint (local Infinity server) and never touches this
module.

Disk-backed checkpoints let an interrupted build resume instead of re-embedding
the whole corpus. The public surface used by the indexer is `_open_checkpoint`
and `_rewrite_inline_chunks`; everything else is internal to the embed path.
"""

import hashlib
import json
import os
import socket
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import SEMANTIC_FIELD, _is_truthy
from logger import access_log
from utils.rate_limiter import RateLimiter
from utils.vector_checkpoint import (
    NullCheckpoint,
    VectorCheckpoint,
    checkpoint_path,
)


# HF's per-endpoint pool 429s well below TEI's max_concurrent_requests=512.
# batch_size × max_input_length must stay under TEI's max_batch_tokens (16384).
_REMOTE_EMBED_CONCURRENCY = int(os.environ.get("HF_DEDICATED_CONCURRENCY", "4"))
_REMOTE_EMBED_BATCH_SIZE = int(os.environ.get("HF_DEDICATED_BATCH_SIZE", "16"))
# -1 disables throttling; HF Dedicated bills by compute-time, not RPM.
_REMOTE_EMBED_RPM = int(os.environ.get("HF_DEDICATED_RPM", "-1"))
_REMOTE_EMBED_MAX_RETRIES = 6
_REMOTE_EMBED_BACKOFF_FLOOR_S = 5
# Cap server-supplied Retry-After so a misbehaving 503 can't park a worker.
_REMOTE_EMBED_BACKOFF_CEILING_S = 60

# HF Dedicated Endpoints scale-to-zero and pass through a transitional state
# while spinning up: 503 (cold start) then 400 {"error":"Bad Request: workload
# is not stopped"} (endpoint mid-deploy, not actually ready). Both are endpoint
# lifecycle states, not real request errors, so we treat them as retryable and
# wait for a successful probe before fanning batches out at a cold endpoint.
_HF_TRANSITIONAL_BODY = "workload is not stopped"
# TEI returns a 500 "input (N tokens) is too large to process. increase the
# physical batch size (current batch size: …)" when a single input exceeds the
# endpoint's max_batch_tokens. That's a permanent endpoint-capacity misconfig
# (fix: redeploy with a larger MAX_BATCH_TOKENS), not a transient error — every
# over-long doc would fail identically on every retry, so retrying just burns
# the budget and stretches a doomed run to ~90 min. Treat it as fatal.
_HF_INPUT_TOO_LARGE_BODY = "too large to process"
# Cold-start budget: wait up to 10 min for the endpoint to warm up, re-probing
# every 10s, before fanning embed batches out at it.
_REMOTE_READY_TIMEOUT_S = 600
_REMOTE_READY_POLL_S = 10

# Disk-backed vector cache: persists embedded batches so an interrupted build
# resumes instead of re-embedding the whole corpus. Defaults on; lives under the
# app working tree (per-container in prod) and is deleted on a successful build.
_EMBED_CHECKPOINT_ENABLED = _is_truthy(
    os.environ.get("EMBED_CHECKPOINT_ENABLED", "true")
)
_EMBED_CHECKPOINT_DIR = "data/embed_checkpoints"


def _embed_text_key(text):
    """Cache key for an embedding: a hash of the exact text sent to the model."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _remote_headers(cfg):
    """Auth + content-type headers for the OpenAI-compatible HF embed endpoint."""
    return {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }


def _remote_payload(cfg, inputs):
    """OpenAI-shape embed body. TEI accepts `truncate` to silently handle inputs
    over max_input_length, so we never have to pre-trim."""
    return json.dumps(
        {"model": cfg["model_id"], "input": inputs, "truncate": True}
    ).encode("utf-8")


def _open_checkpoint(model):
    """Resume cache for this model — a no-op NullCheckpoint when disabled, not a
    semantic model, or unwritable.

    Returning a uniform object (never None) lets callers use it with no guards,
    and degrades gracefully: a checkpoint that can't be created (e.g. read-only
    filesystem) must never block an index build.
    """
    if not (_EMBED_CHECKPOINT_ENABLED and model and model.get("remote_inference")):
        return NullCheckpoint()
    path = checkpoint_path(_EMBED_CHECKPOINT_DIR, model["index"])
    try:
        cp = VectorCheckpoint(path)
    except OSError as e:
        access_log.warning(
            "embed_checkpoint_unavailable", extra={"path": path, "reason": str(e)}
        )
        return NullCheckpoint()
    access_log.info("embed_checkpoint_open", extra={"path": path, "cached": len(cp)})
    return cp


def _remote_failure_retryable(status_code, body):
    """Classify an HTTP failure from the remote embed endpoint as retryable.

    429 and 5xx are the usual transient cases. A 400 is normally fatal (bad
    input / model id), except HF's "workload is not stopped" — that's a
    transitional endpoint lifecycle state, not a bad request, so it's retryable.
    The exception to 5xx is TEI's "too large to process" 500 (input over
    max_batch_tokens): permanent for that input, so it's fatal, not retryable.
    """
    body_l = (body or "").lower()
    if status_code == 500 and _HF_INPUT_TOO_LARGE_BODY in body_l:
        return False
    if status_code == 429 or 500 <= status_code < 600:
        return True
    return status_code == 400 and _HF_TRANSITIONAL_BODY in body_l


def _wait_for_remote_ready(model):
    """Poll the remote endpoint with a tiny embed until it returns 200.

    Slamming HF_DEDICATED_CONCURRENCY workers at a cold/scaling endpoint is what
    produced the 503 → 400 "workload is not stopped" chain that aborted the
    whole run. Block on a single successful probe first (up to
    _REMOTE_READY_TIMEOUT_S), retrying only transitional states; a genuine error
    (bad key, bad model id) surfaces immediately.
    """
    cfg = model["remote_inference"]
    headers = _remote_headers(cfg)
    payload = _remote_payload(cfg, ["ping"])
    deadline = time.monotonic() + _REMOTE_READY_TIMEOUT_S
    attempt = 0
    while True:
        attempt += 1
        try:
            req = urllib.request.Request(
                cfg["url"], data=payload, headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp.read()
            access_log.info("remote_ready", extra={"attempts": attempt})
            return
        except urllib.error.HTTPError as e:
            body = e.read()[:200].decode("utf-8", errors="replace")
            if not _remote_failure_retryable(e.code, body):
                access_log.error(
                    "remote_ready_failed", extra={"status": e.code, "body": body}
                )
                raise
            status, reason = e.code, body
        except (urllib.error.URLError, socket.timeout, ConnectionError) as e:
            status, reason = "network_error", str(e)
        if time.monotonic() >= deadline:
            access_log.error(
                "remote_ready_timeout",
                extra={"status": status, "reason": reason, "waited_s": _REMOTE_READY_TIMEOUT_S},
            )
            raise RuntimeError(
                f"remote endpoint not ready after {_REMOTE_READY_TIMEOUT_S}s "
                f"(last status: {status})"
            )
        access_log.warning(
            "remote_ready_wait",
            extra={"status": status, "attempt": attempt, "wait_s": _REMOTE_READY_POLL_S},
        )
        time.sleep(_REMOTE_READY_POLL_S)


def _embed_via_remote(model, texts, checkpoint=None):
    """Batch-embed `texts` via the configured HF Dedicated Endpoint.

    Returns a list of float vectors aligned with input order. Retries on 429,
    transient 5xx, and HF's transitional 400 ("workload is not stopped") with
    exponential backoff (Retry-After respected when ≥ floor). Captures the
    response body on non-retryable failures (e.g. 400 "inputs cannot be empty")
    to make debugging easier.

    `checkpoint` (a VectorCheckpoint or no-op NullCheckpoint) reuses vectors
    already persisted from an earlier interrupted run (only the misses are
    re-embedded), and each completed batch is persisted as it finishes — so even
    if a later batch raises, the run resumes from where it left off rather than
    from zero.
    """
    cfg = model["remote_inference"]
    headers = _remote_headers(cfg)
    limiter = RateLimiter(_REMOTE_EMBED_RPM, log=access_log)

    def _embed_batch(batch_texts):
        payload = _remote_payload(cfg, batch_texts)
        for attempt in range(_REMOTE_EMBED_MAX_RETRIES):
            limiter.acquire()
            req = urllib.request.Request(
                cfg["url"], data=payload, headers=headers, method="POST"
            )

            status = None
            retry_after = None
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    body = json.loads(resp.read())
                # TEI's /v1/embeddings returns OpenAI shape with L2-normalized vectors.
                return [item["embedding"] for item in body["data"]]
            except urllib.error.HTTPError as e:
                status = e.code
                # Read the body up front — classification needs it (HF signals
                # the transitional state via a 400 body, not a distinct code).
                body_snippet = e.read()[:400].decode("utf-8", errors="replace")
                retryable = _remote_failure_retryable(e.code, body_snippet)
                retry_after = e.headers.get("Retry-After")
                if not retryable or attempt == _REMOTE_EMBED_MAX_RETRIES - 1:
                    access_log.error(
                        "remote_embed_failed",
                        extra={
                            "status": e.code,
                            "body": body_snippet,
                            "batch_size": len(batch_texts),
                        },
                    )
                    raise
            except (urllib.error.URLError, socket.timeout, ConnectionError) as e:
                # DNS failure, connect refused, read timeout, RST mid-stream —
                # treat as transient and retry rather than killing the run.
                status = "network_error"
                if attempt == _REMOTE_EMBED_MAX_RETRIES - 1:
                    access_log.error(
                        "remote_embed_failed",
                        extra={
                            "status": status,
                            "reason": str(e),
                            "batch_size": len(batch_texts),
                        },
                    )
                    raise

            # Shared backoff path for any retryable failure above.
            parsed = (
                float(retry_after)
                if retry_after and retry_after.replace(".", "", 1).isdigit()
                else 0
            )
            # TEI sometimes returns Retry-After: 0 — enforce a floor so we don't
            # immediately re-fire. Cap Retry-After so a single misbehaving 503
            # can't park a worker for many minutes.
            wait = max(
                min(parsed, _REMOTE_EMBED_BACKOFF_CEILING_S),
                _REMOTE_EMBED_BACKOFF_FLOOR_S,
                min(2**attempt, 30),
            )
            access_log.warning(
                "remote_embed_retry",
                extra={"status": status, "attempt": attempt + 1, "wait_s": wait},
            )
            time.sleep(wait)

    checkpoint = checkpoint or NullCheckpoint()
    keys = [_embed_text_key(t) for t in texts]
    out = [None] * len(texts)

    # Reuse any vectors a prior interrupted run already persisted (a
    # NullCheckpoint always misses), so API calls are spent only on the rest.
    miss = []
    for i, k in enumerate(keys):
        cached = checkpoint.get(k)
        if cached is not None:
            out[i] = cached
        else:
            miss.append(i)
    if 0 < len(miss) < len(texts):
        access_log.info(
            "remote_embed_resumed",
            extra={"cached": len(texts) - len(miss), "remaining": len(miss)},
        )

    if not miss:
        return out

    # Batch over the (global) miss indices so vector positions and cache keys
    # stay aligned with the original input order.
    batches = [
        miss[i : i + _REMOTE_EMBED_BATCH_SIZE]
        for i in range(0, len(miss), _REMOTE_EMBED_BATCH_SIZE)
    ]
    first_error = None
    with ThreadPoolExecutor(max_workers=_REMOTE_EMBED_CONCURRENCY) as ex:
        future_to_idxs = {
            ex.submit(_embed_batch, [texts[i] for i in idxs]): idxs
            for idxs in batches
        }
        # as_completed yields futures in completion order, so a single slow batch
        # doesn't idle workers that finished after it but were submitted earlier.
        # Drain every future even after one fails: persist all successes (so the
        # next run resumes) and raise the first error only once the pool is done.
        for f in as_completed(future_to_idxs):
            idxs = future_to_idxs[f]
            try:
                vectors = f.result()
            except Exception as e:  # noqa: BLE001 — re-raised after draining
                if first_error is None:
                    first_error = e
                continue
            # A short response would let zip() silently leave None holes in out,
            # which then get indexed as `embeddings: null`. Treat any count
            # mismatch as a failed batch so the run aborts (and the checkpoint is
            # preserved) instead of writing corrupt vectors.
            if len(vectors) != len(idxs):
                if first_error is None:
                    first_error = RuntimeError(
                        f"remote returned {len(vectors)} vectors for a batch of "
                        f"{len(idxs)} inputs"
                    )
                continue
            for i, vec in zip(idxs, vectors):
                out[i] = vec
            checkpoint.put_many((keys[i], vec) for i, vec in zip(idxs, vectors))
    if first_error is not None:
        raise first_error
    return out


def _inline_chunk_doc(doc, text, vec, inference_id, model_settings):
    """Build the doc shape ES's semantic_text accepts when bypassing inference."""
    return {
        **doc,
        SEMANTIC_FIELD: {
            "text": text,
            "inference": {
                "inference_id": inference_id,
                "model_settings": model_settings,
                "chunks": [{"text": text, "embeddings": vec}],
            },
        },
    }


def _rewrite_inline_chunks(docs, model, checkpoint=None):
    """Replace each doc's plain-text SEMANTIC_FIELD with the full inline-chunks
    structure, with vectors fetched from the model's remote inference API.

    Called only on docs about to be bulk-sent (after incremental diffing) so we
    don't burn API quota embedding unchanged docs.

    The optional `checkpoint` is owned by the caller (open/discard/close): if
    embedding raises partway, the partial vectors stay persisted so the next run
    resumes. The caller must only discard() it once the ES bulk step that
    consumes these vectors has actually succeeded — discarding here would throw
    the cache away while a downstream bulk failure could still force a full
    re-embed.
    """
    texts = [doc[SEMANTIC_FIELD] for doc in docs]

    access_log.info(
        "remote_embed_start",
        extra={
            "model": model["label"],
            "doc_count": len(texts),
            "batch_size": _REMOTE_EMBED_BATCH_SIZE,
            "concurrency": _REMOTE_EMBED_CONCURRENCY,
            "rpm": _REMOTE_EMBED_RPM,
        },
    )
    # Pre-flight: wait for the endpoint to be warm before fanning batches out at
    # it, instead of triggering the cold-start 503 → 400 chain that aborts runs.
    _wait_for_remote_ready(model)

    t0 = time.time()
    vectors = _embed_via_remote(model, texts, checkpoint=checkpoint)
    access_log.info(
        "remote_embed_done",
        extra={
            "model": model["label"],
            "doc_count": len(texts),
            "duration_s": round(time.time() - t0, 1),
        },
    )

    model_settings = {
        "task_type": "text_embedding",
        "dimensions": model["dims"],
        "similarity": "cosine",
        "element_type": "float",
    }
    return [
        _inline_chunk_doc(doc, text, vec, model["inference_id"], model_settings)
        for doc, text, vec in zip(docs, texts, vectors)
    ]
