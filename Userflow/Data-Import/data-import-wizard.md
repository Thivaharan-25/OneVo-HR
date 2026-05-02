# Data Import Wizard

**Area:** People -> Import  
**Trigger:** HR admin starts a bulk employee import  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `org:manage` for resolving departments/job structure during review

---

## Preconditions

- Tenant is provisioned and active -> [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- Org structure exists or can be created from mapped values -> [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions are assigned -> [[Userflow/Auth-Access/permission-assignment|Permission Assignment]]

## Flow Steps

### Step 1: Choose Import Method
- **UI:** People -> Import -> select CSV, Excel, or PeopleHR
- **Backend:** Wizard state stores the selected source
- **Module:** [[modules/data-import/overview|DataImport]]

### Step 2: Upload File or Connect Source
- **CSV/Excel UI:** User uploads file through a drag-drop surface
- **API:** `POST /api/v1/migration/upload-url` returns a pre-signed upload URL
- **PeopleHR UI:** User enters API credentials in the integration card
- **Security:** Credentials are masked and stored through the configured encrypted integration path

### Step 3: Analyse and Map Fields
- **API:** `POST /api/v1/migration/analyse`
- **UI:** Field mapping table shows source columns, sample values, and suggested canonical fields
- **User Action:** HR admin accepts suggestions or changes mappings manually

### Step 4: Resolve Job and Org Grouping
- **UI:** Wizard groups rows by department, job family, job level, and legal entity
- **Backend:** Department/job resolvers match existing org records or mark unresolved values for review
- **Result:** Rows with unresolved required references cannot proceed until fixed or skipped

### Step 5: Validate Rows
- **UI:** Validation summary shows valid rows, warnings, failed rows, duplicates, and skipped rows
- **Backend:** ETL normalises dates, phone numbers, salary amounts, and required identifiers
- **User Action:** Admin fixes mapping, skips bad rows, or cancels the run

### Step 6: Confirm Import
- **API:** `POST /api/v1/migration/bulk-import`
- **Backend:** Creates `migration_runs` with `Pending` status and enqueues the background import job
- **UI:** Progress screen begins polling `GET /api/v1/migration/runs/{id}/progress`

### Step 7: Reconcile Imported Records
- **UI:** Done screen shows success/failed/skipped counts and a 10-15 employee spot-check sample
- **Backend:** Imported records are written to Core HR employee tables
- **User Action:** Admin opens sampled profiles for human verification

## Variations

### PeopleHR Import
- Skips file upload
- Uses the configured PeopleHR adapter to fetch raw rows
- Continues through mapping, grouping, validation, confirmation, and reconciliation

### Partial Import
- Admin can skip rows with warnings or validation failures
- Skipped rows are counted in `migration_runs.skipped_rows`
- The completed run keeps enough metadata for audit and follow-up

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| File type unsupported | Upload rejected before analysis | "Upload a CSV or Excel file" |
| Pre-signed upload expires | Upload fails | "Upload link expired. Try again." |
| Required field unmapped | Validation blocks confirmation | "Map required field: Employee email" |
| Duplicate employee detected | Row is marked warning or failed by policy | Duplicate row with suggested action |
| PeopleHR unavailable | Source connection fails | "PeopleHR is temporarily unavailable" |
| Background job fails | `migration_runs.status = Failed` | Failure summary with retry option |

## Events Triggered

- `MigrationRunCreated`
- `MigrationRunCompleted`
- `EmployeesImported`

## Cross-Module Impact

| Module | Impact |
|:-------|:-------|
| Core HR | Creates employee records and profile data |
| Org Structure | Resolves departments, job families, legal entities, and locations |
| Auth | Optional employee/user invitation can follow imported employees |
| Notifications | Completion/failure notification to the importing admin |
| Audit Logs | Import run and row-count summary recorded for compliance |

## Related Flows

- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Auth-Access/user-invitation|User Invitation]]
- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]]

## Module References

- [[modules/data-import/overview|DataImport]]
- [[modules/core-hr/overview|Core HR]]
- [[modules/org-structure/overview|Org Structure]]
