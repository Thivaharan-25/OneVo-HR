# Employee Onboarding

**Area:** Employee Management  
**Trigger:** Authorized employee-management user clicks "Add Employee" - Sidebar -> Employees -> Add Employee  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `roles:manage` or `access:approve` (view/change generated access), `org:manage` (change department or create position inline)

---

## Preconditions

- Legal entity exists -> [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- Department exists within the target legal entity -> [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Position exists in the selected legal entity and department -> [[Userflow/Org-Structure/position-setup|Position Setup]]
- Onboarding workflow template configured -> [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

---

## The Form

The Add Employee form is a single flow with five named sections presented in order. The admin completes them sequentially; earlier sections must be valid before later sections unlock.

**API:** `GET /api/v1/org/legal-entities`, `GET /api/v1/org/departments?legalEntityId={id}`, `GET /api/v1/org/positions?legalEntityId={id}` - called on entry to populate dropdowns.

---

## Section 1: Identity Basics

| Field | Required | Notes |
|:------|:---------|:------|
| First Name | Yes | |
| Last Name | Yes | |
| Work Email | Yes | Unique across the tenant |

- Phone, address, emergency contacts, dependents, profile photo, bank details, and consent confirmations are completed by the employee after invitation - not collected here.

---

## Section 2: Employment Details

| Field | Required | Notes |
|:------|:---------|:------|
| Legal Entity | Yes | Dropdown from active legal entities; single-company tenants have one option pre-selected |
| Employee Number | Yes | Unique within the selected legal entity |
| Start Date | Yes | |
| Employment Type | Yes | e.g., Full-time, Part-time, Contract |

---

## Section 3: Position Assignment

| Field | Required | Notes |
|:------|:---------|:------|
| Department | Yes | Filtered to departments belonging to the selected legal entity |
| Position | Yes | Filtered to the selected legal entity and department |

- Selecting a position resolves: capacity check, reporting line, department/legal-entity context, and generated access from position access templates.
- If the selected position reports to a vacant unique position: onboarding can continue, but the UI shows "Reporting manager will be unresolved until the parent position is staffed."
- If no suitable position exists yet, admin can create one inline (requires `org:manage`) -> [[Userflow/Org-Structure/position-setup|Position Setup]].

---

## Section 4: Access Handling

- If the actor has `roles:manage` or `access:approve`, the UI displays generated access from the selected position's access templates. Actor can confirm, remove, replace, narrow, or add employee-specific access within entitlement boundaries.
- If the actor does not have `roles:manage` or `access:approve`, the UI must not show role lists, permission details, scope controls, or access-template details. The UI may show only: "Access changes require approval."
- Position access templates with `requires_approval = false` are materialized as `user_roles` after the employee and user account are created.
- Position access templates with `requires_approval = true` are materialized immediately only when the actor has `roles:manage` or `access:approve`; otherwise the backend creates an `access_grant_requests` record.
- Approval routing uses the selected target position's department:
  1. users with `roles:manage` or `access:approve` whose scope covers that department;
  2. tenant-wide `roles:manage` or `access:approve`;
  3. Tenant Admin.
- If multiple approvers match, notify all; first approval wins.
- For pooled positions, an authorized actor changing generated access must choose between applying the change to the position template for all occupants or only to this employee as an employee-specific grant/override.
- Module grants remain bounded by the tenant's active module entitlements.

---

## Section 5: Send Invite

- **UI:** Summary of all entered details. Click "Create Employee and Send Invite" to submit.
- **No invite method selection.** Onboarding always sends an email invitation. The employee uses SSO or password setup depending on tenant settings and allowed login methods - the admin does not choose.
- **API:** `POST /api/v1/employees`
- **Backend:** `EmployeeService.CreateAsync()` -> [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- **DB:** `employees.status` set to `"Onboarding"`

System creates behind the scenes:

1. Person record
2. Employee / employment record
3. Position assignment
4. User account
5. Policy assignments (leave, attendance, monitoring per legal entity)
6. Onboarding tasks
7. Approved or non-approval-required position-template access grants applied; approval-required sensitive grants created as pending requests when needed
8. Onboarding workflow instance created
9. Email invitation sent to the employee

---

## After Invitation (Employee Actions)

### Employee Receives Invitation
- Employee gets email -> clicks link -> accepts invite using password setup or SSO (depending on tenant settings and allowed login methods) -> completes profile.
- **API:** `/api/v1/auth/invitations/{token}`

### Employee Completes Onboarding Checklist
- Employee and admin see the generated checklist (IT setup, badge, training, docs to sign).
- Items are ticked off as completed.
- When all items are done: `employees.status` -> `"Active"`.
- **Backend:** `WorkflowService.CompleteStepAsync()` -> [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]

---

## Variations

### Single-company tenant
- Legal Entity is pre-selected and the field is hidden in Section 2.

### When generated access needs adjustment
- Authorized users adjust in Section 4 before submitting.
- For a unique position, changes normally apply only to this employee's assignment.
- For a pooled position, the UI forces a choice between updating the position template for all occupants or applying an employee-specific grant/override.
- Users without `roles:manage` or `access:approve` cannot view or edit these controls.

### When monitoring is enabled for tenant
- Required Legal & Privacy items are shown during invite acceptance. If monitoring policy changes later, the dynamic Legal & Privacy notice appears on next login or before affected collection starts -> [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
- Agent deployment instructions generated -> [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate work email in tenant | Section 1 validation fails | "An employee with this email already exists" |
| Duplicate employee number in legal entity | Section 2 validation fails | "Employee number already exists for this legal entity" |
| Position at capacity | Section 3 validation fails | "This position has reached its capacity" |
| Position in different legal entity | Section 3 validation fails | "Position does not belong to the selected legal entity" |
| No position selected | Section 3 blocked | Position is required |
| Access approval pending | Employee creation proceeds; sensitive grant inactive | "Access changes are pending approval" |

---

## Events Triggered

- `EmployeeCreated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `EmployeeOnboardingStarted` -> [[backend/messaging/event-catalog|Event Catalog]]
- `UserAccountCreated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `AccessGrantRequested` -> emitted when generated sensitive access needs approval
- `UserRoleAssigned` -> emitted when generated access is confirmed or does not require approval
- Notification: invitation email -> [[backend/notification-system|Notification System]]
- Notification: onboarding tasks assigned to admin -> [[backend/notification-system|Notification System]]

---

## Related Flows

- [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]]
- [[Userflow/Auth-Access/access-policy|Access Policy Reference]]
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]] - reverse flow
- [[Userflow/Employee-Management/profile-management|Profile Management]] - employee completes profile after invite
- [[Userflow/Data-Import/employee-csv-import|Employee CSV Import]] - bulk alternative: upload CSV, resolve org structure, confirm access impact, import and send invites

---

## Module References

- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/org-structure/positions/overview|Positions]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[backend/notification-system|Notification System]]
