# UI Visual Refactor

## Overview

The frontend keeps the existing Mind Salon information architecture and protocol semantics, but the visual system has been rebuilt as a themed collaborative studio instead of a dashboard.

The semantic layout remains:

- `SessionNavigation`
- `SessionPulse`
- `ProtocolRail`
- `FocusManuscript`
- `RoleTurnStream`
- `ArtifactThread`
- `MemoryAside`
- `ReviewGate`
- `InterventionBar`

## Visual System

The new design system is driven by CSS variables and Tailwind tokens.

- Typography: display and body families are theme-controlled.
- Color tokens: background, panel, soft surface, line, text, subtext, primary, accent, success, warning, danger, glow.
- Spacing and radius: larger rounded cards and softer padding.
- Elevation: soft, floating, and glow shadows.
- Motion: hover lift, animated hero gradients, stage progress, and turn reveal animation.

Reusable surface patterns:

- `salon-card`: glass-like elevated panel
- `salon-gradient-border`: subtle luminous border treatment
- `salon-orb`: animated accent gradient for avatars and hero marks
- `salon-input` and `salon-button`: shared interactive styling

## Themes

### Youthful Girl

Default theme.

- Soft pastel palette with pink, sky, mint, and lavender accents
- Rounded floating cards
- Bright, gentle gradients
- Friendly studio atmosphere

### Wuxia Princess

- Jade, parchment, ink, and gold palette
- Slightly firmer radius and paper-like surfaces
- Calm academy mood with subtle brush-texture background
- Elegant literary feeling

### 3D Tech Sci-Fi

- Deep navy background with cyan and violet highlights
- Glass panels, stronger glow, HUD-like contrast
- Grid backdrop and luminous accents
- Futuristic command-center mood

## Component Styling Notes

- `SessionPulse` is now the hero card with session state, focus, and round progress.
- `ProtocolRail` uses animated progress plus stage cards.
- `FocusManuscript` is the primary content card for the current artifact.
- `RoleTurnStream` uses distinct role-accent conversation cards with avatars, badges, timestamps, and artifact references.
- `ArtifactThread` supports in-place lineage expansion with `details`.
- `InterventionBar` is presented as an elegant action bar instead of a control strip.

## Theme Engine

Theme selection is stored in the UI store and mirrored to `localStorage`. The active theme is applied through the `data-theme` attribute on the root document element, allowing runtime theme switching without changing data flow or backend contracts.
