# Department Hierarchy

**Area:** Org Structure  
**Trigger:** Admin creates or modifies department structure (user action - configuration)  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `employees:read` (to list positions for head position selection)

---

## Preconditions

- A Company is selected in the topbar. Internally, the selected Company maps to `legal_entity_id`.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Departments
- **UI:** Sidebar -> Organization -> Departments -> view org chart tree or list view for the selected Company.
- **API:** `GET /api/v1/org/departments?view=tree` using selected Company context.

### Step 2: Create Department
- **UI:** With Company selected in the topbar, click "Add Department" and enter name.
- **Validation:** Name unique within the selected Company. Internal department code may be generated or edited by authorized admins, but normal setup does not require HR to provide a code.

### Step 3: Set Hierarchy
- **UI:** Select parent department inside the selected Company, or set as root.
- **Backend:** DepartmentService.CreateAsync() -> [[modules/org-structure/departments/overview|Departments]]

### Step 4: Assign Department Head Position
- **UI:** Search and select a `unique`-type position inside the selected Company as the department head position.
- **API:** `POST /api/v1/org/departments`
- **DB:** `departments` - new record with `parent_department_id`, `head_position_id`, and internal `legal_entity_id` from selected Company.
- **Note:** The position may currently be vacant; UI shows the current occupant's name or "Vacant" if unoccupied.

### Step 5: View in Org Chart
- **UI:** Department appears in interactive org chart -> expandable tree -> shows head and employee count.

## Variations

### When moving a department
- Change parent department -> all sub-departments move with it.
- Employee reporting lines may need review.

- Can see employees allowed by management coverage from the department view.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Circular hierarchy | Validation fails | "Cannot set parent - would create circular reference" |
| Duplicate name in Company | Validation fails | "Department name already exists in this Company" |
| Delete with employees | Blocked | "Reassign 15 employees before deleting" |

## Events Triggered

- `DepartmentCreated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `DepartmentMoved` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Org-Structure/legal-entity-setup|Company Setup]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]

## Module References

- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/overview|Org Structure]]
