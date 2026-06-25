# Requests Center

## Purpose

Requests Center is the Super Admin queue for demo/trial requests that require platform-side review. Paid activation is not approved here; customers self-activate by entering company details, confirming employee count, selecting an allowed plan/add-ons, receiving the first invoice, and paying it.

## Tabs

| Tab | Purpose |
|---|---|
| Demo Requests | Review requests for demo/trial access |
| Trial Extension Requests | Review demo tenants requesting additional trial days |

## Storage

| Queue | Table | Notes |
|---|---|---|
| Demo Requests | `demo_access_requests` | Public demo inquiry requests only; submission does not create a tenant/account. Approval creates or updates the demo tenant and links `created_tenant_id`. |
| Trial Extension Requests | `trial_extension_requests` | Existing demo tenant requests for additional trial days. |

## Permissions

| Action | Permission |
|---|---|
| View requests | `platform.requests.read` |
| Approve/reject demo access or trial extension | `platform.requests.manage` |

Customer Support is a separate sidebar item and module. It may link to a tenant request context, but support tickets are not a Requests Center tab.

## UI Surfaces

| Surface | Route | Description |
|---|---|---|
| Requests Center list | `/platform/requests` | Tabbed view - Demo Requests and Trial Extension Requests tables |
| Demo Request detail | `/platform/requests/demo/{id}` | Requester/company details, requested access, duplicate history, admin notes, audit history |
| Trial Extension detail | `/platform/requests/trial-extensions/{id}` | Tenant summary, trial info, extension reason, usage stats, audit history |
| Approval modal (demo) | Dialog on detail page | Selected demo profile, admin notes, tenant-visible message, confirm button |
| Rejection modal (demo) | Dialog on detail page | Rejection reason (required), tenant-visible note, confirm button |
| Approval modal (trial extension) | Dialog on detail page | Approved days (required), admin notes, tenant-visible note, confirm button |
| Rejection modal (trial extension) | Dialog on detail page | Rejection reason (required), tenant-visible note, confirm button |
| Loading state | `/platform/requests` | Skeleton rows while request tables load |
| Empty state | `/platform/requests` | Per-tab empty message when there are no demo or trial extension requests |
| Error state | `/platform/requests` | Error banner with retry action when the API fails |

Read-only state: accounts with `platform.requests.read` but not `platform.requests.manage` see all tables and detail pages but approve/reject buttons are hidden and modals cannot be opened.
