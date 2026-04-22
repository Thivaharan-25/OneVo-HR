# Spec: Sidebar Capsule Polish — Compact + Violet Glow

**Date:** 2026-04-20

## Problem

After the shrink-wrap/centering change, the `IconRail` capsule has three visual issues:
1. An orphaned horizontal spacer `<div>` at the bottom — an artifact of the old full-height design.
2. Icon buttons at `h-10` (40px) make the capsule taller than it needs to be.
3. The border and shadow are neutral white — the capsule doesn't feel connected to the violet design language.
4. No visual separation between primary nav icons and utility icons (Admin, Settings).

## Design

### 1. Remove bottom spacer (`IconRail.tsx`)

Delete the trailing `<div className="shrink-0 w-7 h-[1px] bg-white/[0.07] mb-1" />`. The capsule now shrink-wraps cleanly with no hanging artifact.

### 2. Compact icon buttons (`IconRail.tsx`)

Change icon button height from `h-10` to `h-8` (40px → 32px). This reduces the overall capsule height and tightens the visual density.

### 3. Group nav vs. utility icons (`IconRail.tsx`)

Split the icon list into two logical groups:
- **Primary nav:** Home, People, Workforce, Org, Calendar, Inbox
- **Utility:** Admin, Settings

Add `mt-2` to the first utility icon button to create a small visible gap between the groups. No divider line — just spacing.

### 4. Violet-tinted border + ambient glow (`index.css`)

Update `.rail-capsule`:

| Property | Before | After |
|---|---|---|
| `border` | `1px solid rgba(255,255,255,0.08)` | `1px solid rgba(124,58,237,0.18)` |
| `box-shadow` | `0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06)` | `0 20px 60px rgba(0,0,0,0.5), 0 0 30px rgba(124,58,237,0.07), inset 0 1px 0 rgba(255,255,255,0.07)` |

## Files to Change

| File | Change |
|---|---|
| `demo/src/components/layout/IconRail.tsx` | Remove spacer div, `h-10` → `h-8`, add `mt-2` gap before utility icons |
| `demo/src/index.css` | Update `.rail-capsule` border + box-shadow |

## Out of Scope

- No changes to icon set, active state styles, logo, or ExpansionPanel
- No changes to DashboardLayout or Topbar offsets
- No labels added
