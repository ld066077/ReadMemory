import unittest

from helpers import FIXTURE_QUOTE, FIXTURE_WORD, ImportedFixture


class Phase4ReadingNotesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = ImportedFixture()
        cls.service = cls.fixture.service
        cls.book_id = cls.fixture.book_id

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.cleanup()

    def test_progress_and_notes_are_persisted(self) -> None:
        stop_quote = FIXTURE_QUOTE
        progress = self.service.log_progress(
            book_id=self.book_id,
            stop_quote=stop_quote,
            user_note="first session",
        )
        latest = self.service.get_latest_anchor(book_id=self.book_id)

        vocab = self.service.add_vocabulary(
            book_id=self.book_id,
            words=[FIXTURE_WORD],
            source_sentence=stop_quote,
            user_meaning=FIXTURE_WORD,
        )
        sentence = self.service.add_sentence(
            book_id=self.book_id,
            sentence=stop_quote,
            reason_saved="fixture check",
        )
        thought = self.service.add_thought(
            book_id=self.book_id,
            thought_text="The quote frames the reader's memory.",
            related_quote=stop_quote,
        )
        today = self.service.get_today_records(book_id=self.book_id)

        self.assertEqual(progress["session"]["user_note"], "first session")
        self.assertIsNotNone(latest)
        self.assertEqual(vocab[0]["word"], FIXTURE_WORD)
        self.assertEqual(sentence["sentence"], stop_quote)
        self.assertEqual(thought["thought_text"], "The quote frames the reader's memory.")
        self.assertGreaterEqual(len(today["sessions"]), 1)
        self.assertGreaterEqual(len(today["vocabulary"]), 1)
        self.assertGreaterEqual(len(today["sentences"]), 1)
        self.assertGreaterEqual(len(today["thoughts"]), 1)
