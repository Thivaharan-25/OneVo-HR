# Dashboard Userflow

## Actor

Platform account with `platform.dashboard.view`.

## Journey

1. Operator signs in to `console.onevo.io`.
2. Console opens `/`.
3. Dashboard loads platform summary, health, alerts, recent events, tenant distribution, and quick links.
4. Operator clicks a card to navigate to the owning module.

## APIs Used

- `GET /admin/v1/dashboard/summary`
- `GET /admin/v1/dashboard/platform-health`
- `GET /admin/v1/dashboard/recent-events`
- `GET /admin/v1/dashboard/alerts`

## Notes

Dashboard has no side panel. It is read-only and does not own mutation flows.
