# Legal Entities — End-to-End Logic

**Module:** Org Structure  
**Feature:** Legal Entities

---

## Create Legal Entity

### Flow

```
POST /api/v1/legal-entities
  -> LegalEntityController.Create(CreateLegalEntityCommand)
    -> [RequirePermission("settings:admin")]
    -> FluentValidation: name required, registration_number required + unique,
       country_id must reference valid country, address_json schema validated
    -> LegalEntityService.CreateAsync(command, ct)
      -> 1. Validate country_id exists in countries table
      -> 2. Check registration_number uniqueness within tenant
      -> 3. Build LegalEntity entity (is_active = true)
      -> 4. Persist to legal_entities table
      -> 5. Publish LegalEntityCreated domain event
      -> Return Result<LegalEntityDto>
    -> 201 Created
```

## List Legal Entities

### Flow

```
GET /api/v1/legal-entities
  -> [RequirePermission("settings:admin")]
  -> LegalEntityService.GetAllAsync(ct)
    -> 1. Query legal_entities filtered by tenant_id
    -> 2. Include country navigation property
    -> 3. Return List<LegalEntityDto>
  -> 200 OK
```

## Update Legal Entity

### Flow

```
PUT /api/v1/legal-entities/{id}
  -> [RequirePermission("settings:admin")]
  -> LegalEntityService.UpdateAsync(id, command, ct)
    -> 1. Load entity by id, verify ownership by tenant
    -> 2. If registration_number changed, re-validate uniqueness
    -> 3. Update fields (name, registration_number, country_id, address_json)
    -> 4. Persist changes
    -> 5. Publish LegalEntityUpdated domain event
    -> Return Result<LegalEntityDto>
  -> 200 OK
```

## Deactivate Legal Entity

### Flow

```
PUT /api/v1/legal-entities/{id}/deactivate
  -> [RequirePermission("settings:admin")]
  -> LegalEntityService.DeactivateAsync(id, ct)
    -> 1. Load entity
    -> 2. Check no active departments reference this legal entity
    -> 3. Check no active payroll connections reference this legal entity
    -> 4. Set is_active = false
    -> 5. Publish LegalEntityDeactivated event
    -> Return Result.Success()
  -> 200 OK
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Duplicate registration number | 409 | "Registration number already exists" |
| Invalid country_id | 422 | "Country not found" |
| Deactivate with active departments | 409 | "Cannot deactivate: active departments exist" |
| Entity not found | 404 | "Legal entity not found" |
| Missing required fields | 400 | Validation errors |

### Edge Cases

- Registration numbers may contain special characters (dashes, slashes) depending on country
- address_json is stored as JSONB, validated against a flexible schema allowing country-specific formats
- Deactivation is soft-delete; historical references from payroll runs remain intact

## Related

- [[legal-entities|Overview]]
- [[departments]]
- [[reference-data]]
- [[event-catalog]]
- [[error-handling]]
