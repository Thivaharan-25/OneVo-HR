# Dashboard - End-to-End Logic

## Purpose

The Dashboard is the first screen shown after login at `console.onevo.io`. It gives the platform operations team a real-time cross-tenant view of platform health, tenant activity, aggregate device health, billing state, and security alerts. It is read-only - no mutations happen from the dashboard; Phase 1 device data is summary-only.

---

## Screen Layout

```
+--------------------------------------------------------------+
|  KPI Summary Row  (6 cards across)                           |
|-------------------------+------------------------------------+
|  Platform Health        |  Tenant Distribution               |
|  Overview (donut)       |  (donut by plan tier)              |
|-------------------------+-------------------+----------------+
|  Active Users Over Time (line chart)        |                |
|-------------------------+-------------------+  Quick Actions |
|  Device Status          |  Alerts Overview  |  Panel         |
|  (donut + list)         |  (donut + list)   |                |
|-------------------------+-------------------+                |
|  System Resource Utilization (3 gauges)     |                |
|---------------------------------------------+----------------+
|  Recent System Events (table, last 10 rows)                  |
\--------------------------------------------------------------+
```

---

## Dashboard Load Sequence

1. Platform account opens `console.onevo.io` - session validation runs (platform-admin JWT checked).
2. Frontend determines the dashboard time window from the toolbar selector (default: Last 24 Hours).
3. Frontend fires all dashboard API calls in parallel - widgets render independently as their data arrives.
4. If a widget's API call fails, that widget shows an inline error state with a retry button. Other widgets are unaffected.
5. Security/compliance alert widget failure is **high-visibility**: shows a red error card rather than a generic spinner. Other widget failures show a gray "Could not load" state.

**Toolbar controls:**

| Control | Type | Options | Effect |
|---|---|---|---|
| Time window selector | Dropdown | Last 1 Hour, Last 24 Hours (default), Last 7 Days, Last 30 Days | Changes the `from` / `to` query params on all widget API calls |
| Refresh button | Icon button | N/A | Re-fires all API calls with current time window |
| Export button | Button with icon | Downloads dashboard summary as PDF or CSV | `GET /admin/v1/dashboard/export?format={pdf|csv}&from=...&to=...` |

---

## KPI Summary Cards

Six cards in a row. Each card shows: metric name, primary number, delta vs previous period (green up / red down), and subtitle text.

### Card 1 - Total Tenants
| Property | Value |
|---|---|
| API | `GET /admin/v1/dashboard/summary` |
| Field | `total_tenants` |
| Display | Large number, e.g. "128" |
| Delta | `+5 (4.07%) vs yesterday` - calculated from `tenants_created_in_window` |
| Delta color | Green when positive (new tenants added) |
| Click-through | Navigates to `/platform/tenants` |
| Query source | `COUNT(*) FROM tenants WHERE status != 'cancelled'` |

### Card 2 - Active Users
| Property | Value |
|---|---|
| API | `GET /admin/v1/dashboard/summary` |
| Field | `active_users` |
| Display | Large number, e.g. "18,642" |
| Delta | `+812 (4.55%) vs yesterday` |
| Definition | Users who have had at least one API call or login within the time window, across all active tenants |
| Delta color | Green when positive |
| Click-through | Navigates to `/platform/tenants` filtered to active tenants |

### Card 3 - Active Devices
| Property | Value |
|---|---|
| API | `GET /admin/v1/dashboard/summary` |
| Field | `active_devices` |
| Display | Large number, e.g. "24,758" |
| Delta | `+812 (4.55%) vs yesterday` |
| Definition | Devices with at least one heartbeat signal within the time window |
| Delta color | Green when positive |
| Click-through | None in Phase 1; detailed Device Management is Phase 2 |

