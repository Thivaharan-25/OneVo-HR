# Legal Entities - End-to-End Logic

**Module:** Org Structure  
**Feature:** Legal Entities

This file is retained for older links. The canonical module overview is [[modules/org-structure/legal-entities/overview|Legal Entities]].

---

## Create Legal Entity

```text
POST /api/v1/org/legal-entities
  -> LegalEntityController.Create(CreateLegalEntityCommand)
    -> [RequirePermission("org:manage")]
    -> Validate name, country, currency, optional registration/tax fields
    -> LegalEntityService.CreateAsync(command, ct)
      -> 1. Validate country exists
      -> 2. Default currency from country when omitted
      -> 3. Create legal_entities row scoped to tenant
      -> 4. Publish LegalEntityCreated
      -> 5. If country set, publish LegalEntityCountrySet
    -> 201 Created
```

## Update Legal Entity

```text
PUT /api/v1/org/legal-entities/{id}
  -> LegalEntityController.Update(id, UpdateLegalEntityCommand)
    -> [RequirePermission("org:manage")]
    -> Validate entity belongs to current tenant
    -> LegalEntityService.UpdateAsync(id, command, ct)
      -> 1. Validate country exists
      -> 2. Update legal entity registration/settings fields
      -> 3. If country changed, publish LegalEntityCountrySet
    -> 200 OK
```

## Rules

- Single-company tenants have one legal entity.
- Multi-company tenants can have multiple legal entities inside the same tenant.
- Departments and positions must belong to one legal entity.
- Position reporting cannot cross legal entities.
- Root positions with no reporting manager are allowed.

## Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Invalid country_id | 422 | "Country not found" |
| Invalid currency_code | 422 | "Currency not supported" |
| Duplicate legal entity name | 409 | "Legal entity name already exists" |
| Parent cycle | 422 | "Parent relationship would create a cycle" |
