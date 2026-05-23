import unittest

from helpers import ImportedFixture


class Phase8ReviewQueueTests(unittest.TestCase):
    def test_due_reviews_and_result_updates(self) -> None:
        fixture = ImportedFixture()
        try:
            service = fixture.service
            quote = "On the Heights of Despair"
            service.log_progress(book_id=fixture.book_id, stop_quote=quote)
            vocab = service.add_vocabulary(book_id=fixture.book_id, words=["despair"], source_sentence=quote)
            due = service.get_due_reviews()

            self.assertTrue(due)
            review = next(item for item in due if item["item_id"] == vocab[0]["id"])
            correct = service.record_review_result(review_item_id=review["id"], result="correct")
            wrong = service.record_review_result(review_item_id=review["id"], result="wrong")

            self.assertEqual(correct["last_result"], "correct")
            self.assertGreater(correct["interval_days"], 1)
            self.assertEqual(wrong["last_result"], "wrong")
            self.assertEqual(wrong["interval_days"], 1)
        finally:
            fixture.cleanup()

