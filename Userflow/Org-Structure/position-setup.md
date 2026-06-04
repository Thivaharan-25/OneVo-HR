# Position Setup

**Area:** Org Structure  
**Trigger:** Admin creates or modifies the position structure (user action — configuration)  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `employees:read` (to browse existing positions for reports-to selection)

---

## Preconditions

- Legal entity exists → [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- Department exists within the target legal entity → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

---

## Flow Steps

### Step 1: Navigate to Positions
- **UI:** Sidebar → Organization → Positions → list view grouped by legal entity and department
- **API:** `GET /api/v1/org/positions?legalEntityId={id}` — returns all positions for the selected legal entity

### Step 2: Select Legal Entity (multi-company tenants)
- **UI:** Legal entity selector at the top of the Positions page; defaults to the first active entity
- Single-company tenants skip this — the only legal entity is pre-selected and the selector is hidden

### Step 3: Create Position
- **UI:** Click "Add Position" → side panel or modal with the following fields:

| Field | Required | Notes |
|:------|:---------|:------|
| Position Name | Yes | Unique within the legal entity |
| Legal Entity | Yes | Pre-selected from Step 2; not editable inline |
| Department | Yes | Dropdown filtered to departments belonging to the selected legal entity |
| Capacity | Yes | Integer ≥ 1; represents the headcount ceiling for this position |
| Reports To | No | Position picker filtered to same legal entity; leave blank for root positions |
| Linked Roles / Permissions | No | Multi-select from tenant roles catalog; these are confirmed when an employee is placed into the position |

- **API:** `POST /api/v1/org/positions`
- **DB:** `positions` — new record with `legal_entity_id`, `department_id`, `reports_to_position_id` (nullable), `capacity`

### Step 4: Confirm Linked Roles
- **UI:** After selecting linked roles, a summary panel shows: "Assigning an employee to this position will grant: [role list]"
- Admin confirms or adjusts before saving
- Roles are stored as suggestions on the position; they are not applied to any employee until an assignment is made

### Step 5: Save
- **UI:** Click "Create Position" → position appears in the list under the selected department
- **API:** Returns `PositionDto` with current occupancy count (0 for new positions) and capacity

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
- **UI:** Select a department → click "Suggest Positions"
- System generates a suggested set of positions based on the department name (e.g., Engineering → Engineering Manager × 1, Tech Lead × 5, Senior Engineer × 30, Software Engineer × 60)
- Admin edits capacity and reports-to for each suggestion in a table view; unneeded rows can be removed
- Click "Create All" → system creates each position individually; each inherits the legal entity and department context
- **API:** `POST /api/v1/org/positions/bulk` — accepts an array of position commands; returns per-item results

### Multi-Company: Apply Template Across Legal Entities
- **UI:** After reviewing the suggested position set, admin sees "Apply to other companies" toggle
- Select one or more additional legal entities → system creates separate, independent position records per legal entity
- Each legal entity's positions use that entity's departments (resolved by department name match within the target entity)
- If a matching department does not exist in a target legal entity, that entity is skipped with a warning; it does not block creation for other entities

### Edit Existing Position
- **UI:** Click a position → edit panel; all fields editable except Legal Entity (immutable after creation)
- Capacity reductions below current occupancy are blocked: "Reduce capacity: 3 employees currently assigned"
- Reports-to changes are validated to remain within the same legal entity
- **API:** `PUT /api/v1/org/positions/{id}`

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate position name in legal entity | Validation fails | "A position with this name already exists in [Legal Entity]" |
| Department not in selected legal entity | Validation fails | "Department does not belong to the selected legal entity" |
| Reports-to in a different legal entity | Validation fails | "Reporting position must be in the same legal entity" |
| Circular reporting chain | Validation fails | "Cannot set reporting line — would create a circular reporting chain" |
| Capacity set below current occupancy | Blocked | "Cannot reduce capacity below current headcount of [N]" |
| Legal entity not found or inactive | 422 | "Legal entity not found or is inactive" |

---

## Events Triggered

- `PositionCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `PositionUpdated` → [[backend/messaging/event-catalog|Event Catalog]]

---

## Related Flows

- [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Org-Structure/job-family-setup|Job Hierarchy Setup]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]

---

## Module References

- [[modules/org-structure/overview|Org Structure]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
