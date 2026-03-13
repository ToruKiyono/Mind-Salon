from dataclasses import dataclass


@dataclass(slots=True)
class SalonConfig:
    max_deliberation_rounds: int = 3
    default_pattern_id: str = "pattern.plan_review_execute"
    max_retry: int = 1
    memory_retrieval_top_k: int = 5
    enable_tool_calling: bool = True
