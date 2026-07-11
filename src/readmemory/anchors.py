from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .repository import Repository, match_score, normalize_quote


@dataclass(frozen=True)
class AnchorCandidate:
    source_unit_id: str
    unit_type: str
    chapter_index: int | None
    paragraph_index: int | None
    sentence_index: int | None
    text: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_unit_id": self.source_unit_id,
            "unit_type": self.unit_type,
            "chapter_index": self.chapter_index,
            "paragraph_index": self.paragraph_index,
            "sentence_index": self.sentence_index,
            "text": self.text,
            "confidence": round(self.confidence, 4),
        }


class AnchorResolver:
    def __init__(self, repo: Repository):
        self.repo = repo

    def _dedupe_candidates(self, candidates: list[AnchorCandidate]) -> list[AnchorCandidate]:
        seen: set[tuple[int | None, int | None, str]] = set()
        deduped: list[AnchorCandidate] = []
        for candidate in candidates:
            key = (candidate.chapter_index, candidate.paragraph_index, normalize_quote(candidate.text))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(candidate)
        return deduped

    def find_anchor(
        self,
        *,
        book_id: str,
        quote: str,
        limit: int = 5,
        create_anchor: bool = False,
    ) -> dict[str, Any]:
        normalized_query = normalize_quote(quote)
        candidates: list[AnchorCandidate] = []
        for unit in self.repo.source_units_for_anchor_search(book_id=book_id):
            score = match_score(quote, unit["text"])
            if score >= 0.35:
                candidates.append(
                    AnchorCandidate(
                        source_unit_id=unit["id"],
                        unit_type=unit["unit_type"],
                        chapter_index=unit["chapter_index"],
                        paragraph_index=unit["paragraph_index"],
                        sentence_index=unit["sentence_index"],
                        text=unit["text"],
                        confidence=score,
                    )
                )

        candidates.sort(key=lambda item: item.confidence, reverse=True)
        candidates = self._dedupe_candidates(candidates)[:limit]
        selected = None
        status = "not_found"
        if candidates:
            exact_candidates = [
                item for item in candidates if normalize_quote(item.text) == normalized_query
            ]
            if exact_candidates:
                top = sorted(
                    exact_candidates,
                    key=lambda item: (
                        item.chapter_index or 0,
                        item.paragraph_index or 0,
                        item.sentence_index or 0,
                        0 if item.unit_type == "sentence" else 1,
                    ),
                )[0]
                selected = top.to_dict()
                if create_anchor:
                    selected = self.repo.create_anchor(
                        book_id=book_id,
                        source_unit_id=top.source_unit_id,
                        anchor_quote=quote,
                        confidence=top.confidence,
                    )
                status = "resolved"
            else:
                top = candidates[0]
                second = candidates[1] if len(candidates) > 1 else None
                if top.confidence >= 0.8 and (second is None or top.confidence - second.confidence >= 0.05):
                    selected = top.to_dict()
                    if create_anchor:
                        selected = self.repo.create_anchor(
                            book_id=book_id,
                            source_unit_id=top.source_unit_id,
                            anchor_quote=quote,
                            confidence=top.confidence,
                        )
                    status = "resolved"
                elif top.confidence >= 0.35:
                    status = "ambiguous"

        return {
            "book_id": book_id,
            "quote": quote,
            "status": status,
            "selected": selected,
            "candidates": [item.to_dict() for item in candidates],
        }
