# Employee CSV Import

**Area:** People → Import  
**Trigger:** Authorized employee-import user uploads a CSV file to bulk-create employees (user action — configuration)  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `org:manage` (to create missing departments or positions during review)

---

## Preconditions

- Legal entities exist → [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- Departments exist within each legal entity → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Positions exist within each department → [[Userflow/Org-Structure/position-setup|Position Setup]]
- CSV prepared using the correct template (see headers below)
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

> Org structure must be set up before running a CSV import. The import resolves employees into existing legal entities, departments, and positions — it does not create org structure from CSV values.

---

## CSV Templates

Use business names in the CSV. Do not use internal codes, UUIDs, or technical identifiers.

### Multi-company tenant

```text
Employee Number
First Name
Last Name
Work Email
Legal Entity
Department
Position
Start Date
Employment Type
```

### Single-company tenant

```text
Employee Number
First Name
Last Name
Work Email
Department
Position
Start Date
Employment Type
```

For single-company tenants the `Legal Entity` column is omitted — the wizard infers the only active legal entity. If a `Legal Entity` column is present in the file, its value must match the tenant's legal entity name exactly or the row is rejected.

---

## Flow Steps

### Step 1: Upload CSV
- **UI:** People → Import → select CSV → drag-drop or browse to upload file
- **API:** `POST /api/v1/migration/upload-url` → returns pre-signed upload URL; client PUTs file directly
- **Backend:** File is staged in object storage; a `migration_runs` record is created with status `Pending`
- **Validation:** File must be `.csv` or `.xlsx`; rejected immediately if unsupported format

### Step 2: Map Standard Headers
- **UI:** Field mapping table shows source column names alongside sample row values and suggested canonical fields
- **Behaviour:** The eight standard headers (see above) are auto-matched; admin confirms or corrects any unrecognised column names
- **API:** `POST /api/v1/migration/analyse`
- **Rule:** All eight required columns must be mapped before the wizard proceeds. Extra columns in the CSV are retained as raw archive data — they are not silently discarded

### Step 3: Resolve Org Structure
- **UI:** For each row the wizard resolves `Legal Entity → Department → Position` using the business names from the CSV
- **Resolution order:**
  1. Match Legal Entity by name within tenant (single-company: inferred)
  2. Match Department by name within the resolved legal entity
  3. Match Position by name within the resolved legal entity and department
- **Ambiguity:** If a name matches more than one record within the legal entity scope, the row moves to a review screen where the admin selects the correct record
- **API:** `GET /api/v1/org/legal-entities`, `GET /api/v1/org/departments?legalEntityId={id}`, `GET /api/v1/org/positions?legalEntityId={id}`
- **Unresolved rows:** Rows with unresolved required org references cannot proceed until fixed, skipped, or the missing structure is created outside the wizard

### Step 4: Show Access Impact
- **UI:** After org resolution, the wizard shows the roles and permissions linked to each resolved position across all rows — grouped by position for review
- **Behaviour:** Admin reviews the access that will be granted to imported employees by position assignment
- **Rule:** This is a confirmation preview only. Position access templates generate per-employee grants or approval requests using the same model as individual onboarding. Users without `roles:manage` or `access:approve` do not see role lists, permission details, or scope controls.

### Step 5: Validate Rows
- **UI:** Validation summary groups rows into: valid, warnings, hard errors, and skipped
- **Admin actions:** Fix the source file and re-upload, skip individual bad rows, or cancel the run
- **Hard errors** block the row — cannot be imported without correction:

| Hard Error | Description |
|:-----------|:------------|
| Unknown legal entity | Value in `Legal Entity` column does not match any active legal entity in the tenant |
| Department not in legal entity | Department name found in tenant but does not belong to the resolved legal entity |
| Position not in legal entity | Position name found in tenant but does not belong to the resolved legal entity |
| Position belongs to another legal entity | Position resolves to a different legal entity than the one on the row |
| Position capacity exceeded | Importing this employee would push position occupancy above its capacity |
| Circular reporting chain | The position's reporting chain would create a cycle after assignment |
| Duplicate employee number in legal entity | Employee number already exists for an employee in the resolved legal entity |
| Duplicate work email in tenant | Work email already exists for any employee across the tenant |

- **Warnings** allow the row to proceed but require acknowledgement:

| Warning | Description |
|:--------|:------------|
| Reporting position is vacant | The position's `reports_to` position has no current occupant — reporting manager will be unresolved until that position is staffed |
| Position near capacity | Position is at 80 %+ of capacity after this import batch |
| No reporting manager | The assigned position is a root position — employee will have no reporting manager |

### Step 6: Confirm and Import
- **UI:** Summary counts: valid rows, warning rows (acknowledged), skipped rows, hard-error rows (excluded). Click "Import [N] employees" to proceed.
- **API:** `POST /api/v1/migration/bulk-import`
- **Backend:** Enqueues background import job; polling begins via `GET /api/v1/migration/runs/{id}/progress`
- **On completion per row:**
  1. Person record created
  2. Employee / employment record created
  3. Position assignment created
  4. User account created
  5. Policy assignments applied (leave, attendance, monitoring per legal entity)
  6. Approved or non-approval-required position-template grants applied; approval-required sensitive grants created as pending requests when needed
  7. Onboarding tasks generated

### Step 7: Send Invitations
- **UI:** Done screen shows imported, skipped, and failed counts plus a 10–15 employee spot-check sample. "Send invitations" button is shown.
- **Behaviour:** Email invitations are not sent automatically on import. The admin reviews the spot-check sample, then confirms invite sending. Invitations go to all successfully imported employees.
- **API:** `POST /api/v1/migration/runs/{id}/send-invites`
- **Employee experience:** Same as individual onboarding — employee receives email, accepts via SSO or password setup depending on tenant settings and allowed login methods

---

## Variations

### Single-company tenant
- `Legal Entity` column omitted from template; legal entity resolved automatically
- Step 3 skips the legal entity match and goes straight to department resolution

### Partial import (some rows have hard errors)
- Valid and warning-acknowledged rows are imported; hard-error rows are excluded
- Excluded rows are listed in the audit report with their specific error
- Admin can fix the source file and run a second import for the excluded rows; duplicate checks prevent re-importing already-imported employees

### Re-import after correction
- Duplicate email and duplicate employee number checks prevent double-importing the same employee
- Admin re-uploads a corrected file; previously imported rows are rejected as duplicates, corrected rows proceed normally

---

## Error Scenarios

| Scenario | Step | What happens | User sees |
|:---------|:-----|:-------------|:----------|
| Unsupported file format | 1 | Upload rejected | "Upload a CSV or Excel file" |
| Pre-signed upload URL expired | 1 | Upload fails | "Upload link expired — try again" |
| Required column not mapped | 2 | Wizard blocked | "Map required field: [column name]" |
| Name ambiguous within legal entity | 3 | Row goes to review | Admin selects correct record from matched list |
| All rows are hard errors | 5 | Import blocked | "No valid rows to import — fix errors and re-upload" |
| Background job fails mid-run | 6 | Run status → `Failed` | Failure summary with retry option |
| Invitations partially fail | 7 | Per-employee failure noted | "3 of 47 invitations failed to send — retry from audit report" |

---

## Events Triggered

- `MigrationRunCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `MigrationRunCompleted` → [[backend/messaging/event-catalog|Event Catalog]]
- `EmployeesImported` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification: completion / failure → importing admin → [[backend/notification-system|Notification System]]

---

## Related Flows

- [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]] — must exist before import
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]] — must exist before import
- [[Userflow/Org-Structure/position-setup|Position Setup]] — must exist before import
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] — single-employee alternative
- [[Userflow/Data-Import/data-import-wizard|Data Import Wizard]] — underlying Phase 1 CSV/Excel wizard mechanism; PeopleHR is Phase 2

---

## Module References

- [[modules/data-import/overview|Data Import]]
- [[modules/core-hr/overview|Core HR]]
- [[modules/org-structure/overview|Org Structure]]
- [[modules/org-structure/positions/overview|Positions]]
- [[backend/notification-system|Notification System]]
