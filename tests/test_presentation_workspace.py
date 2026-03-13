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


class TestPresentationWorkspace(unittest.TestCase):
    def test_workspace_state_and_artifact_thread(self) -> None:
        app = MindSalonApp()
        task_id = app.submit_request("Build semantic workspace state")
        summary = app.run_until_idle()[0]

        cache: dict[str, ExecutionSummary] = {task_id: summary}
        service = SalonWorkspaceService(
            app,
            cache.get,
            is_paused=lambda: False,
            run_pending=lambda: {"executed": 0},
            set_paused=lambda paused: {"paused": paused},
        )

        state = service.get_session_workspace_state(task_id)
        self.assertIsNotNone(state)
        assert state is not None
        self.assertEqual(state["task_id"], task_id)
        self.assertIn("review_gate", state)
        self.assertIn("events", state)
        self.assertTrue(state["artifacts"])

        thread = service.get_artifact_thread(task_id)
        self.assertIsNotNone(thread)
        assert thread is not None
        self.assertEqual(thread["task_id"], task_id)
        self.assertIn("lineage", thread)


if __name__ == "__main__":
    unittest.main()
