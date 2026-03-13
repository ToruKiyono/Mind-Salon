from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mind_salon.llm import LLMClient


@dataclass(slots=True)
class ToolCall:
    name: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentAction:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    decision: str = "continue"


class BaseAgent:
    role_type: str = "generic"

    def act(self, *, context: dict[str, Any], llm: LLMClient | None, allow_tool_calls: bool) -> AgentAction:
        raise NotImplementedError


class LLMAgent(BaseAgent):
    def __init__(self, role_type: str, system_prompt: str) -> None:
        self.role_type = role_type
        self.system_prompt = system_prompt

    def act(self, *, context: dict[str, Any], llm: LLMClient | None, allow_tool_calls: bool) -> AgentAction:
        llm_text = ""
        if llm is not None:
            llm_resp = llm.generate(system_prompt=self.system_prompt, user_prompt=_render_context(context))
            llm_text = llm_resp.content
        else:
            llm_text = f"{self.role_type} processed stage={context.get('stage')}"

        tool_calls: list[ToolCall] = []
        if allow_tool_calls and context.get("stage") == "execution":
            tool_calls.append(ToolCall(name="generate_result", args={"goal": context.get("goal", "")}))

        decision = "approve" if context.get("stage") == "deliberation" else "continue"
        if context.get("stage") == "review":
            decision = "pass"

        return AgentAction(content=llm_text, tool_calls=tool_calls, decision=decision)


def _render_context(context: dict[str, Any]) -> str:
    lines = [f"{k}: {v}" for k, v in context.items()]
    return "\n".join(lines)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.role_type] = agent

    def get(self, role_type: str) -> BaseAgent:
        if role_type not in self._agents:
            raise KeyError(f"Agent not found: {role_type}")
        return self._agents[role_type]

    def has(self, role_type: str) -> bool:
        return role_type in self._agents
