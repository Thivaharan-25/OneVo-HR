# Tenant Management - End-to-End Logic

## Purpose

Tenant Management is the central management screen for all tenant organizations. Operators use it to find tenants, inspect their status, view usage, manage subscriptions, suspend or unsuspend access, impersonate tenant admins for support, and configure all tenant-level settings after initial provisioning.

**Entry:** Platform Management -> Tenants (sidebar)
**Route:** `/platform/tenants`

---

## Tenant List Screen

### Page Header

| Element | Description |
|---|---|
| Page title | "Tenant Directory" |
| Page subtitle | "View and manage all tenant organizations on the OneVo platform." |
| Create button | `+ Create Tenant` - top-right, visible only to accounts with `platform.tenants.create`; hidden (not disabled) when permission absent |
| More options | `...` kebab button - top-right next to Create - options: Export Tenant List (CSV), Bulk Status Change (requires confirmation) |

### KPI Summary Row (4 cards)

Displayed at the top of the list before the filter bar.

| Card | Metric | Definition | Color |
|---|---|---|---|
| Total Tenants | Count of all non-cancelled tenants | `COUNT(*) WHERE status != 'cancelled'` | Neutral |
| Active Tenants | Count with `status = 'active'` | Shown with percentage: "92.19%" of total | Green |
| Suspended Tenants | Count with `status = 'suspended'` | Shown with percentage: "5.47%" of total | Orange |
| Inactive / Pending Tenants | Count with status IN ('provisioning', 'trial_expired', 'pending_payment') | 2.34% of total | Gray |
| Total Users | Sum of active user counts across all tenants | Cross-tenant aggregate | Blue |

### Filter Bar

Positioned between KPI cards and the tenants table.

| Control | Type | Options | Behavior |
|---|---|---|---|
| Search | Text input | Searches tenant name, domain, tenant code | Debounced 300ms, calls `GET /admin/v1/tenants?search={q}` |
| Status | Dropdown | All, Active, Trial, Trial Expired, Suspended, Provisioning, Pending Payment, Cancelled | Adds `?status={value}` to API call |
| Subscription Plan | Dropdown | All + each plan name from plan catalog | Adds `?plan_id={id}` |
| Work Mode | Dropdown | All, Hybrid, Remote, On-site | Adds `?work_mode={value}` |
| Region | Dropdown | All + ISO country codes with flag + name | Adds `?country={code}` |
| Filters button | Opens advanced filter drawer | Additional filters: Created date range, estimated employee count, Has suspended users, Has active alerts | |
| Clear button | Resets all filters | Clears search and all dropdowns to "All" | |

### Tenants Table

**API:** `GET /admin/v1/tenants?{filter_params}&page={n}&per_page={n}&sort={field}&order={asc|desc}`

**Columns:**

| Column | Label | Sortable | Width | Description |
|---|---|---|---|---|
| Checkbox | (no label) | No | 40px | Multi-select for bulk actions |
| Avatar + Name | "Tenant Name <->" | Yes, default sort | Flexible | Two-letter initials avatar with tenant color, company name (bold), plan tier label below |
| Tenant ID | "Tenant ID" | Yes | 120px | `TEN-XXXXXX` format |
| Domain | "Domain" | Yes | 160px | Primary domain |
| Plan | "Subscription Plan" | Yes | 130px | Colored badge: Enterprise (dark blue), Business (medium blue), Professional (light blue), Custom (gray) |
| Users | "Users" | Yes | 70px | Total user count for this tenant |
| Status | "Status <->" | Yes | 120px | Colored badge - see Status Badge Logic below |
| Work Mode | "Work Mode" | Yes | 110px | Text label: Hybrid, Remote, On-site |
| Region | "Region" | Yes | 90px | Country flag emoji + ISO country code |
| Created | "Created On <->" | Yes | 120px | "May 12, 2024" format |
| Actions | "Actions" | No | 80px | Eye icon (view) + `...` kebab |

### Status Badge Logic

