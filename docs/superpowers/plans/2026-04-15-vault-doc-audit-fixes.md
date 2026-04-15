# Vault Doc Audit Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix every wrong link, wrong phase assignment, and stale table count found in the full vault audit.

**Architecture:** All changes are documentation-only (`.md` files). No code changes. Each task is independent.

**Tech Stack:** Markdown files in Obsidian vault (wikilinks, frontmatter).

---

## What Was Found

### A. Wrong Links

| Location | Issue | Fix |
|:---------|:------|:----|
| `ADE-START-HERE.md:186` | `[[current-focus/DEV3-payroll\|Payroll]]` — file `DEV3-payroll.md` does not exist | Replace with `[[current-focus/DEV3-calendar\|Calendar]]` |
| `backend/module-catalog.md` row 7 | `[[database/performance\|Performance]]` — points to DB query-optimization doc, not the module spec | Replace with `[[modules/performance/overview\|Performance]]` |

### B. Wrong Phase Assignments

**Root cause:** The 2026-04-08 restructure spec (`docs/superpowers/specs/2026-04-08-phase1-restructure-and-ade-design.md`) swapped Payroll → Phase 2 and Calendar → Phase 1. The spec and the module overview files were updated, but `ADE-START-HERE.md` (the primary AI agent entry point) and `docs/vault-structure-guide.md` were never updated to match.

