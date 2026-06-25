# Position Setup

**Area:** Org Structure  
**Trigger:** Admin creates or edits a position  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `roles:manage` to edit position access; `position:approve` to approve generated position access

---

## Phase 1 Source of Truth

Positions are the source of org structure, reporting lines, occupancy, optional default access, and management coverage. Management coverage is the single source for employee visibility and Phase 1 approval routing.

Position setup is Company-context first. The selected Company in the topbar is the operating boundary for the form. Internally, that Company maps to `legal_entity_id`; admins do not select legal entity inside the Create/Edit Position modal.

The Create/Edit Position modal has two layers:

1. **Core Position Structure** - always visible.
2. **Grant system access from this position** - optional block, hidden until the admin enables it.

No Phase 1 position flow depends on the Workflow Engine. Sensitive access uses a lightweight approval record and notifications to the single eligible owner resolved from management coverage.

---

## Core Position Structure

| Field | Required | Notes |
|:------|:---------|:------|
| Position name | Yes | Unique within the selected Company |
| Position code | Optional | Stable import/integration code |
| Company context | Yes | Comes from the topbar-selected Company; maps internally to `legal_entity_id` |
| Department | Yes | Must belong to the selected Company |
| Reports to | Conditional | Required unless this is a root position; same-Company `unique` position |
| Type | Yes | `unique` capacity 1 or `pooled` capacity > 1 |
| Capacity / max occupancy | Yes | `unique` requires 1; `pooled` must be >= 1 |
| Status | Yes | Active or inactive |
| Description / notes | Optional | Internal admin note |

Company context is not decorative. Positions belong to one Company, departments belong to one Company, and reporting lines do not cross Companies. Internally this boundary is stored as `legal_entity_id`.

---

## Optional Access Block

The access block appears only after the admin clicks **Grant system access from this position**.

| Field | Required | Notes |
|:------|:---------|:------|
| Role granted | Yes | Dropdown of tenant roles; include a + button to create a new role without leaving the position screen |
| Can manage employees in | Yes | Selected positions, selected departments, or entire company |
| Department selector | Conditional | Multi-select shown only for Selected departments; limited to the selected Company |
| Position selector | Conditional | Multi-select shown only for Selected positions; limited to the selected Company |
| Requires approval before access is applied | Optional | Checkbox only. Unchecked applies access automatically; checked creates an approval request before access becomes active |

Admin-facing management coverage options are only:

- Selected departments
- Selected positions
- Entire company

If **Entire company** is selected, no selector is shown and the UI displays: "This position can manage employees across the selected company."

Do not expose these terms in the tenant-admin UI: scope, coverage area, reporting tree, direct reports, fallback priority, secondary approver, priority number. Use: **Can manage employees in**, **Primary owner**, **Backup owner 1**, **Backup owner 2**, **System access from reporting structure**, **Make primary**.

> Primary owner / Backup owner labels are display labels for ordered management coverage owners. They are not hardcoded routing slots. Backend routing must support any number of active coverage owners. For monitoring alerts, recipient selection is availability-based through Monitoring Policy. For approval routing, owners are ordered by `owner_order` and permission checks; if the first owner is unavailable and the workflow/policy requires availability-aware routing, continue to the next eligible owner.

If **Requires approval** is checked, access generated from this position remains pending until the management coverage resolver assigns one eligible owner. There is no workflow picker and no approval-flow selector in Phase 1.

---

## Reports-To Generated Coverage

When Position A reports to Position B, Position B automatically gets locked position-level management coverage over Position A. This appears in Position B's **Can manage employees in** list with a lock/system indicator and cannot be removed manually.

If an admin tries to remove locked generated coverage, block it and show:

```text
This access comes from the reporting structure. Change the position's Reports to value to remove it.
```

Example: Backend Engineer reports to Backend Lead. Backend Lead automatically gets **Can manage employees in: Backend Engineer**. If Frontend Engineer also reports to Backend Lead, Backend Lead also gets **Frontend Engineer**.

Generated reporting-structure coverage is access/routing data. The org chart still renders only the Reports to relationship.

---

## Manual Coverage And Owner Order

Manual coverage can be added through **Grant system access from this position**. Supported levels are only:

