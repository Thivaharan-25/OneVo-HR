# Department Hierarchy

**Area:** Org Structure  
**Trigger:** Admin creates or modifies department structure (user action — configuration)
**Required Permission(s):** `org:manage`  
**Related Permissions:** `employees:read` (to list positions for head position selection)

---

## Preconditions

- Legal entity exists → [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Departments
- **UI:** Sidebar → Organization → Departments → view org chart tree or list view
- **API:** `GET /api/v1/org/departments?legalEntityId={id}` (tree structure)

### Step 2: Create Department
- **UI:** Select legal entity → click "Add Department" → enter name
- **Validation:** Name unique within legal entity. Internal department code may be generated or edited by authorized admins, but normal setup does not require HR to provide a code.

### Step 3: Set Hierarchy
- **UI:** Select parent department inside the same legal entity, or set as root
- **Backend:** DepartmentService.CreateAsync() → [[modules/org-structure/departments/overview|Departments]]

### Step 4: Assign Department Head Position
- **UI:** Search and select a `unique`-type position (within the same legal entity) as the department head position
- **API:** `POST /api/v1/org/departments`
- **DB:** `departments` — new record with `parent_department_id`, `head_position_id`
- **Note:** The position may currently be vacant; UI shows the current occupant's name or "Vacant" if unoccupied

### Step 5: View in Org Chart
- **UI:** Department appears in interactive org chart → expandable tree → shows head and employee count

## Variations

### When moving a department
- Change parent department → all sub-departments move with it
- Employee reporting lines may need review

### When user also has `employees:read` with team/department policy
- Can see employees within scope of their access policy from the department view

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Circular hierarchy | Validation fails | "Cannot set parent — would create circular reference" |
| Duplicate name in legal entity | Validation fails | "Department name already exists in this legal entity" |
| Delete with employees | Blocked | "Reassign 15 employees before deleting" |

## Events Triggered

- `DepartmentCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `DepartmentMoved` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- [[Userflow/Org-Structure/team-creation|Team Creation]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]

## Module References

- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/overview|Org Structure]]

