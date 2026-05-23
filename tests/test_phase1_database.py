from pathlib import Path
import tempfile
import unittest

from readmemory.repository import Repository
from readmemory.storage import Store


class Phase1DatabaseTests(unittest.TestCase):
    def test_schema_and_core_crud(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "readmemory.sqlite"
            store = Store(db_path)
            store.initialize()
            repo = Repository(store)

            book = repo.create_book(title="Fixture", epub_hash="hash-1")
            source_unit = repo.create_source_unit(
                book_id=book["id"],
                unit_type="paragraph",
                text="I am writing this at a time when I have nothing to say.",
            )
            anchor = repo.create_anchor(
                book_id=book["id"],
                source_unit_id=source_unit["id"],
                anchor_quote="I am writing this",
            )
            vocab = repo.create_vocabulary_note(book_id=book["id"], anchor_id=anchor["id"], word="despair")
            sentence = repo.create_sentence_note(
                book_id=book["id"],
                anchor_id=anchor["id"],
                sentence="I am writing this at a time when I have nothing to say.",
            )
            thought = repo.create_thought_note(
                book_id=book["id"],
                anchor_id=anchor["id"],
                thought_text="The opening binds writing to exhaustion.",
            )
            review = repo.create_review_item(
                book_id=book["id"],
                item_type="vocabulary",
                item_id=vocab["id"],
                due_at="2026-05-24",
            )

            self.assertTrue(book["id"].startswith("book_"))
            self.assertEqual(repo.get_book(book["id"])["title"], "Fixture")
            self.assertEqual(vocab["word"], "despair")
            self.assertEqual(sentence["anchor_id"], anchor["id"])
            self.assertEqual(thought["book_id"], book["id"])
            self.assertEqual(review["item_id"], vocab["id"])