1. Position coverage.
2. Department coverage.
3. Company-wide coverage.

There is no employee-specific coverage.

For each covered target, owners are ordered as Primary owner, Backup owner 1, Backup owner 2, and so on. The first position that covers a target becomes Primary owner. Later positions become backups. The UI must not expose numeric order or fallback checkboxes.

When adding coverage to a target that already has an owner, show an inline note under the selected chip/list row:

```text
Backend Engineer is already managed by Backend Lead as Primary owner. HR Manager will be added as Backup owner 1.
```

Show one action link: **Make primary**.

If clicked, confirm:

```text
Make HR Manager the Primary owner for Backend Engineer? Backend Lead will move to Backup owner 1.
```

On confirm, reorder the owners for that target and shift existing owners down. Keep locked reporting-structure coverage present.

---

## Position List

The position list should use concise operational columns:

| Column | Notes |
|:---|:---|
| Position | Name and code |
| Department | Department inside the selected Company |
| Company | Company boundary |
| Type | Unique or pooled |
| Occupancy | Current occupants / capacity |
| Reports to | Reporting position |
| Role granted | Configured role from the optional access block |
| Manages employees in | Compact chips such as Backend Engineer, Engineering, Entire company; generated reporting-structure coverage has a lock/system indicator |
| Access status | Active, pending approval, or inactive |
| Status | Active/inactive |
| Actions | View/edit, assign, deactivate where permitted |

---

## Org Chart

The org chart uses the Reports to relationship only. Do not render department or company-wide management coverage as org chart children. Coverage is access/routing, not org structure.

Cards may show:

- Position name
- Assigned employee or vacancy
- Occupancy
- Department
- Quick vacancy/access badges

Editing opens the position detail/modal. Do not edit permissions directly on chart cards.

---

## Multi-Position Assignment Model

An employee may hold multiple active position assignments, but exactly one is the **Primary Employment Assignment**.

The primary assignment is the only source for:

- Primary Company
- Time Off policy
- Attendance / clock-in policy
- Work schedule
- Holiday calendar
- Payroll / statutory employment context

Additional assignments are **Additional Authority Assignments**. They may grant role/access/approval authority, including cross-Company authority, but they must not create a second Time Off policy, schedule, attendance policy, payroll context, or primary Company.

Hard rules:

- One employee cannot hold two active employment assignments inside the same Company.
- If a second seat is needed inside the same Company, use transfer or promotion.
- Cross-legal-entity authority assignments are allowed.
- Cross-legal-entity reporting lines are not allowed.

---

## Save Behavior

1. Resolve the selected Company from the topbar and map it to `legal_entity_id`.
2. Validate the actor has `org:manage` in that Company.
3. Validate department and reporting position belong to that Company.
4. Validate occupancy and reporting-cycle rules.
5. Create/update `positions`.
6. Create/update locked generated management coverage when Reports to changes.
7. If access is enabled, persist the position's role grant rule and manual management coverage.
8. If approval is required, generated access stays pending until approved through the management coverage resolver.
9. Notify the single eligible owner through Notifications; Phase 1 does not invoke Workflow Engine.

---

## Error Scenarios

| Scenario | User sees |
|:---|:---|
| Duplicate position name in Company | "A position with this name already exists in this Company." |
| Department belongs to another Company | "Department does not belong to the selected Company." |
| Reports-to position belongs to another Company | "Reporting position must be in the same Company." |
| Circular reporting chain | "This reporting line would create a cycle." |
| Capacity below current occupancy | "Cannot reduce capacity below current occupancy." |
| Remove locked reporting-structure coverage | "This access comes from the reporting structure. Change the position's Reports to value to remove it." |
| Approval required | Access remains pending and approvers are notified |

---

## Events Triggered

- `PositionCreated`
- `PositionUpdated`
- `ManagementCoverageGenerated`
- `ManagementCoverageReordered`
- `PositionAccessGrantRuleCreated`
- `PositionAccessGrantRuleUpdated`
- `AccessGrantRequested` when access requires approval

---

## Related Flows

- [[Userflow/Org-Structure/legal-entity-setup|Company Setup]]
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Auth-Access/access-policy|Management Coverage Reference]]
