from __future__ import annotations

from mind_salon.models import Session, SessionState
from mind_salon.store import InMemoryStore


class SessionManager:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def create(self, task_id: str, participants: list[str], pattern: str) -> Session:
        session = Session(task_id=task_id, participants=participants, active_pattern=pattern)
        self._store.add_session(session)
        return session

    def close(self, session: Session) -> None:
        session.state = SessionState.CLOSED
