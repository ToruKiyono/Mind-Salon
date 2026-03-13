from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mind_salon import MindSalonApp


class TestRoleLlmRouting(unittest.TestCase):
    def test_role_llm_map_routes_per_role(self) -> None:
        app = MindSalonApp()
        task_id = app.submit_request(
            "Validate per-role model routing",
            constraints={
                "role_llm_map": {
                    "planner": "mock/planner-a",
                    "architect": "mock/architect-b",
                    "reviewer": "mock/reviewer-c",
                }
            },
        )
        summary = app.run_until_idle()[0]
        self.assertEqual(summary.task_id, task_id)
        self.assertEqual(summary.final_status, "done")

        by_role = {x.role: x.payload.get("content", "") for x in summary.stage_results}
        self.assertIn("[mock-llm:mock/planner-a]", str(by_role.get("planner", "")))
        self.assertIn("[mock-llm:mock/architect-b]", str(by_role.get("architect", "")))
        self.assertIn("[mock-llm:mock/reviewer-c]", str(by_role.get("reviewer", "")))


if __name__ == "__main__":
    unittest.main()
