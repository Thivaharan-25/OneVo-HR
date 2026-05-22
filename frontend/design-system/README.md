# Design System

**Angular Material 21 + Tailwind CSS 4** — "Selective Drama" design language. Glassmorphism on hero surfaces (sidebar, stat cards, modals), flat on workhorse pages (tables, forms, detail sections). Violet Electric accent palette. Outfit + Geist typography.

## Foundations

Visual building blocks that every component inherits:

- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — brand, semantic, status, severity, surface tokens (light + dark)
- [[frontend/design-system/foundations/typography|Typography]] — Outfit + Geist font scale, weights, monospace for data
- [[frontend/design-system/foundations/spacing|Spacing]] — 4px base unit, layout spacing rules, component internal spacing
- [[frontend/design-system/foundations/elevation|Elevation]] — shadow scale, z-index layers, flat-by-default philosophy
- [[frontend/design-system/foundations/motion|Motion]] — duration scale, easing curves, animation keyframes, reduced-motion
- [[frontend/design-system/foundations/iconography|Iconography]] — Material Symbols icon system, size scale, domain icon map
- [[frontend/design-system/naming-conventions|Naming Conventions]] — user-facing label rules, system-to-label mapping

## Components

- [[frontend/design-system/components/component-catalog|Component Catalog]] — shadcn/ui primitives + composed components (DataTable, StatCard, etc.)

## Patterns

Reusable interaction patterns with code examples:

- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — dashboard layout, page types (list, detail, dashboard), responsive breakpoints
- [[frontend/design-system/patterns/form-patterns|Form Patterns]] — Angular Reactive Forms + Zod, multi-step wizards, inline editing, filter forms, validation
- [[frontend/design-system/patterns/table-patterns|Table Patterns]] — DataTable architecture, column types, sorting, pagination, bulk actions, export
- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]] — sidebar states, topbar, Quick Search, breadcrumbs, tab navigation
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] — chart library choice, chart types per page, custom components (timeline, heatmap)

## Theming

- [[frontend/design-system/theming/dark-mode|Dark Mode]] — system + user preference, color token mapping, chart adaptation
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — customizable tokens, logo injection, contrast safety

## Key Principles

1. **Selective Drama** — glass surfaces for hero elements (sidebar, KPI cards, modals), flat for workhorse elements (tables, forms, detail sections)
2. **Action → Awareness → Analysis** — dashboard and page layouts prioritize what needs user action first, then context, then deep data
3. **8-pillar navigation** — icon rail + expansion panel. Everything else is discoverable within pages or via Quick Search
4. **Information density** — compact tables, small cards, 14px body text. This is a work tool, not a marketing site
5. **Status at a glance** — color-coded badges, pulsing dots, severity indicators
6. **Permission-aware** — components hide or mask content based on permissions (role + employee-level overrides)
7. **Accessible** — WCAG 2.1 AA, keyboard nav, screen reader support. Glass degrades gracefully under `prefers-contrast: more`
8. **Responsive by design** - optimized across mobile, tablet, laptop, and desktop from Phase 1
9. **Simple naming** — every label passes the "would a non-technical HR manager understand this in 1 second?" test

## Phase 1 Responsive Requirement

All OneVo HR frontend UI must be responsive by design from Phase 1. Every shell, page, form, table, dashboard, and workflow must provide a usable experience across mobile, tablet, laptop, and desktop viewports. Desktop-first layouts are acceptable only when they include explicit responsive adaptations for smaller screens.

Every page must define behavior for:

| Viewport | Width | Required behavior |
|:---------|:------|:------------------|
| Mobile | `<640px` | Single-column content, mobile navigation drawer, touch-safe controls, card/list alternatives for dense tables |
| Tablet | `640-1023px` | Hidden or collapsible sidebar, content-first layout, compact filters/actions |
| Laptop | `1024-1279px` | Compact rail-first shell, optional collapsed panel, dense but readable work surfaces |
| Desktop | `>=1280px` | Full shell with rail, expansion panel, topbar, and full data surfaces |
