# Task: Core HR — Employee Profile

**Assignee:** Dev 1
**Module:** CoreHR
**Priority:** Critical
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]], [[current-focus/DEV3-org-structure|DEV3 Org Structure]] (employees reference departments, job titles, teams)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `employees` table + full CRUD endpoints
- [ ] Employee number auto-generation (tenant-scoped sequence)
- [ ] 1:1 linking to `users` via `user_id`
- [ ] Manager hierarchy via self-referencing `manager_id` (CTE queries for org tree)
- [ ] `employee_addresses` CRUD (permanent, current, emergency)
- [ ] `employee_dependents` CRUD
- [ ] `employee_qualifications` CRUD with document upload
- [ ] `employee_work_history` CRUD
- [ ] `employee_salary_history` — append-only, new entry on salary change
- [ ] `employee_bank_details` — **encrypted** `account_number_encrypted` via `IEncryptionService` (AES-256)
- [ ] `employee_emergency_contacts` CRUD
- [ ] `employee_custom_fields` CRUD (tenant-configurable)
- [ ] Avatar upload via `IFileService`
- [ ] `GET /api/v1/employees/me` (own profile, `employees:read-own`)
- [ ] `GET /api/v1/employees/{id}/team` (direct reports, `employees:read-team`)
- [ ] Cursor-based pagination on employee list
- [ ] FluentValidation for all create/update commands
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/core-hr/overview|core-hr]] — module architecture
- [[backend/shared-kernel|Shared Kernel]] — BaseEntity, BaseRepository, IEncryptionService
- [[security/data-classification|Data Classification]] — PII fields, encryption requirements
- [[backend/module-catalog|Module Catalog]] — dependencies
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped employee data

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/hr/employees/
├── page.tsx                      # Employee directory (list + grid, DataTable with search, filters, pagination)
├── new/page.tsx                  # Create employee (multi-step wizard via client-side state)
├── @modal/                       # Parallel route: intercepted create
│   └── (.)new/page.tsx           # Create modal over list
├── [id]/
│   ├── layout.tsx                # Shared layout for detail views (breadcrumbs, back nav)
│   ├── loading.tsx               # Skeleton while loading
│   ├── not-found.tsx             # Employee not found
│   ├── page.tsx                  # Employee detail (tabbed: profile, addresses, dependents, qualifications, salary, bank)
│   ├── timeline/page.tsx         # Lifecycle timeline
│   └── @panel/                   # Parallel route: intercepted edit
│       └── (.)edit/page.tsx      # Edit panel over detail
├── components/                   # Colocated feature components
│   ├── EmployeeDataTable.tsx     # Sortable columns, search, filters
│   ├── EmployeeTabs.tsx          # Tab navigation for detail page
│   ├── EmployeeWizardSteps.tsx   # Multi-step create form stepper
│   └── AvatarUpload.tsx          # Profile photo upload
└── _types.ts                     # Local TypeScript definitions
```

### What to Build

- [ ] Employee list page with DataTable (sortable columns, search, department filter, status filter)
- [ ] Employee detail page with tabs: Personal Info, Addresses, Dependents, Qualifications, Work History, Salary, Bank Details, Emergency Contacts
- [ ] Create employee form (multi-step wizard: personal → employment → compensation → review, client-side state stepper)
- [ ] Edit employee via intercepting route — `@panel/(.)edit/page.tsx` renders as slide-over panel from detail, full page on direct nav
- [ ] Section-specific edit modals (e.g., edit salary only) with PermissionGate per section
- [ ] Employee self-service: own profile view (read-only except allowed fields, permission-driven — no separate route group)
- [ ] Colocated components: EmployeeDataTable, EmployeeTabs, EmployeeWizardSteps, AvatarUpload
- [ ] `loading.tsx` skeleton for detail page, `not-found.tsx` for invalid employee IDs
- [ ] PermissionGate wrapper for edit/delete actions (`employees:update`, `employees:delete`)

### Userflows

- [[Userflow/Employee-Management/profile-management|Profile Management]] — view/edit employee profile
- [[Userflow/Employee-Management/dependent-management|Dependent Management]] — add/edit dependents
- [[Userflow/Employee-Management/qualification-tracking|Qualification Tracking]] — manage qualifications + documents
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]] — salary and bank details

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/employees` | List employees (paginated) |
| GET | `/api/v1/employees/{id}` | Get employee detail |
| POST | `/api/v1/employees` | Create employee |
| PUT | `/api/v1/employees/{id}` | Update employee |
| GET | `/api/v1/employees/me` | Own profile |
| GET | `/api/v1/employees/{id}/team` | Direct reports |
| GET | `/api/v1/employees/{id}/addresses` | Employee addresses |
| POST | `/api/v1/employees/{id}/addresses` | Add address |
| GET | `/api/v1/employees/{id}/dependents` | Employee dependents |
| POST | `/api/v1/employees/{id}/dependents` | Add dependent |
| GET | `/api/v1/employees/{id}/qualifications` | Employee qualifications |
| POST | `/api/v1/employees/{id}/qualifications` | Add qualification |
| GET | `/api/v1/employees/{id}/salary-history` | Salary history |
| GET | `/api/v1/employees/{id}/bank-details` | Bank details (masked) |
| PUT | `/api/v1/employees/{id}/bank-details` | Update bank details |
| POST | `/api/v1/employees/{id}/avatar` | Upload avatar |

### Frontend References

- [[frontend/architecture/app-structure|Frontend Structure]] — page routing
- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, PageHeader, Avatar
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — detail page layout
- [[frontend/data-layer/api-integration|API Integration]] — API client, pagination pattern
- [[frontend/coding-standards|Frontend Coding Standards]] — component conventions

---

## Related Tasks

- [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] — shared kernel this depends on
- [[current-focus/DEV3-org-structure|DEV3 Org Structure]] — departments, job titles, teams referenced by employees
- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — employee linked to user account via user_id
- [[current-focus/DEV2-core-hr-lifecycle|DEV2 Core Hr Lifecycle]] — lifecycle events update profile (promotions, transfers, salary changes)
- [[current-focus/DEV1-leave|DEV1 Leave]] — leave requests reference employee
- Performance — deferred to Phase 2 (reviews reference employee)
- Payroll — deferred to Phase 2 (payroll reads salary and bank details from employee profile)
