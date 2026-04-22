# ONEVO Neutral Chrome Redesign — Design Spec

**Date:** 2026-04-21  
**Scope:** `demo/` codebase + `frontend/` design system docs  
**Status:** Approved

---

## Overview

Replace the violet-dominant glass aesthetic with a neutral monochromatic chrome system. The navigation shell (rail, expansion panel, topbar) becomes theme-aware neutral. Semantic status colors (green/amber/red) are untouched. The sidebar's two-panel behavior (click icon → expansion panel slides in) is preserved exactly.

---

## 1. Color System

### CSS Custom Properties

Applied via `data-theme="dark"` / `data-theme="light"` on `<html>`.

| Token | Dark | Light |
|---|---|---|
| `--bg-base` | `#0a0a0a` | `#f5f5f5` |
| `--bg-surface` | `#111111` | `#ffffff` |
| `--bg-elevated` | `#1a1a1a` | `#fafafa` |
| `--bg-overlay` | `#222222` | `#f0f0f0` |
| `--bg-hover` | `#2a2a2a` | `#ebebeb` |
| `--border` | `#2a2a2a` | `#e5e5e5` |
| `--border-soft` | `#1f1f1f` | `#efefef` |
| `--fg-1` | `#f5f5f5` | `#0a0a0a` |
| `--fg-2` | `#a3a3a3` | `#525252` |
| `--fg-3` | `#666666` | `#a3a3a3` |
| `--fg-4` | `#3d3d3d` | `#d4d4d4` |
| `--accent-subtle` | `#1e1e1e` | `#f0f0f0` |
| `--accent-border` | `#333333` | `#d4d4d4` |
| `--success` | `#22c55e` | `#16a34a` |
| `--warning` | `#f59e0b` | `#d97706` |
| `--danger` | `#ef4444` | `#dc2626` |
| `--info` | `#3b82f6` | `#2563eb` |

### What Changes

- **Removed:** all violet tokens (`--violet-*`, `glass-violet`, `bloom-active`, `bloom-hover`, `card-depth-glow`, `rail-capsule` violet borders/shadows)
- **Kept:** semantic status colors (success/warning/danger/info) — these are data colors, not chrome
- **Neutral badge pattern:** count badges use `bg-[var(--fg-1)] text-[var(--bg-base)]` (inverted)
- **Notification dot:** `var(--danger)` red — communicates urgency more clearly than violet

### Theme System

- `data-theme` attribute on `<html>` element (matches template pattern)
- First load: read `localStorage` key `theme` (`"dark"` | `"light"` | `"system"`); default `"system"`
- `"system"` mode: mirrors `prefers-color-scheme` media query, updates on OS change
- User toggle: Sun/Moon button in Topbar right side — cycles `system → light → dark`
- Override persists to `localStorage`

---

## 2. Demo Codebase Changes

### 2.1 Theme Infrastructure

**New file: `src/components/ui/ThemeProvider.tsx`**
- Reads `localStorage` on mount, sets `data-theme` on `<html>`
- Listens to `prefers-color-scheme` change events when in `"system"` mode
- Exposes `useTheme()` hook: `{ theme, setTheme }` where theme is `"dark" | "light" | "system"`

**`src/main.tsx`**
- Wrap `<App />` in `<ThemeProvider>`

**`src/index.css`**
- Add `[data-theme="dark"]` and `[data-theme="light"]` CSS variable blocks (tokens above)
- Replace violet scrollbars with neutral: `scrollbar-color: var(--border) transparent`
- Remove `.glass-violet`, `.glass-violet-md`, `.bloom-active`, `.bloom-hover`, `.rail-capsule`, `.card-depth-glow` utilities
- Keep `.card-depth` but update to use `var(--bg-surface)` / `var(--border)` instead of hardcoded values
- Keep gradient text utilities (used in data cards, not chrome)

**`tailwind.config.ts`**
- Change `darkMode: 'class'` → `darkMode: ['selector', '[data-theme="dark"]']` (Tailwind v3.4+ — confirmed v3.4.15 in use)
- This aligns Tailwind `dark:` utilities with the `data-theme` attribute set by ThemeProvider
- Keep `violet` color scale (used in data visualisations, charts, metric cards — not chrome)
- Add neutral surface aliases pointing to CSS vars for use in JSX

### 2.2 DashboardLayout

**Remove:**
- Three `radial-gradient` ambient violet glow divs
- Dot-grid `backgroundImage` pattern div
- The entire `z-0 overflow-hidden` ambient background wrapper

**Change:**
- `style={{ backgroundColor: '#08080f' }}` → `className="bg-[var(--bg-base)]"`
- `text-white` → `text-[var(--fg-1)]`
- `<main className="pt-14 ...">` → `pt-12` (matches new 48px topbar)

### 2.3 IconRail

**Shape change:** floating pill capsule → flush left rail

