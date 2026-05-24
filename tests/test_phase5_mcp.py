import unittest

from helpers import FIXTURE_QUOTE, FIXTURE_WORD, ImportedFixture


class Phase5McpTests(unittest.TestCase):
    def test_service_outputs_are_mcp_ready(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            book_id = fixture.book_id

            anchor = service.find_anchor(book_id=book_id, quote=FIXTURE_QUOTE)
            progress = service.log_progress(book_id=book_id, stop_quote=FIXTURE_QUOTE)
            vocab = service.add_vocabulary(book_id=book_id, words=[FIXTURE_WORD], source_sentence=FIXTURE_QUOTE)
            log = service.get_today_records(book_id=book_id)
            search = service.search_source(book_id=book_id, quote=FIXTURE_QUOTE)

            self.assertEqual(anchor["status"], "resolved")
            self.assertIn("session", progress)
            self.assertTrue(vocab[0]["id"])
            self.assertGreaterEqual(len(log["sessions"]), 1)
            self.assertGreaterEqual(len(search["matches"]), 1)
        finally:
            fixture.cleanup()
