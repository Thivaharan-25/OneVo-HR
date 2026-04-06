# Knowledge Base Changelog

## 2026-04-06 - Two-Pillar Architecture Redesign (HR + Workforce Intelligence)

- **Added:** Pillar 2: Workforce Intelligence — 5 new modules (WorkforcePresence, ActivityMonitoring, IdentityVerification, ExceptionEngine, ProductivityAnalytics)
- **Added:** Agent Gateway module — desktop agent data ingestion, device JWT auth
- **Added:** 22 individual module files in `docs/architecture/modules/` (one per module, interconnected via wikilinks)
- **Added:** 12 new task files for Weeks 2-4 developer assignments
- **Changed:** Module count 18 → 22, table count 126 → 151
- **Changed:** Old Attendance module → WorkforcePresence (unified biometric + agent + manual presence)
- **Changed:** `AI_CONTEXT/project-context.md` — two-pillar architecture, 4 product configurations, monitoring model
- **Changed:** `AI_CONTEXT/tech-stack.md` — added Desktop Agent tech, Frontend tech, new architecture patterns
- **Changed:** `AI_CONTEXT/current-focus.md` — new 4-week delivery plan with Agent Gateway (Week 1), Workforce Intelligence (Weeks 2-4)
- **Changed:** `AI_CONTEXT/known-issues.md` — added 9 monitoring gotchas (data volume, raw buffer, agent auth, etc.)
- **Changed:** `AI_CONTEXT/rules.md` — added Section 3 Workforce Intelligence Rules, 90+ RBAC permissions
- **Changed:** `docs/architecture/module-catalog.md` — INDEX file linking to individual module docs
- **Changed:** `docs/security/auth-architecture.md` — device JWT, monitoring permissions in roles
- **Changed:** `docs/security/data-classification.md` — RESTRICTED classification for screenshots/verification photos, monitoring retention
- **Changed:** `docs/database/performance.md` — activity partitioning (daily/monthly), Workforce Intelligence indexes
- **Changed:** `docs/architecture/messaging/event-catalog.md` — 15+ new Workforce Intelligence events
- **Changed:** `docs/architecture/external-integrations.md` — Work Activity bridge, biometric moved to IdentityVerification
- **Changed:** `.cursor/rules/project-context.mdc` — updated for 22 modules, two pillars, monitoring rules
- **Updated:** 4 existing WEEK1 task files (22 modules, industry profile, Agent Gateway, monitoring permissions)
- **Changed:** `README.md` — two-pillar overview, product configurations
- **Added:** Monitoring configuration model: industry profile → tenant toggles → per-employee overrides
- **Added:** Three privacy modes: full transparency, partial, covert
- **Why:** Client requirement for workforce monitoring + productivity intelligence. Redesigned as a two-pillar platform rather than bolting monitoring onto HR.

## 2026-04-05 - Rename to ONEVO + Frontend Scope Update

- **Changed:** Renamed all references from "Selfvora" to "ONEVO" across entire knowledge base (~30 files)
- **Changed:** Updated C# namespaces from `Selfvora.*` to `ONEVO.*` (e.g., `ONEVO.Modules.CoreHR`, `ONEVO.SharedKernel`)
- **Changed:** Updated technical strings (cache keys, DB names, URLs, JWT issuer/audience) from `selfvora` to `onevo`
- **Changed:** Frontend (React/Next.js 14) is now **in scope** for Phase 1 — built after backend foundation
- **Removed:** "Frontend React application — separate team/effort" from exclusions list
- **Why:** System name was always ONEVO. Frontend delivery is part of the same 1-month timeline, backend just gets built first.

## 2026-04-05 - Initial Setup

- **Added:** Complete ONEVO Backend Secondary Brain with all directories and files
- **Added:** AI_CONTEXT files: [[project-context]], [[rules]], [[tech-stack]], [[current-focus]], [[known-issues]]
- **Added:** Architecture docs: [[module-catalog]], [[module-boundaries]], [[shared-kernel]], [[multi-tenancy]], messaging ([[event-catalog]], [[exchange-topology]], [[error-handling]])
- **Added:** Database docs: schema conventions, [[migration-patterns]], [[performance|performance guide]]
- **Added:** API docs: design standards, versioning, error handling
- **Added:** Security docs: [[auth-architecture]], [[data-classification]], [[compliance]]
- **Added:** Testing docs: strategy, conventions
- **Added:** Deployment docs: [[ci-cd-pipeline]], [[environment-parity]]
- **Added:** Guide docs: [[coding-standards]], [[git-workflow]], [[logging-standards]]
- **Added:** 4-week delivery plan with developer assignments
- **Added:** Cursor rules for AI agent guidance
- **Why:** Initial project setup — establishing the complete secondary brain for ONEVO backend development with .NET 9
