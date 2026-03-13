from __future__ import annotations

from mind_salon.models import MemoryRecord, Task
from mind_salon.store import InMemoryStore


class MemoryEngine:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def write_feedback(self, task: Task, summary: str) -> MemoryRecord:
        rec = MemoryRecord(
            scope="long_term",
            source_task_id=task.task_id,
            content=summary,
            tags=["feedback", task.status.value],
        )
        self._store.add_memory(rec)
        return rec

    def retrieve(self, *, query: str, top_k: int = 5) -> list[MemoryRecord]:
        scored: list[tuple[int, MemoryRecord]] = []
        q = query.lower()
        for records in self._store.memory.values():
            for rec in records:
                hay = f"{rec.content} {' '.join(rec.tags)}".lower()
                score = 1 if q and q in hay else 0
                if score > 0:
                    scored.append((score, rec))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
