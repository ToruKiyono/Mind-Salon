# UI Session State Model

## Canonical View State

The frontend consumes a semantic state object from backend:

```ts
SalonSessionState {
  sessionId: string
  taskId: string
  taskTitle: string
  pattern: string
  stage: string
  round: number
  maxRounds: number
  activeRole?: string
  focusArtifactId?: string
  artifacts: ArtifactNode[]
  turns: RoleTurn[]
  memory: MemoryRecord[]
  protocol: ProtocolState
  reviewGate: ReviewGateState
  events: SessionEvent[]
}
```

Role turn payload may include adaptation signals:

- `role_reflection`
- `role_corrected`
- `role_strategy_updated`

## Design Rule

Frontend must render this state directly.  
Frontend must not reconstruct semantics from low-level tables/logs.
