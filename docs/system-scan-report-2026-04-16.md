# ONEVO System Scan Report

**Date:** 2026-04-16
**Scope:** Full brain repo scan — architecture, security, ADE correctness
**Files Reviewed:** ADE-START-HERE.md, ade/README.md, AI_CONTEXT/*, backend/module-catalog.md, current-focus/README.md, current-focus/DEV1-*.md, security/auth-architecture.md, current-focus/WMS-bridge-integration.md, known-issues.md, rules.md, project-context.md

---

## Summary

**4 Architecture Issues** · **3 Security Issues** · **4 Documentation/ADE Gaps**

No show-stopping blocking issues. Two findings require a decision before ADE agents write code
(Reporting Engine scope, Direct-call contradiction). Three security findings should be fixed before
implementation reaches those features.

---

## Architecture Issues

---

### ARCH-01 — Reporting Engine Built Inside Phase 1 Task (CRITICAL for ADE)

**Severity:** High — ADE agents will be confused or produce wrong output

**Where:**
- `ADE-START-HERE.md` Phase 2 list → "Reporting Engine — Subsumed by Productivity Analytics for Phase 1"
- `backend/module-catalog.md` row 19 → Reporting Engine = Phase 2, 3 tables, Owner: Dev 1
- `current-focus/DEV1-productivity-analytics.md` → Acceptance criteria explicitly includes:
  - `report_definitions` table
  - `report_executions` table
  - `report_templates` table
  - CSV + Excel export
  - Report builder frontend page at `/reports/builder/`
  - API endpoints `/api/v1/reports/*`

**Problem:**
The Phase 2 deferred module (Reporting Engine) is being fully implemented inside a Phase 1 task.
An ADE agent reading `ADE-START-HERE.md` sees "Reporting Engine = Phase 2 — Do NOT build" and then
reads `DEV1-productivity-analytics.md` and sees acceptance criteria to build exactly those tables.
This contradiction will either cause the agent to skip those criteria (wrong) or build them while
confused about the module boundary (inconsistent namespace placement).

**Decision needed:**
Either:
- (A) Update ADE-START-HERE.md: "Reporting Engine is built as part of Productivity Analytics in Phase 1 — the 3 core tables live under ProductivityAnalytics namespace" — and remove it from Phase 2 list
- (B) Remove the report builder criteria from DEV1-productivity-analytics.md and defer to Phase 2

**Recommended:** Option A. The work is already scoped into Phase 1 via the task file. Just fix the entry point to stop calling it deferred.

---

### ARCH-02 — Discrepancy Engine Missing from ADE-START-HERE.md (HIGH)

**Severity:** High — ADE agents won't know this Phase 1 module exists

**Where:**
- `ADE-START-HERE.md` Phase 1 table → 15 modules listed, no Discrepancy Engine
- `backend/module-catalog.md` row 11a → Discrepancy Engine, Phase 1, 2 tables, Dev 3, Week 3

**Problem:**
The ADE entry point is the first file every ADE agent reads. It lists exactly which modules to build.
Discrepancy Engine (`ONEVO.Modules.DiscrepancyEngine`) is a Phase 1 module with its own namespace,
2 tables (`discrepancy_events`, `wms_daily_time_logs`), and a task file. It is completely absent
from the ADE-START-HERE.md Phase 1 module table.

An ADE agent assigned to DEV3 Activity Monitoring would eventually find the discrepancy engine
referenced in `modules/discrepancy-engine/overview.md`, but the agent has no signal from the entry
point that this module is in scope. The Work Activity bridge (Bridge 3) also depends on
`wms_daily_time_logs` which belongs to this module.

**Fix:** Add row to ADE-START-HERE.md Phase 1 table:
```
| 11a | **Discrepancy Engine** | WMS time log vs activity data cross-check | [[modules/discrepancy-engine/overview\|Discrepancy Engine]] |
```

---

### ARCH-03 — "Never Direct Service Calls" Contradicts Sync Query Pattern (HIGH)

**Severity:** High — ADE agents will refuse to write valid sync calls

**Where:**
- `ADE-START-HERE.md` Key Architecture Concepts: "Cross-module communication via domain events only — **never direct service calls**"
- `AI_CONTEXT/project-context.md`: "Inter-module communication: sync (direct service calls) for queries, domain events for side effects"
- `backend/module-catalog.md`: "Sync (direct): Module A calls Module B's public interface (via DI)"

**Problem:**
The entry point says **never** direct service calls. The architecture docs say direct calls ARE
allowed for synchronous queries. The distinction is: domain events for side effects, direct calls
for queries. But ADE-START-HERE.md uses the word "never" with no qualification.

Concrete example that breaks: `DEV1-leave.md` acceptance criteria includes:
> "Calendar conflict detection: call `ICalendarConflictService` on submission"

This is a direct service call between Leave → Calendar. An ADE agent obeying the entry point
would refuse to implement this, or wrap it in a domain event when a direct synchronous call
is the correct pattern.

**Fix:** Replace the sentence in ADE-START-HERE.md with:
> "Cross-module communication: **direct interface calls** for synchronous queries (e.g., `ICalendarConflictService`), **domain events** for side effects. Never import another module's internal classes."

---

### ARCH-04 — Module Count Inconsistency in project-context.md (MEDIUM)

**Severity:** Medium — ADE agents won't produce wrong code, but cross-referencing is confusing

**Where:**
- `AI_CONTEXT/project-context.md` Section 4: "22 modules", "168 database tables"
- `backend/module-catalog.md` footer: "23 modules, 170 tables (128 Phase 1 · 42 Phase 2)"

**Problem:** Discrepancy Engine (11a, 2 tables) and the 5 WMS integration tables explain the
difference. `project-context.md` was not updated when these were added. Any ADE agent comparing
these two files will get conflicting counts.

**Fix:** Update `project-context.md` Section 4 to: "23 modules, 170 tables (128 Phase 1, 42 Phase 2)"

---

## Security Issues

---

### SEC-01 — bcrypt Used for Bridge API Key Hashing (WRONG ALGORITHM)

**Severity:** Medium — Architectural error, performance impact, wrong tool for the job

**Where:** `current-focus/WMS-bridge-integration.md` — `bridge_api_keys` table schema:
```
key_hash (varchar) — bcrypt hash of the key
```

**Problem:**
bcrypt is a password hashing function — it is intentionally slow (100–300ms per verification)
to resist brute-force attacks on human-memorable passwords. Bridge API keys are long random
strings (e.g., 32+ bytes of entropy) that don't need bcrypt's work factor.

Using bcrypt to verify a bridge API key on every API call means:
- Every bridge request takes 100–300ms just for key verification
- Under load (WMS syncing hundreds of employees), this becomes a bottleneck
- bcrypt's slowness provides zero security benefit for a random high-entropy key

**Fix:** Use **HMAC-SHA256** or **SHA-256** for API key storage:
```
key_hash (varchar) — SHA-256 hash of the key (hex encoded)
```
Verification: `SHA256(submittedKey) == storedHash` — constant-time comparison (use `CryptographicOperations.FixedTimeEquals`).

If you want a pepper for extra security, use HMAC-SHA256 with a server-side secret key from config.

---

### SEC-02 — Covert Monitoring Mode May Violate GDPR

**Severity:** High — Legal compliance risk, must be reviewed before implementation

**Where:**
- `AI_CONTEXT/project-context.md` Section 5: "Three privacy transparency modes: full (employees see everything), partial (see own data), covert (employer only)"
- `ADE-START-HERE.md`: "No data captured before clock-in, during breaks, or after clock-out. This is a **GDPR requirement**."

**Problem:**
GDPR Article 13 requires data controllers to inform employees about the processing of their
personal data — including what is collected, the purpose, and the retention period. "Covert"
mode means the employee has no visibility into what is being monitored.

Monitoring an employee's keystrokes, app usage, and screenshots without their knowledge is
a potential GDPR violation in the EU/UK, and similarly illegal under privacy laws in many
other jurisdictions (e.g., DPDP Act 2023 in India, PDPA in Malaysia).

**This does NOT mean covert mode cannot exist.** It means:
1. Employees must still receive a privacy notice at onboarding (even in covert mode)
2. "Covert" should mean "employees cannot see live data or history" — not "employees don't know monitoring exists"
3. The compliance.md doc must explicitly document what disclosures are required even in covert mode
4. ADE agents implementing this feature must be given these constraints — currently rules.md does not mention them

**Immediate action:** Before any ADE agent implements the privacy transparency mode feature,
add a note to `AI_CONTEXT/rules.md` Section 3 (Workforce Intelligence Rules):
> "Covert mode hides monitoring data from employee self-service views. It does NOT exempt the tenant from informing employees that monitoring exists. Tenant onboarding must include a mandatory data processing disclosure step. See security/compliance.md."

---

### SEC-03 — Screenshot Blob URLs Have No Expiry/Signed URL Spec

**Severity:** Medium — Authorization bypass risk after initial access

**Where:**
- `AI_CONTEXT/known-issues.md`: "Only show [screenshots] to users with `workforce:view` permission. Never cache screenshots in browser storage."
- No specification anywhere for how screenshot blob URLs are served

**Problem:**
Screenshots are stored in Azure Blob Storage via `file_records`. If the frontend receives a
permanent public blob URL and renders it in an `<img>` tag, that URL:
- Bypasses RBAC after the first access (the URL itself is the access credential)
- Can be bookmarked, shared, or logged in browser history
- Persists after the employee's `workforce:view` permission is revoked

**Fix:** Specify in `modules/activity-monitoring/screenshots/overview.md` and `backend/shared-kernel.md`:
> "Screenshot URLs must be served as time-limited SAS (Shared Access Signature) tokens via `IFileService.GetTemporaryUrlAsync(fileRecordId, expiry: TimeSpan.FromMinutes(15))`. The frontend never stores raw blob URLs — it requests a fresh SAS URL on each view. SAS tokens expire 15 minutes after generation."

This should be part of `IFileService`'s contract for RESTRICTED-classified files.

---

## ADE / Documentation Gaps

---

### DOC-01 — `modules/analytics/overview.md` Deleted but Uncommitted

**Severity:** Low — Dead link risk

**Where:** Git status: `D modules/analytics/overview.md`

If any other file links to `modules/analytics/overview.md`, those links are now broken.
The deletion should be committed so the brain repo is in a clean state.

**Fix:** `git add modules/analytics/overview.md && git commit -m "docs: remove deprecated analytics overview"`

---

### DOC-02 — `database/schemas/discrepancy-engine.md` Untracked

**Severity:** Low — ADE agents from fresh clones won't have this file

**Where:** Git status: `?? database/schemas/discrepancy-engine.md`

The schema file for Discrepancy Engine exists in the working directory but is not committed.
ADE agents that clone the backend repo will not have this schema available.

**Fix:** `git add database/schemas/discrepancy-engine.md && git commit -m "docs: add discrepancy engine schema"`

---

### DOC-03 — rules.md Uses Wrong Task File Pattern (`WEEK*.md` vs `DEV*.md`)

**Severity:** Low — Minor naming inconsistency, potential ADE confusion

**Where:** `AI_CONTEXT/rules.md` Section 9 Task Completion Rules:
> "Checkboxes live ONLY in individual task files (`current-focus/WEEK*.md`), NOT in `current-focus/README.md`"

Actual task files are named `DEV1-infrastructure-setup.md`, `DEV2-auth-security.md`, etc.
There are no `WEEK*.md` files. An ADE agent parsing this instruction literally would search
for `WEEK*.md` and find nothing.

**Fix:** Update `rules.md` Section 9 to: "Checkboxes live ONLY in individual task files (`current-focus/DEV*.md`)"

---

### DOC-04 — No Concurrent Brain Repo Write Strategy for Parallel ADE Sessions

**Severity:** Low — Race condition in multi-agent workflows

**Where:** `ade/README.md`: "Cross-dev parallel: Multiple devs can run their ADE sessions simultaneously"

If Dev 1 and Dev 3 ADE sessions both run in parallel and both update checkboxes in their
respective task files simultaneously, a git conflict will occur if they share a git remote
for the brain repo. The ADE README documents no merge/locking strategy.

**Fix:** Add to `ade/README.md`:
> "**Concurrent sessions:** Each dev's task files are in separate files (`DEV1-*.md`, `DEV3-*.md`). Parallel sessions should each commit to their own file — no two devs share a task file. If a merge conflict occurs on `current-focus/README.md`, use the latest version from the running session."

---

## What Is NOT an Issue

The following were examined and confirmed correct:

- **JWT authentication** — RS256, access token in memory, refresh in HttpOnly Secure cookie, rotation on use with chain audit. Correctly designed.
- **Tenant isolation** — BaseRepository + PostgreSQL RLS dual-layer. The `TenantId = Guid` string interpolation gotcha is documented in known-issues.md. Acceptable as long as the pattern is not extended.
- **Agent JWT vs User JWT separation** — Device JWT contains `type: "agent"` claim, no HR permissions. Correctly isolated.
- **Argon2id for passwords** — Correct algorithm choice.
- **Activity data privacy rules** — "Never log PII or activity content" is clear and enforced in rules.md.
- **GDPR monitoring lifecycle** (clock-in → clock-out boundary) — Correctly documented and enforced as a hard rule.
- **Module boundary enforcement** — ArchUnitNET tests + namespace rules are correctly specified.
- **Phase 2 guard rules** — Phase 2 deferred list and `## Phase 2 Features` sections in module overviews are consistently structured.

---

## Action Items by Priority

| # | Issue | Owner | Action |
|:--|:------|:------|:-------|
| 1 | ARCH-01: Reporting Engine phase confusion | Product Owner | Update ADE-START-HERE.md to remove Reporting Engine from Phase 2 deferred list |
| 2 | ARCH-02: Discrepancy Engine missing | Product Owner | Add Discrepancy Engine to ADE-START-HERE.md Phase 1 table |
| 3 | ARCH-03: "Never direct calls" contradiction | Product Owner | Fix ADE-START-HERE.md wording to allow sync query calls |
| 4 | SEC-02: Covert mode GDPR | Product Owner + Legal | Add GDPR disclosure requirement to rules.md before implementation |
| 5 | SEC-01: bcrypt for API keys | Dev 4 | Change bridge_api_keys.key_hash to use SHA-256 |
| 6 | SEC-03: Screenshot signed URLs | Dev 3 | Add SAS URL spec to IFileService contract and screenshots overview |
| 7 | ARCH-04: Module count mismatch | Product Owner | Update project-context.md counts |
| 8 | DOC-02: Untracked discrepancy schema | Any dev | Commit the file |
| 9 | DOC-03: WEEK*.md naming | Any dev | Fix rules.md reference |
| 10 | DOC-01: analytics deletion | Any dev | Commit the deletion |
| 11 | DOC-04: Concurrent write strategy | Product Owner | Add note to ade/README.md |
