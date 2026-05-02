# Feature Catalog: ONEVO

**Last Updated:** 2026-04-29

## Architecture Overview

ONEVO follows **Clean Architecture + CQRS** (.NET 9). All features are **feature folders** within `ONEVO.Application/Features/` and `ONEVO.Domain/Features/`.

There are **no separate module `.csproj` files**. The canonical database catalog currently lists **252 unique schema tables**, all served by a single `ApplicationDbContext`.

See [[backend/folder-structure|Folder Structure]] for the full solution layout.

---

## Unified Platform Model

```
ONEVO PLATFORM
  ┌─────────────────────────────────────────────────────┐
  │  ONEVO Frontend (Vite + React 19)                           │
  │    HR Sidebar ──────┐                               │
  │    Work Management Sidebar─┼──→  ONEVO.Api (.NET 9)        │
  │    IDE Extension ───┘      single host, all pillars  │
  └─────────────────────────────────────────────────────┘
                               ↕ ApplicationDbContext
                            PostgreSQL (single database)
```

Work Management is **Pillar 3** - it is internal to ONEVO. All three pillars share the same database, the same ApplicationDbContext, and the same domain event bus.

---

## Product Configuration Matrix

IDE Extension is bundled inside the WorkSync Pack — it is not sold separately. Desktop Agent is bundled inside the Workforce Intelligence Pack. Chat AI is the only standalone add-on in Phase 1.

| Tier | Core | HR Pack | Workforce Intelligence Pack (incl. Desktop Agent) | WorkSync Pack (incl. IDE Extension) | Chat AI Add-on |
|------|:----:|:-------:|:-------------------------------------------------:|:------------------------------------:|:--------------:|
| HR Management | ✓ | ✓ | ✗ | ✗ | ✗ |
| WorkSync Only | ✓ | ✗ | ✗ | ✓ | optional |
| HR + Workforce Intel | ✓ | ✓ | ✓ | ✗ | ✗ |
| HR + WorkSync | ✓ | ✓ | ✗ | ✓ | optional |
| Full Suite | ✓ | ✓ | ✓ | ✓ | optional |

---

## Billing Packs

Tenants are provisioned by an ONEVO operator with a specific pack set. Once active, tenant admins can self-add packs and the Chat AI add-on through the billing section of the app. See [[Userflow/Platform-Setup/billing-subscription|Billing & Subscription]].

| Pack | Modules Included | Pricing Unit |
|------|-----------------|--------------|
| **HR Pack** | Org Structure, Core HR, Leave, Calendar, Skills Core | Per active employee / month |
| **Workforce Intelligence Pack** | Workforce Presence, Activity Monitoring, Discrepancy Engine, Identity Verification, Exception Engine, Productivity Analytics + Desktop Agent | Per monitored device / month |
| **WorkSync Pack** | Projects, Tasks, Planning, OKR, Time, Resources, Chat, Collaboration, Analytics, Integrations + IDE Extension | Per active employee / month |
| **Chat AI Add-on** | AI-assisted chat actions, premium AI detections (W9) | Per active employee / month |

Phase 2 modules (Payroll, Performance, HR Documents, Governance, Skill & Talent Development, etc.) are introduced as standalone add-ons when released. The operator adds them to the module catalog in the Developer Console; they then appear as purchasable add-ons for all tenants.

---

## Feature Registry

### Pillar 1: HR Management

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 1 | Infrastructure | `Features/InfrastructureModule` | 4 | Phase 1 |
| 2 | Auth & Security | `Features/Auth` | 9 | Phase 1 |
| 3 | Org Structure | `Features/OrgStructure` | 12 | Phase 1 |
| 4 | Core HR | `Features/CoreHR` | 13 | Phase 1 |
| 5 | Leave | `Features/Leave` | 5 | Phase 1 |
| 6 | Payroll | `Features/Payroll` | 11 | Phase 2 |
| 7 | Performance | `Features/Performance` | 7 | Phase 2 |
| 8 | Skills & Learning | `Features/Skills` | 15 (5 P1 + 10 P2) | Mixed |
| 9 | HR Documents | `Features/Documents` | 4 P2 new (documents table shared with WorkManagement.Collaboration) | Phase 2 |

> **Org Structure note:** Includes `team_roles`, `team_role_permissions`, `team_member_roles` for stacking permissions across multiple team memberships (12 tables, up from 9).

> **HR Documents note:** The `documents` and `document_versions` tables are created in Phase 1 by WorkManagement.Collaboration. HR Documents (Phase 2) adds `document_categories`, `document_templates`, `document_access_logs`, `document_acknowledgements` only.

### Pillar 2: Workforce Intelligence

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 10 | Workforce Presence | `Features/WorkforcePresence` | 12 | Phase 1 |
| 11 | Activity Monitoring | `Features/ActivityMonitoring` | 9 | Phase 1 |
| 11a | Discrepancy Engine | `Features/DiscrepancyEngine` | 2 | Phase 1 |
| 12 | Identity Verification | `Features/IdentityVerification` | 6 | Phase 1 |
| 13 | Exception Engine | `Features/ExceptionEngine` | 5 | Phase 1 |
| 14 | Productivity Analytics | `Features/ProductivityAnalytics` | 5 | Phase 1 |

