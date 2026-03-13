from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
import unittest

from mind_salon import MindSalonApp


class TestMvpV02(unittest.TestCase):
    def test_single_task_runs_to_done(self) -> None:
        app = MindSalonApp()
        task_id = app.submit_request("Build a tiny collaboration loop")

        results = app.run_until_idle()
        self.assertEqual(len(results), 1)
        summary = results[0]
        self.assertEqual(summary.task_id, task_id)
        self.assertEqual(summary.final_status, "done")

        stored_task = app.store.tasks[task_id]
        self.assertEqual(stored_task.status.value, "done")
        self.assertTrue(app.store.messages_by_task[task_id])

        # v0.2 features
        self.assertTrue(summary.artifact_tree)
        self.assertTrue(app.store.memory["long_term"])
        self.assertTrue(any(m.type.value == "tool_call" for m in app.store.messages_by_task[task_id]))


if __name__ == "__main__":
    unittest.main()

