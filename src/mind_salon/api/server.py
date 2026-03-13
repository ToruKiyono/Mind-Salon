from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from mind_salon import MindSalonApp
from mind_salon.presentation import SalonWorkspaceService
from mind_salon.runtime import ExecutionSummary


class _RuntimeState:
    def __init__(self) -> None:
        self.app = MindSalonApp()
        self.paused = False
        self._summaries: dict[str, ExecutionSummary] = {}
        self._updated_at = datetime.now(timezone.utc)
        self.workspace = SalonWorkspaceService(
            self.app,
            self._summaries.get,
            is_paused=lambda: self.paused,
            run_pending=self.run_pending,
            set_paused=self.set_paused,
        )

    def submit_task(
        self,
        goal: str,
        auto_run: bool,
        role_llm_map: dict[str, str] | None = None,
        role_agent_map: dict[str, list[str] | str] | None = None,
    ) -> dict[str, Any]:
        constraints: dict[str, Any] = {}
        if role_llm_map:
            constraints["role_llm_map"] = role_llm_map
        if role_agent_map:
            constraints["role_agent_map"] = role_agent_map
        task_id = self.app.submit_request(goal, constraints=constraints)
        if auto_run and not self.paused:
            self.run_pending()
        self._touch()
        return {"task_id": task_id}

    def run_pending(self) -> dict[str, Any]:
        ran = self.app.run_until_idle()
        for summary in ran:
            self._summaries[summary.task_id] = summary
        self._touch()
        return {"executed": len(ran)}

    def continue_task(self, task_id: str, user_input: str, auto_run: bool) -> dict[str, Any] | None:
        ok = self.app.continue_task(task_id, user_input)
        if not ok:
            return None
        if auto_run and not self.paused:
            self.run_pending()
        self._touch()
        return {"task_id": task_id}

    def set_paused(self, paused: bool) -> dict[str, Any]:
        self.paused = paused
        self._touch()
        return {"paused": self.paused}

    def get_state(self) -> dict[str, Any]:
        tasks = sorted(self.app.store.tasks.values(), key=lambda t: t.created_at, reverse=True)
        payload_tasks: list[dict[str, Any]] = []
        for task in tasks:
            summary = self._summaries.get(task.task_id)
            sessions = [s for s in self.app.store.sessions.values() if s.task_id == task.task_id]
            current = sessions[-1] if sessions else None
            payload_tasks.append(
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "goal": task.goal,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "artifact_count": len(self.app.store.artifacts_by_task.get(task.task_id, [])),
                    "message_count": len(self.app.store.messages_by_task.get(task.task_id, [])),
                    "final_status": summary.final_status if summary else None,
                    "trace_id": summary.trace_id if summary else None,
                    "pattern_id": current.active_pattern if current else None,
                    "round_index": current.round_index if current else 0,
                }
            )
        return {
            "runtime": {
                "paused": self.paused,
                "has_pending": self.app.task_scheduler.has_pending(),
                "task_count": len(payload_tasks),
                "memory_count": len(self.app.store.memory.get("long_term", [])),
                "updated_at": self._updated_at.isoformat(),
            },
            "tasks": payload_tasks,
        }

    def get_task_detail(self, task_id: str) -> dict[str, Any] | None:
        task = self.app.store.tasks.get(task_id)
        if task is None:
            return None
        messages = self.app.store.messages_by_task.get(task_id, [])
        artifacts = self.app.store.artifacts_by_task.get(task_id, [])
        sessions = [s for s in self.app.store.sessions.values() if s.task_id == task_id]
        summary = self._summaries.get(task_id)
        memory = [m for m in self.app.store.memory.get("long_term", []) if m.source_task_id == task_id]

        return {
            "task": {
                "task_id": task.task_id,
                "title": task.title,
                "goal": task.goal,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "artifacts": list(task.artifacts),
                "constraints": task.constraints,
            },
            "messages": [
                {
                    "message_id": m.message_id,
                    "from_role": m.from_role,
                    "to_role": m.to_role,
                    "type": m.type.value,
                    "payload": m.payload,
                    "trace_id": m.trace_id,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ],
            "artifacts": [
                {
                    "artifact_id": a.artifact_id,
                    "task_id": a.task_id,
                    "type": a.type,
                    "created_by": a.created_by,
                    "content_ref": a.content_ref,
                    "parent_artifact_id": a.parent_artifact_id,
                    "quality_status": a.quality_status,
                    "version": a.version,
                    "metadata": a.metadata,
                    "created_at": a.created_at.isoformat(),
                }
                for a in artifacts
            ],
            "artifact_tree": self.app.store.get_artifact_tree(task_id),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "task_id": s.task_id,
                    "participants": list(s.participants),
                    "active_pattern": s.active_pattern,
                    "round_index": s.round_index,
                    "state": s.state.value,
                    "started_at": s.started_at.isoformat(),
                    "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                }
                for s in sessions
            ],
            "summary": (
                {
                    "task_id": summary.task_id,
                    "final_status": summary.final_status,
                    "trace_id": summary.trace_id,
                    "stage_results": [
                        {
                            "stage": x.stage,
                            "role": x.role,
                            "decision": x.decision,
                            "payload": x.payload,
                            "trace_id": x.trace_id,
                        }
                        for x in summary.stage_results
                    ],
                    "artifact_tree": summary.artifact_tree,
                }
                if summary
                else None
            ),
            "memory": [
                {
                    "memory_id": m.memory_id,
                    "scope": m.scope,
                    "source_task_id": m.source_task_id,
                    "content": m.content,
                    "tags": m.tags,
                    "confidence": m.confidence,
                    "updated_at": m.updated_at.isoformat(),
                }
                for m in memory
            ],
        }

    def get_session_workspace_state(self, task_id: str) -> dict[str, Any] | None:
        return self.workspace.get_session_workspace_state(task_id)

    def get_session_events(self, task_id: str) -> list[dict[str, Any]] | None:
        events = self.workspace.stream_session_events(task_id)
        if events is None:
            return None
        return [asdict(event) for event in events]

    def get_artifact_thread(self, task_id: str) -> dict[str, Any] | None:
        return self.workspace.get_artifact_thread(task_id)

    def control_session(self, task_id: str, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.workspace.control_session(task_id, action=action, payload=payload)

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)


