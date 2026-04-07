# Department Hierarchy

**Area:** Org Structure  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `employees:read` (to assign department head)

---

## Preconditions

- At least one legal entity exists → [[legal-entity-setup]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Departments
- **UI:** Sidebar → Organization → Departments → view org chart tree or list view
- **API:** `GET /api/v1/org/departments` (tree structure)

### Step 2: Create Department
- **UI:** Click "Add Department" → enter name, code
- **Validation:** Name unique within legal entity, code unique globally

### Step 3: Set Hierarchy
- **UI:** Select parent department (or set as root) → select legal entity → assign cost center (optional)
- **Backend:** DepartmentService.CreateAsync() → [[departments]]

### Step 4: Assign Department Head
- **UI:** Search and select employee as department head
- **API:** `POST /api/v1/org/departments`
- **DB:** `departments` — new record with `parent_department_id`, `head_employee_id`

### Step 5: View in Org Chart
- **UI:** Department appears in interactive org chart → expandable tree → shows head and employee count

## Variations

### When moving a department
- Change parent department → all sub-departments move with it
- Employee reporting lines may need review

### When user also has `employees:read-team`
- Can see all employees within the department from the department view

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Circular hierarchy | Validation fails | "Cannot set parent — would create circular reference" |
| Duplicate name in entity | Validation fails | "Department name already exists in this legal entity" |
| Delete with employees | Blocked | "Reassign 15 employees before deleting" |

## Events Triggered

- `DepartmentCreated` → [[event-catalog]]
- `DepartmentMoved` → [[event-catalog]]

## Related Flows

- [[legal-entity-setup]]
- [[team-creation]]
- [[employee-onboarding]]
- [[employee-transfer]]

## Module References

- [[departments]]
- [[org-structure]]
- [[cost-centers]]
