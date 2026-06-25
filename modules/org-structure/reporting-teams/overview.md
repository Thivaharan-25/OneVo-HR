# Reporting Teams

**Module:** Org Structure
**Feature:** Reporting Teams
**Phase:** Phase 1

Reporting teams are derived from the reporting-manager structure and rendered as hierarchy-based reporting views.

## Source Of Truth

Position hierarchy is the source of truth:

1. `positions.reports_to_position_id` defines the reporting line.
2. `position_assignments` places employees into positions.
3. `employee_hierarchy_closure` derives manager-to-employee reporting membership for org-chart views.

The backend returns a manager's reporting view from `employee_hierarchy_closure`:

| Team type | Rule |
|:----------|:-----|
| Direct reporting team | `ancestor_employee_id = managerEmployeeId` and `depth = 1` |
| Full reporting team | `ancestor_employee_id = managerEmployeeId` and `depth >= 1` |

## Rules

- Reporting teams are generated when position assignments or reporting lines change.
- Reporting membership is recalculated from current position assignments and reporting lines.
- Employees move between reporting teams by transfer, promotion, position reassignment, or reporting-line change.
- Reporting views are display/query views only.
- Access, employee visibility, and approval routing still come from roles, position access grants, and **Can manage employees in** coverage.

## API

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/reporting-team?managerEmployeeId={id}&depth=direct` | `employees:read` | Direct reports for a reporting manager |
| GET | `/api/v1/org/reporting-team?managerEmployeeId={id}&depth=full` | `employees:read` | Full reporting tree for a reporting manager |

## Related

- [[modules/org-structure/overview|Org Structure]]
- [[modules/org-structure/positions/overview|Positions]]
- [[database/schemas/org-structure|Org Structure Schema]]
