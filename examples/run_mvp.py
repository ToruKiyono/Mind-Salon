from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mind_salon import MindSalonApp


if __name__ == "__main__":
    app = MindSalonApp()
    task_id = app.submit_request("Design a minimal API gateway and execution loop")
    print(f"submitted: {task_id}")

    summaries = app.run_until_idle()
    for summary in summaries:
        print(f"task={summary.task_id} status={summary.final_status} trace={summary.trace_id}")
        for stage in summary.stage_results:
            print(f"  - {stage.stage} ({stage.role}): {stage.decision}")
        print(f"artifact_tree={summary.artifact_tree}")