### Card 4 - Today's Active Users
| Property | Value |
|---|---|
| API | `GET /admin/v1/dashboard/summary` |
| Field | `todays_active_users` |
| Display | Large number, e.g. "12,315" |
| Subtitle | "63.27% of total users" - calculated as `todays_active_users / total_users * 100` |
| Delta color | Green when above 60% of total, yellow 40-60%, red below 40% |
| Click-through | Navigates to Reports / Analytics filtered to today's user activity |

### Card 5 - Alerts (Total)
| Property | Value |
|---|---|
| API | `GET /admin/v1/dashboard/alerts` |
| Field | `total_alerts` |
| Display | Large number, e.g. "27" with badge breakdown below: "8 Critical - 19 Warning" |
| Delta color | Red when Critical > 0 - this card always has a warning state when any critical alerts exist |
| Click-through | Navigates to `/security/security-center` |
| Critical count display | Shown in red text |
| Warning count display | Shown in orange text |

### Card 6 - Platform Uptime
| Property | Value |
|---|---|
| API | `GET /admin/v1/dashboard/platform-health` |
| Field | `uptime_percentage_30d` |
| Display | Percentage to 2 decimal places, e.g. "99.96%" |
| Subtitle | "No downtime" when 100% (within rounding), or "X hours downtime" when below |
| Delta color | Green when >= 99.9%, yellow 99.0-99.89%, red below 99.0% |
| Click-through | Navigates to `/operations/platform-health` |

---

## Platform Health Overview Widget

### What It Shows

Left: Large donut chart showing overall health percentage.
Right: Service list with name, status badge, and uptime percentage.

### Monitored Services

| Service Name | What It Represents | Healthy Threshold |
|---|---|---|
| API Gateway | ONEVO backend API response success rate | p99 latency < 500ms, error rate < 0.1% |
| Auth Service | Primary login, MFA verification, token validation, session creation success rate | Success rate > 99.9% |
| Data Service | Database read/write success rate | Error rate < 0.01% |
| Sync Service | Real-time SignalR hub connections | Drop rate < 1% in window |
| Reporting Engine | Report generation job success rate | Failure rate < 1% |
| AI Insights Engine | AI inference request success rate | Error rate < 2%, p95 < 3s |

### Status Badge Logic Per Service

| Status Badge | Color | Condition |
|---|---|---|
| Healthy | Green | All metrics within thresholds |
| Degraded | Yellow | Any metric outside threshold but service still responding |
| Down | Red | Service not responding or error rate > 50% |
| Unknown | Gray | Health check data not received within last 2 minutes |

### Overall Health Percentage Calculation

```
overall_health = (SUM of individual service uptimes) / (number_of_services * 100)
```

Weighted: API Gateway, Auth Service, and Data Service are weight 2x; others are weight 1x.

---

## Tenant Distribution Widget

### What It Shows

Donut chart: breakdown of total tenants by subscription plan tier.

| Segment | Plan Tier | Color |
|---|---|---|
| Enterprise | Enterprise plan tenants | Dark blue |
| Business | Business plan tenants | Medium blue |
| Professional | Professional plan tenants | Light blue |
| Pending Payment | Tenants with first invoice open and unpaid | Blue |

Below donut: "Total Tenants: 128 / Active Tenants: 118"

**Click-through:** "View All Tenants" -> `/platform/tenants` filtered by clicked segment.

---

## Active Users Over Time Chart

### What It Shows

Line chart with time on X-axis and active user count on Y-axis. Time resolution adapts to time window:

| Time Window | Resolution | X-Axis Labels |
|---|---|---|
| Last 1 Hour | 5-minute buckets | HH:MM |
| Last 24 Hours | Hourly buckets | 12 AM, 4 AM, 8 AM, 12 PM, 4 PM, 8 PM |
| Last 7 Days | Daily buckets | Day names |
| Last 30 Days | Daily buckets | Date labels |

**Peak annotation:** Vertical marker at the peak data point - "Peak: 18,952 users at 11:20 AM".

