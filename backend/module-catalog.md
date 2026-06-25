# Feature Catalog: ONEVO

**Last Updated:** 2026-05-13

## Architecture Overview

ONEVO follows **Clean Architecture + CQRS**. The backend targets **.NET 10 / C# 14**. All features are **feature folders** within `ONEVO.Application/Features/` and `ONEVO.Domain/Features/`.

There are **no separate module `.csproj` files**. The canonical database catalog currently lists **252 unique schema tables**, all served by a single `ApplicationDbContext`.

See [[backend/folder-structure|Folder Structure]] for the full solution layout.

---

## Unified Platform Model

```
ONEVO PLATFORM
  +-----------------------------------------------------+
  |  ONEVO Frontend (Vite + React 19)                           |
  |    HR Sidebar ------+                               |
  |    Work Management Sidebar-+--?  ONEVO.Api (.NET 10)|
  |    IDE Extension (Phase 2) -+ single host, all pillars|
  +-----------------------------------------------------+
                               ? ApplicationDbContext
                            PostgreSQL (single database)
```

Work Management is **Pillar 3** - it is internal to ONEVO. All three pillars share the same database and the same ApplicationDbContext. Domain events are optional and are used only for justified post-save side effects.

---

## Product Configuration Matrix

ONEVO uses Subscription Plans with base modules, optional module add-ons, resource-only add-ons, and always-included Foundation modules. Tenant access controls whether tenant admins can configure/manage the module (`Full`), only consume/use tenant-provided setup (`Use only`), only view module outputs (`View only`), or have no tenant-facing access (`None`).

| # | Module | Layer | Plan Role | Tenant Access |
|---:|---|---|---|---|
| 1 | Authentication and Authorization | Foundation | Always Included | None |
| 2 | Tenant Configuration and Onboarding | Foundation | Always Included | None |
| 3 | Roles and Permissions | Foundation | Always Included | Use only |
| 4 | Profile Management | HR Core | Plan-selected module | Full |
| 5 | Attendance and Time Off Management | HR Core | Plan-selected module | Full |
| 6 | E2E Monitoring | Intelligence | Plan-selected module | View only |
| 7 | Productivity and Performance Analytics | Intelligence | Plan-selected module | View only |
| 8 | Monitoring Alerts | Intelligence | Phase 1 lightweight alerts; full Exception Engine is Phase 2 | View only |
| 9 | Overtime Management | Intelligence | Plan-selected module | Full |
| 10 | Project Management | Work Management | Plan-selected module | Full |
| 11 | Third Party Integrations | Work Management | Plan-selected module | Full |
| 12 | Agentic Chat | Work Management | Phase 2 plan-selected module | Full |
| 13 | IDE Extension | Work Management | Phase 2 plan-selected module | Full |

---

## Subscription Plan Composition

Tenants are provisioned or upgraded onto one selected base plan. The selected plan can include base modules, optional module add-ons, and resource-only add-ons. See [[Userflow/Platform-Setup/billing-subscription|Billing & Subscription]].

| Component | Meaning |
|---|---|
| Foundation | Always included services required for every tenant |
| Base package modules | Included automatically when the plan is selected |
| Optional module add-ons | Added only when selected and charged once |
| Resource-only add-ons | Extra Storage Pack and Extra AI Token Pack; no module entitlement |

Phase 2 modules (Payroll, Performance, HR Documents, Governance, Skill & Talent Development, etc.) are introduced as standalone add-ons when released. The operator adds them to the module catalog in the Developer Console; they then appear as purchasable add-ons for all tenants.

### Module Pricing Brackets

Module Catalog pricing, storage, and AI values are references only. Company-size pricing brackets live in Subscription Plans. The tenant owner's confirmed employee count selects the applicable tier for first-invoice calculation, and both calculated price and any operator override are stored for audit.

Example: for the `51-200` employee range, the selected base plan plus selected add-ons displays the calculated price for the tenant before any operator-negotiated override.

