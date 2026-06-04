# Legal Entities - Testing

**Module:** Org Structure  
**Feature:** Legal Entities

This file is retained for older links. The canonical module overview is [[modules/org-structure/legal-entities/overview|Legal Entities]].

## Unit Test Coverage

- Create legal entity with valid country/currency succeeds.
- Duplicate legal entity name inside tenant is rejected.
- Invalid country is rejected.
- Invalid currency is rejected.
- Parent legal entity cycle is rejected.
- Country change publishes `LegalEntityCountrySet`.

## Integration Test Coverage

- `POST /api/v1/org/legal-entities` requires `org:manage`.
- `GET /api/v1/org/legal-entities` returns only legal entities for current tenant.
- Single-company tenant can operate with one default legal entity.
- Multi-company tenant can create multiple legal entities.
- Department and position creation must reject legal entity mismatches.
