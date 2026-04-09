# Dependents & Contacts — End-to-End Logic

**Module:** Core HR
**Feature:** Dependents & Emergency Contacts

---

## Add Dependent

### Flow

```
POST /api/v1/employees/{id}/dependents
  -> DependentController.Add(id, AddDependentCommand)
    -> [RequirePermission("employees:write")] or own profile
    -> DependentService.AddAsync(employeeId, command, ct)
      -> 1. Validate relationship type: spouse, child, parent, other
      -> 2. INSERT into employee_dependents
      -> 3. If is_emergency_contact = true:
         -> Also INSERT/UPDATE employee_emergency_contacts
      -> Return Result.Success(dependentDto)
```

## Manage Emergency Contacts

### Flow

```
POST /api/v1/employees/{id}/emergency-contacts
  -> ContactController.Add(id, AddContactCommand)
    -> [RequirePermission("employees:write")] or own profile
    -> ContactService.AddAsync(employeeId, command, ct)
      -> 1. Validate: name, phone required
      -> 2. INSERT into employee_emergency_contacts
      -> 3. If is_primary = true:
         -> Unset previous primary contact
      -> Return Result.Success(contactDto)
```

## Related

- [[modules/core-hr/dependents-contacts/overview|Dependents & Contacts Overview]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