---

## Feature Registry

### Pillar 1: HR Management

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 1 | Infrastructure | `Features/InfrastructureModule` | 4 | Phase 1 |
| 2 | Auth & Security | `Features/Auth` | 9 | Phase 1 |
| 3 | Org Structure | `Features/OrgStructure` | 12 | Phase 1 |
| 4 | Core HR | `Features/CoreHR` | 13 | Phase 1 |
| 5 | Time Off | `Features/TimeOff` | 5 | Phase 1 |
| 6 | Payroll | `Features/Payroll` | 11 | Phase 2 |
| 7 | Performance | `Features/Performance` | 7 | Phase 2 |
| 8 | Skills & Learning | `Features/Skills` | 15 (5 P1 + 10 P2) | Mixed |
| 9 | HR Documents | `Features/Documents` | 4 P2 new (documents table shared with WorkManagement.Collaboration) | Phase 2 |


> **HR Documents note:** The `documents` and `document_versions` tables are created in Phase 1 by WorkManagement.Collaboration. HR Documents (Phase 2) adds `document_categories`, `document_templates`, `document_access_logs`, `document_acknowledgements` only.

### Pillar 2: Monitoring

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 10 | Time & Attendance | `Features/TimeAttendance` | 12 | Phase 1 |
| 11 | Activity Monitoring | `Features/ActivityMonitoring` | 9 | Phase 1 |
| 11a | Discrepancy Engine | `Features/DiscrepancyEngine` | 2 | Phase 1 |
| 12 | Identity Verification | `Features/IdentityVerification` | 6 | Phase 1 |
| 13 | Exception Engine | `Features/ExceptionEngine` | 5 | Phase 2 |
| 14 | Productivity Analytics | `Features/ProductivityAnalytics` | 5 | Phase 1 |

### Pillar 3: Work Management

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| W1 | Foundation | `Features/WMFoundation` | 5 | Phase 1/2 |
| W2 | Projects | `Features/Projects` | 7 | Phase 1 |
| W3 | Tasks | `Features/Tasks` | 13 | Phase 1 |
| W4 | Planning | `Features/Planning` | 7 | Phase 2 |
| W5 | OKR & Goals | `Features/OKR` | ~5 | Phase 2 |
| W6 | Time | `Features/Time` | ~4 | Phase 1 |
| W7 | Resources | `Features/Resources` | ~3 | Phase 2 |
| W8 | Chat & Messaging | `Features/Chat` | 8 | Phase 2 |
| W9 | Agentic Chat AI | `Features/ChatAI` | 2 (ai_action_jobs + premium_ai_detections) | Phase 2 |
| W10 | Collaboration | `Features/Collaboration` | 4 new + extends documents | Phase 1 |
| W11 | Analytics & Insights | `Features/WorkSyncAnalytics` | 7 | Phase 2 |
| W12 | Integrations | `Features/WorkSyncIntegrations` | 7 | Phase 2 |

Schema files: [[database/schemas/wms-project-management|Project Management]], [[database/schemas/wms-task-management|Task Management]], [[database/schemas/wms-planning|Sprint Planning]], [[database/schemas/wms-collaboration|Collaboration]], [[database/schemas/wms-analytics|Analytics]], [[database/schemas/wms-integrations|Integrations]]. [[database/schemas/wms-chat|Chat + Chat AI]] is Phase 2.

### IDE Extension

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| IDE | IDE Extension | `Features/IDEExtension` | 5 | Phase 2 |

Schema file: [[database/schemas/ide-extension|IDE Extension]]

Tag engine, context engine, agent entitlement, and SignalR IDEHub spec: [[modules/ide-extension/overview|IDE Extension Overview]]

