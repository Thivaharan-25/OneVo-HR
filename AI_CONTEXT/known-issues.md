# Known Issues & Gotchas: ONEVO

**Last Updated:** 2026-04-06

---

## Active Bugs

| ID | Description | Severity | Workaround | Status |
|:---|:------------|:---------|:-----------|:-------|
| - | No active bugs yet (project in initial development) | - | - | - |

---

## Gotchas & Non-Obvious Behaviors

Things that work differently than you'd expect. AI agents: pay attention to these before generating code.

### General / Backend

- **[[infrastructure/multi-tenancy|Multi-Tenancy]] Everywhere:** Every single query MUST be tenant-scoped. The `BaseRepository<T>` handles this via `ITenantContext` (see [[backend/shared-kernel|Shared Kernel]]), but if you write raw SQL or use `DbContext` directly, you MUST include `WHERE tenant_id = @tenantId`. PostgreSQL RLS is a safety net, not a replacement for application-level filtering.

- **RLS Interceptor — Guid-only string interpolation:** The `TenantRlsInterceptor` uses `$"SET LOCAL app.current_tenant_id = '{_tenantContext.TenantId}'"`. This is safe **only** because `TenantId` is a `Guid` (hex + hyphens — cannot contain SQL injection characters). **Never copy this pattern for string values.** For any non-`Guid` SET LOCAL, use `SELECT set_config('app.current_tenant_id', $1, true)` with a parameterized `NpgsqlParameter`. See [[infrastructure/multi-tenancy|Multi-Tenancy]] for the safe parameterized alternative.

- **Employee vs User:** `users` is the login identity (authentication). `employees` is the HR identity (business data). They are 1:1 linked via `user_id`. When working with HR features, always query through `employees`, not `users`. The `employees` table is the central hub.

- **organisation_id vs tenant_id (RESOLVED):** Previously some tables used `organisation_id` instead of `tenant_id`. This has been fixed — all tables now use `tenant_id` consistently. No EF Core column mapping workarounds needed. Frontend types should use `tenantId` everywhere as well.

- **Snake Case in DB, PascalCase in C#:** Database uses `snake_case`. C# uses `PascalCase`. EF Core's `.UseSnakeCaseNamingConvention()` handles this automatically. Don't manually specify column names unless there's a mismatch.

- **Encrypted Fields:** These columns use `bytea` type and must be encrypted/decrypted at the application level (see [[security/data-classification|Data Classification]]): `account_number_encrypted` (employee_bank_details), `client_id_encrypted` / `client_secret_encrypted` (sso_providers), `api_key_encrypted` (biometric_devices, hardware_terminals), `credentials_encrypted` (integration_connections, notification_channels). Use `IEncryptionService` with AES-256.

- **JSONB Columns:** Several tables use JSONB for flexible data. Map these to typed C# classes using EF Core's JSONB support. See [[security/data-classification|Data Classification]] for the full JSONB inventory.

- **Self-Referencing Tables:** `departments` (parent_department_id), `employees` (manager_id), `goals` (parent_goal_id), `document_categories` (parent_category_id), `leave_policies` (superseded_by_id), `refresh_tokens` (replaced_by_id). Handle recursive queries with CTEs.

### Workforce Intelligence

- **Attendance → Workforce Presence Rename:** The old `Attendance` module no longer exists. It is now `Workforce Presence` (`ONEVO.Modules.WorkforcePresence`). All attendance-related tables remain but under this new namespace. References to "Attendance" in code should use "WorkforcePresence". See [[modules/workforce-presence/overview|Workforce Presence]].

- **Activity Data Volume:** `activity_snapshots` generates ~240 rows/employee/day (one every 2-3 min for 8 hours). For 500 employees = 120,000 rows/day. Use pg_partman monthly partitions. Always query with `tenant_id` + date range. See [[modules/activity-monitoring/overview|Activity Monitoring]].

- **Raw Buffer Purge:** `activity_raw_buffer` is partitioned by day and auto-purged after 48 hours by a Hangfire daily job. **Never query this table for reporting** — use `activity_daily_summary` instead. See [[modules/activity-monitoring/overview|Activity Monitoring]].

- **Agent Authentication vs User Authentication:** Desktop agents use a separate device-level JWT (issued at registration). This is NOT the same as user JWT. Agent JWT contains `device_id` + `tenant_id` but NO user permissions. The `type: "agent"` claim distinguishes them. Employee context is established at login via the MAUI tray app → the Service calls `POST /api/v1/agent/session/login` which creates a server-side `agent_sessions` record (`device_id → employee_id`). The ingest endpoint validates `payload.employee_id` against this record for every batch — mismatch or missing session returns `403`. See [[modules/agent-gateway/data-collection|Data Collection — Employee-Device Binding]] and [[database/schemas/agent-gateway|Agent Gateway Schema]].

