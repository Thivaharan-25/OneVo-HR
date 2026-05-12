# Company Registration Profile - End-to-End Logic

**Module:** Org Structure  
**Feature:** Company Registration Profile

---

## Update Company Registration Profile

### Flow

```text
PUT /api/v1/company-profile
  -> CompanyProfileController.Update(UpdateCompanyProfileCommand)
    -> [RequirePermission("settings:admin")]
    -> FluentValidation: registered name required, registration_number format valid,
       country_id must reference valid country, currency_code must be valid ISO 4217,
       address_json schema validated
    -> CompanyProfileService.UpdateAsync(command, ct)
      -> 1. Validate country_id exists in countries table
      -> 2. Default currency_code from the selected country when omitted
      -> 3. Update current tenant company registration profile
      -> 4. If country changed, publish CompanyProfileCountrySet
      -> Return Result<CompanyProfileDto>
    -> 200 OK
```

The profile is tenant-local registration/compliance data. It must not be used to model another operating company inside the same tenant.

## Get Company Registration Profile

### Flow

```text
GET /api/v1/company-profile
  -> [RequirePermission("settings:admin")]
  -> CompanyProfileService.GetAsync(ct)
    -> 1. Query profile filtered by current tenant_id
    -> 2. Include country navigation property
    -> 3. Return CompanyProfileDto
  -> 200 OK
```

## Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Invalid country_id | 422 | "Country not found" |
| Invalid currency_code | 422 | "Currency not supported" |
| Missing required fields | 400 | Validation errors |

## Related

- [[modules/org-structure/legal-entities/overview|Overview]]
- [[modules/infrastructure/reference-data/overview|Reference Data]]
- [[modules/shared-platform/company-connections/overview|Company Connections]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
