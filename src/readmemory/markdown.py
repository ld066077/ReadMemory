from __future__ import annotations

from pathlib import Path
from typing import Any


def render_daily_log(*, date: str, records: dict[str, list[dict[str, Any]]], reviews: list[dict[str, Any]]) -> str:
    lines = [f"# English Reading Log - {date}", ""]

    lines.extend(["## Progress", ""])
    if records["sessions"]:
        for session in records["sessions"]:
            lines.append(f"- Session `{session['id']}`")
            lines.append(f"  - Status: {session['status']}")
            lines.append(f"  - Words read: {session['words_read']}")
            if session.get("user_note"):
                lines.append(f"  - Note: {session['user_note']}")
    else:
        lines.append("- No reading session recorded.")
    lines.append("")

    lines.extend(["## Vocabulary", ""])
    if records["vocabulary"]:
        for item in records["vocabulary"]:
            suffix = f" - {item['source_sentence']}" if item.get("source_sentence") else ""
            lines.append(f"- {item['word']}{suffix}")
    else:
        lines.append("- No vocabulary notes.")
    lines.append("")

    lines.extend(["## Sentences", ""])
    if records["sentences"]:
        for item in records["sentences"]:
            lines.append(f"- {item['sentence']}")
    else:
        lines.append("- No sentence notes.")
    lines.append("")

    lines.extend(["## Thoughts", ""])
    if records["thoughts"]:
        for item in records["thoughts"]:
            lines.append(f"- {item['thought_text']}")
    else:
        lines.append("- No thought notes.")
    lines.append("")

    lines.extend(["## Review Items", ""])
    if reviews:
        for item in reviews:
            lines.append(f"- {item['item_type']}: `{item['item_id']}` due {item['due_at']}")
    else:
        lines.append("- No due review items.")
    lines.append("")

    return "\n".join(lines)


def write_daily_log(*, output_dir: Path, date: str, markdown: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{date}-reading-log.md"
    path.write_text(markdown, encoding="utf-8")
    return path

