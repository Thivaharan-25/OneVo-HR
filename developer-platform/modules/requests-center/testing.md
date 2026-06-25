# Requests Center - Testing

## Required Tests

### Permission & Visibility
- Demo access requests require `platform.requests.read` to view.
- Accounts with `platform.requests.read` but not `platform.requests.manage` see tables and detail pages but approve/reject buttons are hidden.
- Read-only accounts cannot open approval or rejection modals.
- Approve/reject actions are visible only when the account has `platform.requests.manage`.
- Approval/rejection requires `platform.requests.manage`.

### Demo Request Flow
- `POST /api/v1/demo/request` creates a `demo_access_requests` row with `status = pending_review`.
- Demo access approval validates requested access against active Demo Profiles.
- Demo access approval creates or updates the demo tenant.
- Demo access approval applies the selected demo profile limits.
- Demo access approval sets `demo_access_requests.status = approved` and stores `created_tenant_id`.
- Demo access rejection sets `demo_access_requests.status = rejected` and does not create a tenant.
- Demo access rejection requires a rejection reason - submit is blocked if empty.
- Demo approval requires selected demo profile before submit.

### Demo Upgrade Flow
- Demo upgrade submit rejects plans not allowed by Demo Profile.
- Demo upgrade submit rejects add-ons not allowed by Demo Profile.
- Demo upgrade submit hides/rejects duplicate module charges.
- Demo upgrade submit calculates shared storage and AI allowance from base plan plus selected add-ons.
- Demo upgrade submit generates the first invoice from the confirmed employee count/company-size bracket.

### Trial Extension Flow
- Trial extension request approval updates trial end date.
- Trial extension approval requires approved days - submit is blocked if empty or zero.
- Trial extension approval rejects negative or non-numeric approved days.
- Approved days may differ from requested days.
- Trial extension rejection keeps original trial end date.
- Trial extension rejection requires a rejection reason - submit is blocked if empty.

### Status Transitions
- Demo request: `pending_review` -> `approved` or `pending_review` -> `rejected`. No other transitions allowed.
- Trial extension: `pending_review` -> `approved` or `pending_review` -> `rejected`. No other transitions allowed.

### Audit & Notifications
- Every approval or rejection writes an audit log entry.
- Every approval or rejection sends a tenant notification.
- Tenant-visible notes are included in notification emails when provided.
