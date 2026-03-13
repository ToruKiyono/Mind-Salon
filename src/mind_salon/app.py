from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from mind_salon.agents import AgentRegistry, LLMAgent
from mind_salon.config import SalonConfig
from mind_salon.gateway import GatewayLayer
from mind_salon.kernel import SalonKernel
from mind_salon.llm import LLMClient, LLMResponse, MockLLM, TaggedMockLLM
from mind_salon.llm.siliconflow import SiliconFlowLLM
from mind_salon.models import Message, MessageType, Task, TaskStatus
from mind_salon.runtime import ExecutionSummary, RuntimeExecutionLoop
from mind_salon.schedulers import CollaborationScheduler, TaskScheduler
from mind_salon.store import InMemoryStore


class _FallbackLLM:
    """Use primary LLM first and degrade to fallback LLM on runtime failure."""

    def __init__(self, primary: LLMClient, fallback: LLMClient, route_model: str) -> None:
        self._primary = primary
        self._fallback = fallback
        self.route_model = route_model
        self.last_backend = "unknown"
        self.last_error = ""

    def generate(self, *, system_prompt: str, user_prompt: str) -> LLMResponse:
        try:
            resp = self._primary.generate(system_prompt=system_prompt, user_prompt=user_prompt)
            backend = getattr(self._primary, "last_backend", "")
            self.last_backend = backend if isinstance(backend, str) and backend.strip() else self._primary.__class__.__name__.lower()
            self.last_error = ""
            return resp
        except Exception as exc:
            backend = getattr(self._fallback, "last_backend", "")
            self.last_backend = backend if isinstance(backend, str) and backend.strip() else self._fallback.__class__.__name__.lower()
            self.last_error = str(exc)
            return self._fallback.generate(system_prompt=system_prompt, user_prompt=user_prompt)


class _UnavailableLLM:
    """Placeholder LLM that always fails so fallback chain can continue."""

    def __init__(self, route_model: str, reason: str) -> None:
        self.route_model = route_model
        self.last_backend = "unavailable"
        self.last_error = reason
        self._reason = reason

    def generate(self, *, system_prompt: str, user_prompt: str) -> LLMResponse:
        raise RuntimeError(self._reason)


