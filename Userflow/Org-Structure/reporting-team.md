# Reporting Team

**Area:** Org Structure
**Trigger:** Authorized user opens an org-chart reporting view
**Required Permission(s):** `employees:read`

Reporting teams are org-chart/reporting views only. The system resolves reporting membership from position reporting lines.

This view does not grant employee visibility, approval authority, or system access. Employee visibility and approval routing are resolved through Org Structure management coverage and permission checks.

## Flow Steps

### Step 1: Resolve Manager Context
- **UI:** User opens a reporting-team or org-chart view.
- **Backend:** Resolve the manager employee ID from the current user or selected manager.

### Step 2: Load Reporting Team
- **API:** `GET /api/v1/org/reporting-team?managerEmployeeId={id}&depth=direct`
- **Alternative:** `depth=full` for indirect reports.
- **DB:** Read from `employee_hierarchy_closure`.

### Step 3: Display Members
- **UI:** Show employees under that reporting manager.
- **Rule:** Membership changes only when position assignments or reporting lines change.

## Rules

- Direct team means direct reports only.
- Full team means all descendants in the manager's reporting tree.
- Reporting membership is recalculated from current position assignments and reporting lines.
- The reporting view uses `employee_hierarchy_closure` as its source of truth.
- A reporting team cannot cross legal entities through reporting lines.
- Do not use this reporting view as the source for access, employee visibility, or approval routing.

## Related

- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[modules/org-structure/reporting-teams/overview|Reporting Teams]]
