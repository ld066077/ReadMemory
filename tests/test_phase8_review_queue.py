import unittest

from helpers import FIXTURE_QUOTE, FIXTURE_WORD, ImportedFixture


class Phase8ReviewQueueTests(unittest.TestCase):
    def test_due_reviews_and_result_updates(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            quote = FIXTURE_QUOTE
            service.log_progress(book_id=fixture.book_id, stop_quote=quote)
            vocab = service.add_vocabulary(book_id=fixture.book_id, words=[FIXTURE_WORD], source_sentence=quote)
            due = service.get_due_reviews()
            upcoming = service.get_due_reviews(mode="upcoming")
            all_reviews = service.get_due_reviews(mode="all")

            self.assertEqual(due, [])
            self.assertTrue(upcoming)
            review = next(item for item in all_reviews if item["item_id"] == vocab[0]["id"])
            self.assertEqual((review["title"], review["context"]), (FIXTURE_WORD, quote))
            correct = service.record_review_result(review_item_id=review["id"], result="correct")
            wrong = service.record_review_result(review_item_id=review["id"], result="wrong")

            self.assertEqual(correct["last_result"], "correct")
            self.assertGreater(correct["interval_days"], 1)
            self.assertEqual(wrong["last_result"], "wrong")
            self.assertEqual(wrong["interval_days"], 1)
        finally:
            fixture.cleanup()
