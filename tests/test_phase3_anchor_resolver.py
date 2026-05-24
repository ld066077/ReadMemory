import unittest

from helpers import FIXTURE_QUOTE, ImportedFixture


class Phase3AnchorResolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = ImportedFixture()
        cls.service = cls.fixture.service
        cls.book_id = cls.fixture.book_id

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.cleanup()

    def test_exact_quote_resolves_anchor(self) -> None:
        result = self.service.find_anchor(book_id=self.book_id, quote=FIXTURE_QUOTE)

        self.assertEqual(result["status"], "resolved")
        self.assertIsNotNone(result["selected"])
        self.assertGreaterEqual(result["candidates"][0]["confidence"], 0.8)
        self.assertIn("chapter_index", result["candidates"][0])

    def test_normalized_quote_resolves_anchor(self) -> None:
        result = self.service.find_anchor(book_id=self.book_id, quote="the margin remembers   every careful sentence")

        self.assertEqual(result["status"], "resolved")
        self.assertIsNotNone(result["selected"])

    def test_unrelated_quote_is_not_final_progress(self) -> None:
        result = self.service.find_anchor(book_id=self.book_id, quote="zzzz qqqq no such phrase abc")

        self.assertIn(result["status"], {"not_found", "ambiguous"})
        self.assertIsNone(result["selected"])