**API:** `GET /admin/v1/dashboard/user-activity-timeseries?from=...&to=...&resolution=hourly`

---

## Device Status Widget

### What It Shows

Donut chart: aggregate breakdown of registered devices by current connection status.

| Segment | Condition | Color |
|---|---|---|
| Online | Device heartbeat received within last 5 minutes | Green |
| Idle | Device heartbeat received, no active user session for > 30 minutes | Yellow |
| Offline | No heartbeat received in last 15 minutes | Gray |

Below donut: row showing Sync Success Rate - "98.71%" with a sparkline showing trend over the time window.

**Sync Success Rate definition:** `(successful agent data sync events) / (total expected sync events) * 100` - calculated per polling cycle. An expected sync event is any device that checked in at least once in the window and was expected to check in again within its configured polling interval.

**Click-through:** none in Phase 1. "View All Devices" is Phase 2 with Device Management.

---

## Alerts Overview Widget

This is the most critical widget on the dashboard. It shows all active (unresolved) alerts across all tenants and platform systems.

### What It Shows

Left: Donut chart broken into severity segments.
Right: Severity count list with label and count.

| Segment | Label | Color |
|---|---|---|
| Critical | Critical | Red |
| Warning | Warning | Orange |
| Info | Info | Blue |
| Resolved | Resolved (in window) | Green |

Below: "MTTR (Mean Time To Resolve): 1h 42m" - average time from alert creation to resolution for alerts resolved in the time window.

---

## Alert Detection Mechanism - How the System Knows About Alerts

Alerts are not manually created by operators. They are generated automatically by the backend through three detection pathways. Every pathway writes a row to the `platform_alerts` table using `IAlertService.CreateAlertAsync(alertCode, severity, tenantId, title, detail)`.

### Pathway 1 - MediatR Domain Event Handlers

Most alerts originate from domain events published inside the ONEVO backend using MediatR's `INotificationHandler<TEvent>` pattern.

**Flow:**
```
User action or system event occurs
        |
        v
Domain event published: IPublisher.Publish(new LoginFailedEvent(...))
        |
        v
AlertCreationHandler : INotificationHandler<LoginFailedEvent>
        |
        |-- Checks threshold: has this IP exceeded 10 failures in 5 minutes?
        |   (reads rolling count from Phase 1 in-memory cache)
        |
        |-- YES -> IAlertService.CreateAlertAsync(
        |           alertCode: "auth.brute_force_detected",
        |           severity: AlertSeverity.Critical,
        |           tenantId: tenantId,
        |           title: "Brute force attempt detected",
        |           detail: $"IP {ip} made {count} failed attempts in 5 minutes"
        |         )
        |
        \-- Writes row to platform_alerts table
            Sends push notification if severity = Critical
```

**Domain events that create alerts:**

| Event Class | Published By | Alert Code Created |
|---|---|---|
| `LoginFailedEvent` | Auth module | `auth.failed_login_spike` / `auth.brute_force_detected` (threshold-gated) |
| `AccountLockedEvent` | Auth module | `auth.admin_account_locked` |
| `IdentityVerificationFailedEvent` | Identity Verification module | `identity.verification_failed_spike` (threshold-gated: >=3 in 1h) |
| `PaymentFailedEvent` | Billing / SharedPlatform | `billing.payment_failed` / `billing.payment_failed_final` (attempt count-gated) |
| `SubscriptionExpiredEvent` | Billing job | `billing.subscription_expired` |
| `SubscriptionExpiringEvent` | Billing job | `billing.subscription_expiring` |
| `AgentTamperDetectedEvent` | Agent Gateway | `agent.tamper_detected` |
| `AgentMassDisconnectEvent` | Agent Gateway | `agent.mass_disconnect` (threshold: >=20% devices in 5 min) |
| `ExceptionRuleFiredEvent` | Exception Engine | `exception.rule_triggered` |
| `WebhookProcessingFailedEvent` | Billing / SharedPlatform | `billing.webhook_processing_failed` (dead-letter) |
| `TenantActivatedEvent` | SharedPlatform | `tenant.activated` (Info) |
| `TenantSuspendedEvent` | SharedPlatform | `tenant.suspended` (Info) |
| `NewDeviceRegisteredEvent` | Agent Gateway | `tenant.new_device_registered` (Info) |
| `UserInvitedEvent` | Auth module | `tenant.admin_invited` (Info) |

