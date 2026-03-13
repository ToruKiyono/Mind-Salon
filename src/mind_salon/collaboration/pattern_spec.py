from __future__ import annotations

from dataclasses import dataclass

from mind_salon.models import TaskStatus


@dataclass(slots=True)
class PatternStep:
    stage: TaskStatus
    role: str
    allow_tool_calls: bool = False


@dataclass(slots=True)
class PatternSpec:
    pattern_id: str
    goal: str
    roles: list[str]
    steps: list[PatternStep]
