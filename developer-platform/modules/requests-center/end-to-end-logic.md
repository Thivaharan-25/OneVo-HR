# Requests Center - End-to-End Logic

## Demo Requests

0. Applicant submits `POST /api/v1/demo/request`; backend validates anti-abuse controls, normalizes requester/company details, checks obvious duplicates, and inserts `demo_access_requests.status = pending_review`. This is inquiry intake only and does not create a tenant, user account, session, or entitlement.
1. Super Admin opens Requests Center -> Demo Requests.
2. Page lists rows from `demo_access_requests`: requester, email, company, requested subdomain, requested demo profile, requested modules, status, submitted date, reviewed by, and actions.
3. Super Admin opens a pending request.
4. Detail page shows requester details, company details, requested demo profile, requested modules, duplicate/request history, admin notes, tenant-visible note, and audit history.
5. Approve requires `platform.requests.manage`.
6. Approval modal:
   - Admin selects a demo profile from active Demo Profiles dropdown.
   - Optionally enters admin notes (internal-only) and a tenant-visible message.
   - Confirm action remains disabled until a demo profile is selected.
   - Clicks "Approve & Create Demo Tenant".
   - Backend validates requested access against selected Demo Profile.
   - Creates or updates the demo tenant.
   - Applies the selected demo profile limits.
   - Updates `demo_access_requests.status = approved`, sets `reviewed_by_id`, `reviewed_at`, and `created_tenant_id`.
   - Notifies the requester (includes tenant-visible message if provided).
   - Writes audit log.
7. Rejection modal:
   - Admin enters rejection reason (required).
   - Optionally enters a tenant-visible note.
   - Confirm action remains disabled until rejection reason is present.
   - Clicks "Reject Request".
   - Updates `demo_access_requests.status = rejected`, records rejection reason and tenant-visible note.
   - Notifies the requester (includes tenant-visible note if provided).
   - Writes audit log.
   - Does not create a tenant.

Paid activation is customer self-service. The customer enters company details, confirms employee count, selects an allowed plan/add-ons, receives an automatically generated first invoice based on the matching company-size range, pays, and then becomes active. That path does not enter Requests Center.

## Trial Extension Requests

1. Super Admin opens Requests Center -> Trial Extension Requests.
2. Page shows total requests, pending review, approved, near limit, and expired.
3. Table shows tenant, current trial end date, requested days, requested by, usage summary, status, submitted date, and actions.
4. Detail page shows tenant summary, trial information, extension reason, requested days, response-by date, and current usage.
5. Approval modal:
   - Admin enters approved extension days (required - may differ from requested days).
   - Optionally enters admin notes (internal-only) and a tenant-visible note.
   - Confirm action remains disabled until approved days is a positive number.
   - Clicks "Approve Extension".
   - Updates trial end date, notifies tenant, and writes audit log.
6. Rejection modal:
   - Admin enters rejection reason (required).
   - Optionally enters a tenant-visible note.
   - Confirm action remains disabled until rejection reason is present.
   - Clicks "Reject Extension".
   - Keeps original trial end date, notifies tenant, and writes audit log.