class MindSalonApiHandler(BaseHTTPRequestHandler):
    runtime = _RuntimeState()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_cors_headers()
        self.end_headers()
        self._log_api(HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/state":
            self._json(HTTPStatus.OK, self.runtime.get_state())
            return
        if self.path.startswith("/api/sessions/") and self.path.endswith("/workspace"):
            task_id = self.path.removeprefix("/api/sessions/").removesuffix("/workspace").strip().rstrip("/")
            detail = self.runtime.get_session_workspace_state(task_id)
            if detail is None:
                self._json(HTTPStatus.NOT_FOUND, {"error": f"Session not found for task: {task_id}"})
                return
            self._json(HTTPStatus.OK, detail)
            return
        if self.path.startswith("/api/sessions/") and self.path.endswith("/events"):
            task_id = self.path.removeprefix("/api/sessions/").removesuffix("/events").strip().rstrip("/")
            events = self.runtime.get_session_events(task_id)
            if events is None:
                self._json(HTTPStatus.NOT_FOUND, {"error": f"Session not found for task: {task_id}"})
                return
            self._json(HTTPStatus.OK, {"events": events})
            return
        if self.path.startswith("/api/sessions/") and self.path.endswith("/artifacts/thread"):
            task_id = self.path.removeprefix("/api/sessions/").removesuffix("/artifacts/thread").strip().rstrip("/")
            thread = self.runtime.get_artifact_thread(task_id)
            if thread is None:
                self._json(HTTPStatus.NOT_FOUND, {"error": f"Session not found for task: {task_id}"})
                return
            self._json(HTTPStatus.OK, thread)
            return
        if self.path.startswith("/api/tasks/"):
            task_id = self.path.removeprefix("/api/tasks/").strip()
            detail = self.runtime.get_task_detail(task_id)
            if detail is None:
                self._json(HTTPStatus.NOT_FOUND, {"error": f"Task not found: {task_id}"})
                return
            self._json(HTTPStatus.OK, detail)
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/sessions/control":
            body = self._read_json_body()
            if body is None:
                return
            action = str(body.get("action", "")).strip()
            payload = body.get("payload")
            if action != "start_salon":
                self._json(HTTPStatus.BAD_REQUEST, {"error": "Only action=start_salon is supported on this endpoint."})
                return
            if not isinstance(payload, dict):
                payload = {}
            goal = str(payload.get("goal", "")).strip()
            if not goal:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "payload.goal is required for start_salon."})
                return
            auto_run = bool(payload.get("auto_run", True))
            role_llm_map = payload.get("role_llm_map") if isinstance(payload.get("role_llm_map"), dict) else None
            role_agent_map = payload.get("role_agent_map") if isinstance(payload.get("role_agent_map"), dict) else None
            self._json(
                HTTPStatus.CREATED,
                self.runtime.submit_task(goal, auto_run, role_llm_map=role_llm_map, role_agent_map=role_agent_map),
            )
            return

        if self.path.startswith("/api/sessions/") and self.path.endswith("/control"):
            task_id = self.path.removeprefix("/api/sessions/").removesuffix("/control").strip().rstrip("/")
            body = self._read_json_body()
            if body is None:
                return
            action = str(body.get("action", "")).strip()
            if not action:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "Field 'action' is required."})
                return
            payload = body.get("payload")
            if payload is not None and not isinstance(payload, dict):
                self._json(HTTPStatus.BAD_REQUEST, {"error": "Field 'payload' must be an object when provided."})
                return
            result = self.runtime.control_session(task_id, action, payload=payload if isinstance(payload, dict) else None)
            if result.get("ok") is False and "Unsupported action" in str(result.get("error", "")):
                self._json(HTTPStatus.BAD_REQUEST, result)
                return
            if result.get("ok") is False and "task_id" in result:
                self._json(HTTPStatus.NOT_FOUND, result)
                return
            self._json(HTTPStatus.OK, result)
            return

        if self.path.startswith("/api/tasks/") and self.path.endswith("/followup"):
            task_id = self.path.removeprefix("/api/tasks/").removesuffix("/followup").strip()
            if not task_id:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "Task id is required."})
                return
            body = self._read_json_body()
            if body is None:
                return
            user_input = str(body.get("input", "")).strip()
            if not user_input:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "Field 'input' is required."})
                return
            auto_run = bool(body.get("auto_run", True))
            result = self.runtime.continue_task(task_id, user_input, auto_run=auto_run)
            if result is None:
                self._json(HTTPStatus.NOT_FOUND, {"error": f"Task not found: {task_id}"})
                return
            self._json(HTTPStatus.OK, result)
            return

        if self.path == "/api/tasks":
            body = self._read_json_body()
            if body is None:
                return
            goal = str(body.get("goal", "")).strip()
            if not goal:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "Field 'goal' is required."})
                return
            auto_run = bool(body.get("auto_run", True))
            role_llm_map = body.get("role_llm_map") if isinstance(body.get("role_llm_map"), dict) else None
            role_agent_map = body.get("role_agent_map") if isinstance(body.get("role_agent_map"), dict) else None
            self._json(
                HTTPStatus.CREATED,
                self.runtime.submit_task(goal, auto_run, role_llm_map=role_llm_map, role_agent_map=role_agent_map),
            )
            return
        if self.path == "/api/runtime/pause":
            body = self._read_json_body()
            if body is None:
                return
            paused = bool(body.get("paused", True))
            self._json(HTTPStatus.OK, self.runtime.set_paused(paused))
            return
        if self.path == "/api/runtime/continue":
            self._json(HTTPStatus.OK, self.runtime.run_pending())
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _set_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(int(status))
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        self._log_api(status)

    def _read_json_body(self) -> dict[str, Any] | None:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "Request body is required."})
            return None
        raw = self.rfile.read(content_length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON body."})
            return None

    def _log_api(self, status: HTTPStatus) -> None:
        print(f"[api] {self.command} {self.path} -> {int(status)}")


def run_api_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), MindSalonApiHandler)
    print(f"Mind Salon API server running at http://{host}:{port}")
    print("Use Ctrl+C to stop.")
    server.serve_forever()
