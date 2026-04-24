# HR Import Onboarding — Design Spec

**Date:** 2026-04-24  
**Status:** Approved for implementation planning  
**Scope:** Initial tenant setup only — bulk import employees + org structure from existing HR systems

---

## 1. Problem

New tenants joining ONEVO must manually create every employee one by one through a 7-step form. For companies migrating from an existing HR system (e.g. PeopleHR) or holding employee data in CSV/Excel files, this is a major friction point. This feature replaces that manual process with a guided import wizard.

---

## 2. Scope

### In scope
- CSV / Excel file upload path
- PeopleHR API connector path
- Auto-creation of: departments (headless), job families, job levels, job titles, teams
- Employee skill import → taxonomy draft creation + employee profile assignment
- Org hierarchy (reporting lines) import
- Import history visible in Settings → Integrations

### Out of scope
- Ongoing sync (this is initial setup only)
- Policy import (leave policies, compensation bands — set up manually after)
- Department head assignment (done post-import via Organisation screen)
- Role-per-job-level configuration (done post-import via Job Families settings)
- Required skills on job families (done post-import — Phase 2 gap analysis reads these)
- BambooHR, Workday, ADP connectors (future — adapter pattern makes these easy to add)

---

## 3. Entry Points

| Location | What it does |
|---|---|
| **Employee list screen** → "Import Employees" button | Primary entry — opens the full-screen wizard |
| **Settings → Integrations** | Shows saved API connections, import history; can also trigger wizard |

The wizard opens as a full-screen overlay (not a small modal). Back/Next navigation throughout.

---

## 4. Wizard Flow

### Step 1 — Choose Import Method
Two cards presented:
- **Upload CSV or Excel file**
- **Connect PeopleHR**

---

### Step 2a — Upload File (CSV path)
- Drag & drop or browse
- Accepts `.csv`, `.xlsx`, `.xls`
- File is uploaded via a **signed Cloudflare R2 URL** (pre-signed, single-use, expires in 1 hour) — the browser uploads directly to R2, never through the ONEVO API server
- **Email transfer is explicitly not supported** — no file attachment accepted via email at any point
- System parses the file from R2, reads column headers, loads Row 1 as the sample employee
- Proceeds to Step 3

### Step 2b — Connect PeopleHR (API path)
- Input: API key field
- If a saved PeopleHR connection exists in Integrations, offer "Use saved connection" option
- On submit: system calls PeopleHR API, fetches employee list
- Proceeds to Step 3 (auto-mapped, admin confirms)
- Option at end: "Save this connection to Integrations" toggle

---

### Step 3 — Review Column Mapping

**Layout:** Table with columns — Your Column | Mapped To | Sample Value (Row 1) | Status

**Auto-matching logic:** System matches source columns to ONEVO fields by name similarity (e.g. `first_name` → First Name, `email` → Email). All matches are pre-filled but fully editable.

**Dropdown filtering rules (per row):**
1. **Exclusivity** — fields already claimed by another row are removed from this dropdown
2. **Type detection** — sample value infers compatible fields:
   - Date format → Start Date, Date of Birth only
   - Email format → Email only
   - "Full Time / Part Time / Contract" → Employment Type only
   - Short name-like text → name fields, Job Title, Manager
   - Comma-separated words → Skills
3. **Grouping** — remaining options shown in categories: Personal / Employment / Compensation / Skip

**Required fields** (must be mapped or import is blocked):
- First Name, Last Name, Email, Department, Job Title, Employment Type, Start Date, Reporting Manager

**Optional fields:** Phone, Date of Birth, Gender, Nationality, Address, Team, Salary, Skills

**Missing required fields** shown in red with note: "Employees will be flagged Needs Completion"

**Unrecognised columns** shown in amber with dropdown to assign or skip

**Job Title special case:** If no separate Job Family or Job Level column is detected, a notice appears: "No Job Family/Level column found — you'll group these in the next step."

**PeopleHR path:** Fields are auto-mapped. Same table shown for confirmation. Admin can edit any row.

**Preview bar:** Below the table, shows how Row 1 (sample employee) will be imported with current mapping. Admin confirms: "Looks right → Apply to all N employees"

