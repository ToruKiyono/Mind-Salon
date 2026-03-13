from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mind_salon import MindSalonApp


class TestFollowupSession(unittest.TestCase):
    def test_continue_task_reuses_same_task(self) -> None:
        app = MindSalonApp()
        task_id = app.submit_request("Draft a launch plan")
        first = app.run_until_idle()[0]
        self.assertEqual(first.task_id, task_id)
        self.assertEqual(first.final_status, "done")

        ok = app.continue_task(task_id, "Now break this into week-by-week actions.")
        self.assertTrue(ok)
        second = app.run_until_idle()[0]
        self.assertEqual(second.task_id, task_id)
        self.assertEqual(second.final_status, "done")
        self.assertGreater(len(app.store.messages_by_task[task_id]), 1)
        self.assertIn("[follow-up]", app.store.tasks[task_id].goal)


if __name__ == "__main__":
    unittest.main()
