# Management Coverage Reference

**Area:** Auth & Access  
**Related:** [[Userflow/Auth-Access/permissions-reference|Permissions Reference]] - [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] - [[Userflow/Auth-Access/role-creation|Role Creation]]

---

## Phase 1 Source of Truth

A role answers **what the user can do**. Management coverage answers **which employees the user's position can manage** and who receives Phase 1 approval requests.

Tenant-admin UI must use simple language:

- Role granted
- Can manage employees in
- Selected departments
- Selected positions
- Entire company

Do not expose internal terms such as scope, coverage area, reporting tree, direct reports, fallback priority, secondary approver, or priority number in tenant-admin UX.

Phase 1 access does not depend on Workflow Engine. Sensitive position-derived access uses management coverage and lightweight approval records.

---

## Where Access Comes From

Employee visibility and approval routing come from management coverage:

| Source | Meaning |
|:---|:---|
| Reports to generated coverage | Locked position-level coverage from the reporting structure |
| Manual position coverage | Position can manage selected positions |
| Manual department coverage | Position can manage selected departments |
| Manual company-wide coverage | Position can manage the entire selected Company |

Roles and permission overrides decide actions. Management coverage decides employee visibility and approval ownership.

---

## Position-Based Access UI

When **Grant system access from this position** is enabled on a position:

| Field | Meaning |
|:---|:---|
| Role granted | Default granted role from this position |
| Can manage employees in | Selected positions, selected departments, or entire company |
| Requires approval | Access stays pending until an authorized actor approves |

Reports-to generated coverage appears as **System access from reporting structure**, is locked, and cannot be removed manually.

---

## Owner Order

For every covered target, keep ordered owners:

| UI label | Meaning |
|:---|:---|
| Primary owner | First eligible owner tried for the target |
| Backup owner 1 | Tried after Primary owner |
| Backup owner 2 | Tried after Backup owner 1 |

Admins can use **Make primary** to reorder owners. The UI must not expose numeric priority fields or fallback checkboxes. Backend queries enforce management coverage; the frontend never submits employee ID lists as authorization evidence.

---

## Approval Behavior

Access approval is required when:

- The position's access rule says approval is required.
- The actor lacks authority to apply the grant directly.
- A transfer or promotion changes position-derived access and the target access is sensitive.

Owner resolution in Phase 1:

1. Position coverage owners in order: Primary owner, Backup owner 1, Backup owner 2, etc.
2. Department coverage owners in the same order.
3. Company-wide coverage owners in the same order.
4. Routing issue.

If no valid owner exists, create a routing issue with: "No eligible owner could approve this request. Check position coverage and permissions." Do not guess, assign randomly, notify unrelated users, or send duplicate approval requests.

Direct apply for a CEO or explicit bypass is valid only when the product rule allows it and the action is audited.

---

## Transfer and Promotion

When transfer or promotion changes position-derived access:

1. Load target position's **Role granted**.
2. Load target position's **Can manage employees in** coverage and owner order.
3. Load target position's **Requires approval** state.
4. If direct apply is allowed and approval is not required, apply directly.
5. Otherwise create an approval request and assign it to the single eligible owner resolved from management coverage.

If the movement does not change position-derived access, do not regenerate access.

---

## Multi-Position Access

Primary Employment Assignment controls employment policy. Additional Authority Assignments may grant role/access/approval authority without changing time_off, schedule, attendance, payroll, holiday calendar, or primary legal entity.

One employee cannot hold two active employment assignments inside the same legal entity. Use transfer or promotion instead.

---

## Default Policy

If a user has no role grant and no employee visibility grant, they have no employee access except self-service routes explicitly allowed by permissions such as `employees:read-own`.
