# Task: Leave Module

**Assignee:** Dev 1
**Module:** Leave
**Priority:** High
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]], [[current-focus/DEV1-core-hr-profile|DEV1 Core Hr Profile]] (employee context), [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (workflow engine)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `leave_types` table + CRUD (Annual, Sick, Maternity, etc.) — uses `tenant_id`
- [ ] `leave_policies` table with versioning chain (`superseded_by_id`)
- [ ] Policy matching: leave type + country + job level combination
- [ ] Active policy query: `WHERE superseded_by_id IS NULL`
- [ ] `leave_entitlements` table — calculated per employee per year
- [ ] Entitlement calculation: accrual method (`annual`, `monthly`, `daily`) + proration for mid-year hires
- [ ] Carry forward logic: max days + expiry months
- [ ] `leave_requests` table + submit/approve/reject workflow
- [ ] Request validation: check sufficient balance, no overlapping requests, max consecutive days
- [ ] Calendar conflict detection: call `ICalendarConflictService` on submission, store `conflict_snapshot_json` on `leave_requests`
- [ ] Manager approval view: show conflict snapshot (at submission) + live re-check (current conflicts)
- [ ] `LeaveRequested` notification to manager includes conflict count if > 0
- [ ] `leave_balances_audit` — append-only balance change log
- [ ] Workflow integration for approval routing (manager -> HR for long leave)
- [ ] Domain events: `LeaveRequested`, `LeaveApproved`, `LeaveRejected`, `LeaveCancelled`
- [ ] `LeaveApproved` -> update `presence_sessions` status to `on_leave`
- [ ] `GET /api/v1/leave/calendar` — team leave calendar view
- [ ] `GET /api/v1/leave/requests/me` — own requests (`leave:read-own`)
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/leave/overview|leave]] — module architecture
- [[modules/core-hr/overview|core-hr]] — employee context (country, job level for policy matching)
- [[modules/workforce-presence/overview|workforce-presence]] — presence status updated on LeaveApproved
- [[modules/calendar/overview|calendar]] — conflict detection via ICalendarConflictService
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped leave types and policies

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/hr/leave/
├── page.tsx                      # Leave requests (own or team — permission-driven, no separate route group)
├── calendar/page.tsx             # Leave calendar view (monthly, color-coded)
├── balances/page.tsx             # Leave balances
├── policies/page.tsx             # Leave policy config (admin)
├── components/                   # Colocated feature components
│   ├── LeaveRequestForm.tsx      # Apply / edit leave request (with conflict warnings)
│   ├── LeaveCalendar.tsx         # Calendar with leave overlays
│   ├── LeaveBalanceCard.tsx      # Balance summary cards per type
│   └── LeavePolicyEditor.tsx     # Policy CRUD form with version history
└── _types.ts                     # Local TypeScript definitions

# Note: No separate (employee) route group. Self-service leave uses the same /hr/leave/
# pages with permission-driven views (leave:read-own shows own data, leave:read-team shows team).
```

### What to Build

- [ ] Leave requests list page (DataTable: employee, type, dates, status, actions) — permission-driven view
- [ ] Leave request detail modal (view request + conflict snapshot + approve/reject)
- [ ] Team leave calendar (LeaveCalendar — monthly view with color-coded leave types)
- [ ] Leave balances page (LeaveBalanceCard per type: used / remaining / pending)
- [ ] Leave policy admin page (LeavePolicyEditor — CRUD policies, version history)
- [ ] Submit new request form (LeaveRequestForm — type, dates, reason, half-day toggle)
- [ ] Leave request approval flow UI (approve/reject with comments)
- [ ] Conflict warning banner on request submission
- [ ] Colocated components: LeaveRequestForm, LeaveCalendar, LeaveBalanceCard, LeavePolicyEditor
- [ ] PermissionGate: `leave:create`, `leave:approve`, `leave:read-team`, `leave:read-own`

### Userflows

- [[Userflow/Leave/leave-request-submission|Leave Request Submission]] — employee submits leave request
- [[Userflow/Leave/leave-approval|Leave Approval]] — manager reviews and approves/rejects
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]] — cancel pending/approved leave
- [[Userflow/Leave/leave-balance-view|Leave Balance View]] — view leave balances
- [[Userflow/Leave/leave-type-configuration|Leave Type Configuration]] — admin configures leave types
- [[Userflow/Leave/leave-policy-setup|Leave Policy Setup]] — admin creates/versions policies
- [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]] — assign entitlements to employees

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/leave/types` | List leave types |
| POST | `/api/v1/leave/types` | Create leave type |
| GET | `/api/v1/leave/policies` | List policies |
| POST | `/api/v1/leave/policies` | Create policy |
| GET | `/api/v1/leave/entitlements/{employeeId}` | Employee entitlements |
| GET | `/api/v1/leave/requests` | List leave requests (filtered) |
| POST | `/api/v1/leave/requests` | Submit leave request |
| PUT | `/api/v1/leave/requests/{id}/approve` | Approve request |
| PUT | `/api/v1/leave/requests/{id}/reject` | Reject request |
| PUT | `/api/v1/leave/requests/{id}/cancel` | Cancel request |
| GET | `/api/v1/leave/requests/me` | Own requests |
| GET | `/api/v1/leave/calendar` | Team leave calendar |
| GET | `/api/v1/leave/balances/me` | Own balance summary |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, Calendar, Badge, StatCard
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — status colors for leave types
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV1-core-hr-profile|DEV1 Core Hr Profile]] — employee country and job level used in policy matching
- [[current-focus/DEV3-org-structure|DEV3 Org Structure]] — job levels referenced in policy matching
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — workflow engine used for approval routing
- [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] — presence_sessions updated on leave approval
- Payroll — deferred to Phase 2 (leave deductions read via ILeaveService)
- [[current-focus/DEV3-calendar|DEV3 Calendar]] — Calendar module (ICalendarConflictService)
