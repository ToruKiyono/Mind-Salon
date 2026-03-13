from __future__ import annotations

from mind_salon.models import TaskStatus


ORDERED_STAGES: list[TaskStatus] = [
    TaskStatus.INTENT,
    TaskStatus.PROPOSAL,
    TaskStatus.DELIBERATION,
    TaskStatus.EXECUTION,
    TaskStatus.REVIEW,
    TaskStatus.FEEDBACK,
    TaskStatus.DONE,
]


class WorkflowEngine:
    def next_status(self, current: TaskStatus) -> TaskStatus:
        idx = ORDERED_STAGES.index(current)
        if idx >= len(ORDERED_STAGES) - 1:
            return TaskStatus.DONE
        return ORDERED_STAGES[idx + 1]
