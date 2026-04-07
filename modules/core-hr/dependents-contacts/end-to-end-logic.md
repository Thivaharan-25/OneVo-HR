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

- [[dependents-contacts|Dependents & Contacts Overview]]
- [[employee-profiles]]
- [[offboarding]]
- [[event-catalog]]
- [[error-handling]]