class MindSalonApp:
    """Mind Salon v0.2 single-node runtime with pluggable agents and tools."""

    def __init__(self, config: SalonConfig | None = None, llm_client: LLMClient | None = None) -> None:
        self.config = config or SalonConfig()
        self.store = InMemoryStore()
        self.gateway = GatewayLayer()
        self.task_scheduler = TaskScheduler()
        self.collab_scheduler = CollaborationScheduler(self.config)
        self.kernel = SalonKernel.create(self.store, self.config)
        self.llm_client = llm_client or self._build_default_llm()
        self._agent_specs, self._role_policies = self._load_agent_routing_settings()
        self._llm_cache: dict[str, LLMClient] = {}
        self._rr_counters: dict[str, int] = {}
        self.agents = self._build_default_agents()
        self.loop = RuntimeExecutionLoop(
            self.kernel,
            self.store,
            self.config,
            self.agents,
            self.llm_client,
            llm_selector=self._select_llm_for_role,
        )

    def _build_default_agents(self) -> AgentRegistry:
        registry = AgentRegistry()
        for role_type in ["planner", "architect", "reviewer", "critic", "creator", "verifier", "coordinator"]:
            registry.register(LLMAgent(role_type=role_type, system_prompt=f"You are {role_type} in Mind Salon."))
        return registry

    def register_tool(self, name: str, handler) -> None:
        self.kernel.tool.register(name, handler)

    def register_agent(self, agent) -> None:
        self.agents.register(agent)

    def submit_request(self, user_input: str, constraints: dict[str, Any] | None = None) -> str:
        trace_id = f"trace_{uuid4().hex[:10]}"
        task, intent = self.gateway.parse_request(user_input, trace_id, constraints=constraints)
        self.store.add_task(task)
        self.store.add_message(intent)
        self.task_scheduler.submit(task)
        return task.task_id

    def continue_task(self, task_id: str, user_input: str) -> bool:
        task = self.store.tasks.get(task_id)
        if task is None:
            return False

        text = user_input.strip()
        if not text:
            return False

        trace_id = f"trace_{uuid4().hex[:10]}"
        latest_session_id = "session_pending"
        sessions = [s for s in self.store.sessions.values() if s.task_id == task_id]
        if sessions:
            latest_session_id = sorted(sessions, key=lambda x: x.started_at)[-1].session_id

        followup = Message(
            task_id=task_id,
            session_id=latest_session_id,
            from_role="user",
            to_role="coordinator",
            type=MessageType.SYSTEM,
            payload={"intent": text, "followup": True},
            trace_id=trace_id,
        )
        self.store.add_message(followup)

        # Keep same task/session thread and make follow-up intent explicit for next round.
        task.goal = f"{task.goal}\n\n[follow-up]\n{text}"
        task.status = TaskStatus.INTENT
        task.touch()
        self.task_scheduler.submit(task)
        return True

    def run_next(self) -> ExecutionSummary | None:
        task = self.task_scheduler.next_task()
        if not task:
            return None
        pattern_id = self.collab_scheduler.pick_pattern(task)
        return self.loop.run_task(task, pattern_id)

    def run_until_idle(self) -> list[ExecutionSummary]:
        results: list[ExecutionSummary] = []
        while self.task_scheduler.has_pending():
            result = self.run_next()
            if result:
                results.append(result)
        return results

    def _select_llm_for_role(self, role: str, task: Task) -> LLMClient | None:
        # Highest priority: per-request direct model mapping.
        role_llm_map = task.constraints.get("role_llm_map")
        if isinstance(role_llm_map, dict):
            model_id = role_llm_map.get(role)
            if isinstance(model_id, str):
                model_id = model_id.strip()
                if model_id:
                    if model_id in self._llm_cache:
                        return self._llm_cache[model_id]
                    llm = self._build_llm_from_model_id(model_id)
                    self._llm_cache[model_id] = llm
                    return llm

        # Medium priority: per-request agent policy override.
        role_agent_map = task.constraints.get("role_agent_map")
        if isinstance(role_agent_map, dict):
            raw_policy = role_agent_map.get(role)
            policy = self._normalize_role_policy(raw_policy)
            llm = self._build_llm_from_role_policy(role, policy)
            if llm is not None:
                return llm

        # Default: settings-based role bindings.
        llm = self._build_llm_from_role_policy(role, self._role_policies.get(role))
        if llm is not None:
            return llm
        return self.llm_client

    def _build_llm_from_role_policy(self, role: str, policy: dict[str, Any] | None) -> LLMClient | None:
        if not isinstance(policy, dict):
            return None
        agents = [x for x in policy.get("agents", []) if isinstance(x, str) and x.strip()]
        if not agents:
            return None
        strategy = str(policy.get("strategy", "fallback")).strip().lower()

        if strategy == "first":
            selected = [agents[0]]
        elif strategy == "round_robin":
            idx = self._rr_counters.get(role, 0)
            selected = [agents[idx % len(agents)]]
            self._rr_counters[role] = idx + 1
        else:
            selected = agents

        return self._build_llm_from_agent_chain(selected, strategy=strategy, role=role)

    def _build_llm_from_model_id(self, model_id: str) -> LLMClient:
        # Explicit mock route for local role-based routing tests.
        if model_id.startswith("mock/"):
            llm = TaggedMockLLM(tag=model_id)
            setattr(llm, "route_model", model_id)
            setattr(llm, "last_backend", "mock")
            setattr(llm, "last_error", "")
            return llm

        api_key = os.getenv("SILICONFLOW_API", "sk-54a1f695c7ec40c8811b3fbda49696d4").strip()
        if api_key:
            strict = os.getenv("MINDSALON_STRICT_LLM", "").strip() in {"1", "true", "TRUE"}
            base_url = os.getenv("SILICONFLOW_BASE_URL", "https://dashscope.aliyuncs.com/apps/anthropic").strip() or "https://dashscope.aliyuncs.com/apps/anthropic"
            api_style = os.getenv("SILICONFLOW_API_STYLE", "auto").strip() or "auto"
            if strict:
                llm = SiliconFlowLLM(api_key=api_key, model=model_id, base_url=base_url, api_style=api_style)
                setattr(llm, "route_model", model_id)
                setattr(llm, "last_backend", "siliconflow")
                setattr(llm, "last_error", "")
                return llm
            return _FallbackLLM(
                SiliconFlowLLM(api_key=api_key, model=model_id, base_url=base_url, api_style=api_style),
                TaggedMockLLM(tag=model_id),
                route_model=model_id,
            )

        # Keep execution alive without external credentials while preserving model route visibility.
        llm = TaggedMockLLM(tag=model_id)
        setattr(llm, "route_model", model_id)
        setattr(llm, "last_backend", "mock")
        setattr(llm, "last_error", "SILICONFLOW_API not set")
        return llm

    def _build_llm_from_agent_chain(self, agent_ids: list[str], strategy: str, role: str) -> LLMClient | None:
        normalized = [agent_id for agent_id in agent_ids if isinstance(agent_id, str) and agent_id.strip()]
        if not normalized:
            return None

        cache_key = f"agent_chain:{role}:{strategy}:{'|'.join(normalized)}"
        if cache_key in self._llm_cache:
            return self._llm_cache[cache_key]

        route_model = " -> ".join(normalized)
        chain: LLMClient | None = None
        for agent_id in normalized:
            spec = self._agent_specs.get(agent_id)
            if not isinstance(spec, dict):
                continue
            next_llm = self._build_llm_from_agent_spec(agent_id, spec)
            if chain is None:
                chain = next_llm
            else:
                chain = _FallbackLLM(chain, next_llm, route_model=route_model)
        if chain is None:
            return None

        fallback_mock = TaggedMockLLM(tag=f"mock/{route_model}")
        setattr(fallback_mock, "route_model", route_model)
        setattr(fallback_mock, "last_backend", "mock")
        setattr(fallback_mock, "last_error", "")
        chain = _FallbackLLM(chain, fallback_mock, route_model=route_model)
        self._llm_cache[cache_key] = chain
        return chain

    def _build_llm_from_agent_spec(self, agent_id: str, spec: dict[str, Any]) -> LLMClient:
        provider = str(spec.get("provider", "siliconflow")).strip().lower()
        model = str(spec.get("model", "")).strip()
        route_model = model or f"agent/{agent_id}"

        if provider == "mock":
            tag = model or f"mock/{agent_id}"
            llm = TaggedMockLLM(tag=tag)
            setattr(llm, "route_model", route_model)
            setattr(llm, "last_backend", "mock")
            setattr(llm, "last_error", "")
            return llm

        if provider != "siliconflow":
            return _UnavailableLLM(route_model=route_model, reason=f"Unsupported provider '{provider}' for agent '{agent_id}'.")

        if not model:
            return _UnavailableLLM(route_model=route_model, reason=f"Missing model for agent '{agent_id}'.")

        api_key_env = str(spec.get("api_key_env", "SILICONFLOW_API")).strip() or "SILICONFLOW_API"
        api_key = str(spec.get("api_key", "")).strip() or os.getenv(api_key_env, "").strip()
        if not api_key:
            return _UnavailableLLM(route_model=route_model, reason=f"Missing API key for agent '{agent_id}' via env '{api_key_env}'.")

        base_url = str(spec.get("base_url", "https://dashscope.aliyuncs.com/apps/anthropic")).strip() or "https://dashscope.aliyuncs.com/apps/anthropic"
        api_style = str(spec.get("api_style", "auto")).strip() or "auto"
        timeout = spec.get("timeout_seconds", 60)
        timeout_seconds = timeout if isinstance(timeout, int) and timeout > 0 else 60
        llm = SiliconFlowLLM(api_key=api_key, model=model, base_url=base_url, api_style=api_style, timeout_seconds=timeout_seconds)
        setattr(llm, "route_model", route_model)
        setattr(llm, "last_backend", "siliconflow")
        setattr(llm, "last_error", "")
        return llm

    def _load_agent_routing_settings(self) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        settings_path_env = os.getenv("MINDSALON_SETTINGS_PATH", "").strip()
        settings_path = Path(settings_path_env) if settings_path_env else Path(__file__).resolve().parents[2] / "settings.json"
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return {}, {}
        if not isinstance(data, dict):
            return {}, {}

        raw_agents = data.get("agents")
        raw_bindings = data.get("role_bindings")
        raw_agent_bindings = data.get("agent_bindings")
        if not isinstance(raw_agents, dict):
            return {}, {}

        agents: dict[str, dict[str, Any]] = {}
        policies: dict[str, dict[str, Any]] = {}

        for agent_id, raw in raw_agents.items():
            if not isinstance(agent_id, str):
                continue
            agent_key = agent_id.strip()
            if not agent_key:
                continue
            if isinstance(raw, str):
                model = raw.strip()
                if model:
                    agents[agent_key] = {"provider": "siliconflow", "model": model}
                continue
            if not isinstance(raw, dict):
                continue
            spec: dict[str, Any] = {
                "provider": raw.get("provider", "siliconflow"),
                "model": raw.get("model", ""),
                "api_key_env": raw.get("api_key_env", "SILICONFLOW_API"),
                "base_url": raw.get("base_url", ""),
                "api_style": raw.get("api_style", "auto"),
                "timeout_seconds": raw.get("timeout_seconds", 60),
            }
            if "api_key" in raw:
                spec["api_key"] = raw.get("api_key")
            roles = self._normalize_role_list(raw.get("roles"))
            if roles:
                spec["roles"] = roles
            agents[agent_key] = spec

        if isinstance(raw_bindings, dict):
            for role, raw in raw_bindings.items():
                if not isinstance(role, str):
                    continue
                role_key = role.strip()
                if not role_key:
                    continue
                policy = self._normalize_role_policy(raw)
                if policy is not None:
                    policies[role_key] = policy

        if isinstance(raw_agent_bindings, dict):
            for agent_id, roles_raw in raw_agent_bindings.items():
                if not isinstance(agent_id, str):
                    continue
                agent_key = agent_id.strip()
                if not agent_key:
                    continue
                roles = self._normalize_role_list(roles_raw)
                for role in roles:
                    self._append_policy_agent(policies, role, agent_key)

        for agent_id, spec in agents.items():
            roles = spec.get("roles", [])
            if isinstance(roles, list):
                for role in roles:
                    if isinstance(role, str) and role.strip():
                        self._append_policy_agent(policies, role.strip(), agent_id)

        return agents, policies

    def _append_policy_agent(self, policies: dict[str, dict[str, Any]], role: str, agent_id: str) -> None:
        existing = policies.get(role)
        if not isinstance(existing, dict):
            policies[role] = {"agents": [agent_id], "strategy": "fallback"}
            return
        agents = existing.get("agents", [])
        if not isinstance(agents, list):
            agents = []
        if agent_id not in agents:
            agents.append(agent_id)
        existing["agents"] = agents
        strategy = existing.get("strategy", "fallback")
        existing["strategy"] = strategy if isinstance(strategy, str) and strategy.strip() else "fallback"
        policies[role] = existing

    def _normalize_role_list(self, raw: Any) -> list[str]:
        if isinstance(raw, str):
            candidate = raw.strip()
            return [candidate] if candidate else []
        if not isinstance(raw, list):
            return []
        values: list[str] = []
        for item in raw:
            if not isinstance(item, str):
                continue
            candidate = item.strip()
            if candidate:
                values.append(candidate)
        return values

    def _normalize_role_policy(self, raw: Any) -> dict[str, Any] | None:
        if isinstance(raw, str):
            candidate = raw.strip()
            if not candidate:
                return None
            return {"agents": [candidate], "strategy": "fallback"}
        if isinstance(raw, list):
            agents = self._normalize_role_list(raw)
            if not agents:
                return None
            return {"agents": agents, "strategy": "fallback"}
        if not isinstance(raw, dict):
            return None

        agents = self._normalize_role_list(raw.get("agents"))
        if not agents:
            agents = self._normalize_role_list(raw.get("chain"))
        if not agents:
            return None

        strategy = str(raw.get("strategy", "fallback")).strip().lower() or "fallback"
        if strategy not in {"fallback", "first", "round_robin"}:
            strategy = "fallback"
        return {"agents": agents, "strategy": strategy}

    def _build_default_llm(self) -> LLMClient:
        api_key = os.getenv("SILICONFLOW_API", "").strip()
        if api_key:
            model = os.getenv("SILICONFLOW_MODEL", "qwen-plus").strip() or "qwen-plus"
            base_url = os.getenv("SILICONFLOW_BASE_URL", "https://dashscope.aliyuncs.com/apps/anthropic").strip() or "https://dashscope.aliyuncs.com/apps/anthropic"
            api_style = os.getenv("SILICONFLOW_API_STYLE", "auto").strip() or "auto"
            strict = os.getenv("MINDSALON_STRICT_LLM", "").strip() in {"1", "true", "TRUE"}
            if strict:
                llm = SiliconFlowLLM(api_key=api_key, model=model, base_url=base_url, api_style=api_style)
                setattr(llm, "route_model", model)
                setattr(llm, "last_backend", "siliconflow")
                setattr(llm, "last_error", "")
                return llm
            return _FallbackLLM(
                SiliconFlowLLM(api_key=api_key, model=model, base_url=base_url, api_style=api_style),
                MockLLM(),
                route_model=model,
            )
        return MockLLM()