| Property | Before | After |
|---|---|---|
| Position | `fixed left-3 top-[60px] bottom-4` | `fixed left-0 top-[48px] bottom-0` |
| Width | 76px (`w-[76px]`) | 64px (`w-16`) |
| Container style | `rail-capsule` (pill, violet border, glass) | `bg-[var(--bg-surface)] border-r border-[var(--border)]` |
| Border radius | 20px | none |
| Icon size | 24px | 16px |
| Active text color | `text-violet-200` + drop-shadow glow | `text-[var(--fg-1)]` |
| Inactive text color | `text-white/30` | `text-[var(--fg-3)]` |
| Hover text color | `text-white/65` | `text-[var(--fg-2)]` |
| Active indicator | violet dot + bloom glow | 4px neutral dot (`var(--fg-1)`) below icon |
| Animations | bloom-in, bloom-hover | none — simple `transition-colors` |
| Inbox badge | `bg-violet-400` dot | `bg-[var(--danger)]` dot (red) |

**Preserved:** all click logic, `PANEL_PILLARS` toggle behavior, module permission gating.

### 2.4 ExpansionPanel

**Behavior:** unchanged — `translateX` slide-in on pillar click, `panelOpen` state, section label at top.

| Property | Before | After |
|---|---|---|
| Background | `bg-[#0a0a14]/90 backdrop-blur-2xl` | `bg-[var(--bg-surface)]` |
| Border | `border-r border-white/[0.07]` | `border-r border-[var(--border)]` |
| Section label color | `text-white/35` | `text-[var(--fg-3)]` |
| Ambient breath gradient | violet gradient-to-b overlay | removed |
| Active item bg | `bg-violet-600/[0.18]` | `bg-[var(--accent-subtle)]` |
| Active item border | `border-violet-500/[0.28]` + glow shadow | `border border-[var(--accent-border)]` |
| Active item text | `text-white/90` | `text-[var(--fg-1)]` |
| Active left-edge bar | violet gradient bar + violet glow | removed |
| Active icon color | `text-violet-400` | `text-[var(--fg-1)]` |
| Inactive item | `text-white/45` | `text-[var(--fg-3)]` |
| Hover item | `text-white/75 bg-white/[0.05]` | `text-[var(--fg-2)] bg-[var(--bg-hover)]` |
| Footer divider | `via-violet-500/20` gradient | `bg-[var(--border-soft)]` solid 1px |

### 2.5 Topbar

| Property | Before | After |
|---|---|---|
| Height | 56px (`h-14`) | 48px (`h-12`) |
| Background | `bg-[#08080f]/85 backdrop-blur-2xl` | `bg-[var(--bg-surface)]` |
| Border | `border-white/[0.06]` | `border-b border-[var(--border)]` |
| Logo mark | `bg-gradient-violet` + glow | `bg-[var(--fg-1)] text-[var(--bg-base)]` |
| Breadcrumb separators | `text-white/20` | `text-[var(--fg-4)]` |
| Tenant name color | `tenantColor` (kept) | `tenantColor` (kept — tenant branding unaffected) |
| Search box | `bg-white/[0.04] border-white/[0.07]` | `bg-[var(--bg-elevated)] border-[var(--border)]` |
| Inbox badge | `bg-violet-500` pill + pulse + glow | `bg-[var(--fg-1)] text-[var(--bg-base)]` neutral pill |
| Notification dot | `bg-violet-400` | `bg-[var(--danger)]` |
| Avatar online dot | `bg-green-400 border-[#08080f]` | `bg-[var(--success)] border-[var(--bg-surface)]` |
| Theme toggle | absent | Sun/Moon button added, right of bell |
| Dividers | `bg-white/[0.08]` | `bg-[var(--border)]` |

---

## 3. Frontend Docs Updates

### 3.1 `color-tokens.md`

Replace the Tailwind HSL violet token table with the neutral CSS custom property table from Section 1. Update semantic usage table to reference `--fg-*` / `--bg-*` tokens. Remove violet gradient entries from the Gradients table (keep only chart-fill gradient which is data, not chrome).

### 3.2 `dark-mode.md`

- Change strategy from `next-themes` / `.dark` class to `data-theme` attribute
- Update CSS variable blocks to neutral tokens
- Update `ThemeToggle` code example to cycles system/light/dark
- Note: `prefers-color-scheme` is the default, user override via localStorage
- Update glass surface section: dark glass is `var(--bg-surface)` solid, light is `var(--bg-surface)` solid — no backdrop-blur in chrome

### 3.3 `navigation-patterns.md`

- Icon Rail: update width to 64px, icon size to 16px, remove bloom/glow active state, change container from capsule to flush
- Active indicator: neutral dot (`var(--fg-1)`) below icon
- Expansion panel active: update to neutral `accent-subtle` + `accent-border`
- Topbar height: update to 48px
- Add theme toggle entry to Topbar element table

### 3.4 `iconography.md`

- Update nav icon size from `h-5 w-5` (20px) to `h-4 w-4` (16px)
- Update icon stroke: remove `strokeWidth` variation between active/inactive — use single weight `1.75` throughout

---

## Constraints

- The `demo/` is a Vite + React + TypeScript project — no Next.js, so no `app/layout.tsx`
- `tailwind.config.ts` uses `darkMode: 'class'` currently — switching to `selector` with `[data-theme="dark"]`
- Violet color scale stays in Tailwind config (used in metric cards, charts, data viz — not removed from the project, only from chrome)
- `tenantColor` in Topbar breadcrumb stays dynamic — tenant branding is unaffected
- No changes to any page-level components (`modules/`) or mock data