| Location | Issue | Fix |
|:---------|:------|:----|
| `ADE-START-HERE.md:54` (Phase 1 module table row #14) | Lists **Payroll** as Phase 1 build target | Replace with **Calendar** |
| `ADE-START-HERE.md:59–71` (Phase 2 "Do NOT Build" table) | Lists **Calendar** as Phase 2 deferred | Replace Calendar with **Payroll** |
| `ADE-START-HERE.md:105` (Build Order section) | "Week 4 (Analytics + **Payroll**)" | Change to "Week 4 (Analytics + **Calendar**)" |
| `ADE-START-HERE.md:108` (Build Order section) | "DEV3: **Payroll**" | Change to "DEV3: **Calendar**" |
| `docs/vault-structure-guide.md:66` | `calendar/ ← Company events (Phase 2)` | Change Phase 2 → Phase 1 |

**Ground truth (source of record):**
- `modules/payroll/overview.md:4` → `**Phase:** 2 — Deferred` ✓
- `modules/calendar/overview.md:4` → `**Phase:** 1 — Build` ✓
- `backend/module-catalog.md` row 6 → Payroll = Phase 2 ✓
- `backend/module-catalog.md` row 18 → Calendar = Phase 1 ✓
- `database/schema-catalog.md` → Calendar listed under Phase 1 ✓

### C. Stale Table Counts

| Location | Stale Value | Correct Value |
|:---------|:------------|:--------------|
| `database/README.md` | "~153 tables across 22 modules" | **168 tables (128 Phase 1, 40 Phase 2) across 22 modules** |
| `docs/HR-Scope-Document-Phase1-Phase2.md:173` | "153 database tables (106 Phase 1, 47 Phase 2)" | **168 database tables (128 Phase 1, 40 Phase 2)** |

**Canonical source:** `database/schema-catalog.md` Summary section (168 / 128 / 40).

### D. Schema Catalog Phase 2 Count Needs Verification

The Phase 2 section headers in `database/schema-catalog.md` sum to **42** (11+7+10+6+2+3+3), but the Summary block says **40**. Before touching it, the actual table rows per Phase 2 module must be counted to determine whether the Summary is wrong or the headers are wrong.

---

## File Map

| Action | File |
|:-------|:-----|
| Modify | `ADE-START-HERE.md` — 5 changes (Phase 1 list, Phase 2 list, build order x2, Dev 3 link) |
| Modify | `backend/module-catalog.md` — 1 change (Performance link) |
| Modify | `docs/vault-structure-guide.md` — 1 change (calendar Phase 2 → Phase 1) |
| Modify | `database/README.md` — 1 change (table count) |
| Modify | `docs/HR-Scope-Document-Phase1-Phase2.md` — 1 change (table count) |
| Verify then possibly modify | `database/schema-catalog.md` — verify Phase 2 section header sum vs summary |

---

## Task 1: Fix ADE-START-HERE.md Phase Assignments + Broken Link

The primary AI agent entry point has Payroll and Calendar swapped in the module table, Phase 2 list, build order, and task link.

**Files:**
- Modify: `ADE-START-HERE.md`

- [ ] **Step 1: Fix Phase 1 module table row #14**

Find this exact text (around line 54):
```
| 14 | **Payroll** | Providers, tax, payslips + activity data feed (read-only, informational) | [[modules/payroll/overview\|Payroll]] |
```

Replace with:
```
| 14 | **Calendar** | Company events, leave-conflict checks via `ICalendarConflictService` | [[modules/calendar/overview\|Calendar]] |
```

- [ ] **Step 2: Fix Phase 2 "Do NOT Build" table**

Find the existing Calendar row in the Phase 2 table (around line 70):
```
| **Calendar** | Company events — not monitoring |
```

Replace with:
```
| **Payroll** | Full payroll engine — Phase 2 only; activity data feed is read-only in Phase 1 |
```

- [ ] **Step 3: Fix Build Order header (line ~105)**

Find:
```
Week 4 (Analytics + Payroll):
```

Replace with:
```
Week 4 (Analytics + Calendar):
```

- [ ] **Step 4: Fix Build Order body (line ~108)**

Find:
```
  DEV3: Payroll
```

Replace with:
```
  DEV3: Calendar
```

- [ ] **Step 5: Fix Dev 3 task link (line ~186)**

Find:
```
[[current-focus/DEV3-payroll|Payroll]]
```

Replace with:
```
[[current-focus/DEV3-calendar|Calendar]]
```

- [ ] **Step 6: Verify the file looks correct**

Open `ADE-START-HERE.md` and confirm:
- Phase 1 table row #14 shows Calendar
- Phase 2 list shows Payroll (not Calendar)
- Build order Week 4 shows Calendar
- Dev 3 task links include `DEV3-calendar` not `DEV3-payroll`

- [ ] **Step 7: Commit**

```bash
git add ADE-START-HERE.md
git commit -m "fix: swap Payroll→Phase2 and Calendar→Phase1 in ADE-START-HERE"
```

---

## Task 2: Fix Performance Module Link in module-catalog.md

The Performance module row in `backend/module-catalog.md` links to `database/performance.md` (a DB query-optimization doc) instead of the Performance module spec.

**Files:**
- Modify: `backend/module-catalog.md`

- [ ] **Step 1: Find and fix the wrong link**

Find (row 7 in Pillar 1 table):
```
| 7   | Performance       | [[database/performance\|Performance]]
```

Replace with:
```
| 7   | Performance       | [[modules/performance/overview\|Performance]]
```

- [ ] **Step 2: Commit**

```bash
git add backend/module-catalog.md
git commit -m "fix: correct Performance module link in module-catalog"
```

---

## Task 3: Fix vault-structure-guide.md Calendar Phase Label

**Files:**
- Modify: `docs/vault-structure-guide.md`

- [ ] **Step 1: Fix the label**

Find (around line 66):
```
├── calendar/                ← Company events (Phase 2)
```

Replace with:
```
├── calendar/                ← Company events (Phase 1)
```

- [ ] **Step 2: Commit**

```bash
git add docs/vault-structure-guide.md
git commit -m "fix: correct calendar folder phase label to Phase 1"
```

---

## Task 4: Fix Stale Table Counts

Two files still say 153 tables (the pre-WMS count). The canonical source (`database/schema-catalog.md`) says 168.

**Files:**
- Modify: `database/README.md`
- Modify: `docs/HR-Scope-Document-Phase1-Phase2.md`

- [ ] **Step 1: Fix database/README.md**

Find:
```
- **Total Tables:** ~153 across 22 modules (see [[database/schema-catalog|Schema Catalog]])
```

Replace with:
```
- **Total Tables:** 168 across 22 modules — 128 Phase 1, 40 Phase 2 (see [[database/schema-catalog|Schema Catalog]])
```

Also find the second occurrence in the Quick Links table (around line 92):
```
| [[database/schema-catalog\|Schema Catalog]] | Master index of all ~153 tables, grouped by module with phase tags |
```

Replace with:
```
| [[database/schema-catalog\|Schema Catalog]] | Master index of all 168 tables (128 Phase 1, 40 Phase 2), grouped by module with phase tags |
```

- [ ] **Step 2: Fix docs/HR-Scope-Document-Phase1-Phase2.md**

Find (line 173):
```
| **Scale** | Designed for 153 database tables (106 Phase 1, 47 Phase 2), 22 modules, 90+ permissions |
```

Replace with:
```
| **Scale** | Designed for 168 database tables (128 Phase 1, 40 Phase 2), 22 modules, 90+ permissions |
```

- [ ] **Step 3: Commit**

```bash
git add database/README.md docs/HR-Scope-Document-Phase1-Phase2.md
git commit -m "fix: update stale 153-table count to 168 (128 P1, 40 P2)"
```

---

## Task 5: Verify Schema Catalog Phase 2 Table Count

The Phase 2 section headers in `database/schema-catalog.md` sum to **42** but the Summary block claims **40**. Verify before touching anything.

**Files:**
- Read + verify: `database/schema-catalog.md`

- [ ] **Step 1: Count actual table rows in each Phase 2 module section**

Read `database/schema-catalog.md` and count `| \`tablename\`` rows under each Phase 2 module:

| Module | Header Claims | Actual Rows |
|:-------|:-------------|:------------|
| Payroll | 11 | ? |
| Performance | 7 | ? |
| Skills & Learning (Phase 2) | 10 | ? |
| Documents | 6 | ? |
| Grievance | 2 | ? |
| Expense | 3 | ? |
| Reporting Engine | 3 | ? |
| **Total** | **42** | **?** |

- [ ] **Step 2a: If actual rows = 40 (two headers overclaim)**

Update the overclaiming section headers to match their actual row counts.
Then verify that `42 − 2 = 40` and the Summary block (40 Phase 2, 168 total) is correct.

Commit:
```bash
git add database/schema-catalog.md
git commit -m "fix: correct Phase 2 module section headers in schema-catalog (42→40)"
```

- [ ] **Step 2b: If actual rows = 42 (Summary underclaims)**

Update the Summary block:

Find:
```
- **Total Tables:** 168
- **Phase 1 Tables:** 128
- **Phase 2 Tables:** 40
```

Replace with:
```
- **Total Tables:** 170
- **Phase 1 Tables:** 128
- **Phase 2 Tables:** 42
```

Then also update Tasks 4's `database/README.md` and `docs/HR-Scope-Document-Phase1-Phase2.md` to use 170/128/42 instead of 168/128/40.

Commit:
```bash
git add database/schema-catalog.md database/README.md docs/HR-Scope-Document-Phase1-Phase2.md
git commit -m "fix: correct Phase 2 table count in schema-catalog summary (40→42)"
```

---

## Self-Review

**Spec coverage check:**
- Wrong link 1 (DEV3-payroll) — covered in Task 1 Step 5 ✓
- Wrong link 2 (database/performance) — covered in Task 2 ✓
- Phase assignment: Payroll/Calendar in ADE-START-HERE — covered in Task 1 ✓
- Phase label in vault-structure-guide — covered in Task 3 ✓
- Stale 153-count in database/README — covered in Task 4 ✓
- Stale 153-count in HR-Scope doc — covered in Task 4 ✓
- Schema catalog Phase 2 sum discrepancy — covered in Task 5 ✓

**No placeholders.** Every step shows the exact old text and the exact replacement.

**Type consistency:** All wikilink targets verified against actual file paths observed in `find` output.
