# 2026-04-07: Userflow Folder + Technical Documentation Restructure

## Userflow Folder (NEW)
- **Added:** `Userflow/` — 93 end-to-end user flow files across 18 feature areas
- **Added:** Flows are **permission-based, not role-based** — since roles are dynamic (created via Job Family with custom permissions)
- **Added:** Each flow includes: required permissions, UI steps, API calls, backend logic, DB tables, error scenarios, events triggered, and wikilinks to module docs
- **Added:** Flow areas: Platform-Setup, Auth-Access, Org-Structure, Employee-Management, Leave, Workforce-Presence, Performance, Payroll, Skills-Learning, Documents, Workforce-Intelligence, Exception-Engine, Analytics-Reporting, Grievance, Expense, Calendar, Notifications, Configuration

## Technical Documentation Restructure
- **Changed:** `architecture/` → `backend/` (9 files + messaging/ subfolder)
- **Changed:** `architecture/frontend-*.md` → `frontend/` (renamed: `structure.md`, `state-management.md`)
- **Changed:** `cross-cutting/guides/frontend-*.md` → `frontend/` (`api-integration.md`, `coding-standards.md`)
- **Changed:** `cross-cutting/testing/frontend-testing.md` → `frontend/testing.md`
- **Changed:** `design-system/` → `frontend/design-system/` (6 files)
- **Changed:** `cross-cutting/database/` → `database/` (3 files)
- **Changed:** `cross-cutting/guides/coding-standards.md` → `code-standards/backend-standards.md` (renamed)
- **Changed:** `cross-cutting/guides/` → `code-standards/` (git-workflow, logging-standards)
- **Changed:** `cross-cutting/testing/README.md` → `code-standards/testing-strategy.md`
- **Changed:** `cross-cutting/security/` → `security/` (5 files)
- **Changed:** `cross-cutting/deployment/` + `cross-cutting/observability/` + `cross-cutting/multi-tenancy.md` → `infrastructure/` (6 files)
- **Changed:** `cross-cutting/messaging/` → `backend/messaging/` (4 files)
- **Deleted:** `architecture/`, `cross-cutting/`, `design-system/` (all files moved, folders removed)
- **Updated:** All wikilinks vault-wide for renamed files (`coding-standards` → `backend-standards`, `frontend-structure` → `structure`, `frontend-state-management` → `state-management`)
- **Updated:** Root `README.md` with new folder structure and information layers table