### Pathway 2 - Background Health Check Jobs

Infrastructure health alerts are generated by scheduled background jobs (Hangfire) that poll service health endpoints every 2 minutes.

**Job: `PlatformHealthCheckJob` (every 2 minutes)**
```
For each monitored service (API Gateway, Auth, Data Service, Sync, Reporting, AI Engine):
  1. Call internal health endpoint: GET /health/{serviceName}
  2. Measure response time and check HTTP status
  3. If status = Down (no response or error) for 2 consecutive checks:
     -> CreateAlertAsync("infra.service_down", Critical, tenantId: null, ...)
  4. If status = Degraded (latency > threshold or error rate > 0.1%):
     -> CreateAlertAsync("infra.service_degraded", Warning, tenantId: null, ...)
  5. If previously degraded/down and now healthy:
     -> IAlertService.AutoResolveAlert(alertCode: "infra.service_degraded", ...)
```

**Job: `ResourceUtilizationCheckJob` (every 5 minutes)**
```
Read CPU, memory, storage metrics from infrastructure monitoring API
If CPU > 80% for >5 min: CreateAlert("infra.high_cpu", Warning)
If Memory > 80% for >5 min: CreateAlert("infra.high_memory", Warning)
If Storage > 85%: CreateAlert("infra.storage_near_limit", Warning)
When any metric returns below threshold: IAlertService.AutoResolveAlert(...)
```

**Job: `DunningCheckJob` (daily at 02:00 UTC)**
```
For each tenant_subscription where next_billing_date <= today and payment_status != 'paid':
  Check payment_attempt_count
  -> Schedule retry or escalate to Critical alert
```

**Job: `TrialExpiryCheckJob` (daily at 01:00 UTC)**
```
For each tenant where status = 'trial':
  If trial_end_at is within configured warning window:
    Create or update trial expiring soon attention item
  If trial_end_at < now:
    Set tenant.status = 'trial_expired'
    Block demo access except upgrade/support flows where policy allows
    Create audit log and tenant notification
```

Billing alerts are still driven by invoice/payment status. Trial follow-up alerts and payment alerts are separate dashboard attention streams.

### Pathway 3 - Webhook Handlers

Payment gateway webhooks (Paddle, PayHere) trigger alerts as part of their event processing in `WebhookRetryJob`.

```
POST /webhooks/paddle received
        |
        v
Signature verified -> payload enqueued in webhook_event_queue
        |
        v
WebhookProcessingService processes event:
  payment_intent.payment_failed -> PaymentFailedEvent published -> Pathway 1
  customer.subscription.deleted -> SubscriptionExpiredEvent published -> Pathway 1
  charge.dispute.created -> CreateAlert("billing.dispute_opened", Warning, tenantId)
  Dead-letter (5 retries exhausted) -> CreateAlert("billing.webhook_processing_failed", Critical)
```

### Alert Deduplication

Before creating any alert, `IAlertService.CreateAlertAsync` checks:
```
Does an ACTIVE (not resolved) alert with the same alert_code + tenant_id already exist?
  YES -> Update existing alert's detail and updated_at - do NOT create a duplicate
  NO  -> Insert new platform_alerts row
```

This prevents alert floods. For example, if CPU stays above 80% for 2 hours, only one Warning alert exists - it is not re-created every 5 minutes.

### Auto-Resolution

