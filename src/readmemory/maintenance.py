from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import json


class MaintenanceMixin:
    store: Any

    def _entity_spec(self, entity_type: str) -> tuple[str, set[str]]:
        specs = {
            "session": ("reading_sessions", {"session_date", "user_note", "status"}),
            "vocabulary": (
                "vocabulary_notes",
                {"word", "lemma", "source_sentence", "user_meaning", "ai_context_meaning", "note_date"},
            ),
            "sentence": (
                "sentence_notes",
                {"sentence", "reason_saved", "pattern_note", "imitation_examples", "note_date"},
            ),
            "thought": ("thought_notes", {"thought_text", "related_quote", "tags", "note_date"}),
        }
        if entity_type not in specs:
            raise ValueError("entity_type must be session, vocabulary, sentence, or thought")
        return specs[entity_type]

    def edit_item(
        self, *, entity_type: str, item_id: str, changes: dict[str, Any]
    ) -> dict[str, Any]:
        table, allowed = self._entity_spec(entity_type)
        invalid = set(changes) - allowed
        if invalid or not changes:
            fields = ", ".join(sorted(invalid)) if invalid else "none supplied"
            raise ValueError(f"invalid editable fields: {fields}")
        current = self.store.fetchone(f"SELECT * FROM {table} WHERE id = ?", (item_id,))
        if not current:
            raise KeyError(item_id)
        previous = {key: current.get(key) for key in changes}
        assignments = ", ".join(f"{key} = ?" for key in changes)
        params = list(changes.values())

        # Sync group_key when lemma changes on vocabulary notes.
        if entity_type == "vocabulary" and "lemma" in changes:
            new_lemma = changes["lemma"]
            group_key = new_lemma.strip().lower() if new_lemma else None
            assignments += ", group_key = ?"
            params.append(group_key)
            previous["group_key"] = current.get("group_key")

        params.extend([self._now(), item_id])
        self.store.execute(f"UPDATE {table} SET {assignments}, updated_at = ? WHERE id = ?", tuple(params))
        self._record_action(
            action_type="edit",
            entity_type=entity_type,
            entity_id=item_id,
            payload={"previous": previous},
        )
        return self.store.fetchone(f"SELECT * FROM {table} WHERE id = ?", (item_id,))

    def reconcile_item(
        self, *, entity_type: str, item_id: str, quote: str
    ) -> dict[str, Any]:
        table, _ = self._entity_spec(entity_type)
        current = self.store.fetchone(f"SELECT * FROM {table} WHERE id = ?", (item_id,))
        if not current:
            raise KeyError(item_id)
        result = self.find_anchor(book_id=current["book_id"], quote=quote)
        if result["status"] != "resolved" or not result["selected"]:
            return {"status": result["status"], "item": current, "anchor_result": result}
        anchor = self._materialize_anchor(
            book_id=current["book_id"], quote=quote, selected=result["selected"]
        )
        if entity_type == "session":
            previous = {
                "end_anchor_id": current.get("end_anchor_id"),
                "status": current.get("status"),
            }
            self.store.execute(
                "UPDATE reading_sessions SET end_anchor_id = ?, status = ?, updated_at = ? WHERE id = ?",
                (anchor["id"], "partial", self._now(), item_id),
            )
        else:
            previous = {"anchor_id": current.get("anchor_id")}
            self.store.execute(
                f"UPDATE {table} SET anchor_id = ?, updated_at = ? WHERE id = ?",
                (anchor["id"], self._now(), item_id),
            )
        self._record_action(
            action_type="reconcile",
            entity_type=entity_type,
            entity_id=item_id,
            payload={"previous": previous},
        )
        return {
            "status": "reconciled",
            "item": self.store.fetchone(f"SELECT * FROM {table} WHERE id = ?", (item_id,)),
            "anchor": anchor,
        }

    def delete_item(self, *, entity_type: str, item_id: str) -> dict[str, Any]:
        table, _ = self._entity_spec(entity_type)
        current = self.store.fetchone(f"SELECT * FROM {table} WHERE id = ?", (item_id,))
        if not current:
            raise KeyError(item_id)
        reviews = []
        if entity_type != "session":
            reviews = self.store.fetchall("SELECT * FROM review_items WHERE item_id = ?", (item_id,))
            self.store.execute("DELETE FROM review_items WHERE item_id = ?", (item_id,))
        self.store.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
        self._record_action(
            action_type="delete",
            entity_type=entity_type,
            entity_id=item_id,
            payload={"row": current, "reviews": reviews},
        )
        return {"status": "deleted", "entity_type": entity_type, "item_id": item_id}

    def undo_last(self) -> dict[str, Any]:
        action = self.store.fetchone(
            "SELECT * FROM action_history WHERE undone_at IS NULL "
            "ORDER BY created_at DESC, rowid DESC LIMIT 1"
        )
        if not action:
            return {"status": "nothing_to_undo"}
        table, _ = self._entity_spec(action["entity_type"])
        payload = json.loads(action["payload"])
        entity_id = action["entity_id"]
        action_type = action["action_type"]
        if action_type == "create":
            if action["entity_type"] != "session":
                self.store.execute("DELETE FROM review_items WHERE item_id = ?", (entity_id,))
            self.store.execute(f"DELETE FROM {table} WHERE id = ?", (entity_id,))
        elif action_type in {"edit", "reconcile"}:
            previous = payload["previous"]
            assignments = ", ".join(f"{key} = ?" for key in previous)
            params = tuple(previous.values()) + (self._now(), entity_id)
            self.store.execute(
                f"UPDATE {table} SET {assignments}, updated_at = ? WHERE id = ?", params
            )
        elif action_type == "delete":
            self._restore_row(table, payload["row"])
            for review in payload.get("reviews", []):
                self._restore_row("review_items", review)
        else:
            raise ValueError(f"unsupported undo action: {action_type}")
        self.store.execute(
            "UPDATE action_history SET undone_at = ? WHERE id = ?", (self._now(), action["id"])
        )
        return {
            "status": "undone",
            "action_type": action_type,
            "entity_type": action["entity_type"],
            "item_id": entity_id,
        }

    def _restore_row(self, table: str, row: dict[str, Any]) -> None:
        columns = list(row)
        placeholders = ", ".join("?" for _ in columns)
        self.store.execute(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            tuple(row[column] for column in columns),
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
