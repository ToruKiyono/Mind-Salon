from __future__ import annotations

from mind_salon.models import Role, RoleLifecycleState, RoleProfile, RoleReflection, TaskStatus


DEFAULT_ROLE_BY_STAGE: dict[TaskStatus, str] = {
    TaskStatus.INTENT: "planner",
    TaskStatus.PROPOSAL: "architect",
    TaskStatus.DELIBERATION: "reviewer",
    TaskStatus.EXECUTION: "creator",
    TaskStatus.REVIEW: "verifier",
    TaskStatus.FEEDBACK: "coordinator",
}

_ROLE_RESPONSIBILITIES: dict[str, list[str]] = {
    "planner": ["task scoping", "plan framing"],
    "architect": ["solution design", "structure proposal"],
    "reviewer": ["critique", "challenge assumptions"],
    "critic": ["challenge", "failure analysis"],
    "creator": ["execution", "artifact generation"],
    "verifier": ["review decision", "quality gate"],
    "coordinator": ["session coordination", "handoff and closure"],
}

_ROLE_BOUNDED_RULES: dict[str, list[str]] = {
    "planner": ["must not approve review gate", "must stay in planning scope"],
    "architect": ["must not override verifier decision", "must keep design rationale explicit"],
    "reviewer": ["must challenge proposal without changing protocol authority"],
    "critic": ["must stress-test logic, not redefine task ownership"],
    "creator": ["must execute agreed plan, not bypass review gate"],
    "verifier": ["owns decision gate within protocol", "must not absorb execution role"],
    "coordinator": ["must enforce protocol sequencing", "must not collapse specialized roles"],
}

_ROLE_STRATEGY_AXES: dict[str, list[str]] = {
    "planner": ["clarity", "constraint coverage"],
    "architect": ["modularity", "tradeoff explicitness"],
    "reviewer": ["counter-example depth", "risk surfacing"],
    "critic": ["adversarial rigor", "edge-case coverage"],
    "creator": ["execution completeness", "artifact precision"],
    "verifier": ["gate strictness", "evidence quality"],
    "coordinator": ["handoff quality", "protocol timing"],
}


class RoleEngine:
    def __init__(self) -> None:
        self._roles: dict[str, Role] = {}

    def get_or_create(self, role_type: str) -> Role:
        if role_type not in self._roles:
            role = Role(
                role_type=role_type,
                capabilities=[f"{role_type}.default"],
                authority_scope=["task.read", "task.write"],
                context_scope=["task", "session", "memory", "artifact"],
                profile=RoleProfile(
                    role_type=role_type,
                    responsibilities=_ROLE_RESPONSIBILITIES.get(role_type, [f"{role_type}.generic"]),
                    bounded_rules=_ROLE_BOUNDED_RULES.get(role_type, ["must follow protocol authority"]),
                    allowed_strategy_axes=_ROLE_STRATEGY_AXES.get(role_type, ["output quality"]),
                ),
            )
            role.lifecycle_state = RoleLifecycleState.ACTIVE
            self._roles[role_type] = role
        return self._roles[role_type]

    def get_or_create_for_stage(self, stage: TaskStatus) -> Role:
        return self.get_or_create(DEFAULT_ROLE_BY_STAGE[stage])

    def reflect_and_adapt(self, role_type: str, *, stage: str, decision: str, llm_error: str, content: str) -> RoleReflection:
        role = self.get_or_create(role_type)
        adap = role.adaptation

        issue_key = self._issue_key(stage=stage, decision=decision, llm_error=llm_error, content=content)
        issue_count = adap.recurring_issues.get(issue_key, 0) + 1
        adap.recurring_issues[issue_key] = issue_count

        reflection = f"{role_type} reflected on stage={stage}, decision={decision}, issue={issue_key}."
        adap.reflection_count += 1
        adap.last_reflection = reflection

        corrected = issue_count >= 2 or bool(llm_error.strip())
        correction = ""
        if corrected:
            correction = f"{role_type} corrected recurring issue '{issue_key}' under protocol bounds."
            adap.correction_count += 1
            adap.last_correction = correction

        strategy_updated = issue_count >= 3
        strategy_update = ""
        if strategy_updated:
            axis = (role.profile.allowed_strategy_axes[0] if role.profile and role.profile.allowed_strategy_axes else "quality")
            strategy_update = f"{role_type} updated strategy on axis={axis} with bounded responsibility."
            if len(adap.strategy_notes) >= 8:
                adap.strategy_notes = adap.strategy_notes[-7:]
            adap.strategy_notes.append(strategy_update)
            adap.strategy_update_count += 1
            adap.last_strategy_update = strategy_update

        return RoleReflection(
            reflection=reflection,
            corrected=corrected,
            correction=correction,
            strategy_updated=strategy_updated,
            strategy_update=strategy_update,
            recurring_issue_key=issue_key,
        )

    def _issue_key(self, *, stage: str, decision: str, llm_error: str, content: str) -> str:
        if llm_error.strip():
            return "llm_error"
        lowered = content.lower()
        if "unknown" in lowered or "unsure" in lowered:
            return "uncertainty"
        if decision.lower() in {"reject", "revise"}:
            return "quality_gate_fail"
        if stage == "deliberation":
            return "deliberation_gap"
        return "general"
