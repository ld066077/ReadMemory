from pathlib import Path
import tempfile
import unittest

from helpers import ImportedFixture


class Phase7MarkdownExportTests(unittest.TestCase):
    def test_daily_log_contains_all_sections_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fixture = ImportedFixture()
            service = fixture.service
            book_id = fixture.book_id
            quote = "On the Heights of Despair"

            service.log_progress(book_id=book_id, stop_quote=quote)
            service.add_vocabulary(book_id=book_id, words=["despair"], source_sentence=quote)
            service.add_sentence(book_id=book_id, sentence=quote)
            service.add_thought(book_id=book_id, thought_text="The title frames the mood.", related_quote=quote)

            first = service.generate_daily_log(book_id=book_id, output_dir=tmp_path)
            second = service.generate_daily_log(book_id=book_id, output_dir=tmp_path)
            content = Path(first["path"]).read_text(encoding="utf-8")

            self.assertEqual(first["path"], second["path"])
            self.assertIn("## Progress", content)
            self.assertIn("## Vocabulary", content)
            self.assertIn("## Sentences", content)
            self.assertIn("## Thoughts", content)
            self.assertIn("## Review Items", content)
            self.assertEqual(content, Path(second["path"]).read_text(encoding="utf-8"))
            fixture.cleanup()
