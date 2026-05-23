from __future__ import annotations

from pathlib import Path
import tempfile

from readmemory.service import ReadMemoryService
from readmemory.storage import Store


FIXTURE = Path(__file__).parent / "On the Heights of Despair (E. M. Cioran).epub"


class ImportedFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "readmemory.sqlite")
        self.store.initialize()
        self.service = ReadMemoryService(self.store)
        self.book_id = self.service.import_book(FIXTURE)["book"]["id"]

    def cleanup(self) -> None:
        self.tmp.cleanup()