---

### Step 4 — Organise Job Titles
*(Only shown when no Job Family / Job Level column was mapped in Step 3)*

System scans all rows, extracts unique job titles, and groups them by department name as a starting suggestion for job family.

**Layout:** One card per detected job family. Each card shows:
- Editable job family name (text input)
- List of job titles within that family, each with a level dropdown
- Employee count per title
- Admin can rename the family, move titles between families, or create a new family

**Level options in dropdown:** If the tenant already has job levels configured, those are shown. If no levels exist yet (typical for a brand-new tenant doing their first import), the wizard offers 4 default levels: Junior, Senior, Lead, Director. These are auto-created in `job_levels` with ranks 100, 200, 300, 400 respectively. Admin can rename them in Organisation → Job Families after import.

**Ungrouped titles** (where auto-grouping couldn't determine family) appear at the bottom in amber — admin assigns family and level manually.

**Auto-create behaviour:**
- Job families → created as stubs (`job_families` table)
- Job levels → created as stubs with numeric rank (`job_levels` table)
- Job titles → created linking family + level (`job_titles` table)
- All imported employees assigned default **Employee** role — admin configures role-per-level in Organisation → Job Families post-import

---

### Step 5 — Validation

System applies the mapping to all rows and runs validation. Two-panel layout:

**Left panel — employee counts:**
- N employees ready ✓
- N employees have issues (missing required fields) — option to Skip or Fix inline

**Right panel — auto-created dependencies:**
Shows everything the import will create automatically, grouped by type:
- Departments (N) — created without department heads
- Teams (N) — with detected leads if found
- Job Families (N) + Job Levels (N) + Job Titles (N)
- Draft Skills (N) — created in "Imported" category in taxonomy; no proficiency levels yet

**Hierarchy validation:**
- Reporting lines mapped and validated
- Circular references (employee reports to themselves) detected and flagged
- "Preview org chart →" button

**Department head note:** Departments created without heads. Assign in Organisation → Departments after import.

---

### Step 6 — Confirm & Import

Summary screen showing totals: employees to import, entities to create, rows to skip.

"Start Import" button enqueues the import job via **BullMQ**. A live progress percentage is shown throughout (e.g. "Importing... 142 / 247 employees"). Admin can navigate away — import continues in background and they are notified on completion via the platform notification system.

---

### Step 7 — Done

"N employees imported successfully. N skipped (view report)."

Returns to Employee list, now populated. Link to import report for skipped rows.

---

## 5. ETL Pipeline (Transform Phase)

Before the validation screen is shown (Step 5), the system runs a transformation pipeline on all rows:

| Transform | Rule |
|---|---|
| Date fields | Normalised to ISO 8601 (`YYYY-MM-DD`) — accepts DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD |
| Phone numbers | Validated and normalised to E.164 format (e.g. `+44XXXXXXXXXX`, `+94XXXXXXXXXX`) — invalid formats flagged, not blocked |
| Salary fields | Validated as numeric — non-numeric values flagged |
| Duplicate employee ID | Detected within the file — duplicate rows flagged in validation |
| Duplicate email | Checked against existing ONEVO records — blocked if already exists |
| Null required fields | Flagged — employees can still be imported with "Needs Completion" status |

Transformation runs as a **BullMQ background job** to prevent timeout failures on large datasets. The admin sees a "Processing your file..." state before the validation screen appears.

---

## 6. Bulk Import Endpoint

Records are written via `POST /api/migration/bulk-import` in **batches of 500–1,000 records per call**.

**Idempotency:** The endpoint uses `INSERT … ON CONFLICT DO UPDATE` logic keyed on employee ID and email. Running the same import twice will not create duplicate records — it will update existing ones. This makes re-runs safe after partial failures.

---

## 7. Post-Import Validation (Reconciliation Phase)

After the import job completes, an automated reconciliation check runs:

1. **Record count check** — source row count must match destination employee count exactly
2. **Checksum validation** — total salary sum and department employee counts compared between source and destination
3. **Reconciliation report** — generated as a downloadable PDF showing: total migrated records, errors, warnings, skipped entries
4. **Spot-check checklist** — provided to the HR admin to manually verify 10–15 randomly sampled employee records against their source system

The reconciliation report and spot-check checklist are accessible from the Done screen and from Settings → Integrations → Import History.

---

## 8. Skill Import Behaviour (Phase 1)

Employee skills in the source data (e.g. "React (Advanced), Python (Intermediate)") are handled as follows:

1. Each unique skill name extracted across all rows
2. Skills created as **drafts** in the taxonomy under a new "Imported" category — no proficiency level labels, no category structure yet
3. Each employee's skills added to their profile via `POST /api/v1/employees/{id}/skills` with status `validated` (admin is performing the import, equivalent to manager adding skills directly)
4. Admin enriches the taxonomy (add categories, proficiency labels) in Skills & Talent post-import

Skills field in CSV expected format: comma-separated, optionally with proficiency in parentheses — e.g. `React (Advanced), Python (Intermediate)` or just `React, Python` (proficiency defaults to level 1 if not specified).

---

## 9. Settings → Integrations Alignment

The Integrations screen (Platform-Setup area) shows a card per connected HR system:

| Field | Value |
|---|---|
| System name | PeopleHR |
| Status | Connected / Not connected |
| API key | Masked (last 4 chars shown) |
| Last import | Date + employee count |
| Import history | Log of all past imports with status |

Future connectors (BambooHR, Workday, ADP) follow the same card pattern. Each connector is a separate adapter that normalises data to the same internal format — the wizard itself does not change.

---

## 10. Import Transaction Order

To resolve the chicken-and-egg dependency problem, the backend creates entities in this order within a single transaction:

1. Departments (headless — `head_employee_id` null)
2. Teams (without leads)
3. Job Families
4. Job Levels
5. Job Titles (links family + level)
6. Skill taxonomy drafts (creates skills in "Imported" category)
7. Employees (linked to department, job title)
8. Employee skill declarations (links employees to draft skills)
9. Reporting lines (`employees.manager_id` populated — all employees now exist)
10. Team leads assigned (all employees now exist)

If any step fails, the entire import rolls back. Admin sees a clear error report.

---

## 11. Post-Import Admin Checklist (shown on Done screen)

- [ ] Assign department heads in Organisation → Departments
- [ ] Configure roles per job level in Organisation → Job Families
- [ ] Set required skills on job families in Organisation → Job Families (feeds Phase 2 gap analysis)
- [ ] Enrich skill taxonomy (add categories, proficiency labels) in Skills & Talent
- [ ] Review employees flagged "Needs Completion" and fill missing fields

---

## 12. Migration Audit & Security

- A `migration_runs` table records every migration event: who initiated it (`initiated_by_user_id`), when it ran (`started_at`, `completed_at`), how many records were processed, and final status (success / partial / failed)
- All migration activity is included in the platform-wide audit log (`audit_logs` table)
- Customer data files uploaded to Cloudflare R2 are **automatically deleted within 48 hours** of successful import — a scheduled cleanup job handles this
- If import fails, files are retained for 7 days to allow retry, then deleted

---

## 13. Permissions Required

| Action | Permission |
|---|---|
| Access import wizard | `employees:write` |
| Create departments / job families | `settings:admin` |
| Import compensation data | `payroll:write` |
| Create skills in taxonomy | `skills:manage` |
| Add skills to employee profiles | `skills:write` (scoped to team) |

---

## 14. Error Handling

| Scenario | Behaviour |
|---|---|
| Duplicate email in file | Row flagged in validation — skip or fix |
| Duplicate email already in ONEVO | Row blocked — shown in error report |
| Circular reporting line | Auto-detected in Step 5, flagged for admin review |
| PeopleHR API key invalid | Step 2b shows error inline, admin re-enters |
| PeopleHR API rate limit hit | Import pauses, retries with backoff, resumes automatically |
| File format not supported | Step 2a shows error: "Please upload a .csv, .xlsx or .xls file" |
| Import partially fails mid-run | Full rollback — no partial state left in DB |
