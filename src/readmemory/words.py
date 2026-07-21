from __future__ import annotations

import re


def normalize_word(word: str) -> str:
    """Return the lowercase form for basic duplicate detection.

    All lemmatization decisions are delegated to the agent. This function
    only normalizes case and strips punctuation so that "Weariness" and
    "weariness" can be compared without a full NLP pipeline.
    """
    text = word.strip().lower()
    text = re.sub(r"[^a-z'-]", "", text)
    return text


def words_match(a: str, b: str) -> bool:
    return normalize_word(a) == normalize_word(b)
