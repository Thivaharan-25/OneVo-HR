# Contract: HR Employee + Leave + Calendar

**Backend owner:** DEV2 Tasks 1-3  
**Consumers:** DEV6 Tasks 1-2, DEV8 (leave and clockin tags)  
**Canonical source:** `ONEVO.Application/Features/CoreHR/` and `ONEVO.Application/Features/Leave/`

---

## GET `/api/v1/employees` (cursor paginated)

```ts
interface EmployeeListItemDto {
  id: string
  employee_number: string
  full_name: string
  email: string
  job_title: string
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
  job_title: string
  job_family: string
  department: { id: string; name: string }
  team: { id: string; name: string } | null
  location: { id: string; name: string } | null
  manager: { id: string; full_name: string } | null
  employment_start_date: string   // ISO date
  status: "active" | "onboarding" | "on_leave" | "offboarded"
  avatar_url: string | null
}
```

## GET `/api/v1/leave/balance`

```ts
interface LeaveBalanceDto {
  leave_type_id: string
  leave_type_name: string
  available_days: number
  used_days: number
  pending_days: number
  upcoming_days: number
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
- Leave balance is per-employee; manager sees team summary via `/api/v1/leave/team-summary`
- Calendar feed query params: `from`, `to` (ISO dates), `employee_ids[]` (optional filter)

