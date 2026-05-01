"""Tests for SHORTCODE_PATTERN.

Note: the pattern is executed by Elasticsearch's Java regex engine in
production. These tests use Python's `re` module to verify intent. The
constructs we use (character classes, alternation, \\s, non-capturing groups)
behave identically in both engines.

Run with:  python -m unittest discover tests
"""

import re
import unittest

from utils.shortcode_pattern import SHORTCODE_PATTERN


def strip(text):
    return re.sub(SHORTCODE_PATTERN, " ", text)


class ShortcodeStripTests(unittest.TestCase):
    def test_strips_simple_open_and_close(self):
        self.assertEqual(strip("[matn]hello[/matn]"), " hello ")

    def test_strips_all_known_shortcodes(self):
        for tag in ("matn", "commentary", "narrator", "prematn", "postmatn"):
            self.assertEqual(strip(f"[{tag}]x[/{tag}]"), " x ")

    def test_strips_attributed_shortcode_with_double_quotes(self):
        s = '[narrator id="1001" tooltip="إسماعيل بن إبراهيم"]Abu[/narrator]'
        self.assertEqual(strip(s), " Abu ")

    def test_strips_attributed_shortcode_with_single_quotes(self):
        self.assertEqual(strip("[tag attr='value']x[/tag]"), " x ")

    def test_strips_attributed_shortcode_with_bare_value(self):
        self.assertEqual(strip("[tag attr=bare]x[/tag]"), " x ")

    def test_strips_self_closing_shortcode(self):
        self.assertEqual(strip("before [br/] after"), "before   after")

    def test_strips_unknown_but_shortcode_shaped_tags(self):
        # Future-proofing: any tag-shaped token is stripped.
        self.assertEqual(strip("[somefuture id=\"5\"]z[/somefuture]"), " z ")

    def test_preserves_multi_word_parenthetical_asides(self):
        s = "Keep [bleeding (from the womb) in between a woman periods] intact"
        self.assertEqual(strip(s), s)

    def test_preserves_qur_an_aside(self):
        s = "Keep [The understanding of the Quran and As-Sunna] intact"
        self.assertEqual(strip(s), s)

    def test_preserves_text_outside_shortcodes(self):
        s = "The Prophet (saws) said, [matn]be kind[/matn] to your neighbor."
        self.assertEqual(strip(s), "The Prophet (saws) said,  be kind  to your neighbor.")

    def test_does_not_match_brackets_with_leading_space(self):
        # Tag name must be the first thing after `[`.
        self.assertEqual(strip("[ matn]x[/matn]"), "[ matn]x ")

    def test_does_not_match_brackets_with_leading_digit(self):
        self.assertEqual(strip("[1matn]x[/matn]"), "[1matn]x ")

    def test_strips_adjacent_shortcodes_without_merging_words(self):
        # Replacement is a space, so adjacent words don't fuse together.
        out = strip("foo[matn][/matn]bar")
        self.assertNotIn("foobar", out)
        self.assertIn("foo", out)
        self.assertIn("bar", out)

    def test_known_false_positive_single_word_in_brackets(self):
        # Documented trade-off: a bare single-word bracket is structurally
        # indistinguishable from a [tag] shortcode, so it gets stripped.
        # If this ever needs to change, update SHORTCODE_PATTERN.
        self.assertEqual(strip("[Al-Bukhari]"), " ")


if __name__ == "__main__":
    unittest.main()
