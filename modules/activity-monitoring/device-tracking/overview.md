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

- [[activity-monitoring|Activity Monitoring Module]]
- [[device-tracking/end-to-end-logic|Device Tracking — End-to-End Logic]]
- [[device-tracking/testing|Device Tracking — Testing]]
- [[raw-data-processing/overview|Raw Data Processing]]
- [[daily-aggregation/overview|Daily Aggregation]]
- [[data-classification]]
- [[retention-policies]]
- [[multi-tenancy]]
- [[WEEK3-activity-monitoring]]
