from __future__ import annotations

from pathlib import Path
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from readmemory.service import ReadMemoryService
from readmemory.storage import Store


FIXTURE_TITLE = "ReadMemory Sample Reader"
FIXTURE_AUTHOR = "ReadMemory Tests"
FIXTURE_QUOTE = "The margin remembers every careful sentence."
FIXTURE_WORD = "margin"


def write_sample_epub(path: Path) -> Path:
    chapter_body = "\n\n".join(
        [
            FIXTURE_QUOTE,
            "A quiet reader marks a page and returns with a sharper question.",
            "Source text stays grounded when notes point back to exact words.",
            "Review cards become useful when they keep the original context nearby.",
        ]
        * 35
    )
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=0)
        archive.writestr(
            "META-INF/container.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OPS/package.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
""",
        )
        archive.writestr(
            "OPS/package.opf",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<package version="3.0" unique-identifier="bookid" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">readmemory-sample-reader</dc:identifier>
    <dc:title>{FIXTURE_TITLE}</dc:title>
    <dc:creator>{FIXTURE_AUTHOR}</dc:creator>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>
""",
        )
        archive.writestr(
            "OPS/chapter1.xhtml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>{FIXTURE_TITLE}</title></head>
  <body>
    <h1>{FIXTURE_TITLE}</h1>
    {''.join(f'<p>{paragraph}</p>' for paragraph in chapter_body.split(chr(10) + chr(10)))}
  </body>
</html>
""",
        )
    return path


class ImportedFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.epub_path = write_sample_epub(Path(self.tmp.name) / "readmemory-sample-reader.epub")
        self.store = Store(Path(self.tmp.name) / "readmemory.sqlite")
        self.store.initialize()
        self.service = ReadMemoryService(self.store)
        self.book_id = self.service.import_book(self.epub_path)["book"]["id"]

    def cleanup(self) -> None:
        self.tmp.cleanup()
