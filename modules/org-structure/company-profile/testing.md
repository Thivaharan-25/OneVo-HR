# Companies - Testing

**Module:** Org Structure  
**Feature:** Company Setup

This file is retained for older links. Company records are stored in `legal_entities`. The canonical module overview is [[modules/org-structure/legal-entities/overview|Companies / Legal Entities]].

## Unit Test Coverage

- Create Company with valid country/currency succeeds.
- Duplicate Company name inside tenant is rejected.
- Invalid country is rejected.
- Invalid currency is rejected.
- Parent Company cycle is rejected.
- Country change publishes `LegalEntityCountrySet`.

## Integration Test Coverage

- `POST /api/v1/org/legal-entities` requires `org:manage`.
- `GET /api/v1/org/legal-entities` returns only Companies for current tenant.
- Single-company tenant can operate with one default Company.
- Multi-company tenant can create multiple Companies.
- Department and position creation must reject Company mismatches.
