# UI Refactor Summary

## What Changed in `docs/ui`

- Replaced prior mixed docs with concept-first structure:
  - `00-ui-salon-principles.md`
  - `01-ui-session-state-model.md`
  - `02-ui-event-and-protocol.md`
  - `03-ui-artifact-model.md`
  - `10-ui-design.md`
  - `11-ui-visual-direction.md`
  - `12-ui-design-system.md`
  - `20-ui-layout.md`
  - `21-ui-wireframe.md`
  - `22-ui-components.md`
  - `23-ui-interaction.md`
  - `30-ui-frontend-architecture.md`

## What Changed in `src/mind_salon`

- Added semantic presentation layer:
  - `src/mind_salon/presentation/contracts.py`
  - `src/mind_salon/presentation/service.py`
- API now exposes session-centric semantic routes:
  - `/api/sessions/{task_id}/workspace`
  - `/api/sessions/{task_id}/events`
  - `/api/sessions/{task_id}/artifacts/thread`
  - `/api/sessions/control`
  - `/api/sessions/{task_id}/control`
- Added frontend API contract doc: `docs/frontend-api-contract.md`.

## What Moved from Workspace to Inspector

Low-level controls are now explicitly scoped to Inspector/Dev Mode:

- runtime endpoint configuration
- per-role model routing
- low-level runtime pause toggles
- raw event stream view

Default workspace stays collaboration-first.

## Alignment with Mind Salon Philosophy

- Session-first state model is primary.
- Protocol and review gate are explicit in default UI.
- Artifact lineage is emphasized over raw logs.
- Challenge/critique/revision semantics are visible in turn stream.
- Frontend consumes semantic collaboration state instead of reconstructing from low-level runtime objects.
- Roles support bounded self-correction and memory-informed strategy evolution with traceable events.
