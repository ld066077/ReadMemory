from pathlib import Path
from unittest import mock
from zipfile import ZipFile
import sqlite3
import tempfile
import unittest

from helpers import FIXTURE_QUOTE, FIXTURE_WORD, ImportedFixture, write_sample_epub
from readmemory.paths import ReadMemoryPaths
from readmemory.service import ReadMemoryService
from readmemory.storage import Store


class Phase11V014Tests(unittest.TestCase):
    def test_v2_database_migrates_note_dates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "readmemory.sqlite"
            store = Store(db_path)
            store.initialize()
            store.execute(
                "UPDATE schema_meta SET value = '2' WHERE key = 'schema_version'"
            )
            store.execute(
                "INSERT INTO books (id, title, language, epub_hash, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                ("book_old", "Old", "en", "old-hash", "2026-01-02T00:00:00+00:00", "2026-01-02T00:00:00+00:00"),
            )
            store.execute(
                "INSERT INTO vocabulary_notes "
                "(id, book_id, word, note_date, created_at, updated_at) VALUES (?, ?, ?, NULL, ?, ?)",
                ("vocab_old", "book_old", "old", "2026-01-03T04:05:06+00:00", "2026-01-03T04:05:06+00:00"),
            )
            store.initialize()
            version = store.fetchone(
                "SELECT value FROM schema_meta WHERE key = 'schema_version'"
            )
            note = store.fetchone(
                "SELECT note_date FROM vocabulary_notes WHERE id = ?", ("vocab_old",)
            )
            self.assertEqual(version["value"], "3")
            self.assertEqual(note["note_date"], "2026-01-03")

    def test_explicit_note_date_appears_in_matching_daily_log(self) -> None:
        fixture = ImportedFixture()
        try:
            target = "2099-02-03"
            service = fixture.service
            service.log_progress(
                book_id=fixture.book_id,
                stop_quote=FIXTURE_QUOTE,
                session_date=target,
            )
            vocab = service.add_vocabulary(
                book_id=fixture.book_id,
                words=[FIXTURE_WORD],
                source_sentence=FIXTURE_QUOTE,
                note_date=target,
            )
            sentence = service.add_sentence(
                book_id=fixture.book_id,
                sentence=FIXTURE_QUOTE,
                note_date=target,
            )
            thought = service.add_thought(
                book_id=fixture.book_id,
                thought_text="dated thought",
                related_quote=FIXTURE_QUOTE,
                note_date=target,
            )
            records = service.get_today_records(book_id=fixture.book_id, on_date=target)
            with tempfile.TemporaryDirectory() as output:
                log = service.generate_daily_log(
                    book_id=fixture.book_id, on_date=target, output_dir=Path(output)
                )["markdown"]

            self.assertEqual(vocab[0]["note_date"], target)
            self.assertEqual(sentence["note_date"], target)
            self.assertEqual(thought["note_date"], target)
            self.assertEqual(len(records["sessions"]), 1)
            self.assertEqual(len(records["vocabulary"]), 1)
            self.assertEqual(len(records["sentences"]), 1)
            self.assertEqual(len(records["thoughts"]), 1)
            self.assertIn(FIXTURE_WORD, log)
            self.assertIn(FIXTURE_QUOTE, log)
            self.assertIn("dated thought", log)
        finally:
            fixture.cleanup()

    def test_import_rolls_back_on_unit_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            epub = write_sample_epub(tmp_path / "sample.epub")
            store = Store(tmp_path / "readmemory.sqlite")
            store.initialize()
            service = ReadMemoryService(store)

            real_connect = store.connect

            class FailingConnection:
                def __init__(self, conn):
                    self.conn = conn
                    self.units = 0

                def execute(self, sql, params=()):
                    if "INSERT INTO source_units" in sql:
                        self.units += 1
                        if self.units == 2:
                            raise RuntimeError("simulated import failure")
                    return self.conn.execute(sql, params)

                def __getattr__(self, name):
                    return getattr(self.conn, name)

            with mock.patch.object(store, "connect", side_effect=lambda: FailingConnection(real_connect())):
                with self.assertRaises(RuntimeError):
                    service.import_book(epub)

            self.assertEqual(store.fetchone("SELECT COUNT(*) AS count FROM books")["count"], 0)
            self.assertEqual(store.fetchone("SELECT COUNT(*) AS count FROM source_units")["count"], 0)

    def test_backup_contains_snapshot_config_and_exports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = ReadMemoryPaths(
                config_dir=root / "config",
                config_path=root / "config" / "readmemory.toml",
                data_dir=root / "data",
                db_path=root / "data" / "readmemory.sqlite",
                books_dir=root / "data" / "books",
                exports_dir=root / "data" / "exports",
                logs_dir=root / "data" / "logs",
            )
            paths.ensure()
            paths.config_path.write_text('log_level = "INFO"\n', encoding="utf-8")
            paths.exports_dir.joinpath("sample.md").write_text("sample", encoding="utf-8")
            store = Store(paths.db_path)
            store.initialize()
            service = ReadMemoryService(store, paths=paths)
            result = service.backup(output_dir=root / "backups")

            archive_path = Path(result["path"])
            self.assertTrue(archive_path.exists())
            with ZipFile(archive_path) as archive:
                names = set(archive.namelist())
                self.assertIn("database/readmemory.sqlite", names)
                self.assertIn("config/readmemory.toml", names)
                self.assertIn("exports/sample.md", names)
                self.assertIn("manifest.json", names)
                snapshot = root / "snapshot.sqlite"
                snapshot.write_bytes(archive.read("database/readmemory.sqlite"))
            conn = sqlite3.connect(snapshot)
            try:
                self.assertEqual(
                    conn.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()[0],
                    "3",
                )
            finally:
                conn.close()
