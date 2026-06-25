# PeopleHR Full Migration

**Module:** [[modules/data-import/overview|DataImport]]  
**Phase:** Phase 2  
**Source:** PeopleHR API  
**Purpose:** Lossless, auditable migration of PeopleHR tenant data into ONEVO canonical HR modules  
**Mode:** Initial onboarding migration first; recurring sync may reuse the same adapter later

---

## Migration Principle

PeopleHR migration must be treated as a staged migration pipeline, not a direct employee import. The target is not "perfect mapping on the first pass"; the target is that no source data is silently lost.

Every PeopleHR record must end in one of these states:

- **Imported** - written to the correct ONEVO canonical table.
- **Needs review** - blocked by missing mapping, duplicate identity, invalid dates, missing employee link, or unresolved org data.
- **Archived raw** - retained exactly as fetched because ONEVO does not yet have a canonical destination.
- **Skipped by admin** - explicitly skipped with a reason and audit entry.

No PeopleHR field may be discarded without a migration result row explaining why.

---

## Supported Scope Matrix

| PeopleHR area | Target ONEVO module/table | Migration status | Notes |
|:--------------|:--------------------------|:-----------------|:------|
| Employees | Core HR: `employees`, employee profile tables | Supported | Primary identity source. |
| Departments | Org Structure: `departments` | Supported | Create or resolve during org grouping. |
| Positions / roles | Org Structure: `positions` and position-based access grants | Supported with review | HR admin confirms position mapping and generated access. |
| Reporting hierarchy | Org Structure: `positions`, `position_reporting_history`, `position_assignments`, `employee_hierarchy_closure` | Supported with org review | Source reporting relationships are converted into effective-dated position reporting rows after employees and positions are staged. |
| Legal entities / locations | Org Structure: legal entities and locations | Supported with review | Unknown legal entity values require admin resolution. Single-company tenants can default unresolved company values to the tenant's only legal entity when the admin confirms. |
| Salary / compensation | Core HR / Payroll: compensation, salary history, payroll profile | Supported with review | Currency, salary amount, pay frequency, and effective date must validate. |
| Holiday / Time Off balances | Time Off: `time_off_entitlements`, `time_off_balances_audit` | Supported with review | Balance import depends on tenant Time Off policy mapping. |
| Holiday / Time Off bookings | Time Off: `time_off_requests`; Calendar feed side effects | Supported with review | Imported as historical or approved Time Off depending on source status. |
| Absence / sickness | Time Off or absence records | Supported with review | Absence type mapping is required. |
| Timesheets / lateness | Time / Time & Attendance: attendance, timesheets, presence sessions | Partial | Stored raw if ONEVO cannot preserve exact PeopleHR semantics. |
| Documents | Documents: `documents`, `document_versions` | Partial | Metadata imports first; binary download failures remain retryable. |
| Training / CPD / qualifications | Skills staging/raw archive; Phase 1 may map existing skills only | Staged with review | Phase 1 can map existing tenant skills to employee skill requests. Certifications, course enrollments, CPD, and learning records are archived/staged until Phase 2 canonical tables are enabled. |
| Benefits / perks | Payroll / Benefits extension tables | Raw archive first | Canonical mapping depends on benefits module maturity. |
| Appraisals / performance | Performance: reviews, feedback, goals where applicable | Partial | Preserve raw appraisal forms if ONEVO review template differs. |
| Vehicles / driving | Core HR custom fields or future assets module | Raw archive first | Imported to custom fields only when mapped. |
| Maternity / paternity | Time Off: special time off records and employee lifecycle metadata | Supported with review | Requires Time Off type mapping. |
| Assignment / projects | Work Management projects/resources | Partial | Only import when tenant chooses to link PeopleHR assignments to Work Management. |
| Work patterns | Time & Attendance: schedules, roster templates | Supported with review | Requires schedule pattern mapping. |
| Custom screens / custom fields | `employee_custom_fields`, source metadata JSON | Supported | Unknown fields remain available for later mapping. |

---

## Pipeline

```text
PeopleHR API
  -> PeopleHrAdapter
  -> raw staging records
  -> API permission preflight
  -> mapping profile
  -> ETL normalization
  -> validation
  -> dry-run reconciliation
  -> admin approval
  -> ONEVO canonical tables
  -> audit report
```

