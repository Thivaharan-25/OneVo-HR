# Data Import Wizard

**Area:** People -> Import  
**Trigger:** HR admin starts a bulk employee import or PeopleHR full migration  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `org:manage` for resolving departments/job structure during review

---

## Preconditions

- Tenant is provisioned and active -> [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- Org structure exists or can be created from mapped values -> [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions are assigned -> [[Userflow/Auth-Access/permission-assignment|Permission Assignment]]
- For PeopleHR, the admin has an API key with the selected PeopleHR areas enabled.

## Flow Steps

### Step 1: Choose Import Method

- **UI:** People -> Import -> select CSV, Excel, or PeopleHR.
- **Backend:** Wizard state stores the selected source.
- **Module:** [[modules/data-import/overview|DataImport]].

### Step 2: Upload File or Connect Source

- **CSV/Excel UI:** User uploads file through a drag-drop surface.
- **API:** `POST /api/v1/migration/upload-url` returns a pre-signed upload URL.
- **PeopleHR UI:** User enters API credentials in the integration card.
- **Security:** Credentials are masked and stored through the configured encrypted integration path.
- **PeopleHR Preflight:** System checks API key access for selected areas before fetching data.
- **Customer copy:** Show this as "Checking what your API key can access." Do not expose endpoint names, scopes, or adapter details.

### Step 3: Analyse and Map Fields

- **API:** `POST /api/v1/migration/analyse`.
- **UI:** Field mapping table shows source columns/fields, sample values, and suggested canonical fields.
- **User Action:** HR admin accepts suggestions or changes mappings manually.
- **PeopleHR Result:** Every source field is mapped to a canonical ONEVO field, marked as review-needed, or retained as raw archive. No field is silently discarded.
- **Customer copy:** Show only mappings that need confirmation. Confident auto-matches stay collapsed under "Matched automatically."

### Step 4: Resolve Job and Org Grouping

- **UI:** Wizard groups rows by department, job family, job level, legal entity, location, and work pattern.
- **Backend:** Department/job resolvers match existing org records or mark unresolved values for review.
- **Result:** Rows with unresolved required references cannot proceed until fixed, created, archived raw, or skipped.

### Step 5: Validate Rows

- **UI:** Validation summary shows valid rows, warnings, failed rows, duplicates, skipped rows, and raw-archive-only rows.
- **Backend:** ETL normalises dates, phone numbers, salary amounts, enum values, and required identifiers.
- **User Action:** Admin fixes mapping, skips bad rows, accepts raw archive for unsupported fields, or cancels the run.
- **Customer copy:** Group issues by action: "Needs fixing", "Recommended review", and "Kept safely for later".

### Step 6: Confirm Import

- **API:** `POST /api/v1/migration/bulk-import`.
- **Backend:** Creates `migration_runs` or `peoplehr_migration_runs` with `Pending` status and enqueues the background import job.
- **UI:** Progress screen begins polling `GET /api/v1/migration/runs/{id}/progress`.
- **PeopleHR:** First confirmation runs as `DryRun`; commit is enabled only after blocking validation errors are resolved or explicitly skipped where allowed.
- **Customer copy:** Label dry-run as "Preview import" and commit as "Import now".

### Step 7: Reconcile Imported Records

- **UI:** Done screen shows success/failed/skipped/raw-archived counts and a 10-15 employee spot-check sample.
- **Backend:** CSV/Excel records are written to Core HR employee tables; PeopleHR writes approved records to each canonical module after dry-run approval.
- **User Action:** Admin opens sampled profiles for human verification.
- **PeopleHR Audit:** Final report lists selected API areas, detected API access, fetched records, imported records, raw-archived records, skipped records, unresolved mappings, and validation decisions.
- **Customer copy:** Completion screen focuses on imported data, follow-up items, and safe archive. Full audit details live behind "View audit report".

## Variations

### PeopleHR Import

- Skips file upload.
- Uses the configured PeopleHR adapter to fetch raw records.
- Stages raw records before mapping so source data can be retried or remapped later.
- Runs API permission preflight before migration and clearly shows unavailable areas.
- Continues through mapping, grouping, validation, dry-run reconciliation, admin approval, commit, and audit report.
- Supports `DryRun`, `Commit`, `Rollback`, and `Resume`.

PeopleHR import is not limited to employee rows. Full migration scope is defined in [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]] and may include employees, org structure, manager hierarchy, salary, leave, absence, timesheets, documents, training, benefits, appraisals, work patterns, and custom screens depending on API key access.

### Customer Simplicity Rule

The wizard must not expose the full technical migration model to customers. Customers see a guided flow: connect PeopleHR, choose data, check access, review only needed matches, preview import, import now, and view summary. Technical details such as raw staging, payload hashes, adapter fetchers, and canonical table names belong in audit/admin detail views only.

### Partial Import

- Admin can skip rows with warnings or validation failures.
- Skipped rows are counted in `migration_runs.skipped_rows` or PeopleHR mapping results.
- The completed run keeps enough metadata for audit and follow-up.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| File type unsupported | Upload rejected before analysis | "Upload a CSV or Excel file" |
| Pre-signed upload expires | Upload fails | "Upload link expired. Try again." |
| Required field unmapped | Validation blocks confirmation | "Map required field: Employee email" |
| Duplicate employee detected | Row is marked warning or failed by policy | Duplicate row with suggested action |
| PeopleHR unavailable | Source connection fails | "PeopleHR is temporarily unavailable" |
| PeopleHR API scope missing | Preflight marks selected area unavailable | "API key cannot access Salary. Continue without it or update the key." |
| PeopleHR field has no ONEVO destination | Record/field is marked raw archive or review-needed | "This field will be retained as raw source data unless mapped." |
| Background job fails | Migration run status becomes `Failed` | Failure summary with retry option |

## Events Triggered

- `MigrationRunCreated`
- `MigrationRunCompleted`
- `EmployeesImported`
- `PeopleHrPreflightCompleted`
- `PeopleHrDryRunCompleted`
- `PeopleHrMigrationCommitted`

## Cross-Module Impact

| Module | Impact |
|:-------|:-------|
| Core HR | Creates employee records and profile data. |
| Org Structure | Resolves departments, job families, legal entities, locations, manager hierarchy, and work patterns. |
| Leave | Imports leave balances, leave requests, absence, sickness, maternity, and paternity where mapped. |
| Payroll | Imports salary, payroll identifiers, compensation history, and benefits where mapped. |
| Workforce Presence / Time | Imports work patterns, timesheets, lateness, and attendance-like records where mapped. |
| Documents | Imports document metadata and files with retryable download failures. |
| Skills | Imports training, CPD, qualifications, certifications, and skills where mapped. |
| Performance | Imports appraisals/reviews where mapped or archives source forms raw. |
| Auth | Optional employee/user invitation can follow imported employees. |
| Notifications | Completion/failure notification to the importing admin. |
| Audit Logs | Import run, row-count summary, mapping decisions, and admin approvals recorded for compliance. |

## Related Flows

- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Auth-Access/user-invitation|User Invitation]]
- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]]
- [[Userflow/Cross-Module/employee-full-onboarding|Employee Full Onboarding]]

## Module References

- [[modules/data-import/overview|DataImport]]
- [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]]
- [[modules/core-hr/overview|Core HR]]
- [[modules/org-structure/overview|Org Structure]]