When the condition that triggered a Warning alert clears, the background job calls `IAlertService.AutoResolveAlert(alertCode, tenantId)`:
```sql
UPDATE platform_alerts
SET auto_resolved = true, resolved_at = NOW(), resolved_reason = 'condition_cleared'
WHERE alert_code = @alertCode AND tenant_id = @tenantId AND resolved_at IS NULL
```

Critical alerts are never auto-resolved - a platform admin must resolve them manually with a written reason.

---

## Alert Classification System - Full Specification

Every alert in ONEVO has exactly one severity level: **Critical**, **Warning**, or **Info**. Severity is set by the system at alert creation based on the condition that triggered the alert. Operators cannot manually change severity after the fact (they can only acknowledge or resolve).

---

### Critical Alerts - Full Condition Catalog

Critical alerts require immediate attention. They are displayed in red in the dashboard, in the Security Center, and as a persistent banner on the affected tenant's detail page. They are never auto-resolved - a platform admin must acknowledge them with a resolution note.

| Alert Code | Source Module | Trigger Condition | Auto-Created When |
|---|---|---|---|
| `auth.brute_force_detected` | Auth | >= 10 failed login attempts from the same IP to the same tenant within 5 minutes | Login failure events exceed threshold in rolling 5-minute window |
| `auth.admin_account_locked` | Auth | Tenant super-admin account locked due to failed attempts | Account `locked_at` is set |
| `identity.verification_failed_spike` | Identity Verification | >= 3 identity verification failures for different users within 1 hour in the same tenant | Failure event count threshold crossed |
| `auth.suspicious_session` | Auth | Login from an IP or device not seen in the last 90 days for that account, combined with access to high-permission resources | Anomaly detection rule fires |
| `billing.payment_failed_final` | Billing / SharedPlatform | Payment gateway charge fails on 3rd retry with no recovery | Webhook `payment.failed` received and retry count = 3 |
| `billing.subscription_expired` | Billing / SharedPlatform | Tenant subscription end date passed without renewal | Nightly billing job finds expired subscriptions |
| `infra.service_down` | Infrastructure | Any monitored service health check fails for >= 2 consecutive checks (5-minute interval) | Health check job records `status = 'down'` for service |
| `infra.database_unreachable` | Infrastructure | Database connection pool exhausted or primary unreachable | Connection error rate > 80% in 1 minute |
| `agent.tamper_detected` | Agent Gateway | Agent binary hash does not match expected hash for that version | Agent integrity check fails on device check-in |
| `monitoring.data_exfiltration_pattern` | Activity Monitoring / Exception Engine | Bulk file access or download event above configured exception rule threshold | Exception engine fires exfiltration rule |
| `agent.mass_disconnect` | Agent Gateway | >= 20% of a tenant's devices disconnect simultaneously within 5 minutes | Device heartbeat loss spike above threshold |

**Critical alert display rules:**
- Red badge on the Alerts KPI card showing count
- Red callout banner on the affected tenant's detail page
- Listed first in the Security Center alert table, sorted by `created_at` descending within Critical tier
- Push notification to all platform accounts with `platform.alerts.critical_notify` permission

---

### Warning Alerts - Full Condition Catalog

Warning alerts indicate a condition that needs attention but is not immediately service-breaking. Displayed in orange. Can be auto-resolved when the triggering condition clears.

