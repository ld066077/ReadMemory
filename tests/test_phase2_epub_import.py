from pathlib import Path
import tempfile
import unittest

from helpers import FIXTURE_AUTHOR, FIXTURE_QUOTE, FIXTURE_TITLE, write_sample_epub
from readmemory.epub_importer import parse_epub
from readmemory.service import ReadMemoryService
from readmemory.storage import Store


class Phase2EpubImportTests(unittest.TestCase):
    def test_parse_fixture_epub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_sample_epub(Path(tmp) / "readmemory-sample-reader.epub")
            parsed = parse_epub(fixture)

        self.assertEqual(parsed.title, FIXTURE_TITLE)
        self.assertEqual(parsed.author, FIXTURE_AUTHOR)
        self.assertEqual(parsed.language, "en")
        self.assertTrue(parsed.epub_hash)
        self.assertGreater(parsed.total_words, 1000)
        self.assertGreater(len(parsed.source_units), 100)

    def test_import_fixture_and_search_exact_quote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_sample_epub(Path(tmp) / "readmemory-sample-reader.epub")
            store = Store(Path(tmp) / "readmemory.sqlite")
            store.initialize()
            service = ReadMemoryService(store)

            result = service.import_book(fixture)
            duplicate = service.import_book(fixture)

            self.assertEqual(result["status"], "imported")
            self.assertEqual(duplicate["status"], "already_imported")
            self.assertEqual(duplicate["source_units_created"], 0)

            matches = service.search_source(
                book_id=result["book"]["id"],
                quote=FIXTURE_QUOTE,
            )

            self.assertGreater(len(matches["matches"]), 0)
