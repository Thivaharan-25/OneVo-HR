# Audit Console

## Purpose

The Audit Console provides a read-only, cross-tenant view into the OneVo platform audit log. It is the primary tool for compliance investigation, security review, and support escalation where a full trail of user and system actions is required.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `audit_logs` (Auth module) | Read-only — no writes, no deletions |

## Capabilities

### Cross-Tenant Log Viewer
- View audit events across all tenants in a single interface
- Full filter set:
  - **Tenant** — scope to a single tenant
  - **User** — filter by specific user account
  - **Action** — filter by event type (e.g., `login`, `policy_update`, `agent_installed`)
  - **Resource** — filter by the affected resource type or ID
  - **Date range** — narrow to a specific window

### Export
- Export filtered results to CSV for offline analysis, compliance reporting, or handoff to legal/security teams

## Notes

- This module is **strictly read-only**. Audit records cannot be modified, deleted, or suppressed from this interface.
- Access to the Audit Console is itself audit-logged — developer account and query parameters are recorded.
- For cross-tenant queries on large date ranges, apply tenant and date filters first to avoid slow queries.
