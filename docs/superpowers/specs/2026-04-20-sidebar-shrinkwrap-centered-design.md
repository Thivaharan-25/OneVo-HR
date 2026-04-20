# Spec: Sidebar Shrink-wrap & Centered Redesign

**Date:** 2026-04-20

## Problem

The `IconRail` capsule uses `bottom-3` (full viewport height) and a `flex-1` nav container. This leaves a large empty gap below the icons, making the sidebar look sparse and unattractive.

## Design

Three targeted changes:

### 1. Shrink-wrap + vertically centered (`IconRail.tsx`)

Remove full-height stretching. Center the capsule vertically in the viewport.

| Before | After |
|---|---|
| `fixed left-3 top-3 bottom-3 z-50 w-14` | `fixed left-3 top-1/2 -translate-y-1/2 z-50 w-[62px]` |
| Nav items div has `flex-1` | Remove `flex-1` — div wraps its content |

The capsule height becomes exactly as tall as the logo + icons + padding. No empty space.

### 2. Layout margin adjustment (`DashboardLayout.tsx`)

The sidebar is now 62px wide (was 56px). Left offset = 62px + 12px (left-3) + 8px gap = 82px.

| Before | After |
|---|---|
| `ml-[72px]` (rail only) | `ml-[82px]` |
| `ml-[288px]` (rail + panel) | `ml-[298px]` |

### 3. Topbar left offset (`Topbar.tsx`)

| Before | After |
|---|---|
| `left-[72px]` | `left-[82px]` |

## Files to Change

| File | Change |
|---|---|
| `demo/src/components/layout/IconRail.tsx` | Width, position, remove `flex-1` |
| `demo/src/components/layout/DashboardLayout.tsx` | Update both margin values |
| `demo/src/components/layout/Topbar.tsx` | Update left offset |

## Out of Scope

- No changes to icon set, active state styles, or ExpansionPanel
- No changes to icon sizes inside the rail