| Badge | Color | When Applied |
|---|---|---|
| Active | Green dot + "Active" | `status = 'active'` |
| Suspended | Orange dot + "Suspended" | `status = 'suspended'` |
| In Progress | Yellow dot + "In Progress" | `status = 'provisioning'` - creation wizard not complete |
| Trial | Purple dot + "Trial" | `status = 'trial'` - active demo tenant using a Demo Profile |
| Trial Expired | Red dot + "Trial Expired" | `status = 'trial_expired'` - demo access expired or manually expired |
| Pending Payment | Blue dot + "Pending Payment" | `status = 'pending_payment'` after tenant owner confirms plan and invoice is open |
| Cancelled | Gray dot + "Cancelled" | `status = 'cancelled'` |

### Row Actions (kebab ...)

| Action | Permission Required | Behavior |
|---|---|---|
| View Details | `platform.tenants.read` | Navigates to `/platform/tenants/{id}` |
| Edit Profile | `platform.tenants.manage` | Opens edit drawer for company name, legal name, phone, website |
| Suspend | `platform.tenants.suspend` | Opens confirmation dialog - see Suspend flow |
| Impersonate | `platform.tenants.impersonate` | Opens impersonation dialog - see Impersonation flow |
| Export Tenant Data | `platform.tenants.read` | Downloads tenant data summary as CSV |

### Bulk Actions (multi-select)

When one or more checkboxes are selected, a bulk action toolbar appears above the table:

| Action | Permission Required | Behavior |
|---|---|---|
| Suspend Selected | `platform.tenants.suspend` | Confirmation dialog listing affected tenants -> confirms suspension of all selected |
| Export Selected | `platform.tenants.read` | Downloads CSV of selected tenants |
| Assign to Ring | *(Phase 2)* `platform.agent_versions.manage` | Assigns selected tenants to a deployment ring |

**Bulk suspend confirmation:** "You are about to suspend {N} tenants. All users in these tenants will lose access immediately. This cannot be undone without explicitly unsuspending each tenant. Type CONFIRM to proceed."

### Pagination

| Control | Behavior |
|---|---|
| Rows per page | Dropdown: 10, 25, 50, 100 - stored in user preference |
| Page controls | First, Previous, numbered pages, Next, Last |
| Count label | "Showing 1 to 8 of 128 tenants" |

---

## Tenant Detail Screen

**Route:** `/platform/tenants/{id}`

**Access:** Click any tenant row, or the eye icon in Actions column.

**API on load:** `GET /admin/v1/tenants/{id}` - returns full tenant profile, subscription state, module entitlements, user count, device count, provisioning state, active alert count.

### Header Section

| Element | Description |
|---|---|
| Back link | "Back to Tenant Directory" - navigates to `/platform/tenants` |
| Page title | "Tenant Details" |
| Actions button | "Actions v" dropdown button (top-right) - contains all high-risk actions for this tenant |
| More options | `...` next to Actions button |

**Tenant Identity Card (below header):**

| Field | Display |
|---|---|
| Avatar | Two-letter initials, colored |
| Company name | Large bold text |
| Status badge | Colored badge - see Status Badge Logic |
| Plan label | "Enterprise Plan" with colored badge |
| Tenant code | "TEN-000001" |
| Domain | "technova.com" |
| Location | Country flag + country name |
| Customer since | "Customer since May 12, 2024" |
| Primary Admin | Name + email with avatar |
| Subscription Plan | Plan name + "Manage Plan" link |
| Billing Cycle | "Monthly - Next billing: Jun 12, 2025" |
| Status summary | "Active - All systems normal" or alert count if alerts exist |

### Actions Dropdown Contents

| Action | Permission | When Enabled |
|---|---|---|
| Suspend Tenant | `platform.tenants.suspend` | Status = active |
| Unsuspend Tenant | `platform.tenants.suspend` | Status = suspended |
| Cancel Tenant | `platform.tenants.suspend` | Status = active or suspended; irreversible |
| Impersonate as Admin | `platform.tenants.impersonate` | Status = active |
| Override Subscription | `platform.subscriptions.manage` | Any status |
| Send Owner Invite | `platform.tenants.manage` | Status = provisioning or active |
| View Audit Trail | `platform.audit.read` | Any status |
| Export Tenant Data | `platform.tenants.read` | Any status |

---

## Tenant Detail Tabs

### Tab 1 - Overview

Default tab on page load.

**Section: Activity Summary (6 KPI mini-cards in a row)**

