# Mind Salon Architecture

## 1. Overview

Mind Salon has four conceptual layers:

- User Layer
- Runtime Layer
- Agent Layer
- Knowledge Layer

## 2. User Layer

The User Layer provides interaction and observability.

Responsibilities:

- session navigation
- stage/round visibility
- artifact exploration
- protocol and decision transparency
- operator controls (pause/continue/follow-up)

Constraint:

- UI should not collapse into plain chat.

## 3. Runtime Layer

The Runtime Layer orchestrates session execution.

Core components:

- Session Manager
- Workflow Engine
- Protocol Engine
- Role Engine
- Tool Engine
- Message Bus
- Task Scheduler
- Collaboration Scheduler
- Runtime Execution Loop

Responsibilities:

- create/close session
- select pattern
- enforce protocol
- route role turns
- persist messages/artifacts/memory
- emit execution summary

## 4. Agent Layer

The Agent Layer implements role behavior and model routing.

Core concepts:

- role agents (`planner`, `architect`, `reviewer`, `critic`, `creator`, `verifier`, `coordinator`)
- LLM adapters (mock, siliconflow)
- per-role routing policy
- fallback / first / round-robin strategies
- RoleProfile (responsibility bounds)
- RoleAdaptationState (bounded evolution state)
- RoleReflection (traceable self-correction signal)

## 5. Knowledge Layer

The Knowledge Layer supports long-term evolution.

Components:

- in-memory store (current implementation)
- memory records
- artifact tree
- retrieval interface

## 6. Data and Control Flow

High-level flow:

1. user submits task/follow-up
2. scheduler queues task
3. runtime loop executes stages by pattern/protocol
4. agents produce role turns and artifacts
5. review gate decides approve/revise/reject
6. memory is updated
7. API returns runtime/session views

## 7. Runtime Boundary

Current boundary:

- backend API: session/task execution and state
- frontend workspace: visualization and controls

Recommended evolution:

- keep protocol/pattern logic backend-owned
- keep frontend as stateful observer/operator
