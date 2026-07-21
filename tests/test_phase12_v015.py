from pathlib import Path
import tempfile
import unittest

from helpers import FIXTURE_QUOTE, FIXTURE_WORD, ImportedFixture
from readmemory.service import ReadMemoryService
from readmemory.storage import Store
from readmemory.words import normalize_word


class Phase12V015Tests(unittest.TestCase):
    def test_normalize_word_basic(self) -> None:
        # normalize_word only lowercases and strips punctuation; no suffix rules.
        self.assertEqual(normalize_word("weariness"), "weariness")
        self.assertEqual(normalize_word("Weariness"), "weariness")
        self.assertEqual(normalize_word("triumphs"), "triumphs")
        self.assertEqual(normalize_word("annulled"), "annulled")
        self.assertEqual(normalize_word("Doomed"), "doomed")
        self.assertEqual(normalize_word("don't"), "don't")

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
            # First save WITH lemma so group_key is set.
            first = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["margin"],
                source_sentence=FIXTURE_QUOTE,
                meanings=[{"word": "margin", "lemma": "margin"}],
                compact=True,
            )
            self.assertEqual(first["saved_count"], 1)
            # Same lemma via different case should be detected as duplicate.
            second = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["Margin"],
                source_sentence=FIXTURE_QUOTE,
                meanings=[{"word": "Margin", "lemma": "margin"}],
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

    def test_add_vocabulary_no_lemma_no_duplicate(self) -> None:
        """Without agent-provided lemma, no duplicate detection across forms."""
        fixture = ImportedFixture()
        try:
            service = fixture.service
            first = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["doomed"],
                source_sentence=FIXTURE_QUOTE,
                compact=True,
            )
            self.assertEqual(first["saved_count"], 1)
            # Without lemma, "doom" is NOT treated as duplicate of "doomed".
            second = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["doom"],
                source_sentence=FIXTURE_QUOTE,
                compact=True,
            )
            self.assertEqual(second["saved_count"], 1)
            self.assertEqual(second["duplicate_count"], 0)
        finally:
            fixture.cleanup()

    def test_edit_vocabulary_lemma_syncs_group_key(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            result = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["doomed"],
                source_sentence=FIXTURE_QUOTE,
            )
            note_id = result[0]["id"]
            self.assertIsNone(result[0]["group_key"])
            updated = service.edit_item(
                entity_type="vocabulary",
                item_id=note_id,
                changes={"lemma": "doom"},
            )
            self.assertEqual(updated["lemma"], "doom")
            self.assertEqual(updated["group_key"], "doom")
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
            service.add_vocabulary(book_id=fixture.book_id, words=["margin"], source_sentence=FIXTURE_QUOTE)
            reviews = service.get_due_reviews(book_id=fixture.book_id, mode="all")
            self.assertGreater(len(reviews), 0)
            self.assertIn("prompt", reviews[0])
            # Cloze format: word replaced with ______
            self.assertIn("______", reviews[0]["prompt"])
        finally:
            fixture.cleanup()

    def test_batch_record_review_results(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            service.add_vocabulary(
                book_id=fixture.book_id,
                words=["margin", "weariness"],
                source_sentence=FIXTURE_QUOTE,
            )
            reviews = service.get_due_reviews(book_id=fixture.book_id, mode="all")
            self.assertEqual(len(reviews), 2)
            results = [
                {"review_item_id": reviews[0]["id"], "result": "known"},
                {"review_item_id": reviews[1]["id"], "result": "fuzzy"},
                {"review_item_id": "fake_id", "result": "known"},
            ]
            outcome = service.batch_record_review_results(results=results)
            self.assertEqual(outcome["recorded"], 2)
            self.assertEqual(outcome["errors"], ["fake_id"])
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

    def test_get_due_reviews_grouped_by_family(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            service.add_vocabulary(
                book_id=fixture.book_id,
                words=["annulled"],
                source_sentence=FIXTURE_QUOTE,
                meanings=[{"word": "annulled", "lemma": "annul"}],
            )
            service.add_vocabulary(
                book_id=fixture.book_id,
                words=["annul"],
                source_sentence=FIXTURE_QUOTE,
                meanings=[{"word": "annul", "lemma": "annul"}],
            )
            result = service.get_due_reviews(book_id=fixture.book_id, mode="all", group_by_family=True)
            self.assertIn("grouped", result)
            self.assertIn("ungrouped", result)
            self.assertEqual(len(result["grouped"]), 1)
            self.assertEqual(result["grouped"][0]["group_key"], "annul")
            self.assertEqual(len(result["grouped"][0]["items"]), 1)
        finally:
            fixture.cleanup()

    def test_record_review_result_fuzzy(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            service.add_vocabulary(book_id=fixture.book_id, words=["margin"], source_sentence=FIXTURE_QUOTE)
            reviews = service.get_due_reviews(book_id=fixture.book_id, mode="all")
            item_id = reviews[0]["id"]
            result = service.record_review_result(review_item_id=item_id, result="fuzzy")
            self.assertEqual(result["last_result"], "uncertain")
            self.assertEqual(result["interval_days"], 1)  # max(1, 1//2)
        finally:
            fixture.cleanup()

    def test_record_review_result_want_lesson(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            service.add_vocabulary(book_id=fixture.book_id, words=["margin"], source_sentence=FIXTURE_QUOTE)
            reviews = service.get_due_reviews(book_id=fixture.book_id, mode="all")
            item_id = reviews[0]["id"]
            result = service.record_review_result(review_item_id=item_id, result="want_lesson")
            self.assertEqual(result["last_result"], "uncertain")
            self.assertEqual(result["interval_days"], 1)
        finally:
            fixture.cleanup()

    def test_get_and_save_lesson(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            service.add_vocabulary(
                book_id=fixture.book_id,
                words=["annulled"],
                source_sentence=FIXTURE_QUOTE,
                meanings=[{"word": "annulled", "lemma": "annul"}],
            )
            # No lesson yet.
            lesson = service.get_lesson(book_id=fixture.book_id, group_key="annul")
            self.assertEqual(lesson["status"], "found")
            self.assertIsNone(lesson["lesson_content"])
            self.assertIn("annulled", lesson["words"])
            # Save lesson.
            saved = service.save_lesson(
                book_id=fixture.book_id,
                group_key="annul",
                lesson_content="annul: to cancel or invalidate officially",
            )
            self.assertEqual(saved["updated_count"], 1)
            # Retrieve again.
            lesson = service.get_lesson(book_id=fixture.book_id, group_key="annul")
            self.assertEqual(lesson["lesson_content"], "annul: to cancel or invalidate officially")
            self.assertIsNotNone(lesson["lesson_generated_at"])
        finally:
            fixture.cleanup()

    def test_schema_v5_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "readmemory.sqlite"
            store = Store(db_path)
            store.initialize()
            version = store.fetchone("SELECT value FROM schema_meta WHERE key = 'schema_version'")
            self.assertEqual(version["value"], "5")
            # Check new columns exist.
            cols = {row[1] for row in store.connect().execute("PRAGMA table_info(vocabulary_notes)")}
            self.assertIn("lesson_content", cols)
            self.assertIn("lesson_generated_at", cols)

    def test_find_sentence_in_range_with_anchor(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            store = service.store
            # Get real unit ids from the fixture.
            units = store.fetchall(
                "SELECT id, text FROM source_units WHERE book_id = ? AND unit_type = 'sentence' ORDER BY id LIMIT 3",
                (fixture.book_id,),
            )
            self.assertGreaterEqual(len(units), 3)
            # Anchor 1: first unit
            store.execute(
                "INSERT INTO anchors (id, book_id, source_unit_id, anchor_quote, confidence, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("anchor_early", fixture.book_id, units[0]["id"], "The margin", 1.0,
                 "2026-01-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00"),
            )
            # Anchor 2: third unit
            store.execute(
                "INSERT INTO anchors (id, book_id, source_unit_id, anchor_quote, confidence, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("anchor_late", fixture.book_id, units[2]["id"], "Source text", 1.0,
                 "2026-01-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00"),
            )
            # "Source text" is in unit 3; range from anchor_early to anchor_late
            found = service._find_sentence_in_range(
                book_id=fixture.book_id,
                word="Source text",
                anchor_id="anchor_late",
            )
            self.assertIsNotNone(found)
            self.assertIn("Source text", found)
        finally:
            fixture.cleanup()

    def test_add_vocabulary_auto_finds_sentence_in_range(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            store = service.store
            # Get a real unit id.
            unit = store.fetchone(
                "SELECT id FROM source_units WHERE book_id = ? AND unit_type = 'sentence' ORDER BY id LIMIT 1",
                (fixture.book_id,),
            )
            self.assertIsNotNone(unit)
            # Create anchor at that unit
            store.execute(
                "INSERT INTO anchors (id, book_id, source_unit_id, anchor_quote, confidence, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("anchor_test", fixture.book_id, unit["id"], "The margin", 1.0,
                 "2026-01-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00"),
            )
            # Add vocabulary without source_sentence; should auto-find in range.
            result = service.add_vocabulary(
                book_id=fixture.book_id,
                words=["margin"],
                anchor_id="anchor_test",
            )
            self.assertEqual(len(result), 1)
            self.assertIn("margin", result[0]["source_sentence"])
        finally:
            fixture.cleanup()


if __name__ == "__main__":
    unittest.main()