| Card | Metric | Definition |
|---|---|---|
| Total Users | User count | All users in `users` table for this tenant |
| Active Users (Today) | Users active today | Users with API call or login in last 24h |
| Registered Devices | Device count | All `devices` rows with `tenant_id` |
| Active Devices (Today) | Devices active today | Devices with heartbeat in last 24h |
| Data Storage Used | Storage in GB/TB | Sum of data in tenant's storage allocation |
| Platform Health | Health % | Same calculation as global but scoped to this tenant's services |

**Section: User Activity Overview (line chart)**
- Y-axis: User count
- X-axis: Time (last 30 days, daily resolution)
- Three lines: Active Users (blue), Idle Users (yellow), Inactive Users (red)
- Below chart: Average Daily Active Users, Peak Active Users (date + time), Average Session Duration, Average Focus Time
- API: `GET /admin/v1/tenants/{id}/user-activity-timeseries?from=...&to=...`

**Section: Work Mode Distribution (donut chart)**
- Segments: Remote (%), Hybrid (%), On-site (%)
- Centre: Total users count
- Values from `users.work_mode` distribution for this tenant

**Section: Subscription & Limits (right panel)**
| Metric | Display | Progress bar |
|---|---|---|
| User Seats | "3,842 / 10,000" | Filled %, changes yellow > 80%, red > 95% |
| Data Storage | "1.24 TB / 5 TB" | Same threshold logic |
| Devices | "4,758 / 15,000" | Same threshold logic |
| API Calls (Monthly) | "2.31M / 10M" | Same threshold logic |

**Section: Recent Alerts (3 rows)**
Shows the 3 most recent active alerts for this specific tenant.

| Column | Description |
|---|---|
| Severity icon | Triangle (warning), Circle-X (critical), Circle-i (info) |
| Alert description | e.g., "High idle time detected for multiple users" |
| Timestamp | e.g., "May 20, 2025 10:15 AM" |
| Badge | Warning / Critical / Info colored badge |

"View All Alerts" link -> navigates to Security Center filtered to this tenant.

**Section: Top Departments by Activity (bar chart)**
Horizontal bar chart showing top 5 departments ranked by user activity count.

| Column | Description |
|---|---|
| Department name | e.g., "Engineering" |
| User count | Number of active users in department |
| Percentage | Of total active users |

API: `GET /admin/v1/tenants/{id}/department-activity?limit=5`

**Section: Integrations Status**
List of configured integrations with connection status badge.

| Column | Description |
|---|---|
| Integration logo | Icon |
| Integration name | e.g., "Microsoft 365", "Azure AD (SSO)", "Biometric System" |
| Status | Green dot "Connected" / Red dot "Error" / Gray dot "Disconnected" |
| "Manage Integrations" link | Navigates to Integrations tab |

---

### Tab 2 - Usage & Analytics

**API:** `GET /admin/v1/tenants/{id}/analytics?from=...&to=...`

**Time range selector** at top-right of tab: Last 7 Days / Last 30 Days / Last 90 Days / Custom range.

**Sections:**

| Section | Chart Type | Metrics |
|---|---|---|
| Daily Active Users trend | Line chart | DAU per day |
| Session Duration Distribution | Histogram | Minutes per session, binned |
| Feature Usage Breakdown | Horizontal bar | Top 10 features by usage event count |
| Module Engagement | Heatmap | Day x hour grid of activity intensity |
| Device Activity | Stacked bar | Online / Idle / Offline by day |
| Exception Events | Line chart | Exception rule fires per day |

Each section has: title, "View Full Report" link -> Reports / Analytics, and export icon.

---

### Tab 3 - Users

**API:** `GET /admin/v1/tenants/{id}/users?{filters}&page={n}&per_page={n}`

**This tab is read-only.** Operators cannot create, edit, or delete tenant users from this console - user management belongs to the tenant's own HR Admin.

**Columns:**

| Column | Description |
|---|---|
| Avatar + Name | User initials, first name, last name |
| Email | User email address |
| Role | Assigned role(s) - comma-separated if multiple |
| Status | Active (green), Invited (yellow), Suspended (orange), Deactivated (gray) |
| Work Mode | Hybrid / Remote / On-site |
| Department | Org department assignment |
| Last Login | Relative time, e.g., "2 hours ago" or "Never" |
| Actions | Eye icon: view user detail (read-only) |

