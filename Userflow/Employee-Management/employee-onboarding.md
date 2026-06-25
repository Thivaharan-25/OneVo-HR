# Employee Onboarding

**Area:** Employee Management  
**Trigger:** Authorized employee-management user clicks "Add Employee" - Sidebar -> Employees -> Add Employee  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `position:approve` (approve position assignment/access impact), `roles:manage` (edit position access templates), `org:manage` (change department or create position inline)

---

## Preconditions

- Company (legal entity) exists and is selectable from the topbar -> [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- Department exists within the selected Company -> [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Position exists in the selected Company and department -> [[Userflow/Org-Structure/position-setup|Position Setup]]
- Phase 1 Checklist Templates are configured for onboarding tasks. Workflow Engine onboarding templates are Phase 2.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

---

## Compact Add Employee Flow

Add Employee is a compact create flow, not a five-step wizard. The form should collect only the fields needed to create the employee record, primary employment assignment, generated user account, invitation, and onboarding checklist tasks.

**Company context:** The form inherits the Company selected in the topbar. The backend resolves `legal_entity_id` from the selected Company. The form does not expose a legal entity dropdown.

**API:** `GET /api/v1/org/departments?legalEntityId={id}`, `GET /api/v1/org/positions?legalEntityId={id}` - called on entry to populate dropdowns, where `legalEntityId` is resolved from the topbar-selected Company.

---

## Required Fields

| Field | Required | Notes |
|:------|:---------|:------|
| Full Name | Yes | May be split into first/last name internally |
| Work Email | Yes | Unique across the tenant |
| Company | Read-only | Inherited from topbar-selected Company; `legal_entity_id` resolved internally. Single-company tenants may hide this field. |
| Department | Yes | Filtered to departments belonging to the selected Company |
| Position | Yes | Filtered to the selected Company and department |
| Employment Type | Yes | e.g., Full-time, Part-time, Contract |
| Start Date | Yes | |
| Work Mode | Conditional | Required when tenant policy needs it |
| Employee Number | Conditional | Required when tenant policy does not auto-generate it |

- Selecting a position resolves: capacity check, reporting line, department/Company context, and generated access from **Grant system access from this position**.
- Reporting manager is never selected manually during onboarding. It is derived from the selected position's reporting position.
- If the selected position reports to a vacant unique position: onboarding can continue, but the UI shows "Reporting manager will be unresolved until the parent position is staffed."
- If no suitable position exists yet, admin can create one inline (requires `org:manage`) -> [[Userflow/Org-Structure/position-setup|Position Setup]].
- Phone, address, emergency contacts, dependents, profile photo, bank details, and consent confirmations are completed by the employee after invitation unless the tenant explicitly requires them during creation.

---

## Access Handling

- If the actor has authority, the UI displays Role granted, Can manage employees in, and Requires approval from the selected position. These values are deterministic output from the selected position.
- If the actor lacks authority, the UI must not show role lists, permission details, or internal controls. The UI may show only: "Access changes require approval."
- Position access with `requires_approval = false` is materialized as `user_roles` after the employee and user account are created when direct apply is allowed.
- Position access with `requires_approval = true`, or any access applied by an actor without valid authority, creates an approval request.
- Approval routing uses management coverage:
  1. position coverage owners in order;
  2. department coverage owners in order;
  3. company-wide coverage owners in order;
  4. routing issue.
- If no valid owner exists, create a routing issue. Do not notify unrelated owners and do not guess.
- For pooled positions, position access-rule edits affect all current and future occupants.
- Module grants remain bounded by the tenant's active module entitlements.

---

## Create And Invite

- **UI:** Summary of all entered details. Click "Create Employee and Send Invite" to submit.
- **No invite method selection.** Onboarding always sends an email invitation. The employee uses SSO or password setup depending on tenant settings and allowed login methods - the admin does not choose.
- **API:** `POST /api/v1/employees`
- **Backend:** `EmployeeService.CreateAsync()` -> [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- **DB:** `employees.employment_status` set to `onboarding`

System creates behind the scenes:

1. Person record
2. Employee / employment record
3. Position assignment
4. User account
5. Policy assignments (time off, attendance, monitoring per legal entity)
6. Onboarding tasks
7. Approved or non-approval-required position access grants applied; approval-required sensitive grants created as pending requests when needed
8. Onboarding checklist tasks created from `checklist_templates`
9. Email invitation sent to the employee

---

## After Invitation (Employee Actions)

### Employee Receives Invitation
- Employee gets email -> clicks link -> accepts invite using password setup or SSO (depending on tenant settings and allowed login methods) -> completes profile.
- **API:** `/api/v1/auth/invitations/{token}`

### Employee Completes Onboarding Checklist
- Employee and admin see the generated checklist (IT setup, badge, training, docs to sign).
- Items are ticked off as completed.
- When all required onboarding items are done: `employees.employment_status` -> `active`.
- **Backend:** Phase 1 checklist/task completion updates onboarding state directly. Workflow Engine completion is Phase 2.

---

## Variations

### Single-company tenant
- Company context is pre-selected and the Company field may be hidden entirely.

### When generated access needs adjustment
- Authorized users adjust in Section 4 before submitting.
- For a unique position, changes normally apply only to this employee's assignment.
- For a pooled position, position access-rule edits affect all current and future occupants.
- Users without the required management coverage and `position:approve` cannot approve generated access. Users without `roles:manage` cannot edit position access templates.

### When monitoring is enabled for tenant
- Required Legal & Privacy items are shown during invite acceptance. If monitoring policy changes later, the dynamic Legal & Privacy notice appears on next login or before affected collection starts -> [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
- Agent deployment instructions generated -> [[Userflow/Monitoring/agent-deployment|Agent Deployment]]

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate work email in tenant | Section 1 validation fails | "An employee with this email already exists" |
| Duplicate employee number in Company | Section 2 validation fails | "Employee number already exists for this Company" |
| Position at capacity | Section 3 validation fails | "This position has reached its capacity" |
| Position in different Company | Section 3 validation fails | "Position does not belong to the selected Company" |
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
- [[Userflow/Auth-Access/access-policy|Management Coverage Reference]]
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
- [[Userflow/Auth-Access/access-policy|Management Coverage Reference]]
- [[backend/notification-system|Notification System]]
