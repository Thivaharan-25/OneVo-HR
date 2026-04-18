# Dashboard Home Screen — Color Discipline

**Date:** 2026-04-18
**Status:** Approved
**Scope:** Home screen dashboard only (`/` route). All other pages unaffected.

---

## Problem

The dashboard home screen uses up to 6 simultaneous status colors (violet, green, amber, red, cyan, orange). When all appear at once — in KPI badges, alert borders, activity feed icons, and chart series — the user cannot quickly tell what needs their attention. Color loses meaning when everything is colored.

## Design Rule

**On the home screen, color means urgency — nothing else.**

- **Red** (`#ef4444`) — critical, act immediately
- **Amber** (`#f59e0b`) — warning, act soon
- **Zinc** (`#3f3f46` / `#a1a1aa`) — everything else (info, active, partial, neutral)
- **Violet** — brand/interactive only (action buttons, active nav, chart fills) — not a status signal

Green, cyan, and orange are **removed from the home screen**. They remain fully available on detail pages (employee profile, Workforce Live, etc.) where they carry clear contextual meaning.

---

## Section-by-Section Changes

### 1. Primary KPI Cards

| KPI | Before | After |
|:----|:-------|:------|
| Pending Approvals (count > 0) | Violet glow | Violet glow (unchanged) |
| Open Alerts — critical count | Red glow | Red glow (unchanged) |
| Open Alerts — warning count badge | Amber | Amber (unchanged) |
| Expiring Documents | Red glow if critical | Red glow if critical (unchanged) |
| Any info/partial badge | Cyan / Orange | Zinc pill, no color |

No change to violet glow — it signals "this is actionable/interactive", not a status.

### 2. Secondary KPI Cards

| KPI | Before | After |
|:----|:-------|:------|
| Total Employees | Zinc (neutral) | Zinc (unchanged) |
| Attendance Rate | Green if high | Zinc — rate shown as number only |
| New Hires This Month | Zinc | Zinc (unchanged) |
| Avg Productivity Score | Green/amber/red | Zinc — score shown as number only |

Secondary KPIs carry reference data, not urgency signals. No status color needed.

### 3. Alerts Panel

| Severity | Before | After |
|:---------|:-------|:------|
| Critical | Red left border + red dot | Red left border + red dot (unchanged) |
| Warning | Amber left border + amber dot | Amber left border + amber dot (unchanged) |
| Info | Cyan left border + cyan dot | Zinc left border (`#3f3f46`) + zinc dot |
| Partial / Low | Orange left border + orange dot | Zinc left border + zinc dot |

Alert text color: critical rows get `#fafafa` (white), all others get `#a1a1aa` (zinc-400).

### 4. Activity Feed

| Element | Before | After |
|:--------|:-------|:------|
| Action-type icons | Colored per action (green = hire, red = termination, etc.) | All `#52525b` (zinc-600) |
| Avatar rings | Colored by status | No ring (avatar only) |
| Timestamp | Muted | Muted `#71717a` (unchanged) |

The action label (text) carries enough meaning without icon color.

### 5. Charts

#### Attendance Area Chart
| Element | Before | After |
|:--------|:-------|:------|
| Primary line + fill | Violet | Violet (unchanged) |
| Secondary line (comparison) | Cyan `#06b6d4` | Violet-light `#8b5cf6` |

#### Department Headcount Ring Chart
| Series | Before | After |
|:-------|:-------|:------|
| Series 1 | `#7c3aed` | `#7c3aed` (unchanged) |
| Series 2 | `#06b6d4` (cyan) | `#8b5cf6` (violet-light) |
| Series 3 | `#f59e0b` (amber) | `#a78bfa` (violet-muted) |
| Series 4+ | `#22c55e` (green) | `#4c1d95` (violet-deep) |

Violet shades are distinct enough at chart size; tooltip labels prevent ambiguity.

---

## Token Changes (Home Screen Only)

These are **component-level overrides** applied within the `DashboardHome` layout context. Global tokens are unchanged so other pages are unaffected.

| Token / Usage | Old value | New value |
|:--------------|:----------|:----------|
| Chart series 2 | `#06b6d4` | `#8b5cf6` |
| Chart series 3 | `#f59e0b` | `#a78bfa` |
| Chart series 4 | `#22c55e` | `#4c1d95` |
| Alert info border | `--status-info` (`#06b6d4`) | `#3f3f46` |
| Alert partial border | `--status-partial` (`#f97316`) | `#3f3f46` |
| Activity icon color | various | `#52525b` |
| Secondary KPI rate color | `--status-active` | `--muted-foreground` |

Implementation approach: wrap the home screen in a `data-color-mode="minimal"` attribute or a `DashboardHomeProvider` context. Components read this context and apply the zinc fallbacks accordingly. This keeps global tokens clean.

---

## What Does NOT Change

- Alert severity on all other pages (full 5-color system stays)
- Employee profile status badges (green active, cyan on-leave, etc.)
- Workforce Live dashboard (full color palette)
- Sidebar active states (violet)
- Buttons, form elements, focus rings (violet brand)
- Toast notifications (severity-matched colors)
- Charts on non-home pages (violet + cyan + amber palette stays)

---

## Success Criteria

- A user looking at the home screen can immediately identify what needs action by scanning for red, then amber
- No other color appears in the status/alert layer of the home screen
- The change is invisible to users on all other pages