**Filters:**
| Filter | Options |
|---|---|
| Search | Name or email |
| Status | All / Active / Invited / Suspended / Deactivated |
| Role | All + each role name in this tenant |
| Department | All + each department in this tenant |

---

### Tab 4 - Devices

**API:** `GET /admin/v1/tenants/{id}/devices?{filters}&page={n}&per_page={n}`

**Read-only.** Operators can view device state; device deregistration must go through DeviceManagement module with explicit permission.

**Columns:**

| Column | Description |
|---|---|
| Device name | Hostname from agent registration |
| Device ID | Internal device UUID |
| OS | Operating system + version |
| Agent Version | *(Phase 2)* Installed agent version with badge: Up to date (green) / Outdated (orange) / Unsupported (red) |
| Status | Online (green) / Idle (yellow) / Offline (gray) |
| Assigned User | User assigned to this device |
| Last Seen | Relative timestamp of last heartbeat |
| Deployment Ring | Internal / Beta / GA |

**Filters:**
| Filter | Options |
|---|---|
| Search | Device name or ID |
| Status | All / Online / Idle / Offline |
| Agent Version | *(Phase 2)* All / Up to date / Outdated / Unsupported |
| Deployment Ring | *(Phase 2)* All / Internal / Beta / GA |

---

### Tab 5 - Subscriptions

**API:** `GET /admin/v1/tenants/{id}/subscription`

**Section: Current Plan**

| Field | Displayed Value |
|---|---|
| Plan name | e.g., "Enterprise" |
| Commercial model | Subscription or Full License + Maintenance |
| Billing cycle | Monthly / Annual |
| Calculated price | e.g., "GBP 4,200 / month" |
| Override price | If set: "GBP 3,800 / month (overridden)" in orange |
| Payment gateway | "Stripe - Production" / "Paddle - Production" / "PayHere - Production" |
| Billing start date | "Jun 1, 2024" |
| Next billing date | "Jun 1, 2025" |
| AI token limit | "500,000 / month" |
| Storage limit | "5 TB" |
| Payment status | Paid / Overdue (red) / Grace Period / Excepted |

**Section: Module Entitlements Table**

| Column | Description |
|---|---|
| Module name | Full name, e.g., "Time Off Management" |
| Pillar | HR / Monitoring / WorkSync badge |
| Status | Active (green), Available (gray), Disabled (gray) |
| Sales state | purchased / subscription_included / quoted / available / disabled |
| Expiry date | If applicable for a fixed-term purchased entitlement |
| Actions | Toggle module (requires `platform.tenants.manage`) |

**Section: Invoices Table**

| Column | Description |
|---|---|
| Invoice number | Linked to download PDF |
| Period | "May 2025" |
| Amount | Formatted currency |
| Status | Paid (green) / Overdue (red) / Draft (gray) / Void (gray) |
| Issued date | Date |
| Paid date | Date or "-" |
| Actions | Download PDF, View payment details |

**Override Subscription action** (in Actions dropdown):
- Opens a form overlay on this tab
- All fields from Step 3 subscription wizard are editable
- Reason field required (min 20 characters)
- Submit calls `PATCH /admin/v1/tenants/{id}/subscription`
- Audit log entry created

---

### Tab 6 - Runtime Overrides & Policies

**API:** `GET /admin/v1/tenants/{id}/feature-flags` and `GET /admin/v1/global-policies?tenant_id={id}`

**Section: Runtime / Feature Flag Overrides**

Table of feature flags available for this tenant and all active per-tenant overrides. Shows flag name, global default, this tenant's override, entitlement validation status, last changed by, and last changed at. "Add Override" opens a side panel. This is the canonical UI for feature flag overrides; Feature Flags is not a top-level sidebar item.

**Section: Global Policy Overrides**

Table of all global policies where this tenant has a non-default value. Shows policy name, global value, this tenant's override, reason, set by.

---

### Tab 7 - Integrations

**API:** `GET /admin/v1/tenants/{id}/integrations`

Lists all integrations visible to this tenant based on their entitled modules.

