"""Shortcode regex used by the Elasticsearch analyzer's pattern_replace
char_filter. Lives in its own module so it can be imported by tests without
pulling in Flask and other runtime deps.

The pattern is consumed by Elasticsearch's Java regex engine in production;
Python's `re` agrees on the constructs we use here, so it's also safe to
exercise from unit tests.
"""

# Matches shortcode-shaped tags so they can be stripped before tokenization:
#   [tag], [/tag], [tag attr="v" attr2='v'], [tag attr=bare], [tag/]
# Tag names are always lowercase in the source data, so capitalized bracketed
# text like "[Al-Bukhari]" is preserved as content. Also designed NOT to match
# multi-word bracketed asides (e.g. "[bleeding (from the womb) ...]").
SHORTCODE_PATTERN = (
    r"""\[/?[a-z][a-z0-9_-]*"""
    r"""(?:\s+[a-zA-Z_:][a-zA-Z0-9_:.-]*\s*=\s*(?:"[^"]*"|'[^']*'|[^\s\]]+))*"""
    r"""\s*/?\]"""
)
