# Known Issues & Gotchas: ONEVO

**Last Updated:** 2026-04-05

## Active Bugs

| ID | Description | Severity | Workaround | Status |
|:---|:------------|:---------|:-----------|:-------|
| - | No active bugs yet (project in initial development) | - | - | - |

## Gotchas & Non-Obvious Behaviors

Things that work differently than you'd expect. AI agents: pay attention to these before generating code.

### General

- **[[multi-tenancy|Multi-Tenancy]] Everywhere:** Every single query MUST be tenant-scoped. The `BaseRepository<T>` handles this via `ITenantContext` (see [[shared-kernel]]), but if you write raw SQL or use `DbContext` directly, you MUST include `WHERE tenant_id = @tenantId`. PostgreSQL RLS is a safety net, not a replacement for application-level filtering.

- **Employee vs User:** `users` is the login identity (authentication). `employees` is the HR identity (business data). They are 1:1 linked via `user_id`. When working with HR features, always query through `employees`, not `users`. The `employees` table is the central hub.

- **organisation_id vs tenant_id (RESOLVED):** Previously some tables used `organisation_id` instead of `tenant_id`. This has been fixed — all tables now use `tenant_id` consistently. No EF Core column mapping workarounds needed.

- **Snake Case in DB, PascalCase in C#:** Database uses `snake_case`. C# uses `PascalCase`. EF Core's `.UseSnakeCaseNamingConvention()` handles this automatically. Don't manually specify column names unless there's a mismatch.

- **Encrypted Fields:** These columns use `bytea` type and must be encrypted/decrypted at the application level (see [[data-classification]]): `account_number_encrypted` (employee_bank_details), `client_id_encrypted` / `client_secret_encrypted` (sso_providers), `api_key_encrypted` (biometric_devices, hardware_terminals), `credentials_encrypted` (integration_connections, notification_channels). Use `IEncryptionService` with AES-256.

- **JSONB Columns:** Several tables use JSONB for flexible data. Map these to typed C# classes using EF Core's JSONB support. See [[known-issues]] old list for full JSONB inventory.

- **Self-Referencing Tables:** `departments` (parent_department_id), `employees` (manager_id), `goals` (parent_goal_id), `document_categories` (parent_category_id), `leave_policies` (superseded_by_id), `refresh_tokens` (replaced_by_id). Handle recursive queries with CTEs.

### Workforce Intelligence (NEW)

- **Attendance → Workforce Presence Rename:** The old `Attendance` module no longer exists. It is now `Workforce Presence` (`ONEVO.Modules.WorkforcePresence`). All attendance-related tables remain but under this new namespace. References to "Attendance" in code should use "WorkforcePresence". See [[workforce-presence]].

- **Activity Data Volume:** `activity_snapshots` generates ~240 rows/employee/day (one every 2-3 min for 8 hours). For 500 employees = 120,000 rows/day. Use pg_partman monthly partitions. Always query with `tenant_id` + date range. See [[activity-monitoring]].

- **Raw Buffer Purge:** `activity_raw_buffer` is partitioned by day and auto-purged after 48 hours by a Hangfire daily job. **Never query this table for reporting** — use `activity_daily_summary` instead. See [[activity-monitoring]].

- **Agent Authentication vs User Authentication:** Desktop agents use a separate device-level JWT (issued at registration). This is NOT the same as user JWT. Agent JWT contains `device_id` + `tenant_id` but NO user permissions. The `type: "agent"` claim distinguishes them. Employee context is linked at login time via the MAUI tray app. See [[agent-gateway]] and [[auth-architecture]].

- **Monitoring Feature Toggles:** Always check `monitoring_feature_toggles` (tenant-level) and `employee_monitoring_overrides` (employee-level) before processing any monitoring data. The desktop agent checks its policy on login, but the **server must double-validate**. See [[configuration]].

- **Screenshot Storage:** Screenshots are stored in blob storage (same as other files via `file_records`). Screenshot metadata in `screenshots` table has `file_record_id` FK. **Never store screenshots in the database.** Screenshots are classified as RESTRICTED data. See [[data-classification]].

- **Identity Verification Photos:** Verification photos are temporary — retained for configurable period (default 30 days) then auto-deleted by retention job. They are NOT the same as employee profile photos. See [[identity-verification]].

- **Exception Engine Timing:** The exception engine only evaluates rules during configured work hours (`exception_schedules`). Off-hours activity data is still collected but does NOT trigger alerts. Always check the schedule first. See [[exception-engine]].

- **Presence Session vs Device Session:** `presence_sessions` is ONE row per employee per day (unified from all sources). `device_sessions` can have MULTIPLE rows per day (one per laptop active/idle cycle). Don't confuse them — presence is the summary, device sessions are the raw source. See [[workforce-presence]].

### Payroll

- **Payroll Pessimistic Locking:** Payroll runs use `SELECT FOR UPDATE` to prevent concurrent modifications. Never run payroll in parallel for the same tenant. Use Hangfire's distributed lock. See [[payroll]].

- **Payroll Reads from Workforce Presence:** Payroll now reads actual worked hours from `IWorkforcePresenceService` (not just clock-in/out). This replaces the old Attendance dependency. See [[payroll]].

### Workflow Engine

- **Workflow Engine is Generic:** The `workflow_definitions` / `workflow_instances` / `approval_actions` system is resource-type agnostic. It works via `resource_type` + `resource_id` polymorphic references. Same engine handles leave, overtime, document, expense approvals.

### Leave

- **Leave Policy Versioning:** `leave_policies` has a `superseded_by_id` column forming a chain. When querying the active policy, always get the one where `superseded_by_id IS NULL` for the given leave type + country + job level combination. See [[leave]].

## Technical Debt

| Area | Description | Impact | Planned Fix |
|:-----|:------------|:-------|:------------|
| - | No technical debt yet (greenfield project) | - | - |

## Deprecated Patterns

- **Don't use:** Direct `DbContext.Set<T>()` calls without `BaseRepository<T>` — bypasses tenant filtering
- **Don't use:** `throw new Exception()` for business logic — use `Result<T>` pattern
- **Don't use:** Synchronous database calls — always `async/await` with `CancellationToken`
- **Don't use:** `string` for IDs — always `Guid` (mapped to `uuid` in PostgreSQL)
- **Don't use:** `DateTime` — use `DateTimeOffset` for timestamps, `DateOnly` for dates, `TimeOnly` for times
- **Don't use:** "Attendance" as module name — it's now "WorkforcePresence"

## Environment-Specific Issues

| Environment | Issue | Notes |
|:------------|:------|:------|
| Local dev | PostgreSQL RLS requires role setup | Use Docker Compose with pre-configured roles |
| Local dev | Redis required for rate limiting and caching | Redis container in Docker Compose |
| Railway | Connection string format differs from local | Use environment-specific appsettings |
