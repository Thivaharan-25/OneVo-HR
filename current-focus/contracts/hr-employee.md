# Contract: HR Employee + Time Off + Calendar

**Backend owner:** DEV2 Tasks 1-3  
**Consumers:** DEV6 Tasks 1-2, DEV8 (time_off and clockin tags)  
**Canonical source:** `ONEVO.Application/Features/CoreHR/` and `ONEVO.Application/Features/TimeOff/`

---

## GET `/api/v1/employees` (cursor paginated)

```ts
interface EmployeeListItemDto {
  id: string
  employee_number: string
  full_name: string
  email: string
  department_name: string
  status: "active" | "onboarding" | "on_leave" | "offboarded"
  avatar_url: string | null
}
```

## GET `/api/v1/employees/{id}`

```ts
interface EmployeeDto {
  id: string
  employee_number: string
  full_name: string
  email: string
  phone: string | null
  department: { id: string; name: string }
  location: { id: string; name: string } | null
  position: { id: string; name: string; code: string; type: "unique" | "pooled" } | null
  reports_to_position: { id: string; name: string; code: string } | null
  resolved_manager: { id: string; full_name: string } | null
  manager_status: "resolved" | "vacant" | "unassigned"
  employment_start_date: string   // ISO date
  status: "active" | "onboarding" | "on_leave" | "offboarded"
  avatar_url: string | null
}
```

## GET `/api/v1/time-off/entitlements/me`

```ts
interface TimeOffBalanceDto {
  time_off_type_id: string
  time_off_type_name: string
  available_minutes: number
  used_minutes: number
  pending_minutes: number
  upcoming_minutes: number
  display_day_equivalent?: number
}
```

## GET `/api/v1/calendar/feed`

```ts
interface CalendarFeedDto {
  holidays: Array<{ date: string; name: string; country_code: string }>
  leaves: Array<{
    id: string; employee_id: string; start_date: string; end_date: string
    type: string; status: "approved" | "pending" | "rejected"
  }>
  shifts: Array<{ id: string; employee_id: string; start_time: string; end_time: string }>
  company_events: Array<{ id: string; title: string; start_date: string; end_date: string }>
}
```

## Notes

- All employee endpoints are tenant-scoped via `ITenantContext`
- `status` drives status badge color in DEV6 employee list (`active` -> green, `onboarding` -> blue, `on_leave` -> amber, `offboarded` -> grey)
- Calendar feed query params: `from`, `to` (ISO dates), `employee_ids[]` (optional filter)

