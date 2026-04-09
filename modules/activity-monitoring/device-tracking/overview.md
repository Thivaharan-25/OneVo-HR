# Device Tracking

**Module:** Activity Monitoring
**Feature:** Device Tracking

---

## Purpose

Tracks device interaction per employee per day — laptop active minutes vs estimated mobile minutes.

## Database Tables

### `device_tracking`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `laptop_active_minutes` | `int` | |
| `estimated_mobile_minutes` | `int` | Estimated from gap analysis |
| `laptop_percentage` | `decimal(5,2)` | |
| `detection_method` | `varchar(30)` | `agent`, `manual` |

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring Module]]
- [[modules/activity-monitoring/device-tracking/end-to-end-logic|Device Tracking — End-to-End Logic]]
- [[modules/activity-monitoring/device-tracking/testing|Device Tracking — Testing]]
- [[frontend/architecture/overview|Raw Data Processing]]
- [[frontend/architecture/overview|Daily Aggregation]]
- [[security/data-classification|Data Classification]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]]
