# Mind Salon Runtime Model

## 1. Runtime Unit

A `Task` is the durable thread of user intent.  
A `Session` is an execution instance for that task.

Current implementation supports:

- create task and execute to completion
- follow-up on the same task and execute next round

## 2. Canonical Stage Flow

Default stage sequence:

1. intent
2. proposal
3. deliberation
4. execution
5. review
6. feedback
7. done

Pattern may change role/stage details, but must preserve protocol constraints.

## 3. Turn Model

A role turn is the smallest execution step in a stage.

Turn payload typically includes:

- role
- stage
- decision
- content
- llm_backend
- llm_model
- llm_error

## 4. Deliberation and Review

Deliberation can iterate with bounded rounds (`max_deliberation_rounds`).

Review gate yields one of:

- approve
- revise
- reject

If rounds exceed limits, runtime can terminate for safety.

## 5. Artifact Model in Runtime

Artifacts are created/updated through stage progression and tool results.

Runtime maintains:

- artifact list by task
- artifact lineage tree (`parent_artifact_id`)
- quality status + versioning metadata

## 6. Event Model

Runtime is event-driven; common events include:

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

## 7. Session View State

Frontend-facing state includes:

- task/session identity
- active pattern/stage/round
- role turns
- artifact thread
- memory slice
- protocol summary
- event stream

## 8. Interaction Actions

Operator actions:

- start task
- follow-up current task/session
- continue pending runtime
- pause/resume runtime

Follow-up keeps the same `task_id` and appends new intent for the next execution round.

## 9. Role Self-Correction and Bounded Evolution

Roles can reflect and improve over time, but within protocol authority and role boundaries.

Runtime tracks:

- role reflection
- recurring issues
- correction events
- strategy updates on bounded axes

These updates are traceable through payload fields and event stream.

## 10. End-to-End Runtime Flow

1. user input enters gateway
2. task queued by scheduler
3. execution loop runs selected pattern
4. agents execute role turns under protocol
5. artifacts and messages persist
6. review gate closes/revises
7. memory updated
8. runtime summary returned
