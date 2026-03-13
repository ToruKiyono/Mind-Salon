# UI Frontend Architecture

## Architecture Rule

React/Next.js is the rendering layer.  
Session semantics come from backend contracts.

## Data Flow

1. Fetch runtime task list
2. Fetch semantic session workspace state
3. Render session-centric components
4. Dispatch session control actions
5. Refresh workspace state

## Contract Boundary

Frontend consumes:

- `get_session_workspace_state(session_id)`
- `stream_session_events(session_id)`
- `get_artifact_thread(session_id)`
- `control_session(session_id, action)`

No client-side reconstruction from raw logs should be required.
