from pathlib import Path
import tempfile
import unittest

from helpers import FIXTURE_QUOTE, FIXTURE_WORD, ImportedFixture
from readmemory.service import ReadMemoryService
from readmemory.storage import Store
from readmemory.words import normalize_word


class Phase12V015Tests(unittest.TestCase):
    def test_normalize_word_basic(self) -> None:
        self.assertEqual(normalize_word("weariness"), "weariness")
        self.assertEqual(normalize_word("Weariness"), "weariness")
        self.assertEqual(normalize_word("triumphs"), "triumph")
        self.assertEqual(normalize_word("annulled"), "annul")
        self.assertEqual(normalize_word("stories"), "story")
        self.assertEqual(normalize_word("carried"), "carry")
        self.assertEqual(normalize_word("making"), "make")
        self.assertEqual(normalize_word("hoped"), "hope")
        self.assertEqual(normalize_word("stopped"), "stop")
        self.assertEqual(normalize_word("consciously"), "conscious")
        self.assertEqual(normalize_word("melancholy"), "melancholy")  # not an adverb
        self.assertEqual(normalize_word("bias"), "bias")  # protected -is
        self.assertEqual(normalize_word("cats"), "cat")
        self.assertEqual(normalize_word("matches"), "match")

    def test_add_vocabulary_compact_summary(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            result = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["margin", "careful", "sentence"],
                source_sentence=FIXTURE_QUOTE,
                compact=True,
            )
            self.assertEqual(result["saved_count"], 3)
            self.assertEqual(result["duplicate_count"], 0)
            self.assertIn("margin", result["words"])
            self.assertIn("anchor_id", result)
        finally:
            fixture.cleanup()

    def test_add_vocabulary_duplicate_detection(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            first = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["margin"],
                source_sentence=FIXTURE_QUOTE,
                compact=True,
            )
            self.assertEqual(first["saved_count"], 1)
            # Same word again should be detected as duplicate.
            second = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["Margin"],  # different case
                source_sentence=FIXTURE_QUOTE,
                compact=True,
            )
            self.assertEqual(second["saved_count"], 0)
            self.assertEqual(second["duplicate_count"], 1)
            self.assertEqual(second["duplicates"][0]["existing_word"], "margin")
        finally:
            fixture.cleanup()

    def test_add_vocabulary_lemma_grouping(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            # First save with lemma.
            first = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["annulled"],
                source_sentence=FIXTURE_QUOTE,
                meanings=[{"word": "annulled", "lemma": "annul"}],
                compact=True,
            )
            self.assertEqual(first["saved_count"], 1)
            # Same lemma via different word form should be duplicate.
            second = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["annul"],
                source_sentence=FIXTURE_QUOTE,
                meanings=[{"word": "annul", "lemma": "annul"}],
                compact=True,
            )
            self.assertEqual(second["duplicate_count"], 1)
            self.assertEqual(second["duplicates"][0]["group_key"], "annul")
        finally:
            fixture.cleanup()

    def test_get_reading_position(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            # No position yet.
            result = service.get_reading_position(book_id=fixture.book_id)
            self.assertEqual(result["status"], "no_position")
            # Log progress and check position.
            service.log_progress(
                book_id=fixture.book_id,
                stop_quote=FIXTURE_QUOTE,
            )
            result = service.get_reading_position(book_id=fixture.book_id)
            self.assertEqual(result["status"], "found")
            self.assertIn("chapter_index", result)
            self.assertIn("anchor_quote", result)
        finally:
            fixture.cleanup()

    def test_get_vocabulary(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            service.add_vocabulary(
                book_id=fixture.book_id,
                words=["margin", "careful"],
                source_sentence=FIXTURE_QUOTE,
            )
            vocab = service.get_vocabulary(book_id=fixture.book_id)
            self.assertEqual(len(vocab), 2)
            words = {row["word"] for row in vocab}
            self.assertIn("margin", words)
            self.assertIn("careful", words)
        finally:
            fixture.cleanup()

    def test_get_vocabulary_grouped(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            service.add_vocabulary(
                book_id=fixture.book_id,
                words=["annulled", "annul"],
                source_sentence=FIXTURE_QUOTE,
                meanings=[
                    {"word": "annulled", "lemma": "annul"},
                    {"word": "annul", "lemma": "annul"},
                ],
            )
            # annulled saved, annul is duplicate.
            vocab = service.get_vocabulary(book_id=fixture.book_id, group_by_lemma=True)
            self.assertEqual(len(vocab), 1)
            self.assertEqual(vocab[0]["group_key"], "annul")
            self.assertIn("annulled", vocab[0]["words"])
        finally:
            fixture.cleanup()

    def test_get_sentences(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            service.add_sentence(
                book_id=fixture.book_id,
                sentence=FIXTURE_QUOTE,
            )
            sentences = service.get_sentences(book_id=fixture.book_id)
            self.assertEqual(len(sentences), 1)
            self.assertEqual(sentences[0]["sentence"], FIXTURE_QUOTE)
        finally:
            fixture.cleanup()

    def test_get_due_reviews_has_prompt(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            service.add_vocabulary(
                book_id=fixture.book_id,
                words=["margin"],
                source_sentence=FIXTURE_QUOTE,
            )
            # mode='all' returns all reviews regardless of due date.
            reviews = service.get_due_reviews(book_id=fixture.book_id, mode="all")
            self.assertGreater(len(reviews), 0)
            self.assertIn("prompt", reviews[0])
            self.assertIn("margin", reviews[0]["prompt"])
        finally:
            fixture.cleanup()

    def test_search_source_prefers_sentence_level(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            result = service.search_source(
                book_id=fixture.book_id,
                quote="margin",
            )
            matches = result["matches"]
            self.assertGreater(len(matches), 0)
            # First match should be sentence-level (not chapter).
            self.assertEqual(matches[0]["unit_type"], "sentence")
            self.assertIn("margin", matches[0]["text"].lower())
        finally:
            fixture.cleanup()

    def test_schema_v4_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "readmemory.sqlite"
            store = Store(db_path)
            store.initialize()
            store.execute(
                "UPDATE schema_meta SET value = '3' WHERE key = 'schema_version'"
            )
            store.execute("DROP INDEX IF EXISTS idx_vocabulary_normalized")
            store.execute("DROP INDEX IF EXISTS idx_vocabulary_group")
            store.execute("ALTER TABLE vocabulary_notes DROP COLUMN normalized_form")
            store.execute("ALTER TABLE vocabulary_notes DROP COLUMN group_key")
            store.execute(
                "INSERT INTO books (id, title, language, epub_hash, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                ("book_old", "Old", "en", "old-hash", "2026-01-02T00:00:00+00:00", "2026-01-02T00:00:00+00:00"),
            )
            store.execute(
                "INSERT INTO vocabulary_notes "
                "(id, book_id, word, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                ("vocab_old", "book_old", "Weariness", "2026-01-03T04:05:06+00:00", "2026-01-03T04:05:06+00:00"),
            )
            store.initialize()
            version = store.fetchone(
                "SELECT value FROM schema_meta WHERE key = 'schema_version'"
            )
            note = store.fetchone(
                "SELECT normalized_form, group_key FROM vocabulary_notes WHERE id = ?", ("vocab_old",)
            )
            self.assertEqual(version["value"], "4")
            self.assertEqual(note["normalized_form"], "weariness")
            self.assertEqual(note["group_key"], "weariness")


if __name__ == "__main__":
    unittest.main()
