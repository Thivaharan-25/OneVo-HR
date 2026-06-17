# Legal Entity Setup

**Area:** Org Structure  
**Trigger:** Admin configures single-company or multi-company structure in Setup / Control Application  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `settings:read`

---

## Preconditions

- Tenant has been provisioned by ONEVO through Developer Platform.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Choose Company Mode
- **UI:** Setup / Control Application -> Organization -> Legal Entities.
- **Options:** Single-company mode or multi-company mode.
- **Rule:** Single-company mode creates one default legal entity. Multi-company mode allows multiple legal entities under the same tenant.

### Step 2: Create Legal Entity
- **UI:** Enter legal entity name, registration number, country, currency, tax identifier if needed, and address.
- **API:** `POST /api/v1/org/legal-entities`
- **Validation:** Name must be unique within tenant. Currency must be a valid ISO 4217 code. Country must be supported.

### Step 3: Parent / Subsidiary Relationship
- **UI:** Optional parent legal entity selector.
- **Rule:** Parent relationship is for setup and reporting context only. It must not allow departments or positions to be shared across legal entities.

### Step 4: Save
- **Backend:** LegalEntityService.CreateAsync() -> [[modules/org-structure/legal-entities/overview|Legal Entities]]
- **DB:** `legal_entities`
- **Result:** Legal entity becomes available for department setup, position setup, employee onboarding, leave policy assignment, attendance policy assignment, and import validation.

## Rules

- Departments belong to one legal entity.
- Positions belong to one legal entity.
- Employees have one primary legal entity in Phase 1.
- Positions cannot be shared across legal entities.
- A position can report only to another position inside the same legal entity.
- Root positions with no reporting manager are allowed.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate legal entity name | Validation fails | "Legal entity name already exists" |
| Invalid currency | Validation fails | "Currency is not supported" |
| Unsupported country | Validation fails | "Country is not supported" |
| Parent cycle | Validation fails | "This parent relationship would create a cycle" |

## Events Triggered

- `LegalEntityCreated`
- `LegalEntityUpdated`
- `LegalEntityCountrySet`

## Related Flows

- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Data-Import/data-import-wizard|Data Import Wizard]]

## Module References

- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/positions/overview|Positions]]