### Shared Foundation

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 15 | Shared Platform | `Features/SharedPlatform` | 35 | Phase 1/2; Phase 1 notifications/billing/config only, Workflow/Automation Engine is Phase 2 |
| 16 | Notifications | `Features/Notifications` | 0 own tables | - |
| 17 | Configuration | `Features/Configuration` | 6 | Phase 1 |
| 18 | Calendar | `Features/Calendar` | 1 | Phase 1 |
| 19 | Reporting Engine | `Features/ReportingEngine` | 3 | Phase 2 |
| 20 | Grievance | `Features/Grievance` | 2 | Phase 2 |
| 21 | Expense | `Features/Expense` | 3 | Phase 2 |
| 22 | Agent Gateway | `Features/AgentGateway` | 6 | Phase 1 |
| 23 | Dev Platform | `Features/DevPlatform` | 5 (P1) + 1 (P2) | Mixed |
| 24 | Microsoft Teams Integration | `Features/Integrations/MicrosoftTeams` | Uses Shared Platform + Work Management Teams tables | Phase 2 |

> **Shared Platform note:** Old external-provisioning tables removed because Work Management is internal. Count is 35 after Microsoft Teams account/token/webhook/delta tables.
> **Agent Gateway note:** Added `agent_install_entitlements` and `agent_install_jobs` for IDE Extension entitlement gating. Count is 6 (was 4).

**Total: ~38 features, 252 unique schema tables in the canonical database catalog**

---

## Feature Folder Structure

Every feature follows the canonical layout in [[backend/folder-structure|Folder Structure]]. The normal Application shape is:

```text
ONEVO.Application/Features/{Feature}/
|-- Commands/
|   `-- {UseCase}/
|       |-- {UseCase}Command.cs
|       |-- {UseCase}Handler.cs
|       `-- {UseCase}Validator.cs
|-- Queries/
|   `-- {UseCase}/
|       |-- {UseCase}Query.cs
|       `-- {UseCase}Handler.cs
|-- DTOs/
|   |-- Requests/
|   `-- Responses/
`-- Interfaces/
```

The normal Domain shape is:

```text
ONEVO.Domain/Features/{Feature}/
`-- Entities/
```

Optional event folders are created only when a use case has justified post-save side effects:

```text
ONEVO.Domain/Features/{Feature}/Events/
ONEVO.Application/Features/{Feature}/EventHandlers/
```

Work Management features are flat - no `WorkManagement/` parent folder. Each WorkSync feature lives directly under `Features/{Feature}/` following the same layout as all other features.

---
## Cross-Feature Communication

| Need | Mechanism |
|------|-----------|
| Read data from another feature | Inject the owning feature's repository/reader interface; never query another feature's DbSet directly |
| Do work in the same use case | Keep it in the command handler or an Application service |
| Trigger decoupled post-save side effect | Optional domain event; `DomainEventDispatchInterceptor` dispatches after save |
| React to a justified event | `INotificationHandler<TEvent>` in optional `EventHandlers/` |
| Background processing | `IBackgroundJobService` (Hangfire) injected in handler |
| Real-time push to IDE | Phase 2 `IIDEHubService` -> SignalR IDEHub (task:updated, chat:message, tag:executed, ai:action_pending) |

No RabbitMQ. No IEventBus. No MassTransit. Most feature communication is direct through Application-owned interfaces; domain events are available by exception for decoupled post-save side effects.

---

## Developer Platform - Admin API

Developer Console endpoints live under `/admin/v1/*` inside the single `ONEVO.Api` host. Phase 1 does not have a separate admin backend service. All data access goes through Application-owned repository/service interfaces exactly like customer APIs. Platform-level cross-tenant reads/writes must be explicit in those interface names and implementations.

| Aspect | Detail |
|:-------|:-------|
| Host project | `ONEVO.Api` - `Controllers/Admin/` |
| JWT Issuer | `onevo-platform-admin` - never valid at `/api/v1/*` |
| Feature data | `Features/DevPlatform` - no TenantId on these entities |