- **Monitoring Feature Toggles:** Always check `monitoring_feature_toggles` (tenant-level) and `employee_monitoring_overrides` (employee-level) before processing any monitoring data. The desktop agent checks its policy on login, but the **server must double-validate**. See [[modules/configuration/overview|Configuration]].

- **Screenshot Storage:** Screenshots are stored in blob storage (same as other files via `file_records`). Screenshot metadata in `screenshots` table has `file_record_id` FK. **Never store screenshots in the database.** Screenshots are classified as RESTRICTED data. See [[security/data-classification|Data Classification]].

- **Identity Verification Photos:** Verification photos are temporary — retained for configurable period (default 30 days) then auto-deleted by retention job. They are NOT the same as employee profile photos. See [[modules/identity-verification/overview|Identity Verification]].

- **Exception Engine Timing:** The exception engine only evaluates rules during configured work hours (`exception_schedules`). Off-hours activity data is still collected but does NOT trigger alerts. Always check the schedule first. See [[modules/exception-engine/overview|Exception Engine]].

- **Presence Session vs Device Session:** `presence_sessions` is ONE row per employee per day (unified from all sources). `device_sessions` can have MULTIPLE rows per day (one per laptop active/idle cycle). Don't confuse them — presence is the summary, device sessions are the raw source. See [[modules/workforce-presence/overview|Workforce Presence]].

- **Activity data can be empty:** If monitoring is disabled for a tenant or employee, activity endpoints return empty arrays, not errors. UI must handle "No monitoring data available" gracefully (frontend).

- **Screenshots are sensitive (frontend):** Only show to users with `workforce:view` permission. Never cache screenshots in browser storage.

- **Exception alerts are real-time:** Use SignalR, don't poll. Show toast notification + badge count. See [[modules/exception-engine/overview|Exception Engine]].

### Payroll

- **Payroll Pessimistic Locking:** Payroll runs use `SELECT FOR UPDATE` to prevent concurrent modifications. Never run payroll in parallel for the same tenant. Use Hangfire's distributed lock. See [[modules/payroll/overview|Payroll]].

- **Payroll Reads from Workforce Presence:** Payroll now reads actual worked hours from `IWorkforcePresenceService` (not just clock-in/out). This replaces the old Attendance dependency. See [[modules/payroll/overview|Payroll]].

### Workflow Engine

- **Workflow Engine is Generic:** The `workflow_definitions` / `workflow_instances` / `approval_actions` system is resource-type agnostic. It works via `resource_type` + `resource_id` polymorphic references. Same engine handles leave, overtime, document, expense approvals.

### Leave

- **Leave Policy Versioning:** `leave_policies` has a `superseded_by_id` column forming a chain. When querying the active policy, always get the one where `superseded_by_id IS NULL` for the given leave type + country + job level combination. See [[modules/leave/overview|Leave]].

### Frontend / API Integration

- **Cursor pagination:** Backend uses cursor-based pagination. Don't build offset-based pagination components.

- **RFC 7807 errors:** All API errors follow Problem Details format. Parse `title`, `detail`, and `errors` array consistently.

- **Access token in memory only** — lost on page refresh. Always implement silent refresh via HttpOnly cookie.

- **Permission array can be large** (90+ permissions). Cache in Zustand store, don't re-fetch on every route change.

- **Device JWT is NOT for frontend** — that's for the desktop agent. Frontend uses standard user JWT.

- **SignalR requires auth** — pass JWT as query param on connection (SignalR standard pattern).

- **Channel permissions** — `workforce-live` and `exception-alerts` channels require `workforce:view` permission. Server will reject unauthorized subscriptions.

- **Reconnection storms** — if server restarts, all clients reconnect simultaneously. Use jitter in reconnection delay.

- **Activity heatmap performance** — hourly intensity data can be up to 24 points per employee per day. For team views with 50+ employees, use server-side aggregation, not client-side computation.

- **Employee list with live status** — the live workforce dashboard shows status for all employees. Use SignalR push updates, not polling individual employee endpoints.

### Desktop Agent — Win32 API Hooks

- **`SetWindowsHookEx` for keyboard/mouse** — use `WH_KEYBOARD_LL` and `WH_MOUSE_LL` (low-level hooks). These work system-wide but require a message pump. The Windows Service must run a message loop on a dedicated thread.
- **Hook thread must be STA** — Win32 hooks require a Single-Threaded Apartment thread with `Application.Run()` or equivalent message loop.
- **Antivirus false positives** — keyboard hooks trigger some AV heuristics. MSIX signing with a trusted certificate mitigates this. Include exclusion documentation for IT teams.

### Desktop Agent — MAUI Tray App

- **MAUI doesn't natively support system tray** — use `CommunityToolkit.Maui` or `H.NotifyIcon.WinUI` for tray icon functionality.
- **MAUI app must NOT be the main entry point** — the Windows Service is the primary process. MAUI app launches separately and connects via Named Pipes.
- **Camera access** — requires `webcam` capability in `Package.appxmanifest`. User is prompted on first use.

