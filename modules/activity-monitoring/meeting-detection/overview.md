# Meeting Detection

**Module:** Activity Monitoring
**Feature:** Meeting Detection

---

## Purpose

Detects meeting sessions from desktop agent data. Phase 1 uses basic process name matching (e.g., `Teams.exe`, `zoom.exe`). Phase 2 will add Microsoft Teams Graph API for rich analytics.

## Database Tables

### `meeting_sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `meeting_start` | `timestamptz` | |
| `meeting_end` | `timestamptz` | |
| `platform` | `varchar(20)` | `teams`, `zoom`, `meet`, `other` |
| `duration_minutes` | `int` | Computed |
| `had_camera_on` | `boolean` | Detected via process inspection |
| `had_mic_activity` | `boolean` | Detected via audio device usage |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/activity/meetings/{employeeId}` | `workforce:view` | Meeting sessions |

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[meeting-detection/end-to-end-logic|Meeting Detection — End-to-End Logic]]
- [[meeting-detection/testing|Meeting Detection — Testing]]
- [[raw-data-processing/overview|Raw Data Processing]]
- [[daily-aggregation/overview|Daily Aggregation]]
- [[data-classification]]
- [[retention-policies]]
- [[multi-tenancy]]
- [[WEEK3-activity-monitoring]]
