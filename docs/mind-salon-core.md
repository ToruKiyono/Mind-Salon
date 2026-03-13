# Mind Salon Core

## 1. Purpose

Mind Salon is a protocol-driven collaborative intelligence system for complex problem solving.

It is not a chatbot. It is a structured multi-role reasoning environment.

## 2. One-Sentence Definition

Mind Salon is a protocol-driven, session-based, artifact-centered collaborative intelligence system.

## 3. Immutable Principles

### 3.1 Collaboration Over Single-Agent Reasoning

Intelligence emerges from role collaboration, not a single model output.

### 3.2 Session Is the Runtime Unit

All reasoning happens inside a Session.

A Session includes:

- task
- pattern
- protocol
- roles
- rounds
- artifacts
- memory

### 3.3 Protocol Governs Interaction

Roles do not act freely. Protocol decides:

- who can speak
- when stage changes
- who owns decision authority
- whether revision is allowed

### 3.4 Pattern Defines Collaboration Strategy

Pattern defines:

- stage sequence
- role participation
- deliberation limits
- decision conditions
- review gates

### 3.5 Artifact Is Primary Output

Messages are reasoning traces. Artifacts are durable outputs.

Examples:

- proposal
- architecture
- plan
- analysis
- review report
- final deliverable

### 3.6 Explicit Artifact Evolution

Artifact lineage must be traceable and versioned.

### 3.7 Review Gate for Convergence

Review decisions must be explicit:

- approve
- revise
- reject

### 3.8 Structured Challenge

Mind Salon requires critical/adversarial pressure to avoid premature consensus.

### 3.9 Memory-Driven Evolution

Memory records successful/failed strategies and improves future sessions.

### 3.10 Role Self-Correction Under Protocol

Roles may self-correct and update strategy over time, but only within:

- protocol authority
- role responsibility boundaries
- traceable memory-informed adaptation

Role evolution must remain bounded and must not collapse specialization.

## 4. Core Concept Loop

Task -> Session -> Pattern -> Protocol -> Role Turns -> Artifact Evolution -> Review Decision -> Memory

## 5. Canonical Roles (Current Runtime)

Current default runtime roles are:

- planner
- architect
- reviewer
- critic
- creator
- verifier
- coordinator

Notes:

- Different patterns may activate subsets of roles.
- Additional roles are allowed, but protocol and pattern must define their authority.

## 6. Session Lifecycle (Canonical)

Canonical stage flow:

1. intent
2. proposal
3. deliberation
4. execution
5. review
6. feedback
7. done

## 7. Event-Driven Runtime

Typical runtime events:

- stage_changed
- round_advanced
- role_turn_started
- role_turn_completed
- artifact_created
- artifact_revised
- review_requested
- review_approved
- review_rejected
- session_paused
- human_intervened

## 8. What May Change

The following may evolve without changing identity:

- LLM providers and adapters
- tool integrations
- runtime infrastructure
- storage/database
- frontend framework
- pattern library

## 9. What Must Not Change

Mind Salon identity depends on:

- session-based collaboration
- protocol-governed interaction
- pattern-driven execution
- artifact-centered reasoning
- review-based convergence
- critical challenge
- memory-based learning

Removing these means the system is no longer Mind Salon.
