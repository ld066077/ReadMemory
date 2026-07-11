import unittest

from helpers import FIXTURE_QUOTE, ImportedFixture


class Phase10CorrectionTests(unittest.TestCase):
    def test_find_anchor_is_read_only_and_unanchored_note_stays_unanchored(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            before = service.store.fetchone("SELECT COUNT(*) AS count FROM anchors")["count"]
            result = service.find_anchor(book_id=fixture.book_id, quote=FIXTURE_QUOTE)
            after = service.store.fetchone("SELECT COUNT(*) AS count FROM anchors")["count"]
            note = service.add_thought(book_id=fixture.book_id, thought_text="No source supplied.")

            self.assertEqual(result["status"], "resolved")
            self.assertEqual(before, after)
            self.assertIsNone(note["anchor_id"])
        finally:
            fixture.cleanup()

    def test_reconcile_edit_delete_and_undo(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            note = service.add_thought(book_id=fixture.book_id, thought_text="Draft thought.")
            reconciled = service.reconcile_item(
                entity_type="thought", item_id=note["id"], quote=FIXTURE_QUOTE
            )
            edited = service.edit_item(
                entity_type="thought",
                item_id=note["id"],
                changes={"thought_text": "Edited thought."},
            )
            deleted = service.delete_item(entity_type="thought", item_id=note["id"])
            restored = service.undo_last()
            restored_note = service.store.fetchone(
                "SELECT * FROM thought_notes WHERE id = ?", (note["id"],)
            )

            self.assertEqual(reconciled["status"], "reconciled")
            self.assertIsNotNone(reconciled["item"]["anchor_id"])
            self.assertEqual(edited["thought_text"], "Edited thought.")
            self.assertEqual(deleted["status"], "deleted")
            self.assertEqual(restored["status"], "undone")
            self.assertEqual(restored_note["thought_text"], "Edited thought.")
        finally:
            fixture.cleanup()

    def test_undo_create_removes_note_and_review(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            note = service.add_sentence(book_id=fixture.book_id, sentence=FIXTURE_QUOTE)
            result = service.undo_last()
            stored = service.store.fetchone(
                "SELECT * FROM sentence_notes WHERE id = ?", (note["id"],)
            )
            reviews = service.store.fetchall(
                "SELECT * FROM review_items WHERE item_id = ?", (note["id"],)
            )

            self.assertEqual(result["action_type"], "create")
            self.assertIsNone(stored)
            self.assertEqual(reviews, [])
        finally:
            fixture.cleanup()
