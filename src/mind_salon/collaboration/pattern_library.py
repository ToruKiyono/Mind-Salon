from __future__ import annotations

from mind_salon.collaboration.pattern_spec import PatternSpec, PatternStep
from mind_salon.models import TaskStatus


PATTERN_LIBRARY: dict[str, PatternSpec] = {
    "pattern.plan_review_execute": PatternSpec(
        pattern_id="pattern.plan_review_execute",
        goal="Fast and controlled delivery for single-node MVP.",
        roles=["planner", "architect", "reviewer", "creator", "verifier", "coordinator"],
        steps=[
            PatternStep(stage=TaskStatus.INTENT, role="planner"),
            PatternStep(stage=TaskStatus.PROPOSAL, role="architect"),
            PatternStep(stage=TaskStatus.DELIBERATION, role="reviewer"),
            PatternStep(stage=TaskStatus.EXECUTION, role="creator", allow_tool_calls=True),
            PatternStep(stage=TaskStatus.REVIEW, role="verifier"),
            PatternStep(stage=TaskStatus.FEEDBACK, role="coordinator"),
        ],
    ),
    "pattern.debate_then_execute": PatternSpec(
        pattern_id="pattern.debate_then_execute",
        goal="Higher scrutiny before execution.",
        roles=["planner", "architect", "critic", "reviewer", "creator", "verifier", "coordinator"],
        steps=[
            PatternStep(stage=TaskStatus.INTENT, role="planner"),
            PatternStep(stage=TaskStatus.PROPOSAL, role="architect"),
            PatternStep(stage=TaskStatus.DELIBERATION, role="critic"),
            PatternStep(stage=TaskStatus.DELIBERATION, role="reviewer"),
            PatternStep(stage=TaskStatus.EXECUTION, role="creator", allow_tool_calls=True),
            PatternStep(stage=TaskStatus.REVIEW, role="verifier"),
            PatternStep(stage=TaskStatus.FEEDBACK, role="coordinator"),
        ],
    ),
}
