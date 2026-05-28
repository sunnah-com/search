"""Disk-backed embedding cache so an interrupted index build can resume.

A single semantic index build embeds the whole corpus (tens of thousands of
docs) by fanning batches out to a remote inference endpoint. Before this cache,
one transient failure on any of the ~3,000 batches raised and discarded every
vector already computed — the next run then re-embedded the entire corpus from
zero.

Vectors are keyed by a hash of the embedded text (the true cache key for an
embedding — independent of unrelated doc fields and stable across rebuild vs.
incremental paths) and persisted as JSON lines. Reads are served from memory;
writes append and fsync per batch so a crash mid-build keeps prior progress.

Lives in utils/ alongside RateLimiter so it can be unit-tested without
importing Flask.
"""

import json
import os
import threading


class VectorCheckpoint:
    """Append-only {text_hash: vector} store backed by a JSONL file.

    Thread-safe: `_embed_via_remote` writes completed batches concurrently from
    a thread pool. One fsync per `put_many` call (i.e. per batch) keeps the
    durability cost bounded while still surviving an abrupt process exit.
    """

    def __init__(self, path):
        self.path = path
        self._lock = threading.Lock()
        self._cache = {}
        self._load()
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._fh = open(path, "a", encoding="utf-8")

    def _load(self):
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    # Tolerate a torn final line from a crash mid-write — every
                    # record above it is intact, so we keep that progress.
                    continue
                self._cache[rec["k"]] = rec["v"]

    def get(self, key):
        return self._cache.get(key)

    def put_many(self, items):
        """Persist an iterable of (key, vector) pairs in one durable write."""
        with self._lock:
            wrote = False
            for key, vector in items:
                if key in self._cache:
                    continue
                self._cache[key] = vector
                self._fh.write(json.dumps({"k": key, "v": vector}) + "\n")
                wrote = True
            if wrote:
                self._fh.flush()
                os.fsync(self._fh.fileno())

    def discard(self):
        """Close and delete the backing file.

        Called once a full build succeeds: the cache only exists to resume an
        interrupted run, and re-embedding of genuinely unchanged docs across
        separate successful builds is already prevented by the contentHash
        incremental diff. So on success the file is dead weight — remove it
        rather than leave hundreds of MB of vectors on disk.
        """
        self.close()
        with self._lock:
            try:
                os.remove(self.path)
            except OSError:
                pass
            self._cache = {}

    def close(self):
        with self._lock:
            if not self._fh.closed:
                self._fh.close()

    def __len__(self):
        return len(self._cache)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class NullCheckpoint:
    """No-op stand-in returned when resume caching is disabled or unavailable.

    Lets callers treat "no checkpoint" and "a checkpoint" uniformly — every
    method is a no-op, so the embed/index paths need no `if checkpoint:` guards.
    """

    def get(self, key):
        return None

    def put_many(self, items):
        pass

    def discard(self):
        pass

    def close(self):
        pass

    def __len__(self):
        return 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass
