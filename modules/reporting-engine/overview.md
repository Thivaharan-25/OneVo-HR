# Module: Reporting Engine

**Feature Folder:** `Application/Features/ReportingEngine`
**Phase:** 2 — Deferred
**Pillar:** Shared Foundation
**Owner:** Dev 1 (Week 4)
**Tables:** 3

> [!WARNING]
> **This module is deferred to Phase 2. Do not implement.** Reporting is subsumed by Productivity Analytics for Phase 1. This generic reporting engine is deferred. Specs are preserved here for future reference.

---

## Purpose

Scheduled and on-demand report generation serving **both pillars** — HR reports (headcount, turnover, leave utilization) and workforce intelligence reports (productivity, exceptions, presence). Supports CSV/Excel export.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/productivity-analytics/overview\|Productivity Analytics]] | `IProductivityAnalyticsService` | Workforce reports |
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | HR reports |
| **Depends on** | [[modules/leave/overview\|Leave]] | `ILeaveService` | Leave utilization reports |
| **Depends on** | [[modules/workforce-presence/overview\|Workforce Presence]] | `IWorkforcePresenceService` | Attendance reports |

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/ReportingEngine/Entities/
  ONEVO.Domain/Features/ReportingEngine/Events/

Application (CQRS):
  ONEVO.Application/Features/ReportingEngine/Commands/
  ONEVO.Application/Features/ReportingEngine/Queries/
  ONEVO.Application/Features/ReportingEngine/DTOs/Requests/
  ONEVO.Application/Features/ReportingEngine/DTOs/Responses/
  ONEVO.Application/Features/ReportingEngine/Validators/
  ONEVO.Application/Features/ReportingEngine/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/ReportingEngine/

API endpoints:
  ONEVO.Api/Controllers/ReportingEngine/ReportingEngineController.cs

---

## Database Tables (3)

### `report_definitions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `name` | `varchar(100)` | |
| `report_type` | `varchar(30)` | `headcount`, `turnover`, `leave_utilization`, `productivity_daily`, `productivity_weekly`, `workforce_summary`, `exception_summary` |
| `parameters_json` | `jsonb` | Filters, date ranges |
| `schedule_cron` | `varchar(50)` | Cron expression (nullable — on-demand) |
| `output_format` | `varchar(10)` | `csv`, `xlsx` |
| `recipients_json` | `jsonb` | Email recipients |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | |
| `created_at` | `timestamptz` | |

### `report_executions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `definition_id` | `uuid` | FK → report_definitions |
| `status` | `varchar(20)` | `queued`, `running`, `completed`, `failed` |
| `file_record_id` | `uuid` | FK → file_records (generated report) |
| `row_count` | `int` | |
| `started_at` | `timestamptz` | |
| `completed_at` | `timestamptz` | |
| `error_message` | `text` | |

### `report_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `name` | `varchar(100)` | |
| `report_type` | `varchar(30)` | |
| `columns_json` | `jsonb` | Column definitions |
| `filters_json` | `jsonb` | Default filters |
| `is_system` | `boolean` | System templates can't be deleted |

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| _(none)_ | — | — | — |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| _(none — reads directly via query service interfaces)_ | — | — | — |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/reports/definitions` | `reports:read` | List report definitions |
| POST | `/api/v1/reports/definitions` | `reports:create` | Create scheduled report |
| POST | `/api/v1/reports/execute/{definitionId}` | `reports:create` | Run report on-demand |
| GET | `/api/v1/reports/executions` | `reports:read` | List past executions |
| GET | `/api/v1/reports/executions/{id}/download` | `reports:read` | Download report file |

## Features

- [[modules/reporting-engine/report-definitions/overview|Report Definitions]] — Scheduled and on-demand report definitions with cron expressions
- [[modules/reporting-engine/report-execution/overview|Report Execution]] — Execution tracking with file record output (CSV/Excel)
- [[modules/reporting-engine/report-templates/overview|Report Templates]] — System and custom column/filter templates per report type

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All definitions and executions are tenant-scoped
- [[security/data-classification|Data Classification]] — Report files stored in blob storage via `file_records`
- [[security/compliance|Compliance]] — Audit and exception reports support both HR and workforce intelligence pillars
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/productivity-analytics/overview|Productivity Analytics]], [[modules/core-hr/overview|Core Hr]]
