# Position Setup

**Area:** Org Structure  
**Trigger:** Admin creates or modifies the position structure (user action - configuration)  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `employees:read` (to browse existing positions for reports-to selection), `roles:manage` or `access:approve` (to configure position access templates)

---

## Preconditions

- Legal entity exists -> [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- Department exists within the target legal entity -> [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

---

## Flow Steps

### Step 1: Navigate to Positions
- **UI:** Sidebar -> Organization -> Positions -> list view grouped by legal entity and department
- **API:** `GET /api/v1/org/positions?legalEntityId={id}` - returns all positions for the selected legal entity

### Step 2: Select Legal Entity Context
- **UI:** Legal entity switcher in the Org Structure top bar, similar to a workspace selector.
- If the user can access one legal entity, that entity is auto-selected and the switcher is hidden or read-only.
- If the user can access multiple legal entities, the user selects the working legal entity before opening Positions.
- Positions list, department pickers, reports-to pickers, create forms, edit forms, and reporting tree all use the active legal entity context.

### Step 3: Create Position
- **UI:** Click "Add Position" -> side panel or modal within the active legal entity context. The form does not show Legal Entity as an editable field.

| Field | Required | Notes |
|:------|:---------|:------|
| Position Name | Yes | Unique within the legal entity |
| Department | Yes | Dropdown filtered to departments belonging to the selected legal entity |
| Position Type | Yes | `unique` or `pooled` |
| Capacity / Max Occupancy | Yes | Integer >= 1; represents the headcount ceiling for this position. `unique` positions must have max occupancy 1 |
| Reports To | No | Position picker filtered to same legal entity; leave blank for root positions |
| Position Access Templates | No | Optional role/scope templates used to generate access grants when an employee is placed into the position. Visible only to users with `roles:manage` or `access:approve` |

- **API:** `POST /api/v1/org/positions`
- **DB:** `positions` - new record with `legal_entity_id` from the active context, `department_id`, `position_type`, `reports_to_position_id` (nullable), `max_occupancy`
- **Backend guard:** the selected legal entity context is still validated server-side; the department and reports-to position must belong to that legal entity.

### Step 4: Configure Position Access Templates
- **UI visibility:** This section is hidden from users who do not have `roles:manage` or `access:approve`.
- **Purpose:** A position access template defines the default access generated when an employee is onboarded, assigned, transferred, or promoted into the position. The position itself is not the active permission grant.
- **Fields per template:** Role, scope type, scope target, sensitivity, `requires_approval`, effective start rule, optional effective end rule.
- **HR coverage rule:** For HR positions, the scope is the employee coverage area, not necessarily the position's own department. Example: an HR employee may sit in the HR department while the template grants `Department = EngineeringDepartmentId`.
- **Approval rule:** If `requires_approval = true`, the grant can be activated immediately only when the actor performing the employee movement has `roles:manage` or `access:approve`. Otherwise the backend creates an access approval request.
- **Target department rule:** Approval routing uses the target position's department, not the actor's department.
- **Pooled position rule:** When editing access on a pooled position, the UI must force the authorized user to choose:
  - Apply to the position template, affecting all current and future occupants.
  - Apply only to the current employee during assignment, creating an employee-specific grant or override.

Example templates:

| Position | Template role | Scope | Approval |
|:---------|:--------------|:------|:---------|
| Software Engineer | Employee | `Own` | Not required |
| Engineering Team Lead | Team Manager | `DirectReports` | Not required unless configured sensitive |
| HR Manager - Engineering | HR Manager | `Department = EngineeringDepartmentId` | Required |

### Step 5: Save
- **UI:** Click "Create Position" -> position appears in the list under the selected department
- **API:** Returns `PositionDto` with current occupancy count (0 for new positions), capacity, and access template summary visible only to access-authorized users

---

## Variations

### Root Position (No Reporting Manager)
- Leave Reports To blank
- System accepts the position; no warning is shown for intentional root positions (CEO, Country Head, etc.)
- If a root position is unexpected (e.g., a non-executive role), the org chart flags it visually but does not block creation

### Reporting Manager Position Is Vacant
- Admin selects a reports-to position that has 0 current occupants
- System accepts and shows: "Reporting manager will be unresolved until this position is staffed"
- Does not block creation or assignment

### Template-Based Bulk Creation
- **UI:** Select a department -> click "Suggest Positions"
- System generates a suggested set of positions based on the department name (e.g., Engineering -> Engineering Manager x 1, Tech Lead x 5, Senior Engineer x 30, Software Engineer x 60)
- Admin edits capacity and reports-to for each suggestion in a table view; unneeded rows can be removed
- Click "Create All" -> system creates each position individually; each inherits the legal entity and department context
- **API:** `POST /api/v1/org/positions/bulk` - accepts an array of position commands; returns per-item results

### Multi-Company: Apply Template Across Legal Entities
- **UI:** After reviewing the suggested position set, admin sees "Apply to other companies" toggle
- Select one or more additional legal entities -> system creates separate, independent position records per legal entity
- Each legal entity's positions use that entity's departments (resolved by department name match within the target entity)
- If a matching department does not exist in a target legal entity, that entity is skipped with a warning; it does not block creation for other entities

### Edit Existing Position
- **UI:** Click a position -> edit panel; all org fields editable except Legal Entity (immutable after creation)
- Capacity reductions below current occupancy are blocked: "Reduce capacity: 3 employees currently assigned"
- Reports-to changes are validated to remain within the same legal entity
- Position access template edits require `roles:manage` or `access:approve`
- For pooled positions, template edits warn that all current and future occupants can be affected
- **API:** `PUT /api/v1/org/positions/{id}`

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate position name in legal entity | Validation fails | "A position with this name already exists in [Legal Entity]" |
| Department not in selected legal entity | Validation fails | "Department does not belong to the selected legal entity" |
| Reports-to in a different legal entity | Validation fails | "Reporting position must be in the same legal entity" |
| Circular reporting chain | Validation fails | "Cannot set reporting line - would create a circular reporting chain" |
| Capacity set below current occupancy | Blocked | "Cannot reduce capacity below current headcount of [N]" |
| Legal entity not found or inactive | 422 | "Legal entity not found or is inactive" |
| User lacks access authority | Access template controls hidden or API blocked | "You do not have permission to configure position access" |

---

## Events Triggered

- `PositionCreated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `PositionUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `PositionAccessTemplateCreated` -> emitted only when an access-authorized user creates a template
- `PositionAccessTemplateUpdated` -> emitted only when an access-authorized user changes a template

---

## Related Flows

- [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Auth-Access/access-policy|Access Policy Reference]]

---

## Module References

- [[modules/org-structure/overview|Org Structure]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/departments/overview|Departments]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
