from __future__ import annotations

import re


def normalize_word(word: str) -> str:
    """Return a conservative normalized form for duplicate detection.

    Only lowercases and strips very common English inflections. The goal is
    to catch obvious duplicates like "Weariness" vs "weariness" or
    "triumphs" vs "triumph", not to be a full lemmatizer. When in doubt the
    original word is returned unchanged so false merges are avoided.
    """
    text = word.strip().lower()
    text = re.sub(r"[^a-z'-]", "", text)
    if len(text) <= 3:
        return text

    # Order matters: longest / most specific first.
    # -ies / -ied -> -y  (stories -> story, carried -> carry)
    if text.endswith("ies") and len(text) > 4:
        return text[:-3] + "y"
    if text.endswith("ied") and len(text) > 4:
        return text[:-3] + "y"

    # -ingly / -edly style are rare; skip.

    # -ing: walking -> walk, making -> make (restore silent-e when the stem
    # looks like CVC), stopping -> stop (drop doubled consonant).
    if text.endswith("ing") and len(text) > 5:
        stem = text[:-3]
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]
        elif len(stem) >= 3 and re.search(r"[aeiou][^aeiouwxy]$", stem):
            # making -> mak + e
            stem = stem + "e"
        return stem

    # -ed: walked -> walk, hoped -> hope, stopped -> stop.
    if text.endswith("ed") and len(text) > 4:
        stem = text[:-2]
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]
        elif len(stem) >= 3 and re.search(r"[aeiou][^aeiouwxy]$", stem):
            stem = stem + "e"
        return stem

    # -es: matches -> match, boxes -> box. Keep -ss/-us/-is intact (bias, this).
    if text.endswith("es") and len(text) > 3:
        if text.endswith(("ches", "shes", "sses", "xes", "zes", "oes")):
            return text[:-2]
        # -ases/-ises/-uses are usually not plural (bias, this) or are (cases).
        # Only strip -es for vowel+es patterns like hopes -> hope, cases -> case.
        if re.search(r"[aeiou]es$", text):
            return text[:-1]  # hopes -> hope (strip just -s)

    # -s: cats -> cat. Protect words ending in ss/us/is/as (bias, this, yes, gas).
    if text.endswith("s") and len(text) > 3:
        if text.endswith(("ss", "us", "is", "as")):
            return text
        # Don't strip -es here; that was handled above.
        if text.endswith("es"):
            return text
        return text[:-1]

    # -ly: quickly -> quick. Only when stem is at least 4 chars.
    if text.endswith("ly") and len(text) > 5:
        stem = text[:-2]
        # melancholy is not an adverb; keep stems ending in -o (melancho -> melancholy is wrong direction).
        if stem.endswith("o"):
            return text
        return stem

    return text


def words_match(a: str, b: str) -> bool:
    return normalize_word(a) == normalize_word(b)