### Desktop Agent — SQLite Buffer

- **WAL mode required** — use Write-Ahead Logging for concurrent read/write (Service writes, sync reads).
- **Buffer size limit** — if SQLite file exceeds 100MB, drop oldest unsent records. Log a warning.
- **Encryption** — use SQLCipher for data-at-rest encryption. Key derived from machine DPAPI.

### Desktop Agent — Network

- **Corporate proxies** — some companies route traffic through HTTP proxies. Agent must respect system proxy settings via `HttpClient.DefaultProxy`.
- **VPN disconnects** — common in remote work. Agent must handle sudden network loss gracefully (buffer locally).
- **Certificate pinning** — in production, pin to ONEVO's certificate to prevent MITM. In dev, allow self-signed.

### Desktop Agent — Device JWT

- **Token stored via DPAPI** — `ProtectedData.Protect()` with `DataProtectionScope.LocalMachine`. This means the token is tied to the machine, not the user.
- **Token refresh** — Device JWT has 24-hour expiry. Agent must refresh before expiry. If refresh fails (revoked), show error in tray app.
- **Multiple users on one machine** — edge case. Device is registered once, but different employees can log in/out. The `employee_id` changes on login, but `device_id` stays the same.

### Desktop Agent — Idle Detection

- **`GetLastInputInfo` quirk** — returns time since last keyboard/mouse input system-wide, NOT per-application. A user typing in Notepad counts as "active" even if they should be in Teams.
- **Screensaver/lock screen** — when the screen locks, `GetLastInputInfo` stops updating. Treat screen lock as idle.
- **Remote desktop** — RDP sessions have their own input state. Agent detects this via session change notifications (`WTSRegisterSessionNotification`).

### Desktop Agent — Meeting Detection

- **Phase 1: Process name matching only** — detect Teams.exe, zoom.exe, meet (Chrome tab — unreliable). This is basic and has false positives (Teams running in background ≠ in meeting).
- **Camera/mic detection** — check if camera/microphone devices are in use via Windows Multimedia API. Presence of camera activity during meeting app = likely in meeting.
- **Phase 2:** Microsoft Teams Graph API will provide accurate meeting data. See [[backend/external-integrations|External Integrations]].

### Desktop Agent — Installation

- **MSIX requires Windows 10 1809+** — older Windows versions not supported.
- **Auto-start** — Windows Service set to `Automatic (Delayed Start)`. MAUI app auto-starts via registry `Run` key for logged-in user.
- **Uninstall** — MSIX uninstall removes both Service and MAUI app. SQLite buffer and logs are cleaned up.
- **Updates** — MSIX supports auto-update from a URL. Agent checks for updates on heartbeat response.

---

## Technical Debt

| Area | Description | Impact | Planned Fix |
|:-----|:------------|:-------|:------------|
| - | No technical debt yet (greenfield project) | - | - |

---

## Deprecated Patterns

- **Don't use:** Direct `DbContext.Set<T>()` calls without `BaseRepository<T>` — bypasses tenant filtering
- **Don't use:** `throw new Exception()` for business logic — use `Result<T>` pattern
- **Don't use:** Synchronous database calls — always `async/await` with `CancellationToken`
- **Don't use:** `string` for IDs — always `Guid` (mapped to `uuid` in PostgreSQL)
- **Don't use:** `DateTime` — use `DateTimeOffset` for timestamps, `DateOnly` for dates, `TimeOnly` for times
- **Don't use:** "Attendance" as module name — it's now "WorkforcePresence" (see [[modules/workforce-presence/overview|Workforce Presence]])
- **Don't use:** Offset-based pagination — backend uses cursor-based pagination only
- **Don't use:** `useEffect` + `useState` for API calls in frontend — use TanStack Query

---

## Environment-Specific Issues

| Environment | Issue | Notes |
|:------------|:------|:------|
| Local dev | PostgreSQL RLS requires role setup | Use Docker Compose with pre-configured roles |
| Local dev | Redis required for rate limiting and caching | Redis container in Docker Compose |
| Railway | Connection string format differs from local | Use environment-specific appsettings |

## Related

- [[AI_CONTEXT/project-context|Project Context]]
- [[AI_CONTEXT/rules|Rules]]
- [[AI_CONTEXT/tech-stack|Tech Stack]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/shared-kernel|Shared Kernel]]
- [[modules/agent-gateway/overview|Agent Gateway]]
- [[security/auth-architecture|Auth Architecture]]
- [[modules/workforce-presence/overview|Workforce Presence]]
- [[modules/activity-monitoring/overview|Activity Monitoring]]
- [[modules/exception-engine/overview|Exception Engine]]
- [[modules/identity-verification/overview|Identity Verification]]
- [[modules/payroll/overview|Payroll]]
- [[modules/configuration/overview|Configuration]]
- [[security/data-classification|Data Classification]]
