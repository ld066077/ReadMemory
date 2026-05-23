from pathlib import Path
import tempfile
import unittest

from readmemory.epub_importer import parse_epub
from readmemory.service import ReadMemoryService
from readmemory.storage import Store


FIXTURE = Path(__file__).parent / "On the Heights of Despair (E. M. Cioran).epub"


class Phase2EpubImportTests(unittest.TestCase):
    def test_parse_fixture_epub(self) -> None:
        parsed = parse_epub(FIXTURE)

        self.assertEqual(parsed.title, "On the Heights of Despair")
        self.assertIn("Cioran", parsed.author or "")
        self.assertTrue(parsed.language)
        self.assertTrue(parsed.epub_hash)
        self.assertGreater(parsed.total_words, 1000)
        self.assertGreater(len(parsed.source_units), 100)

    def test_import_fixture_and_search_exact_quote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "readmemory.sqlite")
            store.initialize()
            service = ReadMemoryService(store)

            result = service.import_book(FIXTURE)
            duplicate = service.import_book(FIXTURE)

            self.assertEqual(result["status"], "imported")
            self.assertEqual(duplicate["status"], "already_imported")
            self.assertEqual(duplicate["source_units_created"], 0)

            matches = service.search_source(
                book_id=result["book"]["id"],
                quote="On the Heights of Despair",
            )

            self.assertGreater(len(matches["matches"]), 0)

