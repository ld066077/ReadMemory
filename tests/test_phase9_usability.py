import unittest

from helpers import FIXTURE_AUTHOR, FIXTURE_QUOTE, FIXTURE_TITLE, FIXTURE_WORD, ImportedFixture


class Phase9UsabilityTests(unittest.TestCase):
    def test_books_can_be_listed_searched_and_resolved(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service

            books = service.list_books()
            search = service.search_books(query="sample reader")
            resolved = service.resolve_book(book_ref="readmemory sample")

            self.assertEqual(len(books), 1)
            self.assertEqual(books[0]["title"], FIXTURE_TITLE)
            self.assertEqual(books[0]["author"], FIXTURE_AUTHOR)
            self.assertEqual(search[0]["id"], fixture.book_id)
            self.assertEqual(resolved["status"], "resolved")
            self.assertEqual(resolved["selected"]["id"], fixture.book_id)
        finally:
            fixture.cleanup()

    def test_book_ref_can_drive_source_anchor_progress_and_notes(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            book_ref = "sample reader"

            source = service.search_source(book_ref=book_ref, quote=FIXTURE_QUOTE)
            anchor = service.find_anchor(book_ref=book_ref, quote=FIXTURE_QUOTE)
            progress = service.log_progress(book_ref=book_ref, stop_quote=FIXTURE_QUOTE)
            vocab = service.add_vocabulary(
                book_ref=book_ref,
                words=[FIXTURE_WORD],
                source_sentence=FIXTURE_QUOTE,
                user_meaning="edge note",
            )
            sentence = service.add_sentence(book_ref=book_ref, sentence=FIXTURE_QUOTE)
            thought = service.add_thought(
                book_ref=book_ref,
                thought_text="This sentence is worth remembering.",
                related_quote=FIXTURE_QUOTE,
            )
            notes = service.search_notes(query=FIXTURE_WORD, book_ref=book_ref)

            self.assertEqual(source["book_id"], fixture.book_id)
            self.assertGreaterEqual(len(source["matches"]), 1)
            self.assertEqual(anchor["status"], "resolved")
            self.assertEqual(progress["session"]["book_id"], fixture.book_id)
            self.assertEqual(vocab[0]["book_id"], fixture.book_id)
            self.assertEqual(sentence["book_id"], fixture.book_id)
            self.assertEqual(thought["book_id"], fixture.book_id)
            self.assertTrue(any(item["note_type"] == "vocabulary" for item in notes))
        finally:
            fixture.cleanup()

    def test_unanchored_progress_is_explicit_and_visible_in_status(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service

            with self.assertRaises(ValueError):
                service.log_progress(
                    book_ref="sample reader",
                    stop_quote="a very rough location that is not in the book",
                )

            progress = service.log_progress(
                book_ref="sample reader",
                stop_quote="a very rough location that is not in the book",
                user_note="chapter 2, somewhere near the end",
                allow_unanchored=True,
            )
            status = service.status()
            unanchored = service.get_unanchored_items()

            self.assertEqual(progress["status"], "unanchored")
            self.assertIsNone(progress["session"]["end_anchor_id"])
            self.assertEqual(progress["session"]["user_note"], "chapter 2, somewhere near the end")
            self.assertGreaterEqual(status["unanchored_session_count"], 1)
            self.assertGreaterEqual(len(unanchored["sessions"]), 1)
        finally:
            fixture.cleanup()

    def test_status_reports_library_and_unanchored_notes(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            vocab = service.add_vocabulary(
                book_ref="sample reader",
                words=["unanchoredword"],
                user_meaning="saved before the source sentence is known",
            )
            status = service.status(book_limit=5, unanchored_limit=5)

            self.assertEqual(status["status"], "ready")
            self.assertEqual(status["book_count"], 1)
            self.assertEqual(status["books"][0]["id"], fixture.book_id)
            self.assertGreaterEqual(status["unanchored_note_count"], 1)
            self.assertTrue(
                any(item["id"] == vocab[0]["id"] for item in status["unanchored_notes"])
            )
        finally:
            fixture.cleanup()
