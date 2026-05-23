from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html import unescape
from pathlib import Path
from posixpath import dirname, normpath
from xml.etree import ElementTree as ET
from zipfile import ZipFile
import re


@dataclass(frozen=True)
class SourceUnit:
    unit_type: str
    chapter_index: int | None
    paragraph_index: int | None
    sentence_index: int | None
    text: str
    word_count: int
    content_hash: str


@dataclass(frozen=True)
class ParsedEpub:
    title: str
    author: str | None
    language: str
    epub_hash: str
    total_words: int
    source_units: list[SourceUnit]


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text_or_none(root: ET.Element, tag: str) -> str | None:
    node = root.find(f".//{{*}}{tag}")
    if node is None or node.text is None:
        return None
    return node.text.strip() or None


def _opf_path(zip_file: ZipFile) -> str:
    container = zip_file.read("META-INF/container.xml")
    root = ET.fromstring(container)
    node = root.find(".//{*}rootfile")
    if node is None:
        raise ValueError("EPUB container.xml does not contain rootfile")
    path = node.attrib.get("full-path")
    if not path:
        raise ValueError("EPUB rootfile is missing full-path")
    return path


def _clean_html(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="ignore")
    text = re.sub(r"(?is)<(script|style).*?>.*?</\\1>", " ", text)
    text = re.sub(r"(?i)</p>|<br\\s*/?>|</h[1-6]>", "\n\n", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s+\n", "\n\n", text)
    return text.strip()


def _split_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if paragraphs:
        return paragraphs
    return [text] if text else []


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _hash_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def parse_epub(path: Path) -> ParsedEpub:
    epub_hash = file_hash(path)
    source_units: list[SourceUnit] = []

    with ZipFile(path) as zip_file:
        opf_path = _opf_path(zip_file)
        opf_dir = dirname(opf_path)
        opf_root = ET.fromstring(zip_file.read(opf_path))

        title = _text_or_none(opf_root, "title") or path.stem
        author = _text_or_none(opf_root, "creator")
        language = _text_or_none(opf_root, "language") or "en"

        manifest: dict[str, str] = {}
        for item in opf_root.findall(".//{*}manifest/{*}item"):
            item_id = item.attrib.get("id")
            href = item.attrib.get("href")
            media_type = item.attrib.get("media-type", "")
            if item_id and href and ("html" in media_type or href.lower().endswith((".html", ".htm", ".xhtml"))):
                manifest[item_id] = normpath(f"{opf_dir}/{href}" if opf_dir else href)

        spine_ids = [
            itemref.attrib["idref"]
            for itemref in opf_root.findall(".//{*}spine/{*}itemref")
            if itemref.attrib.get("idref") in manifest
        ]
        if not spine_ids:
            spine_ids = list(manifest.keys())

        total_words = 0
        for chapter_index, item_id in enumerate(spine_ids, start=1):
            chapter_path = manifest[item_id]
            chapter_text = _clean_html(zip_file.read(chapter_path))
            if not chapter_text:
                continue
            chapter_words = _word_count(chapter_text)
            total_words += chapter_words
            source_units.append(
                SourceUnit(
                    unit_type="chapter",
                    chapter_index=chapter_index,
                    paragraph_index=None,
                    sentence_index=None,
                    text=chapter_text,
                    word_count=chapter_words,
                    content_hash=_hash_text(chapter_text),
                )
            )
            for paragraph_index, paragraph in enumerate(_split_paragraphs(chapter_text), start=1):
                paragraph_words = _word_count(paragraph)
                source_units.append(
                    SourceUnit(
                        unit_type="paragraph",
                        chapter_index=chapter_index,
                        paragraph_index=paragraph_index,
                        sentence_index=None,
                        text=paragraph,
                        word_count=paragraph_words,
                        content_hash=_hash_text(paragraph),
                    )
                )
                for sentence_index, sentence in enumerate(_split_sentences(paragraph), start=1):
                    source_units.append(
                        SourceUnit(
                            unit_type="sentence",
                            chapter_index=chapter_index,
                            paragraph_index=paragraph_index,
                            sentence_index=sentence_index,
                            text=sentence,
                            word_count=_word_count(sentence),
                            content_hash=_hash_text(sentence),
                        )
                    )

    return ParsedEpub(
        title=title,
        author=author,
        language=language,
        epub_hash=epub_hash,
        total_words=total_words,
        source_units=source_units,
    )