The adapter must fetch raw PeopleHR records before any transformation. Mapping and validation operate on staged records so failed or unmapped data can be retried without calling PeopleHR again.

---

## Adapter Components

| Component | Responsibility |
|:----------|:---------------|
| `PeopleHrAdapter` | Coordinates PeopleHR API calls and exposes module-level fetchers. |
| `PeopleHrPreflightService` | Tests API key access for every selected PeopleHR area before migration. |
| `PeopleHrEmployeeFetcher` | Fetches employee identity, contact, job, source reporting relationship, status, and custom field data. |
| `PeopleHrOrgFetcher` | Fetches departments, positions, locations, work patterns, and reporting relationships where available. |
| `PeopleHrSalaryFetcher` | Fetches salary, compensation, payroll identifier, and pay history data where the API key allows it. |
| `PeopleHrTimeOffFetcher` | Fetches Time Off balances, holidays, absence, sickness, maternity, and paternity records. |
| `PeopleHrTimesheetFetcher` | Fetches timesheet, lateness, rota, and work pattern records. |
| `PeopleHrDocumentFetcher` | Fetches document metadata and downloads files with retryable failure tracking. |
| `PeopleHrSkillsFetcher` | Fetches training, CPD, qualifications, certifications, and learning records. |
| `PeopleHrPerformanceFetcher` | Fetches appraisals, reviews, performance notes, and related forms. |
| `PeopleHrCustomScreenFetcher` | Fetches custom screens/custom fields and stores unmapped values losslessly. |

Each fetch result includes `source_endpoint`, `source_action`, `peoplehr_employee_id`, `source_record_id`, `fetched_at`, `payload_hash`, and the raw payload.

---

## Staging Tables

### `peoplehr_migration_runs`

Tracks the whole PeopleHR migration lifecycle.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | Tenant-scoped |
| `initiated_by_user_id` | `uuid` | FK -> users |
| `mode` | `varchar(20)` | `DryRun`, `Commit`, `Rollback`, `Resume` |
| `status` | `varchar(20)` | `Pending`, `Preflight`, `Fetching`, `Mapping`, `Validating`, `ReadyForApproval`, `Committing`, `Completed`, `Failed`, `RolledBack` |
| `selected_scopes_json` | `jsonb` | PeopleHR areas selected by the admin |
| `detected_scopes_json` | `jsonb` | API areas confirmed by preflight |
| `started_at` | `timestamptz` | |
| `completed_at` | `timestamptz` | Nullable |

### `peoplehr_raw_records`

Stores the untouched PeopleHR API payload for every fetched record.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `migration_run_id` | `uuid` | FK -> `peoplehr_migration_runs` |
| `tenant_id` | `uuid` | Tenant-scoped |
| `source_area` | `varchar(50)` | `employee`, `salary`, `time_off`, `absence`, `document`, `training`, etc. |
| `source_record_id` | `varchar(150)` | PeopleHR record identifier when available |
| `peoplehr_employee_id` | `varchar(150)` | Nullable for org-level records |
| `source_endpoint` | `varchar(150)` | API action/endpoint used |
| `payload_hash` | `varchar(128)` | Change detection and audit |
| `payload_json` | `jsonb` | Raw payload |
| `fetched_at` | `timestamptz` | |

### `peoplehr_mapping_profiles`

Stores approved source-to-canonical mapping rules.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | Tenant-scoped |
| `source_area` | `varchar(50)` | Area the mapping applies to |
| `source_field` | `varchar(200)` | PeopleHR field or custom screen field |
| `target_module` | `varchar(50)` | ONEVO destination module |
| `target_table` | `varchar(100)` | Nullable when archived raw |
| `target_field` | `varchar(100)` | Nullable when archived raw |
| `transform_rule_json` | `jsonb` | Date, enum, currency, custom parser, or lookup rule |
| `status` | `varchar(20)` | `active`, `needs_review`, `ignored_by_admin`, `raw_archive_only` |

### `peoplehr_mapping_results`