| Alert Code | Source Module | Trigger Condition | Auto-Resolved When |
|---|---|---|---|
| `auth.failed_login_spike` | Auth | >= 5 failed logins from the same tenant in 1 hour (below brute-force threshold) | No new failures for 1 hour |
| `monitoring.high_idle_time` | Activity Monitoring | > 50% of a tenant's active users show idle state for > 2 consecutive hours during work hours | Idle percentage drops below 30% |
| `infra.service_degraded` | Infrastructure | Service latency p95 > 500ms or error rate 0.1-10% | Service metrics return to healthy thresholds |
| `infra.high_cpu` | Infrastructure | API host CPU > 80% for > 5 minutes | CPU drops below 70% |
| `infra.high_memory` | Infrastructure | API host memory > 80% for > 5 minutes | Memory drops below 70% |
| `infra.storage_near_limit` | Infrastructure | Platform storage utilization > 80% | Utilization drops below 70% |
| `billing.payment_failed` | Billing | First or second payment retry failure | Payment succeeds on retry OR progresses to `billing.payment_failed_final` |
| `billing.subscription_expiring` | Billing | Tenant subscription end date is <= 7 days away with no renewal recorded | Subscription renewed OR end date updated |
| `tenant.storage_limit_approaching` | SharedPlatform | Tenant data storage > 80% of their purchased limit | Tenant storage drops below 70% or limit increased |
| `tenant.ai_token_limit_approaching` | SharedPlatform | Tenant AI token usage > 80% of monthly limit | Token usage drops (new month reset) or limit increased |
| `agent.device_offline` | Agent Gateway | A registered device has not sent a heartbeat for > 1 hour during configured work hours | Device reconnects |
| `agent.outdated_version` | Agent Gateway | >= 30% of a tenant's devices running a version older than current GA by 2+ major versions | Devices update to current version |
| `exception.rule_triggered` | Exception Engine | An active exception rule fires for a tenant user | Rule condition no longer met or alert acknowledged |

**Warning alert display rules:**
- Orange badge component on Alerts KPI card
- Listed in Security Center alert table below Critical alerts
- Auto-resolved warnings are moved to "Resolved" status in the alerts table with `resolved_reason = 'condition_cleared'` and `resolved_at` timestamp
- No push notification by default; operators can configure per-alert-code notification preferences

---

### Info Alerts - Full Condition Catalog

Info alerts are informational events that require no immediate action. Auto-dismissed after 48 hours if not manually reviewed. Displayed in blue.

| Alert Code | Source Module | Trigger Condition |
|---|---|---|
| `tenant.new_device_registered` | Agent Gateway | A new device checks in for the first time for a tenant |
| `tenant.user_created` | Auth | A new user is added to a tenant |
| `tenant.admin_invited` | Auth | Tenant admin invitation email sent |
| `tenant.activated` | Tenant Management | A provisioning tenant is activated |
| `tenant.suspended` | Tenant Management | A tenant is suspended |
| `agent.version_updated` | Agent Gateway | Phase 2 only: an agent deployment ring assignment successfully pushes a new version to a device |
| `billing.plan_changed` | Billing | Tenant subscription plan changed |
| `billing.invoice_generated` | Billing | A new invoice is generated for a tenant |
| `billing.payment_succeeded` | Billing | A payment is collected successfully |
| `config.settings_changed` | Configuration | Tenant settings edited by platform admin |
| `feature_flag.override_set` | Runtime Overrides | A per-tenant feature flag override is created or changed |
| `integration.connected` | Integrations | A tenant successfully connects an integration (e.g., Microsoft 365) |
| `integration.disconnected` | Integrations | A tenant integration is disconnected |

**Info alert display rules:**
- Blue badge count on Alerts KPI card
- Auto-dismissed after 48 hours with `auto_dismissed = true`
- Not shown in the Alerts KPI card Critical/Warning count breakdown - counted separately
- Listed in Security Center alert table below Warning alerts

---

## Alert Object Schema