| Column | Description |
|---|---|
| Integration | Logo + name |
| Module | Which ONEVO module enables this integration |
| Status | Connected / Error / Disconnected / Not configured |
| Connected since | Date if connected |
| Last sync | Relative time of last successful sync |
| Actions | View config (read-only), Disconnect (requires `platform.tenants.manage`) |

**Integration status detail:** Clicking any integration row opens a side panel showing:
- Connection health
- Last error message if Status = Error
- Sync history (last 5 sync events with timestamp and status)
- Configuration reference (no secrets shown)

---

### Tab 8 - Activity Log

**API:** `GET /admin/v1/tenants/{id}/audit?{filters}&page={n}&per_page={n}`

Read-only audit log for all events affecting this specific tenant, across all actors (tenant users, platform admins, system events).

**Columns:**

| Column | Description |
|---|---|
| Timestamp | Full datetime, sortable |
| Actor | Name + type badge: Tenant User / Platform Admin / System |
| Action | Human-readable description, e.g., "User invited", "Plan changed", "Agent suspended" |
| Resource | What was affected - entity type + name |
| IP Address | Source IP |
| Result | Success (green) / Failed (red) |

**Filters:**
| Filter | Options |
|---|---|
| Search | Free text on actor name or action description |
| Date range | Date picker (from / to) |
| Actor type | All / Tenant User / Platform Admin / System |
| Action category | All / Auth / Users / Billing / Settings / Devices / Integrations |
| Result | All / Success / Failed |

---

### Tab 9 - Settings

**API:** `GET /admin/v1/tenants/{id}/settings` (read), `PATCH /admin/v1/tenants/{id}/settings` (write - requires `platform.tenants.manage`)

**Section: Organization Profile**

Editable fields: Company name, Legal company name, Phone number, Website, Company description. Domain is read-only after activation (cannot be changed without manual process).

Each field shows current value, edit icon, saved/error state.

**Section: Operational Settings**

| Setting | Field | Editable | Notes |
|---|---|---|---|
| Primary timezone | Dropdown | Yes | |
| Reporting currency | Dropdown | Yes | |
| Date format | Radio | Yes | |
| Work mode | Radio | Yes | |
| Time Off year start month | Dropdown | Yes | |

**Section: Monitoring Configuration** (shown only if monitoring modules entitled)

| Setting | Field | Editable |
|---|---|---|
| Transparency mode | Radio | Yes |
| Agent visibility | Radio | Yes |
| App usage collection | Toggle | Yes |
| Screenshot capture | Toggle | Yes |
| Input counting | Toggle | Yes |

**Section: Branding** (Phase 2)
White-label branding overrides - planned for Phase 2.

**Save behavior:** Each section has its own "Save Changes" button. Saving calls `PATCH /admin/v1/tenants/{id}/settings` with only the changed section's fields. Each save writes an audit log entry.

---

## Tenant Status Lifecycle - State Machine

```
```
Operator provisioning wizard
  -> PROVISIONING (status = provisioning)
  -> PENDING_PAYMENT (status = pending_payment, first invoice open)
  -> ACTIVE (status = active, invoice paid through configured gateway)

Demo profile flow
  -> TRIAL (status = trial, demo profile applied)
  -> PENDING_PAYMENT (status = pending_payment, self-service upgrade submitted and first invoice open)
  -> ACTIVE (status = active, invoice paid through configured gateway)

Trial expiry path
  -> TRIAL_EXPIRED (status = trial_expired, demo access blocked)
  -> SUSPENDED (status = suspended, payment failure or operator action)
  -> CANCELLED (status = cancelled)
