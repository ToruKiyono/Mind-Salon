from __future__ import annotations

from mind_salon.models import Message
from mind_salon.store import InMemoryStore


class MessageBus:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def publish(self, message: Message) -> None:
        self._store.add_message(message)
