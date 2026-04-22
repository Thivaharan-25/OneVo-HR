# Spec: Move Workforce & Org Tabs to Sidebar

**Date:** 2026-04-19

## Problem

Both the Workforce and Organization pages use horizontal top tab bars for sub-section navigation. This is inconsistent with the rest of the app (People, Admin, Settings, Calendar) which use the left ExpansionPanel sidebar. Additionally, the Org sidebar is missing 3 of its 6 sections.

## Design

Remove the internal top tab bars from both pages and drive navigation entirely through the ExpansionPanel sidebar.

### Workforce

Add `'workforce'` to `PANEL_PILLARS` in `navStore.ts` so the ExpansionPanel opens when Workforce is active.

Add `workforce` to `subNavConfig` in `ExpansionPanel.tsx` with all 5 items:

| Label | Path |
|---|---|
| Overview | `/workforce` |
| Activity | `/workforce?tab=activity` |
| Work Insights | `/workforce?tab=work-insights` |
| Online Status | `/workforce?tab=online-status` |
| Identity Verification | `/workforce?tab=identity-verification` |

`WorkforcePage.tsx` switches from `useState('overview')` to reading `useSearchParams()` — matching the pattern already used in `OrgPage.tsx`. The `flex gap-1 flex-wrap` tab bar row is removed.

### Organization

Extend the existing `org` entry in `subNavConfig` with 3 missing items:

| Label | Path |
|---|---|
| Job Families | `/org?tab=job-families` |
| Legal Entities | `/org?tab=legal-entities` |
| Cost Centers | `/org?tab=cost-centers` |

Remove the top tab bar (`<div className="flex gap-1.5 p-1 rounded-lg ...">`) from `OrgPage.tsx`.

## Files to Change

| File | Change |
|---|---|
| `demo/src/store/navStore.ts` | Add `'workforce'` to `PANEL_PILLARS` |
| `demo/src/components/layout/ExpansionPanel.tsx` | Add `workforce` config; extend `org` config with 3 items |
| `demo/src/modules/workforce/WorkforcePage.tsx` | Remove top tab bar; switch to URL params |
| `demo/src/modules/org/OrgPage.tsx` | Remove top tab bar |

### Icons for Workforce Sidebar

Use icons already available from `lucide-react`. Suggested mapping (implementer may substitute):

| Item | Icon |
|---|---|
| Overview | `LayoutDashboard` |
| Activity | `Activity` |
| Work Insights | `TrendingUp` |
| Online Status | `Wifi` |
| Identity Verification | `Fingerprint` |

## Out of Scope

- No changes to tab content components
- No changes to routing in `App.tsx`
- No icon changes beyond what icons are already used in `ExpansionPanel`
