# Known Issues & Gotchas: Frontend

## Gotchas

### API Integration

- **organisation_id vs tenant_id (RESOLVED):** Previously some backend endpoints returned `organisation_id`. This has been fixed — all tables now use `tenant_id` consistently. Frontend types should use `tenantId` everywhere.
- **Cursor pagination:** Backend uses cursor-based pagination. Don't build offset-based pagination components.
- **RFC 7807 errors:** All API errors follow Problem Details format. Parse `title`, `detail`, and `errors` array consistently.

### Authentication

- **Access token in memory only** — lost on page refresh. Always implement silent refresh via HttpOnly cookie.
- **Permission array can be large** (90+ permissions). Cache in Zustand store, don't re-fetch on every route change.
- **Device JWT is NOT for frontend** — that's for the desktop agent. Frontend uses standard user JWT.

### Real-time

- **SignalR requires auth** — pass JWT as query param on connection (SignalR standard pattern).
- **Channel permissions** — `workforce-live` and `exception-alerts` channels require `workforce:view` permission. Server will reject unauthorized subscriptions.
- **Reconnection storms** — if server restarts, all clients reconnect simultaneously. Use jitter in reconnection delay.

### Workforce Intelligence

- **Activity data can be empty** — if monitoring is disabled for a tenant or employee, activity endpoints return empty arrays, not errors. UI must handle "No monitoring data available" gracefully.
- **Presence session vs device session** — presence is one-per-day summary, device sessions are granular. Use presence for dashboard cards, device sessions for detail drilldown.
- **Screenshots are sensitive** — only show to users with `workforce:view` permission. Never cache in browser storage.
- **Exception alerts are real-time** — use SignalR, don't poll. Show toast notification + badge count.

### Performance

- **Activity heatmap** — hourly intensity data can be up to 24 points per employee per day. For team views with 50+ employees, use server-side aggregation, not client-side computation.
- **Employee list with status** — the live workforce dashboard shows status for all employees. Use SignalR push updates, not polling individual employee endpoints.

## Technical Debt

None yet — greenfield project.
