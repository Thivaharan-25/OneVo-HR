# Permission Assignment

**Area:** Auth & Access  
**Trigger:** Admin assigns roles, permission overrides, or approves position-generated access  
**Required Permission(s):** `roles:manage` to edit role/template setup; `position:approve` to approve generated position access

---

## Phase 1 Source of Truth

Phase 1 uses simple access language:

- Role granted
- Can manage employees in
- Selected departments
- Selected positions
- Entire company

Do not expose internal permission-boundary codes in tenant-admin UX.

Management coverage is the single source for employee visibility and Phase 1 approval routing.

Workflow Engine is not used for Phase 1 role assignment, position access, transfer approval, or promotion approval.

---

## Permission Surfaces

| Surface | Purpose |
|:---|:---|
| Security Roles | Tenant/module authority, stored in `roles`, `role_permissions`, and `user_roles` |
| Position-Based Access | Default role from assigned position |
| Management Coverage | Position, department, and company-wide employee visibility plus approval ownership |
| Employee Overrides | Explicit authorized permission grant/revoke for a specific user |
| Access Approval Requests | Lightweight Phase 1 approval for sensitive access |

---

## Assign Security Role Directly

An authorized admin can assign a role directly to a user/employee.

The assignment may include:

- Role
- Effective dates
- Reason / audit note

Direct role assignment grants actions only. It does not create employee visibility; management coverage does.

---

## Position-Based Grant

When an employee is assigned, transferred, or promoted into a position that has **Grant system access from this position** enabled:

1. Load Role granted.
2. Load Requires approval.
3. Load the target employee and management coverage owners.
4. If actor has authority and approval is not required, create/schedule `user_roles`.
5. Otherwise create an approval request and assign it to the single eligible owner resolved from management coverage.

The position's role is the deterministic default grant from that position.

---

## Approve Generated Access

Triggered by onboarding, transfer, promotion, or position assignment when:

- The position access rule has Requires approval checked.
- The actor lacks authority to apply the access directly.

Owner resolution:

1. Position coverage owners in order: Primary owner, Backup owner 1, Backup owner 2, etc.
2. Department coverage owners in the same order.
3. Company-wide coverage owners in the same order.
4. Routing issue.

If no valid owner exists, create a routing issue. Do not guess, assign randomly, or send duplicate approval requests.

Owner sees employee, source action, requester, target position, Role granted, Can manage employees in, effective date, and reason.

Actions:

- Approve
- Reject
- Add comment

Approval creates/schedules the `user_roles` grant. Rejection leaves the employee movement intact but keeps sensitive access inactive.

---

## Employee Overrides

Use overrides for exceptional cases only. Overrides must be audited and should be time-bound when possible.

Overrides can grant or revoke specific permissions. They do not define employee visibility or approval routing.

---

## Effective Permission Resolution

1. Tenant entitlement and runtime feature flags decide what the tenant has.
2. Roles decide what actions a user can perform.
3. Management coverage decides employee visibility and approval ownership.
4. Backend returns effective capabilities and navigation through `/api/v1/me/app-context`.

---

## Related

- [[Userflow/Auth-Access/role-creation|Role Creation]]
- [[Userflow/Auth-Access/access-policy|Management Coverage Reference]]
- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
