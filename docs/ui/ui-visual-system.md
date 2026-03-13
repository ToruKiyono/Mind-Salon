# UI Visual System

## Intent

Mind Salon is a collaborative thinking universe, not a dashboard. The interface is organized as a spatial studio where reasoning feels staged, alive, and character-driven.

The frontend now centers on ten canonical components:

- `SalonHeader`
- `SessionAtlas`
- `SalonStage`
- `FocusManuscript`
- `RoleOrbit`
- `ProtocolPath`
- `ArtifactGalaxy`
- `MemoryConstellation`
- `ReviewGate`
- `InterventionBar`

## Spatial Blueprint

### SalonHeader

A hero surface that establishes world, identity, runtime pulse, and session context.

### SessionAtlas

A floating navigation atlas for active sessions plus the theme engine. Sessions are rendered as living constellation entries, not sidebar list rows.

### SalonStage

The center of the interface. This is the primary reasoning arena and must remain the visual anchor of the page.

### FocusManuscript

The manuscript is the gravitational center of the workspace. Artifact focus, round state, and current quality metadata gather here.

### RoleOrbit

Role turns unfold around the manuscript as animated dialogue bodies. Roles are treated as characters with identity, motion, and speaking presence.

### ProtocolPath

The runtime protocol is presented as a luminous path across the stage rather than a dashboard rail. It should feel like a route through the collaboration ritual.

### ArtifactGalaxy

Artifacts appear as evolving objects in a galaxy field. Lineage is shown as branching relationships and depth, never as a flat list.

### MemoryConstellation

Memory records appear as stable stars or lantern-like signals held near the stage, supporting but not overpowering the manuscript.

### ReviewGate

The review surface is a decision chamber, not a status widget. It must feel consequential and ritualized.

### InterventionBar

Human steering tools remain present, but they are integrated as studio controls rather than admin controls.

## Motion System

Framer Motion is now part of the frontend visual language.

### Required Motion Behaviors

- stage surfaces enter with depth and lift
- orbit dialogue appears in sequence around the manuscript
- artifacts animate as evolving objects
- progress pulses through the protocol path and manuscript state
- intervention feedback appears as an atmospheric whisper rather than a harsh notification

### Implementation Notes

- use Framer Motion for structural entrance and layout choreography
- preserve moderate pacing; motion should feel alive, not noisy
- keep transitions soft in Youthful Girl, poised in Wuxia Princess, and crisp in 3D Tech Sci-Fi

## Theme Engine

Themes must change more than color. Each theme changes atmosphere, material, typography, and motion feel.

### Youthful Girl

Direction:

- pastel creative studio
- bubble-like glass surfaces
- airy glow and playful movement

Material cues:

- luminous white glass
- pink and sky gradient energy
- soft rounded capsules and floating manuscript light

### Wuxia Princess

Direction:

- ancient scholar academy
- jade and parchment surfaces
- graceful and ceremonial motion

Material cues:

- scroll-like manuscript treatment
- calmer glow
- calligraphic display typography and ink-texture atmosphere

### 3D Tech Sci-Fi

Direction:

- futuristic holographic command center
- layered neon glass
- precise kinetic response

Material cues:

- HUD-like contrast
- stronger depth fields
- luminous protocol path and artifact energy

## Role Identity

Roles are characters in the salon.

Each role surface should include:

- avatar
- badge
- color identity
- expressive dialogue container
- artifact reference when applicable
- timestamp and turn metadata

Primary roles:

- Planner
- Architect
- Critic
- Challenger
- Reviewer

Extended runtime roles may inherit the same system without flattening the visual hierarchy.

## Guardrails

- do not collapse the experience back into cards in columns with uniform shapes
- do not reduce the stage to a dashboard content area
- do not render artifacts as ordinary list items
- do not render role collaboration as plain chat rows
- preserve the manuscript as the visual center of gravity
- preserve protocol-aware, session-first, artifact-centered behavior from the existing UI contracts
