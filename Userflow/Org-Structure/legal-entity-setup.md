# Company Setup

**Area:** Org Structure  
**Trigger:** Admin configures single-company or multi-company structure in the merged customer app shell  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `settings:read`

---

## Preconditions

- Tenant has been provisioned by ONEVO through Developer Platform.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Choose Company Mode
- **UI:** Customer app shell topbar -> tenant/company dropdown -> Add company.
- **Options:** Single-company mode or multi-company mode.
- **Rule:** Single-company mode creates one default Company. Multi-company mode allows multiple Companies under the same tenant.

### Step 2: Create Company
- **UI:** In the topbar company dropdown, click Add company, then enter company name, registration number, country, currency, tax identifier if needed, and address.
- **API:** `POST /api/v1/org/legal-entities`
- **Validation:** Name must be unique within tenant. Currency must be a valid ISO 4217 code. Country must be supported.
- **Storage:** Company records are stored in `legal_entities`.
- **Result:** Newly created Company becomes selectable from the topbar dropdown. Company General settings are edited from Settings > General after selecting that Company.

### Step 3: Parent / Subsidiary Relationship
- **UI:** Optional parent Company selector.
- **Rule:** Parent relationship is for setup and reporting context only. It must not allow departments, positions, or office-location management to be shared across legal entities.

### Step 4: Save
- **Backend:** LegalEntityService.CreateAsync() -> [[modules/org-structure/legal-entities/overview|Legal Entities]]
- **DB:** `legal_entities`
- **Result:** Company becomes available for department setup, position setup, employee onboarding, Time Off policy assignment, attendance policy assignment, and import validation.

## Rules

- Departments belong to one Company.
- Positions belong to one Company.
- Employees have one primary Company from their Primary Employment Assignment.
- Positions cannot be shared across Companies.
- A position can report only to another position inside the same Company.
- Root positions with no reporting manager are allowed.
- Each Company has one office location configured in Settings > General.
- If a customer needs another branch, sub-office, or physical office location, create another Company/legal entity.
- Do not create branch/sub-office records inside one Company in Phase 1.

## Why Company Matters

Company defines the operating boundary inside a tenant. Internally, Company maps to `legal_entity_id`. It affects:

- Departments
- Positions
- Onboarding
- Time Off policy assignment
- Schedule / attendance policy assignment
- Import validation
- Reporting-line boundaries

Additional Authority Assignments may exist across Companies, but they do not change the employee's primary employment policy source. Cross-Company reporting lines are not allowed.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate Company name | Validation fails | "Company name already exists" |
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

- [[modules/org-structure/legal-entities/overview|Companies / Legal Entities]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/positions/overview|Positions]]
