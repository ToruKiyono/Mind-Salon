from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(slots=True)
class ToolResult:
    ok: bool
    output: dict[str, Any]
    error: str | None = None


ToolHandler = Callable[[dict[str, Any]], ToolResult]


class ToolEngine:
    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}
        self.register("generate_result", self._default_generate_result)

    def register(self, name: str, handler: ToolHandler) -> None:
        self._handlers[name] = handler

    def run(self, action: str, payload: dict[str, Any]) -> ToolResult:
        if action not in self._handlers:
            return ToolResult(ok=False, output={}, error=f"Unknown tool: {action}")
        return self._handlers[action](payload)

    def _default_generate_result(self, payload: dict[str, Any]) -> ToolResult:
        goal = payload.get("goal", "task")
        return ToolResult(ok=True, output={"result": f"draft for {goal}"})