Every alert stored in `platform_alerts` table has this shape:

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `alert_code` | varchar(80) | Machine-readable code from the catalogs above |
| `severity` | enum | `critical`, `warning`, `info` |
| `tenant_id` | UUID nullable | Null for platform-level alerts (infrastructure/service alerts); set for tenant-scoped alerts |
| `source_module` | varchar(80) | Module key that generated the alert |
| `title` | varchar(200) | Human-readable title, e.g. "Brute force attempt detected" |
| `detail` | text | Additional context - IP address, affected user count, threshold crossed, etc. |
| `created_at` | timestamptz | When the alert was first raised |
| `auto_resolved` | boolean | True if condition cleared automatically |
| `resolved_at` | timestamptz nullable | When resolved |
| `resolved_by_id` | UUID nullable | Platform account that resolved it (null if auto-resolved) |
| `resolved_reason` | text nullable | Operator-entered resolution note (required for Critical, optional for Warning) |
| `acknowledged_at` | timestamptz nullable | When first acknowledged - distinct from resolved |
| `acknowledged_by_id` | UUID nullable | Platform account that acknowledged |
| `auto_dismissed` | boolean | True when Info alert is auto-dismissed after 48 hours |

---

## Alert Lifecycle State Machine

```
                    +---------+
           Created  |  ACTIVE  |
           ----->   \----+----+
                         |
              +----------+--------------+
              |          |              |
              v          v              v
     +--------------+ +----------+ +------------------+
     | ACKNOWLEDGED | |  AUTO-   | |  AUTO-DISMISSED   |
     | (Critical /  | | RESOLVED | |  (Info only,      |
     |  Warning)    | |(Warning) | |   after 48h)      |
     \------+-------+ \----------+ \------------------+
            |
            v
       +----------+
       | RESOLVED |  <- operator enters resolution note
       \----------+
```

**Resolution rule for Critical:** platform admin must enter a `resolved_reason` of at least 20 characters. Frontend validates before calling `POST /admin/v1/alerts/{id}/resolve`.

**Resolution rule for Warning:** `resolved_reason` optional. Can be resolved without a note.

**Resolution rule for Info:** auto-dismissed. No manual resolution required unless operator explicitly resolves early.

---

## System Resource Utilization Widget

Three circular gauge charts showing current platform resource usage.

| Gauge | Metric | Source | Thresholds |
|---|---|---|---|
| CPU Usage | Current CPU utilization % across all API hosts | Infrastructure monitoring | Green < 60%, Yellow 60-80%, Red > 80% |
| Memory Usage | Current memory utilization % across all API hosts | Infrastructure monitoring | Green < 60%, Yellow 60-80%, Red > 80% |
| Storage Usage | Platform storage used as % of provisioned capacity | Infrastructure monitoring | Green < 70%, Yellow 70-85%, Red > 85% |

Each gauge shows: percentage number, colored ring, label below.

Status text below gauges: "All resources are within normal thresholds." - turns yellow "Attention: [resource] approaching limit." or red "Alert: [resource] above critical threshold." based on gauge values.

---

## Recent System Events Table

Shows the 10 most recent platform-level events across all tenants, sorted by `created_at` descending.

### Columns

| Column | Description | Width |
|---|---|---|
| Time | `created_at` formatted as "May 20, 2025 10:24 AM" | 180px |
| Event | Human-readable event description | Flexible |
| Service | Which ONEVO service or module generated the event | 150px |
| Tenant | Tenant name (linked to tenant detail) - "Global" for platform-level events | 160px |
| Severity | Badge: Info (blue) / Warning (orange) / Critical (red) | 100px |
| Status | Badge: Completed (green) / Resolved (green) / Warning (orange) / Failed (red) | 120px |

### Event Sources

Events in this table come from the audit log (`audit_log` table) filtered to the most impactful event codes. Not all audit events appear here - only events with a platform operational significance:

| Event Type | Appears As |
|---|---|
| Tenant activated | "New tenant onboarded" - Completed |
| Service health alert raised | "[Service name] alert detected" - Warning or Critical |
| Payment succeeded | "Payment collected" - Completed |
| Payment failed | "Payment collection failed" - Critical |
| Agent mass disconnect | "Agent connectivity event" - Warning |
| Security alert raised | "Security event detected" - Critical |
| Platform admin login | "Platform admin login" - Info / Completed |
| Feature flag changed | "Feature flag updated" - Info / Completed |

