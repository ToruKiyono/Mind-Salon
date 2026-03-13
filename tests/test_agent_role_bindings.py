from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mind_salon import MindSalonApp


class TestAgentRoleBindings(unittest.TestCase):
    def test_one_agent_can_drive_multiple_roles(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            settings_path.write_text(
                json.dumps(
                    {
                        "agents": {"shared_mock": {"provider": "mock", "model": "mock/shared"}},
                        "role_bindings": {
                            "planner": ["shared_mock"],
                            "architect": ["shared_mock"],
                            "reviewer": ["shared_mock"],
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            old = os.getenv("MINDSALON_SETTINGS_PATH")
            os.environ["MINDSALON_SETTINGS_PATH"] = str(settings_path)
            try:
                app = MindSalonApp()
                task_id = app.submit_request("Verify shared agent across roles")
                summary = app.run_until_idle()[0]
            finally:
                if old is None:
                    os.environ.pop("MINDSALON_SETTINGS_PATH", None)
                else:
                    os.environ["MINDSALON_SETTINGS_PATH"] = old

        self.assertEqual(summary.task_id, task_id)
        self.assertEqual(summary.final_status, "done")
        by_role = {x.role: str(x.payload.get("content", "")) for x in summary.stage_results}
        self.assertIn("[mock-llm:mock/shared]", by_role.get("planner", ""))
        self.assertIn("[mock-llm:mock/shared]", by_role.get("architect", ""))
        self.assertIn("[mock-llm:mock/shared]", by_role.get("reviewer", ""))

    def test_one_role_can_define_agent_fallback_chain(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            settings_path.write_text(
                json.dumps(
                    {
                        "agents": {
                            "planner_mock": {"provider": "mock", "model": "mock/planner"},
                            "reviewer_bad": {"provider": "unsupported", "model": "bad/model"},
                            "reviewer_mock": {"provider": "mock", "model": "mock/reviewer-fallback"},
                        },
                        "role_bindings": {
                            "planner": ["planner_mock"],
                            "reviewer": ["reviewer_bad", "reviewer_mock"],
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            old = os.getenv("MINDSALON_SETTINGS_PATH")
            os.environ["MINDSALON_SETTINGS_PATH"] = str(settings_path)
            try:
                app = MindSalonApp()
                app.submit_request("Verify reviewer fallback chain")
                summary = app.run_until_idle()[0]
            finally:
                if old is None:
                    os.environ.pop("MINDSALON_SETTINGS_PATH", None)
                else:
                    os.environ["MINDSALON_SETTINGS_PATH"] = old

        reviewer = next((x for x in summary.stage_results if x.role == "reviewer"), None)
        self.assertIsNotNone(reviewer)
        self.assertIn("[mock-llm:mock/reviewer-fallback]", str(reviewer.payload.get("content", "")))

    def test_round_robin_strategy_rotates_agent_per_call(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            settings_path.write_text(
                json.dumps(
                    {
                        "agents": {
                            "planner_a": {"provider": "mock", "model": "mock/planner-a"},
                            "planner_b": {"provider": "mock", "model": "mock/planner-b"},
                        },
                        "role_bindings": {
                            "planner": {"agents": ["planner_a", "planner_b"], "strategy": "round_robin"},
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            old = os.getenv("MINDSALON_SETTINGS_PATH")
            os.environ["MINDSALON_SETTINGS_PATH"] = str(settings_path)
            try:
                app = MindSalonApp()
                app.submit_request("round robin 1")
                summary1 = app.run_until_idle()[0]
                app.submit_request("round robin 2")
                summary2 = app.run_until_idle()[0]
            finally:
                if old is None:
                    os.environ.pop("MINDSALON_SETTINGS_PATH", None)
                else:
                    os.environ["MINDSALON_SETTINGS_PATH"] = old

        planner1 = next((x for x in summary1.stage_results if x.role == "planner"), None)
        planner2 = next((x for x in summary2.stage_results if x.role == "planner"), None)
        self.assertIsNotNone(planner1)
        self.assertIsNotNone(planner2)
        self.assertIn("[mock-llm:mock/planner-a]", str(planner1.payload.get("content", "")))
        self.assertIn("[mock-llm:mock/planner-b]", str(planner2.payload.get("content", "")))

    def test_agent_declared_roles_can_bind_automatically(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            settings_path.write_text(
                json.dumps(
                    {
                        "agents": {
                            "shared_declared": {
                                "provider": "mock",
                                "model": "mock/shared-declared",
                                "roles": ["planner", "architect"],
                            }
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            old = os.getenv("MINDSALON_SETTINGS_PATH")
            os.environ["MINDSALON_SETTINGS_PATH"] = str(settings_path)
            try:
                app = MindSalonApp()
                app.submit_request("roles declared in agent")
                summary = app.run_until_idle()[0]
            finally:
                if old is None:
                    os.environ.pop("MINDSALON_SETTINGS_PATH", None)
                else:
                    os.environ["MINDSALON_SETTINGS_PATH"] = old

        by_role = {x.role: str(x.payload.get("content", "")) for x in summary.stage_results}
        self.assertIn("[mock-llm:mock/shared-declared]", by_role.get("planner", ""))
        self.assertIn("[mock-llm:mock/shared-declared]", by_role.get("architect", ""))


if __name__ == "__main__":
    unittest.main()