### Pillar 3: Work Management

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| W1 | Foundation | `Features/WorkManagement/Foundation` | 5 | Phase 1/2 |
| W2 | Projects | `Features/WorkManagement/Projects` | 7 | Phase 1 |
| W3 | Tasks | `Features/WorkManagement/Tasks` | 13 | Phase 1 |
| W4 | Planning | `Features/WorkManagement/Planning` | 7 | Phase 1 |
| W5 | OKR & Goals | `Features/WorkManagement/OKR` | ~5 | Phase 1 |
| W6 | Time | `Features/WorkManagement/Time` | ~4 | Phase 1 |
| W7 | Resources | `Features/WorkManagement/Resources` | ~3 | Phase 1 |
| W8 | Chat & Messaging | `Features/WorkManagement/Chat` | 8 | Phase 1/2 |
| W9 | Chat AI | `Features/WorkManagement/ChatAI` | 2 (ai_action_jobs + premium_ai_detections) | Phase 1 — **standalone add-on, not bundled in WorkSync Pack** |
| W10 | Collaboration | `Features/WorkManagement/Collaboration` | 4 new + extends documents | Phase 1 |
| W11 | Analytics & Insights | `Features/WorkManagement/Analytics` | 7 | Phase 1 |
| W12 | Integrations | `Features/WorkManagement/Integrations` | 7 | Phase 1 |

Schema files: [[database/schemas/wms-project-management|Project Management]], [[database/schemas/wms-task-management|Task Management]], [[database/schemas/wms-planning|Sprint Planning]], [[database/schemas/wms-chat|Chat + Chat AI]], [[database/schemas/wms-collaboration|Collaboration]], [[database/schemas/wms-analytics|Analytics]], [[database/schemas/wms-integrations|Integrations]]

### IDE Extension

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| IDE | IDE Extension | `Features/IDEExtension` | 5 | Phase 1 |

Schema file: [[database/schemas/ide-extension|IDE Extension]]

Tag engine, context engine, agent entitlement, and SignalR IDEHub spec: [[modules/ide-extension/overview|IDE Extension Overview]]

### Shared Foundation

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 15 | Shared Platform | `Features/SharedPlatform` | 35 | Phase 1/2 |
| 16 | Notifications | `Features/Notifications` | 0 own tables | — |
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

Every feature follows this exact layout within `ONEVO.Application/Features/` and `ONEVO.Domain/Features/`:

```
# Domain layer
ONEVO.Domain/Features/{Feature}/
├── Entities/       EF Core entities (no attributes — configured via Fluent API)
└── Events/         IDomainEvent implementations

# Application layer
ONEVO.Application/Features/{Feature}/
├── Commands/{UseCase}/
│   ├── {UseCase}Command.cs      record : IRequest<Result<ResponseDto>>
│   └── {UseCase}Handler.cs      IRequestHandler<Command, Result<ResponseDto>>
├── Queries/{UseCase}/
│   ├── {UseCase}Query.cs
│   └── {UseCase}Handler.cs
├── DTOs/
│   ├── Requests/                HTTP request body models
│   └── Responses/               handler return types
├── Validators/                  AbstractValidator<{UseCase}Command>
└── EventHandlers/               INotificationHandler<IDomainEvent>

# Infrastructure layer
ONEVO.Infrastructure/Persistence/Configurations/{Feature}/
└── {Entity}Configuration.cs    IEntityTypeConfiguration<T>
```

Work Management features live under `Features/WorkManagement/{SubFeature}/` following the same layout.

---

## Cross-Feature Communication

| Need | Mechanism |
|------|-----------|
| Read data from another feature | Inject `IApplicationDbContext` or `IRepository<T>` — query directly |
| Trigger side effect in another feature | Entity raises `IDomainEvent`; `DomainEventDispatchInterceptor` dispatches after save |
| React to another feature's event | `INotificationHandler<TEvent>` in `EventHandlers/` |
| Background processing | `IBackgroundJobService` (Hangfire) injected in handler |
| Real-time push to IDE | `IIDEHubService` → SignalR IDEHub (task:updated, chat:message, tag:executed, ai:action_pending) |

No RabbitMQ. No IEventBus. No MassTransit. All communication between HR, Workforce Intelligence, and Work Management is in-process.

---

## Developer Platform — Admin API

`ONEVO.Admin.Api` is a separate host inside `ONEVO.sln`. It is not a feature — it has no DbContext. All data access goes through `IApplicationDbContext` via the Application layer exactly like `ONEVO.Api`.

| Aspect | Detail |
|:-------|:-------|
| Host project | `ONEVO.Admin.Api` — separate `Program.cs` |
| JWT Issuer | `onevo-platform-admin` — never valid at `/api/v1/*` |
| Feature data | `Features/DevPlatform` — no TenantId on these entities |
