from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mind_salon import MindSalonApp
from mind_salon.presentation import SalonWorkspaceService
from mind_salon.runtime import ExecutionSummary


class TestRoleAdaptation(unittest.TestCase):
    def test_role_reflection_payload_and_events(self) -> None:
        app = MindSalonApp()
        task_id = app.submit_request("Validate role self-correction pipeline")
        summary = app.run_until_idle()[0]

        role_stage = summary.stage_results[0]
        self.assertIn("role_reflection", role_stage.payload)
        self.assertIn("role_corrected", role_stage.payload)
        self.assertIn("role_strategy_updated", role_stage.payload)

        cache: dict[str, ExecutionSummary] = {task_id: summary}
        service = SalonWorkspaceService(
            app,
            cache.get,
            is_paused=lambda: False,
            run_pending=lambda: {"executed": 0},
            set_paused=lambda paused: {"paused": paused},
        )
        events = service.stream_session_events(task_id)
        self.assertIsNotNone(events)
        assert events is not None
        event_types = {e.type for e in events}
        self.assertIn("role_reflected", event_types)


if __name__ == "__main__":
    unittest.main()