```

### Transition Rules

| From -> To | Endpoint | Permission | Side Effects |
|---|---|---|---|
| provisioning -> pending_payment | `PATCH /admin/v1/tenants/{id}/provision/confirm` | `platform.tenants.activate` | First invoice/payment state is created; tenant remains payment-limited |
| trial -> pending_payment | `POST /api/v1/demo/upgrade/submit` | `billing:manage` | Tenant owner selects allowed plan/add-ons, billing cycle, confirms employee count and billing contact; first invoice is generated from the matching company-size price bracket |
| pending_payment -> active | Gateway webhook | system | Invoice paid through configured gateway; module entitlements become active |
| trial -> trial_expired | Trial expiry job or `PATCH /admin/v1/tenants/{id}/trial/expire` | job or `platform.tenants.manage` | Demo access is blocked and audit/history is written |
| trial_expired -> trial | `PATCH /admin/v1/tenants/{id}/trial/extend` | `platform.tenants.manage` | Trial end date is extended, limits remain governed by Demo Profile unless overridden |
| active -> suspended | `PATCH /admin/v1/tenants/{id}/status` `{"status":"suspended"}` | `platform.tenants.suspend` | All tenant user sessions invalidated immediately; tenant invisible to `/api/v1/*` except admin; audit log entry |
| suspended -> active | `PATCH /admin/v1/tenants/{id}/status` `{"status":"active"}` | `platform.tenants.suspend` | Tenant becomes visible again; audit log entry |
| active/suspended -> cancelled | `PATCH /admin/v1/tenants/{id}/status` `{"status":"cancelled"}` | `platform.tenants.suspend` + separate `platform.tenants.cancel` | Irreversible in normal flow; data preserved for retention period; billing stopped; all sessions invalidated; audit log entry |

---

## Suspend Flow - Full Detail

### Trigger

Actions dropdown -> "Suspend Tenant"

### Confirmation Dialog

| Element | Value |
|---|---|
| Dialog title | "Suspend Tenant" |
| Body text | "Suspending TechNova Solutions will immediately revoke access for all 3,842 users. The tenant's data is preserved. You can unsuspend at any time." |
| Confirmation input | Text field: "Type the tenant domain to confirm: technova.com" |
| Validation | Must exactly match tenant domain - case-insensitive |
| Reason field | Textarea - "Reason for suspension (required)" - min 10 characters |
| Cancel button | Closes dialog, no action |
| Confirm button | Disabled until domain typed correctly AND reason filled; enabled when both pass |

### API Call

**Endpoint:** `PATCH /admin/v1/tenants/{id}/status`

**Request body:**
```json
{
  "status": "suspended",
  "reason": "Non-payment after 3 failed billing attempts. Commercial decision approved by Head of Operations."
}
```

**Response (200 OK):**
```json
{
  "tenant_id": "...",
  "previous_status": "active",
  "new_status": "suspended",
  "suspended_at": "2025-05-20T14:32:00Z",
  "sessions_invalidated": 142
}
```

**Side effects:**
- All active tenant user sessions invalidated (JWT blocklist or session table purge depending on implementation)
- `tenants.status` -> `'suspended'`
- Status badge on list and detail page -> orange "Suspended"
- Tenant removed from all `/api/v1/*` query results
- Audit log: `action = 'tenant.suspended'`, actor, reason, timestamp, previous status
- If tenant has active Paddle subscription: subscription collection paused (via Paddle API call if gateway = paddle)

**Toast on success:** "TechNova Solutions has been suspended. 142 active sessions have been invalidated."

---

## Unsuspend Flow - Full Detail

### Trigger

Actions dropdown -> "Unsuspend Tenant" (only visible when status = suspended)

### Confirmation Dialog

| Element | Value |
|---|---|
| Dialog title | "Unsuspend Tenant" |
| Body text | "Restoring access for TechNova Solutions. Users will be able to log in immediately after confirmation." |
| No slug confirmation | Not required for unsuspend - lower risk action |
| Note field | Optional text: "Internal note for audit log" |
| Confirm button | Always enabled - no input required |

### API Call

**Endpoint:** `PATCH /admin/v1/tenants/{id}/status`

**Request body:**
```json
{
  "status": "active",
  "reason": "Payment dispute resolved. Billing confirmed current."
}
```

**Response (200 OK):**
```json
{
  "tenant_id": "...",
  "previous_status": "suspended",
  "new_status": "active",
  "unsuspended_at": "2025-05-20T16:00:00Z"
}
```

**Toast:** "TechNova Solutions has been reactivated."

---

## Impersonation Flow - Full Detail

### Trigger

Actions dropdown -> "Impersonate as Admin" (visible only when status = active and account has `platform.tenants.impersonate`)

### Confirmation Dialog

| Element | Value |
|---|---|
| Dialog title | "Impersonate Tenant Admin" |
| Warning banner | Red callout: "This action is audit-logged with your account, IP address, and timestamp. The session cannot be extended. You will be opening the main OneVo app as the tenant's super-admin role." |
| Tenant shown | TechNova Solutions |
| Target user field | Dropdown: "Select user to impersonate" - lists all admin-role users for this tenant with name + email |
| Reason field | Required, min 20 characters - "Reason for impersonation (required for compliance audit)" |
| Session duration | Read-only display: "Session TTL: 15 minutes - not renewable" |
| Cancel button | Closes dialog |
| Confirm button | Enabled only when user selected and reason filled |

### API Call

**Endpoint:** `POST /admin/v1/tenants/{id}/impersonate`

**Request body:**
```json
{
  "target_user_id": "user-uuid-...",
  "reason": "Customer reported they cannot see their Time Off balance. Investigating configuration issue before call."
}
```

**Response (200 OK):**
```json
{
  "impersonation_token": "eyJ...",
  "expires_at": "2025-05-20T14:47:00Z",
  "target_tenant_id": "...",
  "target_user_id": "...",
  "audit_log_id": "..."
}
```

**Frontend behavior after success:**
- New browser tab opens to `app.onevo.io/impersonate?token={impersonation_token}`
- Main OneVo app validates the token and opens the session with `"impersonation": true` claim
- A persistent yellow banner appears at the top of the tenant app: "WARNING: Impersonation Session - Platform Admin: engineer@onevo.io - Expires in 15:00" with countdown timer
- Console tab shows: "Impersonation session opened. Tab closes automatically in 15 minutes." with a countdown
- When token expires: tenant app tab redirects to a "Session Expired" page; console tab shows "Impersonation session ended."

**Audit log entry:**
```json
{
  "action": "tenant.impersonated",
  "actor_type": "platform_admin",
  "actor_id": "platform-account-uuid",
  "target_tenant_id": "...",
  "target_user_id": "...",
  "reason": "...",
  "source_ip": "82.45.12.99",
  "session_start": "2025-05-20T14:32:00Z",
  "session_expiry": "2025-05-20T14:47:00Z"
}
```

**Constraints enforced server-side:**
- Token TTL = 900 seconds (15 minutes). Hard-coded. No parameter can change this.
- Token is not renewable. Calling the endpoint again issues a new independent token - each is audit-logged separately.
- Token carries `impersonation: true` claim. The tenant `/api/v1/*` middleware accepts it only at endpoints tagged `[AllowImpersonation]`. Admin endpoints reject it.
- If account lacks `platform.tenants.impersonate`: `403 Forbidden` with code `impersonation_permission_required`.

---

## Send Owner Invite Flow

### Trigger

Actions dropdown -> "Send Owner Invite" - available when:
- Status = provisioning and Step 2 admin account has been set but invite not yet sent
- Status = active and operator wants to re-invite (e.g., invite link expired)

### Dialog

| Element | Value |
|---|---|
| Title | "Send Owner Invite" |
| Display | Shows admin name + email from Step 2 |
| Note | "An invitation email will be sent to james.anderson@technova.com with a link to set their password. The link expires in 72 hours." |
| Send button | Calls `POST /admin/v1/tenants/{id}/invite-admin` |

### API Call

**Endpoint:** `POST /admin/v1/tenants/{id}/invite-admin`

**Request body:**
```json
{
  "resend": true
}
```

**Response (200 OK):**
```json
{
  "invite_sent_at": "2025-05-20T14:00:00Z",
  "invite_expires_at": "2025-05-23T14:00:00Z",
  "recipient_email": "james.anderson@technova.com"
}
```

**State written:**
- `users.invite_sent_at` updated
- `users.invite_expires_at` = `invite_sent_at + 72 hours`
- Audit log: `action = 'tenant.invite_sent'`

**Rule:** If a previous invite has not expired, sending again invalidates the old token and issues a new one. Only one active invite token per user at a time.

---

## API Surface - Full Catalog

| Method | Route | Purpose | Permission | Notes |
|---|---|---|---|---|
| GET | `/admin/v1/tenants` | List tenants with filters | `platform.tenants.read` | Supports `search`, `status`, `plan_id`, `country`, `work_mode`, `page`, `per_page`, `sort`, `order` |
| POST | `/admin/v1/tenants` | Create provisioning draft (Step 1) | `platform.tenants.create` | |
| GET | `/admin/v1/tenants/{id}` | Full tenant detail | `platform.tenants.read` | Includes provisioning_state |
| PATCH | `/admin/v1/tenants/{id}` | Edit tenant profile | `platform.tenants.manage` | Company name, legal name, phone, website |
| PATCH | `/admin/v1/tenants/{id}/admin-account` | Set admin account (Step 2) | `platform.tenants.manage` | |
| PATCH | `/admin/v1/tenants/{id}/subscription` | Set/override subscription (Step 3 + override) | `platform.subscriptions.manage` | Syncs entitlements in same transaction |
| PATCH | `/admin/v1/tenants/{id}/settings` | Save configuration (Step 4 + settings tab) | `platform.tenants.manage` | |
| PATCH | `/admin/v1/tenants/{id}/status` | Status change (suspend/unsuspend/cancel) | `platform.tenants.suspend` | |
| PATCH | `/admin/v1/tenants/{id}/provision/confirm` | Activate provisioning tenant | `platform.tenants.activate` | Runs activation guard checklist |
| POST | `/admin/v1/tenants/{id}/impersonate` | Issue impersonation token | `platform.tenants.impersonate` | Always audit-logged |
| POST | `/admin/v1/tenants/{id}/invite-admin` | Send/resend owner invite | `platform.tenants.manage` | |
| GET | `/admin/v1/tenants/{id}/subscription` | Tenant subscription detail | `platform.subscriptions.read` | |
| GET | `/admin/v1/tenants/{id}/analytics` | Usage analytics | `platform.tenants.read` | |
| GET | `/admin/v1/tenants/{id}/users` | Tenant user list | `platform.tenants.read` | Read-only |
| GET | `/admin/v1/tenants/{id}/devices` | Tenant device list | `platform.tenants.read` | Read-only |
| GET | `/admin/v1/tenants/{id}/feature-flags` | Feature flag overrides | `platform.tenants.read` | |
| GET | `/admin/v1/tenants/{id}/integrations` | Integration status | `platform.tenants.read` | |
| GET | `/admin/v1/tenants/{id}/audit` | Tenant audit log | `platform.audit.read` | |
| GET | `/admin/v1/tenants/{id}/settings` | Tenant settings | `platform.tenants.read` | |
| GET | `/admin/v1/tenants/{id}/provisioning-summary` | Activation blockers checklist | `platform.tenants.read` | |
| GET | `/admin/v1/tenants/{id}/user-activity-timeseries` | User activity chart data | `platform.tenants.read` | |
| GET | `/admin/v1/tenants/{id}/department-activity` | Department activity summary | `platform.tenants.read` | |
| GET | `/admin/v1/tenants/validate` | Validate domain/name uniqueness | `platform.tenants.create` | Called on blur in wizard |
| GET | `/admin/v1/reference/countries/{code}/defaults` | Country default timezone/currency | None | Public within admin namespace |

---

## Error Taxonomy

| HTTP | Code | Condition | User-Facing Message |
|---|---|---|---|
| 403 | `permission_denied` | Account lacks required permission | "You do not have permission to perform this action." |
| 404 | `tenant_not_found` | Tenant ID does not exist | "Tenant not found." |
| 409 | `domain_taken` | Domain already registered | "This domain is already registered to another tenant." |
| 409 | `invalid_status_transition` | e.g., trying to activate an already-active tenant | "This tenant is already active." |
| 422 | `activation_blocked` | Activation guard checklist has failures | Checklist of blocker messages returned |
| 422 | `validation_failed` | Field validation failures | Per-field error messages |
| 422 | `impersonation_target_inactive` | Target user is not active | "The selected user is not active and cannot be impersonated." |
| 422 | `tenant_not_activatable` | Tenant is not in provisioning status | "Only provisioning-status tenants can be activated." |
| 429 | `impersonation_rate_limited` | Too many impersonation requests in short window | "Too many impersonation requests. Wait 5 minutes before retrying." |
| 500 | `internal_error` | Unexpected server error | "An unexpected error occurred. Check the audit log or contact engineering." |
