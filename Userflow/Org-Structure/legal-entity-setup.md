# Legal Entity Setup

**Area:** Org Structure  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `settings:admin` (tenant-level config)

---

## Preconditions

- Tenant provisioned → [[tenant-provisioning]]
- Country data seeded in system → [[infrastructure]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Legal Entities
- **UI:** Sidebar → Organization → Legal Entities → click "Add Legal Entity"
- **API:** `GET /api/v1/org/legal-entities` (list existing)

### Step 2: Enter Entity Details
- **UI:** Form: name, registration number, tax ID, country, address, phone, email
- **Validation:** Name unique within tenant, registration number format per country

### Step 3: Configure Entity Settings
- **UI:** Set default currency, fiscal year start month, work week (Sun-Thu vs Mon-Fri), public holidays calendar
- **Backend:** LegalEntityService.CreateAsync() → [[legal-entities]]

### Step 4: Save
- **API:** `POST /api/v1/org/legal-entities`
- **DB:** `legal_entities` — new record created
- **Result:** Entity available for department assignment, payroll configuration, leave policies

## Variations

### When editing existing entity
- `PUT /api/v1/org/legal-entities/{id}` — update details
- Changes to fiscal year affect payroll and leave entitlement calculations

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate name | Validation fails | "A legal entity with this name already exists" |
| Invalid tax ID format | Validation fails | "Tax ID format invalid for selected country" |
| Entity has employees | Cannot delete | "Cannot delete — reassign employees first" |

## Events Triggered

- `LegalEntityCreated` → [[event-catalog]]

## Related Flows

- [[tenant-provisioning]]
- [[department-hierarchy]]
- [[payroll-provider-setup]]
- [[leave-policy-setup]]

## Module References

- [[legal-entities]]
- [[org-structure]]
