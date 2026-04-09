# Reference Data — End-to-End Logic

**Module:** Infrastructure
**Feature:** Reference Data (Countries)

---

## List Countries

### Flow

```
GET /api/v1/countries
  -> CountryController.List()
    -> [Authenticated]
    -> ReferenceDataService.GetCountriesAsync(ct)
      -> 1. Query countries table (global — no tenant filter)
      -> 2. Cache in Redis (no expiry — static data)
      -> Return Result.Success(countryDtos)
```

### Key Rules

- **Countries table is NOT tenant-scoped** — global reference data.
- **Seeded at application startup** from ISO 3166-1 data.
- **Used by:** leave policies (country-specific), employee profiles (nationality), payroll (tax config).

## Related

- [[modules/infrastructure/reference-data/overview|Overview]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[backend/shared-kernel|Shared Kernel]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
