# App Catalog Manager

## Purpose

The App Catalog Manager maintains the **global app catalog** — a OneVo-curated library of known applications (Chrome, Teams, Slack, VS Code, etc.) that is made available to all tenants. HR admins use this catalog as the primary source when building their monitoring allowlists, instead of typing app names manually or waiting for organic discovery.

It also surfaces **uncatalogued apps** — processes appearing frequently across tenant agents that the dev team hasn't yet classified — so they can be bulk-approved into the catalog with one action.

---

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `global_app_catalog` | Read + write — catalog definitions, `is_public` toggles, metadata |
| `observed_applications` (via SharedPlatform read interface) | Read — aggregate view for "Reported But Uncatalogued" |

`global_app_catalog` lives in the `shared_platform` schema and is owned by the SharedPlatform module's DbContext. The App Catalog Manager accesses it exclusively through `IGlobalAppCatalogService` (SharedPlatform public interface) — never via direct DbContext access.

---

## Capabilities

### App Catalog List

- View all entries in `global_app_catalog`
- Filter by: category (`browser`, `communication`, `development`, `office`, `design`, `other`), publisher, `is_public` status
- Toggle `is_public` inline — flips immediately; all tenants see or lose the app in their catalog browser on next page load
- Edit metadata: display name, category, publisher, icon URL, `is_productive_default`

### Add New App

Form fields required to add a catalog entry:

| Field | Notes |
|---|---|
| App name | Human-readable display name (e.g., "Google Chrome") |
| Process name | Exact process name from agent (e.g., `chrome.exe`) — this is the matching key |
| Category | Picker: browser / communication / development / office / design / other |
| Publisher | Company name (e.g., "Google LLC") |
| Icon URL | CDN URL for display in HR admin UI |
| `is_public` | Whether all tenants can see this immediately |
| `is_productive_default` | Default productivity classification used by monitoring |

When a new app is saved, a background job runs:
```
UPDATE observed_applications
SET global_catalog_id = <new_id>
WHERE process_name = '<process_name>'
```
This auto-links all existing tenant observations across all tenants instantly. Future agent ingest upserts auto-fill `global_catalog_id` at write time.

### Reported But Uncatalogued

A prioritized list of process names appearing in `observed_applications` across multiple tenants that have no `global_catalog_id` match.

- Sorted by: number of tenants reporting the app (descending)
- Shows: process name, tenant count, aggregate employee count across all tenants, first/last seen
- **Bulk approve**: Select one or more entries → fill metadata (name, category, publisher, icon) → save → creates catalog entries + auto-links all existing observations in one transaction
- **Dismiss**: Mark as noise (e.g., OS process, telemetry agent) — won't reappear in this list

### Usage Analytics

Read-only view of catalog adoption:

- "Used by N tenants" count per catalog entry (from `observed_applications.global_catalog_id` count)
- Aggregate total seconds observed and employee count across all tenants
- **Strictly aggregate** — no employee-level data, no per-tenant breakdown, no individual usage visible here

---

## Initial Catalog Seed

The dev team pre-seeds ~40 apps at platform launch so every new tenant's HR admin immediately has a useful catalog without waiting for organic discovery:

| Category | Apps |
|---|---|
| Browser | Chrome, Firefox, Edge |
| Communication | Teams, Slack, Zoom, Google Meet, Discord, Outlook |
| Office | Word, Excel, PowerPoint, OneNote |
| Development | VS Code, Visual Studio, IntelliJ, Git, Docker, Terminal |
| Design | Figma, Adobe Photoshop, Adobe Illustrator |
| Productivity | Notion, Trello, Asana |

All seeded entries have `is_public = true` and `is_productive_default` set appropriately.

---

## Notes

- `process_name` is the canonical matching key across the entire system — the catalog, observed_applications, and app_allowlists all deduplicate and link by this field. A catalog entry's `process_name` must exactly match what the desktop agent reports.
- `is_productive_default` is a starting classification only — HR admins can override productivity classification per app in their own monitoring configuration without affecting the catalog.
- Removing an app from the catalog (`is_public = false`) does not delete existing allowlist entries — tenants that already added the app retain it. The change only prevents the app from appearing in new catalog browsing sessions.
- All catalog writes are audit-logged with the developer account, timestamp, and field-level changes.