Stores the result for each source record and target write.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `migration_run_id` | `uuid` | FK -> `peoplehr_migration_runs` |
| `raw_record_id` | `uuid` | FK -> `peoplehr_raw_records` |
| `target_module` | `varchar(50)` | ONEVO module |
| `target_table` | `varchar(100)` | Nullable |
| `target_record_id` | `uuid` | Nullable until committed |
| `result_status` | `varchar(30)` | `Imported`, `NeedsReview`, `ArchivedRaw`, `SkippedByAdmin`, `Failed` |
| `message` | `text` | Human-readable mapping result |

### `peoplehr_external_id_links`

Preserves stable source identity links.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | Tenant-scoped |
| `onevo_entity_type` | `varchar(50)` | `employee`, `document`, `time_off_request`, etc. |
| `onevo_entity_id` | `uuid` | Canonical ONEVO record id |
| `peoplehr_area` | `varchar(50)` | Source area |
| `peoplehr_record_id` | `varchar(150)` | Source record id |
| `peoplehr_employee_id` | `varchar(150)` | Nullable |
| `payload_hash` | `varchar(128)` | Last imported hash |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `peoplehr_validation_errors`

Stores blocking and non-blocking validation issues.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `migration_run_id` | `uuid` | FK -> `peoplehr_migration_runs` |
| `raw_record_id` | `uuid` | Nullable for run-level errors |
| `severity` | `varchar(20)` | `blocking`, `warning`, `info` |
| `code` | `varchar(100)` | Stable error code |
| `message` | `text` | User-facing message |
| `resolution_status` | `varchar(20)` | `open`, `resolved`, `skipped`, `accepted` |

### `peoplehr_reconciliation_items`

Tracks admin review before commit.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `migration_run_id` | `uuid` | FK -> `peoplehr_migration_runs` |
| `category` | `varchar(50)` | `employee`, `org`, `salary`, `time_off`, etc. |
| `summary` | `text` | Review prompt |
| `sample_source_json` | `jsonb` | Source example |
| `sample_target_json` | `jsonb` | Proposed ONEVO result |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `skipped` |

---

## Identity Matching

Employee matching must be deterministic and reviewable.

Matching priority:

1. Existing `peoplehr_external_id_links`.
2. PeopleHR employee id / external id.
3. Work email within tenant.
4. Employee number or payroll id.
5. Name + date of birth + start date, only as a review candidate.

The migration must never auto-merge two PeopleHR employees into one ONEVO employee unless the match is based on an external id, work email, or admin-approved review item.

---

## API Permission Preflight

Before fetching real migration data, `PeopleHrPreflightService` must test the selected PeopleHR areas and show scope status to the admin.

| Area | Status | Meaning |
|:-----|:-------|:--------|
| Employee | Available | API key can fetch employee data. |
| Salary | Denied | API key lacks salary access. |
| Documents | Available | API key can list/download documents. |
| Appraisals | Not selected | Admin did not include this area. |
| Custom screens | Available | Raw custom fields can be staged. |

The migration cannot be labelled "full" unless every selected area passes preflight or the admin explicitly accepts the missing areas.

---

## Migration Order

PeopleHR data must commit in dependency order:

1. Org structure: legal entities, departments, positions, locations, work patterns.
2. Employees and identity links.
3. Position reporting history and position assignment second pass.
4. User/auth invitation settings.
5. Salary, compensation, payroll profile.
6. Time Off balances, holidays, absence, sickness, maternity, paternity.
7. Attendance, timesheets, lateness, schedules.
8. Documents and document versions.
9. Training, qualifications, CPD, skills.
10. Benefits/perks.
11. Performance/appraisals.
12. Custom screens/custom fields.
13. Final reconciliation and audit report.

---

## Validation Rules

Validation must classify each issue as `blocking`, `warning`, or `info`.

Blocking examples:

- Employee has no usable identity key.
- Duplicate employee match cannot be resolved.
- Reporting relationship points to an unknown employee or unresolved position after staging.
- Required legal entity, department, or position cannot be resolved and admin chose not to create or map it.
- Salary amount or currency is invalid.
- Time Off record has invalid date order.
- Document metadata has no employee link.

Warning examples:

- Optional phone number cannot be normalized.
- Salary is outside configured band.
- Time Off type requires manual mapping.
- Timesheet overlaps existing attendance record.
- Custom field has no canonical ONEVO destination and will be archived raw.

---

## Migration Modes

