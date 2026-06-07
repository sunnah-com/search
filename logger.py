"""The shared `search.access` logger.

Configured once here and imported by every module that logs, so the handler,
formatter, and logger name live in a single place — no module needs to fetch
the logger by name and hope someone else configured it first.
"""

import logging
import sys

from pythonjsonlogger import jsonlogger

_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(
    jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
)

access_log = logging.getLogger("search.access")
access_log.setLevel(logging.INFO)
access_log.addHandler(_handler)
access_log.propagate = False
