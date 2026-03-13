from __future__ import annotations

from mind_salon.config import SalonConfig
from mind_salon.models import Task, TaskStatus


class ProtocolViolation(Exception):
    pass


class ProtocolEngine:
    def __init__(self, config: SalonConfig) -> None:
        self._config = config

    def validate_stage(self, task: Task, target: TaskStatus, deliberation_rounds: int) -> None:
        if task.status == TaskStatus.DELIBERATION and target == TaskStatus.EXECUTION:
            if deliberation_rounds > self._config.max_deliberation_rounds:
                raise ProtocolViolation("Deliberation rounds exceeded maximum")

    def decision_for_stage(self, stage: TaskStatus) -> str:
        if stage == TaskStatus.DELIBERATION:
            return "approve"
        if stage == TaskStatus.REVIEW:
            return "pass"
        return "continue"
