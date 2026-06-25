# Page: Employee Management

**Route:** `/people/employees` (list), `/people/employees/:id` (full-page detail), `/people/employees/new` (create)  
**Permission:** `employees:read` for list/detail, `employees:write` for create/edit

---

## Phase 1 Source of Truth

Employee detail is a full-page screen, not a side drawer or side panel. The page should feel like an operational HR workspace, not a giant form dump.

Do not use one global "Edit Profile" action for every field. Each business section has its own edit action when the actor has permission.

---

## List Layout

The list provides search, filters, and a table of employees. Clicking a row navigates to `/people/employees/:id`.

Recommended columns: Employee, Position, Department, Legal Entity, Employment Type, Work Mode, Status, Reporting Manager, Actions.

---

## Full-Page Detail Header

Top area:

- Back to employees
- Employee name
- Email
- Status chip
- Position / department / legal entity summary
- Work mode chip
- Key employment chips
- Right-side lifecycle actions based on permission:
  - Transfer
  - Promote
  - Start Offboarding
  - Other lifecycle actions already in scope

Lifecycle actions open dedicated compact modals or screens. They are not side sheets as the main employee-detail experience.

---

## Detail Sections

Use section cards, not a tab-heavy employee detail model.

| Section | Purpose |
|:---|:---|
| About / Personal Information | Full name, email, phone, employee number, date of birth where supported, and basic identity fields |
| Employment Status / Job Details | Primary position, department, legal entity, reporting manager, Managed by / coverage owner, employment type, start date, status, and work mode |
| Policy & Access Overrides | Default inherited values, overridden values, and whether access comes from position or override |
| Documents | Employee files and task/document links where enabled |
| Lifecycle / Activity | Transfers, promotions, offboarding, approvals where useful, and lifecycle event history |

### Policy & Access Overrides

Show only controls the actor is allowed to use:

- Role override
- Time off policy override
- Schedule / shift override
- Visibility / management authority summary
- Primary Employment Assignment
- Additional Authority Assignments
- Inherited source and current value for each policy/access item

`Reporting manager` is the position-derived org-chart/reporting value. `Managed by / coverage owner` is a separate field resolved from Org Structure management coverage and is the field used for employee visibility and Phase 1 routing.

---

## Assignment Display

If multiple assignments exist:

- Mark exactly one as **Primary Employment Assignment**.
- Mark others as **Additional Authority Assignments**.
- Show that primary assignment controls legal entity, time off policy, attendance policy, schedule, holiday calendar, and payroll/statutory context.
- Show that additional authority assignments grant access/authority only.

---

## Interactions

- Search filters update URL params.
- Click row -> navigate to full-page employee detail.
- Transfer and Promotion open compact modals.
- Offboarding opens the dedicated offboarding flow.
- Detail sections may lazy-load their data.
- No Phase 1 workflow-engine dependency for transfer/promotion/position access.

---

## Empty States

- No employees: "No employees found. Add your first employee to get started."
- No filter results: "No employees match your filters."
- No authority assignments: "No additional authority assignments."

---

## Related

- [[modules/core-hr/employee-profiles/overview|Employee Profiles Overview]]
- [[modules/core-hr/employee-profiles/end-to-end-logic|Employee Profiles - End-to-End Logic]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
