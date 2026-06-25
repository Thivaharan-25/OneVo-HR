# Requests Center User Flow

## Purpose

Super Admin reviews demo/trial requests that require platform-side approval. Paid activation is customer self-service and does not enter Requests Center.

**Route:** `/platform/requests`

Requests Center route: `/platform/requests`.

---

## Tabs

| Tab | Purpose |
|---|---|
| Demo Requests | Review requests for demo/trial access |
| Trial Extension Requests | Review demo tenants requesting additional trial days |

---

## Permission Behavior

| Permission | Effect |
|---|---|
| `platform.requests.read` | View-only - request tables and detail pages are visible; approve/reject buttons are hidden |
| `platform.requests.manage` | Full access - approve/reject action buttons are visible and functional |

Accounts without `platform.requests.read` do not see the Requests Center sidebar item.

---

## Demo Requests Tab

### Table Columns

| Column | Description |
|---|---|
| Requester | Full name of the person who submitted the demo request |
| Email | Requester's email address |
| Company | Company name provided in the request |
| Requested Subdomain | Subdomain the requester wants for the demo tenant |
| Requested Demo Profile | Demo profile selected or requested by the applicant |
| Requested Modules | Modules the requester is interested in evaluating |
| Status | `pending_review`, `approved`, `rejected` |
| Submitted Date | Date the request was submitted |
| Reviewed By | Platform admin who approved/rejected (blank if pending) |
| Actions | "View" always; "Approve" / "Reject" visible only with `platform.requests.manage` |

### Demo Request Detail Page

| Section | Contents |
|---|---|
| Requester Details | Name, email, phone, company, role/title |
| Company Details | Company name, industry, size, website, subdomain requested |
| Requested Access | Demo profile, requested modules, access notes, requested duration |
| Duplicate / Request History | Previous requests from the same email or company domain, if any |
| Admin Notes | Internal-only notes added by platform admins (not visible to tenant) |
| Tenant-Visible Note | Note sent to the requester on approval/rejection |
| Audit History | Timeline of status changes, reviewer actions, timestamps |

### Demo Request Approval Modal

| Field | Type | Required | Notes |
|---|---|---|---|
| Selected Demo Profile | Dropdown (active demo profiles) | Yes | Determines tenant limits, modules, and trial duration |
| Admin Notes | Textarea | No | Internal-only - not sent to the requester |
| Tenant-Visible Message | Textarea | No | Included in the approval notification email to the requester |
| Confirm Button | "Approve & Create Demo Tenant" | - | Creates or updates the demo tenant with the selected profile |

### Demo Request Rejection Modal

| Field | Type | Required | Notes |
|---|---|---|---|
| Rejection Reason | Textarea | Yes | Internal record - stored in `demo_access_requests` |
| Tenant-Visible Note | Textarea | No | Included in the rejection notification email to the requester |
| Confirm Button | "Reject Request" | - | Sets status to `rejected`, notifies requester |

---

## Trial Extension Requests Tab

### Table Columns

| Column | Description |
|---|---|
| Tenant | Tenant name |
| Current Trial End | Current trial expiration date |
| Requested Days | Number of additional days requested |
| Requested By | Name of the tenant user who submitted the extension request |
| Usage Summary | Brief usage stats (active users, logins, modules used) |
| Status | `pending_review`, `approved`, `rejected` |
| Submitted Date | Date the extension was requested |
| Actions | "View" always; "Approve" / "Reject" visible only with `platform.requests.manage` |

### Trial Extension Detail Page

| Section | Contents |
|---|---|
| Tenant Summary | Tenant name, domain, demo profile, current plan |
| Trial Information | Trial start date, current end date, days remaining |
| Extension Request | Requested days, reason for extension, response-by date |
| Current Usage | Active users, login count, modules accessed, storage used |
| Admin Notes | Internal-only notes |
| Audit History | Timeline of status changes |

### Trial Extension Approval Modal

| Field | Type | Required | Notes |
|---|---|---|---|
| Approved Days | Number input | Yes | Number of days to extend - may differ from requested days |
| Admin Notes | Textarea | No | Internal-only |
| Tenant-Visible Note | Textarea | No | Included in the approval notification to the tenant |
| Confirm Button | "Approve Extension" | - | Updates trial end date |

### Trial Extension Rejection Modal

| Field | Type | Required | Notes |
|---|---|---|---|
| Rejection Reason | Textarea | Yes | Internal record |
| Tenant-Visible Note | Textarea | No | Included in the rejection notification to the tenant |
| Confirm Button | "Reject Extension" | - | Keeps original trial end date |

---

## UI States

| State | Behavior |
|---|---|
| Loading | Skeleton table rows with shimmer animation |
| Empty (no requests) | Centered illustration with "No {demo/trial extension} requests yet" message |
| Error (API failure) | Error banner above table with retry button |
| Read-only (`platform.requests.read` only) | Tables and detail pages render normally; approve/reject buttons are hidden; modals cannot be opened |