**API:** `GET /admin/v1/dashboard/recent-events?limit=10&from=...&to=...`

**Click-through:** "View All Events" -> `/security/audit-logs`

---

## Quick Actions Panel

Right-side panel with 4 shortcuts. Each is a clickable row with chevron icon.

| Label | Navigates To | Permission Required |
|---|---|---|
| Create New Tenant | `/tenants/new` | `platform.tenants.create` |
| Add Platform Admin | `/platform/platform-users/invite` | `platform.accounts.manage` |
| View System Health | `/operations/platform-health` | `platform.health.read` |
| Manage Global Policies | System Config -> Global Policies | `platform.system_config.read` |
| Export Platform Report | `GET /admin/v1/dashboard/export` | `platform.reports.read` |

**Permission enforcement:** Quick action rows that the current account lacks permission for are hidden - not shown as disabled.

---

## Dashboard API Surface

| Method | Route | Description | Permission | Response Fields |
|---|---|---|---|---|
| GET | `/admin/v1/dashboard/summary` | KPI totals | `platform.dashboard.view` | `total_tenants`, `active_tenants`, `suspended_tenants`, `total_users`, `active_users`, `todays_active_users`, `total_devices`, `active_devices`, `idle_devices`, `offline_devices`, `sync_success_rate`, `tenants_created_in_window`, `users_added_in_window`, `devices_added_in_window` |
| GET | `/admin/v1/dashboard/platform-health` | Service health per service + overall | `platform.dashboard.view` | `overall_health_pct`, `uptime_percentage_30d`, `services[]` (name, status, uptime_pct, latency_p95_ms, error_rate_pct) |
| GET | `/admin/v1/dashboard/alerts` | Alert counts by severity + MTTR | `platform.dashboard.view` | `critical_count`, `warning_count`, `info_count`, `resolved_count`, `total_active`, `mttr_minutes` |
| GET | `/admin/v1/dashboard/recent-events` | Last N platform events | `platform.dashboard.view` | `events[]` (time, event_description, service, tenant_name, tenant_id, severity, status) |
| GET | `/admin/v1/dashboard/user-activity-timeseries` | Active user counts over time | `platform.dashboard.view` | `data_points[]` (timestamp, active_users) |
| GET | `/admin/v1/dashboard/tenant-distribution` | Tenant count by plan tier | `platform.dashboard.view` | `tiers[]` (tier_name, tenant_count, percentage) |
| GET | `/admin/v1/dashboard/resource-utilization` | CPU / memory / storage | `platform.dashboard.view` | `cpu_pct`, `memory_pct`, `storage_pct`, `status` |
| GET | `/admin/v1/dashboard/export` | Full dashboard PDF/CSV export | `platform.reports.read` | Binary file download |

### Query Parameters (all GET endpoints)
| Param | Type | Default | Description |
|---|---|---|---|
| `from` | ISO 8601 datetime | 24h ago | Window start |
| `to` | ISO 8601 datetime | now | Window end |
| `limit` | integer | 10 (recent-events only) | Max rows returned |

---

## Failure Handling - Per Widget

| Widget | On API Error | Display |
|---|---|---|
| KPI cards | Each card independent | Gray "-" in value, "Could not load" sub-text, retry icon |
| Platform Health | Critical widget | Red error card: "Health data unavailable - retry to check service status." |
| Alerts Overview | Critical widget | Red error card: "Alert data could not be loaded. Check Security Center directly." |
| Charts | Non-critical | Gray "Could not load chart data." with retry button |
| Resource Utilization | Non-critical | Gray gauges at 0% with "Data unavailable" |
| Recent Events | Non-critical | Empty table with "Could not load recent events." |

**Rule:** Never fail the whole dashboard page for a single widget error. Each widget loads and fails independently. The page structure always renders.

