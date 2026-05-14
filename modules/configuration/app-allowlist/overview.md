# App Allowlist Configuration

**Module:** Configuration
**Feature:** App Allowlist (Three-Tier)

---

## Purpose

Configurable application allowlist that defines which apps are permitted during work time. Follows the **hybrid permission model** — tenant sets defaults, roles can override, individual employees can have further overrides. Non-allowed app usage is logged and triggers exception alerts (NOT blocked).

App identities should come from the Developer Platform App Catalog wherever possible. The App Catalog can be seeded by ONEVO, bulk-approved from tenant observations, or created from a Super Admin/operator Tray App discovery session that captures currently running applications before tenant rollout.

## Three-Tier Model

```
Tenant Default (all employees)
  └── Role Override (per role — e.g., "Developer" gets IDE tools)
       └── Employee Override (per individual — e.g., John gets Figma)
```

**Resolution order (most specific wins per app name):**
1. Employee-level entry → use it
2. Role-level entry → use it
3. Tenant-level entry → use it
4. App not listed → depends on `allowlist_mode`:
   - `allowlist` mode: **not allowed** (flag it)
   - `blocklist` mode: **allowed** (only listed-as-blocked apps are flagged)

## Allowlist Modes

| Mode | Unlisted Apps | Use Case |
|:-----|:-------------|:---------|
| `allowlist` | Flagged as violation | Strict environments — only approved apps allowed |
| `blocklist` | Allowed | Permissive environments — only specific apps blocked |

Default: `allowlist` (configurable in `tenant_settings.settings_json`)

## Integration Points

### Agent Policy Distribution
When an admin changes the app allowlist, the resolved list for each affected employee is included in the agent policy:

```json
{
  "app_allowlist": {
    "mode": "allowlist",
    "apps": [
      { "name": "Microsoft Teams", "category": "communication", "is_allowed": true },
      { "name": "Visual Studio Code", "category": "development", "is_allowed": true }
    ],
    "alert_on_violation": true,
    "violation_threshold_minutes": 5
  }
}
```

The agent caches this allowlist locally. On policy change, agent-gateway sends `RefreshPolicy` command via SignalR.

### Activity Monitoring Integration
During activity data aggregation, each `app_usage` record is checked against the resolved allowlist. If an app is not allowed:
1. The usage is tagged with `is_allowed = false` in `application_usage` table
2. If cumulative non-allowed usage exceeds `violation_threshold_minutes`, a domain event is published
3. Exception engine evaluates and fires alert to reporting manager

### Exception Engine Integration
New rule type: `non_allowed_app_usage`

```json
{
  "rule_type": "non_allowed_app_usage",
  "threshold_json": {
    "max_minutes_per_day": 15,
    "max_consecutive_minutes": 5,
    "alert_severity": "medium"
  }
}
```

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/app-allowlist` | `monitoring:view-settings` | Tenant-level allowlist |
| POST | `/api/v1/settings/app-allowlist` | `monitoring:configure` | Add app to tenant list |
| PUT | `/api/v1/settings/app-allowlist/{id}` | `monitoring:configure` | Update entry |
| DELETE | `/api/v1/settings/app-allowlist/{id}` | `monitoring:configure` | Remove entry |
| GET | `/api/v1/settings/app-allowlist/role/{roleId}` | `monitoring:configure` | Role overrides |
| POST | `/api/v1/settings/app-allowlist/role/{roleId}` | `monitoring:configure` | Add role override |
| GET | `/api/v1/settings/app-allowlist/employee/{employeeId}` | `monitoring:configure` | Employee overrides |
| POST | `/api/v1/settings/app-allowlist/employee/{employeeId}` | `monitoring:configure` | Add employee override |
| GET | `/api/v1/settings/app-allowlist/resolved/{employeeId}` | `monitoring:view-settings` | Resolved (merged) list |

## Key Business Rules

1. **Non-allowed app usage is logged + alerted, NEVER blocked.** The system does not prevent employees from opening any application.
2. **Allowlist changes send `RefreshPolicy`** to all affected agents within 60 seconds.
3. **Role changes cascade.** If an employee's role changes, their resolved allowlist updates on next policy sync.
4. **Audit trail.** All allowlist changes are logged in `app_allowlist_audit` with who changed what and when.
5. **Categories are informational.** Category is for reporting grouping only — it doesn't affect allow/block logic.
6. **Process name is authoritative.** Matching should use the catalog/agent `process_name` case-insensitively. Display app name is metadata only.
7. **Templates use catalog identities.** App Allowlist Templates should reference catalog ids/process names and categories such as browser, communication/meeting, development, office/documentation, design, productivity, and other.

## Related

- [[modules/configuration/overview|Configuration Module]]
- [[modules/configuration/employee-overrides/overview|Employee Overrides]] — Same three-tier pattern for monitoring feature toggles
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]] — Includes resolved allowlist in agent policy
- [[modules/agent-gateway/remote-commands/overview|Remote Commands]] — Sends RefreshPolicy on allowlist change
- [[modules/activity-monitoring/overview|Activity Monitoring]] — Checks allowlist during app usage aggregation
- [[modules/exception-engine/overview|Exception Engine]] — `non_allowed_app_usage` rule type
