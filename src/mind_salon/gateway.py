from __future__ import annotations

from typing import Any

from mind_salon.models import Message, MessageType, Task


class GatewayLayer:
    def parse_request(self, user_input: str, trace_id: str, constraints: dict[str, Any] | None = None) -> tuple[Task, Message]:
        task = Task(title="User Request", goal=user_input, constraints=constraints or {})
        intent = Message(
            task_id=task.task_id,
            session_id="session_pending",
            from_role="gateway",
            to_role="task_scheduler",
            type=MessageType.SYSTEM,
            payload={"intent": user_input},
            trace_id=trace_id,
        )
        return task, intent
