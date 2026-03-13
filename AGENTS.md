# AGENTS.md

## Project Overview

Mind Salon is a collaborative AI system for complex tasks. It is designed to turn a user task into a structured, multi-role session instead of collapsing the experience into a plain chat interface.

The documented architecture has four conceptual layers:

- User Layer: session navigation, observability, operator controls
- Runtime Layer: session orchestration, protocol enforcement, scheduling, persistence
- Agent Layer: role behavior, model routing, bounded self-correction
- Knowledge Layer: memory records, artifact tree, retrieval support

At a high level, the flow is: user input -> scheduler -> runtime execution loop -> role turns and artifacts -> review gate -> memory update -> session/runtime views.

## Key Concepts

The core models are defined in `docs/core-models/`.

- Task: the durable execution unit for user intent. Key fields include `task_id`, `goal`, `constraints`, `status`, `owner_role`, and `artifacts`.
- Role: a bounded collaborator with explicit responsibility and authority. Roles are protocol-constrained and may reflect or adapt, but cannot override protocol authority or drift beyond role scope.
- Message: the structured communication and audit record between roles. Messages carry `task_id`, `session_id`, sender/receiver roles, `type`, `payload`, and `trace_id`.
- Artifact: a deliverable produced during execution. Artifacts have identity, type, version, lineage, creator, and quality metadata.
- Session: the collaboration instance around a task. It tracks participants, active pattern, round index, state, and lifecycle timestamps.
- Memory: the persisted experience layer for reuse. Documented types are short-term memory, long-term memory, and decision log.

## Multi-Agent Workflow

Mind Salon collaboration is governed by the Salon Protocol and pattern system in `docs/collaboration/` and `docs/architecture/workflow-engine.md`.

- Protocol principles: discussion before execution, bounded deliberation, traceable decisions, closed-loop feedback.
- Decision outcomes: `Approve`, `Revise`, `Reject`, `Escalate`.
- Core patterns: Plan-Review-Execute, Debate-Then-Execute, Incremental Delivery, Parallel Specialists.
- Pattern specs define `pattern_id`, roles, entry/exit conditions, steps, failure handling, and metrics.
- Workflow rule: deliberation must pass before execution; review must emit a quality conclusion; feedback must be written back to memory.

Do not treat role turns as free-form chat. They are protocol-bound steps inside a state machine.

## Runtime Execution Model

The runtime model is documented in `docs/runtime/`.

- Canonical stage flow: `intent -> proposal -> deliberation -> execution -> review -> feedback -> done`.
- Execution loop: `Ingress -> Schedule -> Collaborate -> Execute -> Review -> Feedback -> Persist -> Next`.
- Every step must carry `task_id` and `trace_id`.
- State transitions must remain traceable and failure paths recoverable.
- Required contracts: Task Contract, Message Contract, Tool Contract, Decision Contract.
- Non-functional runtime requirements: idempotency, observability, timeout/retry behavior, auditability.
- Runtime artifact handling includes artifact lists by task, lineage via `parent_artifact_id`, and quality/version metadata.

Current documented deployment is a single-node MVP with an in-process API gateway, lightweight scheduler, salon kernel, and local store.

## Repository Structure

- `docs/`: primary source of truth for architecture, runtime, protocol, models, UI state/view contracts, and developer guidance.
- `docs/ui/`: UI design and frontend state/protocol documentation. This is the documented UI layer.
- `src/mind_salon/`: Python implementation of the backend/runtime, including models, kernel, runtime, schedulers, API, collaboration, and store modules.
- `frontend/`: actual frontend implementation in this repository. Use this as the code counterpart to the documented UI layer.
- `examples/`: runnable entry points for MVP, API server, workspace, and SiliconFlow-backed flows.
- `tests/`: verification for runtime and repository behavior where present.

If documentation mentions a conceptual `ui/` area, map that to `docs/ui/` for design/contracts and `frontend/` for implementation in this repository.

## Development Rules for Coding Agents

- Use `docs/` as the source of truth before changing behavior.
- Do not casually change protocol definitions, stage ordering, review outcomes, or pattern semantics.
- Preserve core model schemas for tasks, messages, sessions, artifacts, roles, and memory unless the change is explicitly architectural.
- Follow runtime contracts: structured payloads, traceable transitions, recoverable failure paths, auditable decisions.
- Keep protocol and pattern logic backend-owned unless the docs explicitly place behavior in the frontend.
- Preserve artifact lineage, versioning, and quality metadata when changing runtime or presentation code.

## Safe Editing Rules

- Prefer minimal diffs over broad rewrites.
- Avoid rewriting architecture or protocol docs unless the task explicitly changes system design.
- Respect the collaboration protocol: do not bypass deliberation, review, or feedback gates in code paths that are supposed to enforce them.
- Keep messages structured; do not replace contract-backed data with ad hoc blobs.
- Maintain observability surfaces such as event streams, decision logs, and trace-linked identifiers.
- When editing frontend behavior, preserve the documented session-first, protocol-aware, artifact-centered workspace model.

## How to Contribute Changes

- Read `docs/system-overview/README.md` first, then the relevant `architecture/`, `runtime/`, `collaboration/`, and `core-models/` docs.
- If a code change alters architecture, runtime contracts, protocol behavior, or model shape, update the corresponding docs in the same change.
- Keep frontend session state, backend presentation contracts, and runtime contracts aligned.
- When adding new patterns, ensure they are represented through the documented pattern spec structure.
- Verify that artifact generation, review outcomes, and memory write-back still match the documented workflow.
