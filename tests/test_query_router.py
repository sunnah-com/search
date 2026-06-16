"""Unit tests for query_router — spam detection and route classification.

The router is observational: `route_query` / `routing_decision` classify a query
but do NOT change the served path (production `search()` routes on ?mode= only;
the decision is recorded in shadow-sampling metrics). These tests therefore
exercise the pure classifier directly — no live Flask/ES server needed.

Run with:  python -m unittest discover tests
"""

import unittest

from config import SearchMode
from query_router import is_spam, route_query, routing_decision

SEM = SearchMode.SEMANTIC
LEX = SearchMode.LEXICAL


class RouteQueryTests(unittest.TestCase):
    def test_arabic_routes_to_arabic_variant(self):
        for q in ("صلاة الليل", "الزكاة", "رمضان", "و"):
            self.assertEqual(route_query(q, LEX), ("lexical", "arabic"))

    def test_mixed_arabic_english_routes_arabic(self):
        # A single Arabic character is enough — Arabic tokens dominate intent.
        self.assertEqual(route_query("aisha عائشة", LEX), ("lexical", "arabic"))

    def test_quoted_routes_lexical_no_variant(self):
        for q in ('"prayer at night"', '"Messenger of Allah"', '"Day of Judgement"'):
            self.assertEqual(route_query(q, SEM), ("lexical", None))

    def test_reference_routes_to_reference_variant(self):
        for q in ("bukhari 1", "muslim 2363", "abu dawud 1", "bukahri 1", "5", "42", "1234"):
            self.assertEqual(route_query(q, SEM), ("lexical", "reference"))

    def test_number_first_query_is_not_reference(self):
        # Ends with a word, not a number — conceptual, passes through to mode.
        self.assertEqual(route_query("99 names", SEM), (SEM, None))
        self.assertEqual(route_query("7 levels of hell", SEM), (SEM, None))

    def test_boolean_routes_lexical_no_variant(self):
        for q in ("prayer AND night", "bukhari OR muslim", "prayer NOT shirk"):
            self.assertEqual(route_query(q, SEM), ("lexical", None))

    def test_plain_query_recommends_semantic_regardless_of_mode(self):
        # A plain natural-language query hits none of the lexical-forcing rules,
        # so the router recommends semantic even when lexical was requested.
        self.assertEqual(route_query("prayer at night", SEM), (SEM, None))
        self.assertEqual(route_query("prayer at night", LEX), (SEM, None))


class PriorityTests(unittest.TestCase):
    """Earlier rules always win and override ?mode=semantic."""

    def test_arabic_beats_quotes(self):
        # Quoted Arabic still searches the full corpus via the arabic variant.
        self.assertEqual(route_query('"صلاة الليل"', SEM), ("lexical", "arabic"))

    def test_arabic_overrides_semantic(self):
        self.assertEqual(routing_decision("صلاة الليل", SEM), "lexical_arabic")

    def test_quoted_overrides_semantic(self):
        self.assertEqual(routing_decision('"actions are by intention"', SEM), "lexical")

    def test_reference_overrides_semantic(self):
        self.assertEqual(routing_decision("bukhari 1", SEM), "lexical_reference")

    def test_boolean_overrides_semantic(self):
        self.assertEqual(routing_decision("prayer AND night", SEM), "lexical")


class RoutingDecisionLabelTests(unittest.TestCase):
    def test_labels(self):
        cases = [
            ("صلاة الليل", SEM, "lexical_arabic"),
            ("bukhari 1", SEM, "lexical_reference"),
            ('"angel of death"', SEM, "lexical"),
            ("prayer AND night", SEM, "lexical"),
            ("prayer at night", SEM, "semantic"),
            # Recommendation is independent of requested mode — this is the case
            # that was previously impossible to observe in lexical-served samples.
            ("prayer at night", LEX, "semantic"),
        ]
        for q, mode, expected in cases:
            self.assertEqual(routing_decision(q, mode), expected, q)


class SpamTests(unittest.TestCase):
    def test_spam_caught(self):
        spam = [
            "http://example.com",
            "visit buyfc26coins.com now",
            "+1 (555) 867-5309",
            "aaaaaaaa",
            ";;;;;;;;",
            "!@#$%^&*()",
            "WA 0852 2611 9277 Pasang Interior",
            "x" * 45,
        ]
        for q in spam:
            self.assertTrue(is_spam(q), q)

    def test_real_queries_not_spam(self):
        for q in ("prayer at night", "صلاة الليل", "bukhari 1", "comparing yourself to others"):
            self.assertFalse(is_spam(q), q)

    def test_empty_and_none_not_spam(self):
        self.assertFalse(is_spam(""))
        self.assertFalse(is_spam(None))

    def test_arabic_letters_not_penalised_by_symbol_density(self):
        # .isalpha() is Unicode-aware, so diacriticised Arabic is not flagged.
        self.assertFalse(is_spam("الرحمٰن الرحيم"))


if __name__ == "__main__":
    unittest.main()
