from __future__ import annotations

from mind_salon.collaboration.pattern_spec import PatternSpec, PatternStep


class PatternExecutor:
    def __init__(self, pattern: PatternSpec) -> None:
        self._pattern = pattern

    @property
    def pattern(self) -> PatternSpec:
        return self._pattern

    def steps(self) -> list[PatternStep]:
        return list(self._pattern.steps)
