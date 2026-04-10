# Legal Entity Setup

**Area:** Org Structure  
**Trigger:** Admin creates new legal entity (user action — configuration)
**Required Permission(s):** `org:manage`  
**Related Permissions:** `settings:admin` (tenant-level config)

---

## Preconditions

- Tenant provisioned → [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- Country data seeded in system → [[modules/infrastructure/overview|Infrastructure]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Legal Entities
- **UI:** Sidebar → Organization → Legal Entities → click "Add Legal Entity"
- **API:** `GET /api/v1/org/legal-entities` (list existing)

### Step 2: Enter Entity Details
- **UI:** Form: name, registration number, tax ID, country, address, phone, email
- **Validation:** Name unique within tenant, registration number format per country

### Step 3: Configure Entity Settings
- **UI:** Set default currency, fiscal year start month, work week (Sun-Thu vs Mon-Fri), public holidays calendar
- **Backend:** LegalEntityService.CreateAsync() → [[modules/org-structure/legal-entities/overview|Legal Entities]]

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

- `LegalEntityCreated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]]
- [[Userflow/Leave/leave-policy-setup|Leave Policy Setup]]

## Module References

- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/overview|Org Structure]]
