# Task: Core HR — Employee Lifecycle

**Assignee:** Dev 2
**Module:** CoreHR
**Priority:** Critical
**Dependencies:** [[current-focus/DEV1-core-hr-profile|DEV1 Core Hr Profile]] (employee data), [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (workflow engine)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `employee_lifecycle_events` table — append-only audit trail
- [ ] Lifecycle event types: `hired`, `promoted`, `transferred`, `salary_change`, `suspended`, `terminated`, `resigned`
- [ ] `onboarding_templates` — reusable task templates (per department or global)
- [ ] `onboarding_tasks` — generated from template on hire, assigned to various users
- [ ] Onboarding status tracking (pending -> in_progress -> completed)
- [ ] `offboarding_records` — initiated on termination/resignation
- [ ] Knowledge risk assessment (`low`, `medium`, `high`, `critical`)
- [ ] Penalties tracking (outstanding loans, notice period violations) in `penalties_json`
- [ ] Offboarding workflow integration with workflow engine
- [ ] Domain events: `EmployeeCreated`, `EmployeePromoted`, `EmployeeTransferred`, `EmployeeTerminated`
- [ ] `EmployeeTerminated` event triggers: leave forfeiture, final payroll, agent revocation
- [ ] Promotion flow: update job_title_id + create salary_history entry + lifecycle event
- [ ] Transfer flow: update department_id/team + lifecycle event
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/core-hr/overview|core-hr]] — module architecture, domain events
- [[backend/notification-system|Notification System]] — lifecycle notifications
- [[backend/messaging/event-catalog|Event Catalog]] — domain event definitions
- [[modules/agent-gateway/overview|agent-gateway]] — revoke agent on termination
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped lifecycle data

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/hr/onboarding/
├── page.tsx                      # Active onboarding pipeline (list with progress bars)
├── [id]/
│   ├── loading.tsx               # Skeleton while loading
│   └── page.tsx                  # Onboarding checklist/wizard
├── components/                   # Colocated feature components
│   ├── OnboardingChecklist.tsx   # Task checklist with progress
│   ├── TaskTemplateEditor.tsx    # Template CRUD
│   └── OnboardingProgress.tsx    # Progress bar/stepper
└── _types.ts                     # Local TypeScript definitions

app/(dashboard)/hr/offboarding/
├── page.tsx                      # Active offboarding pipeline
├── [id]/
│   ├── loading.tsx               # Skeleton while loading
│   └── page.tsx                  # Offboarding checklist
└── components/                   # Colocated feature components
    ├── OffboardingChecklist.tsx   # Exit checklist
    └── KnowledgeRiskForm.tsx      # Knowledge transfer risk assessment
```

### What to Build

- [ ] Onboarding dashboard: list all active onboardings with OnboardingProgress bars
- [ ] Onboarding detail page: OnboardingChecklist with assignees, due dates, completion status
- [ ] Onboarding template management: TaskTemplateEditor for create/edit task templates
- [ ] Offboarding detail page: KnowledgeRiskForm + penalties summary + OffboardingChecklist
- [ ] Promotion dialog: select new job title, set new salary, effective date, reason (modal from employee detail)
- [ ] Transfer dialog: select new department/team, effective date, reason (modal from employee detail)
- [ ] Lifecycle events timeline on employee detail page (chronological history — rendered in employees/[id]/timeline)
- [ ] `loading.tsx` skeletons for both onboarding and offboarding detail pages
- [ ] Colocated components: OnboardingChecklist, TaskTemplateEditor, OnboardingProgress, OffboardingChecklist, KnowledgeRiskForm

### Userflows

- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] — full onboarding flow from hire to completion
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]] — termination/resignation flow with knowledge risk
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] — promotion workflow
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]] — department/team transfer workflow

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/employees/{id}/lifecycle-events` | Lifecycle event history |
| POST | `/api/v1/employees/{id}/promote` | Initiate promotion |
| POST | `/api/v1/employees/{id}/transfer` | Initiate transfer |
| POST | `/api/v1/employees/{id}/terminate` | Initiate termination |
| GET | `/api/v1/onboarding` | List active onboardings |
| GET | `/api/v1/onboarding/{employeeId}` | Onboarding detail + tasks |
| PUT | `/api/v1/onboarding/tasks/{taskId}` | Update task status |
| GET | `/api/v1/onboarding/templates` | List templates |
| POST | `/api/v1/onboarding/templates` | Create template |
| GET | `/api/v1/offboarding/{employeeId}` | Offboarding detail |
| PUT | `/api/v1/offboarding/{employeeId}/risk` | Set knowledge risk |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, Badge, Dialog
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — detail page with tabs
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV1-core-hr-profile|DEV1 Core Hr Profile]] — lifecycle events mutate employee profile data
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — workflow engine for offboarding approvals
- Payroll — deferred to Phase 2 (EmployeeTerminated triggers final payroll run)
- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — user account creation on hire
