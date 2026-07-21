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
            title = item.get("title") or item["item_id"]
            lines.append(f"- {item['item_type']}: {title} (due {item['due_at']})")
            if item.get("context"):
                lines.append(f"  - Context: {item['context']}")
    else:
        lines.append("- No due review items.")
    lines.append("")

    return "\n".join(lines)


def write_daily_log(*, output_dir: Path, date: str, markdown: str, filename_pattern: str = "{date}-reading-log.md") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename_pattern.format(date=date)
    path.write_text(markdown, encoding="utf-8")
    return path


def render_weekly_summary(*, summary: dict[str, Any]) -> str:
    totals = summary["totals"]
    lines = [
        f"# English Reading Weekly Summary - {summary['start_date']} to {summary['end_date']}",
        "",
        "## Overview",
        "",
        f"- Reading days: {totals['reading_days']}",
        f"- Reading sessions: {totals['session_count']}",
        f"- Words read: {totals['words_read']}",
        f"- Average words per reading day: {totals['average_words_per_reading_day']}",
        f"- Recommended next session target: {summary['recommended_next_words']} words",
        "",
        "## Notes Captured",
        "",
        f"- Vocabulary: {totals['vocabulary_count']}",
        f"- Sentences: {totals['sentence_count']}",
        f"- Thoughts: {totals['thought_count']}",
        "",
        "## Books",
        "",
    ]
    if summary["books"]:
        for book in summary["books"]:
            lines.append(f"- {book['title']}")
            lines.append(
                f"  - {book['words_read']} words across {book['session_count']} sessions"
            )
            lines.append(
                "  - Notes: "
                f"{book['vocabulary_count']} vocabulary, "
                f"{book['sentence_count']} sentences, "
                f"{book['thought_count']} thoughts"
            )
    else:
        lines.append("- No reading activity or notes recorded.")
    lines.extend(["", "## Daily Activity", ""])
    active_days = [day for day in summary["daily_activity"] if day["activity_count"]]
    if active_days:
        for day in active_days:
            lines.append(
                f"- {day['date']}: {day['words_read']} words, "
                f"{day['session_count']} sessions, {day['note_count']} notes"
            )
    else:
        lines.append("- No activity recorded this week.")
    lines.append("")
    return "\n".join(lines)


def write_weekly_summary(
    *, output_dir: Path, start_date: str, markdown: str
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{start_date}-weekly-summary.md"
    path.write_text(markdown, encoding="utf-8")
    return path