| Mode | Behaviour |
|:-----|:----------|
| `DryRun` | Fetch, stage, map, validate, and reconcile without writing canonical records. |
| `Commit` | Write approved mappings into ONEVO canonical tables and create external id links. |
| `Rollback` | Remove records created by the selected migration run where rollback is safe. |
| `Resume` | Continue a failed migration from the last completed stage using staged raw records. |

Every committed record should retain enough source metadata to trace it back to `peoplehr_raw_records` and the final audit report.

---

## Admin Reconciliation

The admin must review a dry-run dashboard before commit.

Minimum dashboard counts:

- Total records fetched by PeopleHR area.
- Imported-ready records.
- Needs-review records.
- Raw-archive-only records.
- Skipped records.
- Failed records.
- Missing API permission areas.
- Duplicate employee candidates.
- Unmapped source fields.
- Spot-check samples across high-risk categories.

The commit button remains disabled while blocking validation errors are open.

---

## Customer-Facing Flow

The migration engine can be complex, but the customer experience must stay simple. HR admins should not see raw table names, adapter names, staging concepts, endpoint names, payload hashes, or internal pipeline stages unless they open an advanced audit view.

The primary PeopleHR migration flow should be:

1. **Connect PeopleHR** - enter API key and test access.
2. **Choose Data to Import** - select clear categories such as Employees, Time Off, Documents, Payroll, Training, and Performance.
3. **Review Access Check** - show available, unavailable, and not-selected categories in plain language.
4. **Review Field Matches** - show only fields that need confirmation; auto-mapped fields stay collapsed.
5. **Fix Issues** - group problems by employee/category with clear actions: map, create, skip, or keep as archive.
6. **Preview Results** - show counts and samples before anything is written to live ONEVO records.
7. **Import** - commit approved data.
8. **Finish Report** - show what imported, what needs follow-up, and what was safely archived.

The UI must describe outcomes, not implementation. For example:

| Internal concept | Customer-facing wording |
|:-----------------|:------------------------|
| `peoplehr_raw_records` | Safely stored source data |
| `ArchivedRaw` | Kept for later mapping |
| `DryRun` | Preview import |
| `Commit` | Import now |
| API scope denied | API key cannot access this data |
| Blocking validation error | Needs fixing before import |
| Mapping profile | Field matches |
| Reconciliation items | Items to review |

### UX Rules

- Do not show every PeopleHR API category by default. Start with recommended categories and place advanced categories behind "More data types".
- Do not ask the admin to map fields that ONEVO can confidently auto-map.
- Do not block the whole migration for optional data. Block only when core employee identity or required relationships are unsafe.
- Use plain progress labels: `Checking access`, `Reading PeopleHR data`, `Preparing preview`, `Ready to review`, `Importing`, `Done`.
- Keep raw archive as a reassurance, not a scary technical state: "Some fields do not have a ONEVO home yet, so we kept them safely for later."
- Show one final confidence summary before import: records ready, records needing review, categories not accessible, and fields kept for later.
- Keep the audit report downloadable/viewable after completion, but do not make it the main completion screen.

---

## Final Audit Report

Each completed run produces an audit report containing:

- Tenant, admin, start/end timestamps, and migration mode.
- PeopleHR API areas selected and areas confirmed by preflight.
- Endpoints/actions called.
- Counts by area and result status.
- Unmapped fields and raw-archive-only fields.
- Duplicate resolution decisions.
- Validation errors and admin resolutions.
- Record checksums/payload hashes.
- Employee spot-check sample.
- Retryable document download failures.

---

## Relationship to Onboarding

PeopleHR full migration feeds the onboarding chain by creating or updating canonical employee records first. Once an employee is committed, the normal cross-module onboarding reactions can assign Time Off entitlements, shift schedules, payroll profiles, documents, auth invitations, and WorkPulse legal/privacy gates.

PeopleHR source records remain the audit trail; ONEVO canonical tables remain the operating source of truth after commit.

## Related

- [[Userflow/Data-Import/data-import-wizard|Data Import Wizard]]
- [[Userflow/Cross-Module/employee-full-onboarding|Employee Full Onboarding]]
- [[modules/data-import/overview|DataImport]]
- [[database/schemas/configuration|Configuration Schema]]
- [[backend/external-integrations|External Integrations]]
