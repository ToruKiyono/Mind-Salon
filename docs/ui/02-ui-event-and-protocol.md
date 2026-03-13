# UI Event and Protocol Model

## Event Stream

Session events are normalized and ordered:

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

## Protocol Visibility

UI surfaces:

- active stage
- active role
- allowed roles
- round progress
- review decision authority
- revise eligibility

Protocol state drives interaction affordances.
