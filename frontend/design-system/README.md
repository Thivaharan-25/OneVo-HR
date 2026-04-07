# Design System

## Foundation

ONEVO uses **shadcn/ui** as the component foundation — unstyled Radix primitives with Tailwind CSS styling. Components are copied into the project (not imported from a package), allowing full customization.

## Design Tokens

See:
- [[color-tokens]] — brand colors, semantic colors, status colors
- [[typography]] — font scale, weights, line heights

## Components

See:
- [[component-catalog]] — all UI components and when to use them
- [[layout-patterns]] — page layouts, sidebar, content areas
- [[data-visualization]] — charts, heatmaps, sparklines

## Key Principles

1. **Consistency** — use shadcn/ui components, don't build custom ones
2. **Density** — dashboard UIs need information density (compact tables, small cards)
3. **Status at a glance** — color-coded badges, status dots, severity indicators
4. **Responsive** — desktop-first, tablet-compatible (≥768px)
5. **Accessible** — WCAG 2.1 AA minimum (Radix handles most of this)
