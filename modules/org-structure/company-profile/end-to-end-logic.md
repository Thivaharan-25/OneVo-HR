# Companies - End-to-End Logic

**Module:** Org Structure  
**Feature:** Company Setup

This file is retained for older links. Company records are stored in `legal_entities`. The canonical module overview is [[modules/org-structure/legal-entities/overview|Companies / Legal Entities]].

---

## Create Company

```text
POST /api/v1/org/legal-entities
  -> LegalEntityController.Create(CreateLegalEntityCommand)
    -> [RequirePermission("org:manage")]
    -> Validate name, country, currency, optional registration/tax fields
    -> LegalEntityService.CreateAsync(command, ct)
      -> 1. Validate country exists
      -> 2. Default currency from country when omitted
      -> 3. Create `legal_entities` row scoped to tenant
      -> 4. Publish LegalEntityCreated
      -> 5. If country set, publish LegalEntityCountrySet
    -> 201 Created
```

## Update Company

```text
PUT /api/v1/org/legal-entities/{id}
  -> LegalEntityController.Update(id, UpdateLegalEntityCommand)
    -> [RequirePermission("org:manage")]
    -> Validate entity belongs to current tenant
    -> LegalEntityService.UpdateAsync(id, command, ct)
      -> 1. Validate country exists
      -> 2. Update Company registration/settings fields
      -> 3. If country changed, publish LegalEntityCountrySet
    -> 200 OK
```

## Rules

- Single-company tenants have one Company.
- Multi-company tenants can have multiple Companies inside the same tenant.
- Departments and positions must belong to one Company.
- Position reporting cannot cross Companies.
- Root positions with no reporting manager are allowed.

## Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Invalid country_id | 422 | "Country not found" |
| Invalid currency_code | 422 | "Currency not supported" |
| Duplicate Company name | 409 | "Company name already exists" |
| Parent cycle | 422 | "Parent relationship would create a cycle" |
