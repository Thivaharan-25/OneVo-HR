# Dependent Management

**Area:** Employee Management  
**Required Permission(s):** `employees:read-own` (own dependents) or `employees:write` (admin)  
**Related Permissions:** `payroll:read` (view dependent-related benefits)

---

## Preconditions

- Employee exists and is active
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Dependents
- **UI:** Employee Profile → Dependents & Contacts tab
- **API:** `GET /api/v1/employees/{id}/dependents`

### Step 2: Add Dependent
- **UI:** Click "Add Dependent" → enter: name, relationship (spouse, child, parent), date of birth, gender, contact number → toggle "Emergency Contact" → save
- **API:** `POST /api/v1/employees/{id}/dependents`
- **Backend:** DependentService.AddAsync() → [[dependents-contacts]]
- **DB:** `employee_dependents` — record created

### Step 3: Manage Emergency Contacts
- **UI:** Mark any dependent or non-dependent as emergency contact → set priority order (primary, secondary)
- **DB:** `employee_emergency_contacts`

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No emergency contact | Warning on profile | "No emergency contact set" |
| Duplicate dependent | Warning | "A dependent with this name already exists" |

## Events Triggered

- `DependentAdded` → [[event-catalog]]

## Related Flows

- [[profile-management]]
- [[employee-onboarding]]

## Module References

- [[dependents-contacts]]
