# Mind Salon Frontend API Contract

## Session-Centric Endpoints

## `GET /api/sessions/{task_id}/workspace`

Returns semantic workspace state for rendering default UI.

Role turns include bounded evolution signals:

- `role_reflection`
- `role_corrected`
- `role_correction`
- `role_strategy_updated`
- `role_strategy_update`

## `GET /api/sessions/{task_id}/events`

Returns normalized session event stream:

- stage_changed
- round_advanced
- role_turn_started
- role_turn_completed
- role_reflected
- role_corrected
- role_strategy_updated
- artifact_created
- artifact_revised
- review_requested
- review_approved
- review_rejected
- session_paused
- human_intervened

## `GET /api/sessions/{task_id}/artifacts/thread`

Returns artifact nodes and lineage map for artifact-centered views.

## `POST /api/sessions/control`

Global semantic action endpoint.

Supported now:

- `start_salon` with payload `{ goal, auto_run?, role_llm_map?, role_agent_map? }`

## `POST /api/sessions/{task_id}/control`

Per-session semantic action endpoint.

Actions:

- continue_deliberation
- request_review
- enter_revise_path
- pause_session
- human_intervention
- replay_round

## Compatibility Endpoints

Legacy endpoints remain available:

- `/api/tasks`
- `/api/tasks/{task_id}`
- `/api/tasks/{task_id}/followup`
- `/api/runtime/*`
