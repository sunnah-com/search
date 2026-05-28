"""Cross-thread interval pacer for outbound HTTP calls.

Lives in utils/ so it can be reused if more remote inference providers are
added later, and so unit tests can exercise it without importing Flask.
"""

import threading
import time


class RateLimiter:
    """Enforce a minimum 60/rpm gap between successive `acquire()` calls.

    Chose interval pacing over a sliding window because some providers
    (notably Mixedbread's free tier) reject bursts on the first second even
    when the per-minute total is under cap. The window form would allow the
    initial `rpm` calls instantly; this form spaces them evenly.

    Pass rpm = -1 to disable throttling — for providers that don't publish
    an RPM cap (e.g. HF Dedicated Endpoints, which bill by compute time).
    """

    def __init__(self, rpm, log=None):
        self.enabled = rpm > 0
        if rpm == 0 and log is not None:
            log.warning(
                "rate_limiter_rpm_zero", extra={"hint": "use -1 to disable throttling"}
            )
        self.interval = 60.0 / rpm if self.enabled else 0.0
        self.lock = threading.Lock()
        self.next_allowed = 0.0

    def acquire(self):
        if not self.enabled:
            return
        while True:
            with self.lock:
                now = time.monotonic()
                if now >= self.next_allowed:
                    self.next_allowed = now + self.interval
                    return
                wait = self.next_allowed - now
            time.sleep(wait)
