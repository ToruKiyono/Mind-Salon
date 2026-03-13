from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mind_salon import MindSalonApp
from mind_salon.llm import SiliconFlowLLM


def _load_model_from_settings() -> str:
    settings_path = ROOT / "settings.json"
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return ""
    env = data.get("env", {})
    if not isinstance(env, dict):
        return ""
    model = env.get("ANTHROPIC_MODEL", "")
    return model.strip() if isinstance(model, str) else ""


if __name__ == "__main__":
    api_key = os.getenv("SILICONFLOW_API", "").strip()
    if not api_key:
        raise SystemExit("Please set SILICONFLOW_API before running this example.")

    model = os.getenv("SILICONFLOW_MODEL", "").strip() or _load_model_from_settings() or "qwen-plus"
    llm = SiliconFlowLLM(api_key=api_key, model=model)

    app = MindSalonApp(llm_client=llm)
    task_id = app.submit_request("请介绍 Mind Salon 的多角色协作流程")
    summary = app.run_until_idle()[0]

    print(f"task={task_id} status={summary.final_status}")
    for step in summary.stage_results:
        print(f"- {step.stage} ({step.role}): {step.payload.get('content', '')[:120]}")
