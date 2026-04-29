# Feature Catalog: ONEVO

**Last Updated:** 2026-04-27

## Architecture Overview

ONEVO follows **Clean Architecture + CQRS** (.NET 9). The 24 features that were previously separate module projects are now **feature folders** within `ONEVO.Application/Features/` and `ONEVO.Domain/Features/`.

There are **no separate module `.csproj` files**. All 176 tables live in a single `ApplicationDbContext`.

See [[backend/folder-structure|Folder Structure]] for the full solution layout.

---

## Unified Platform Model

```
ONEVO PLATFORM
  ONEVO Frontend (Next.js)
    ├── HR Sidebar        → ONEVO.Api (.NET 9)
    └── Workforce Sidebar → ONEVO.Api + WMS Backend
                                    ↕ bridge contracts
  ONEVO.Api                      WMS Backend
  All features in one host       Projects, Tasks, Sprints…
```

---

## Product Configuration Matrix

| Tier | Core | HR Pillar | Workforce Intel | WMS | Bridges |
|------|:----:|:---------:|:---------------:|:---:|:-------:|
| HR Management | ✓ | ✓ | ✗ | ✗ | — |
| Work Management | ✓ | ✗ | ✗ | ✓ | People Sync only |
| HR + Workforce Intel | ✓ | ✓ | ✓ | ✗ | — |
| HR + Work Management | ✓ | ✓ | ✗ | ✓ | All 5 bridges |
| Full Suite | ✓ | ✓ | ✓ | ✓ | All 5 bridges |

---

## Feature Registry

### Pillar 1: HR Management

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 1 | Infrastructure | `Features/InfrastructureModule` | 4 | Phase 1 |
| 2 | Auth & Security | `Features/Auth` | 9 | Phase 1 |
| 3 | Org Structure | `Features/OrgStructure` | 9 | Phase 1 |
| 4 | Core HR | `Features/CoreHR` | 13 | Phase 1 |
| 5 | Leave | `Features/Leave` | 5 | Phase 1 |
| 6 | Payroll | `Features/Payroll` | 11 | Phase 2 |
| 7 | Performance | `Features/Performance` | 7 | Phase 2 |
| 8 | Skills & Learning | `Features/Skills` | 15 (5 P1 + 10 P2) | Mixed |
| 9 | Documents | `Features/Documents` | 6 | Phase 2 |

### Pillar 2: Workforce Intelligence

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 10 | Workforce Presence | `Features/WorkforcePresence` | 12 | Phase 1 |
| 11 | Activity Monitoring | `Features/ActivityMonitoring` | 9 | Phase 1 |
| 11a | Discrepancy Engine | `Features/DiscrepancyEngine` | 2 | Phase 1 |
| 12 | Identity Verification | `Features/IdentityVerification` | 6 | Phase 1 |
| 13 | Exception Engine | `Features/ExceptionEngine` | 5 | Phase 1 |
| 14 | Productivity Analytics | `Features/ProductivityAnalytics` | 5 | Phase 1 |

### Shared Foundation

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 15 | Shared Platform | `Features/SharedPlatform` | 33 | Phase 1 |
| 16 | Notifications | `Features/Notifications` | 2 | Phase 1 |
| 17 | Configuration | `Features/Configuration` | 6 | Phase 1 |
| 18 | Calendar | `Features/Calendar` | 1 | Phase 1 |
| 19 | Reporting Engine | `Features/ReportingEngine` | 3 | Phase 2 |
| 20 | Grievance | `Features/Grievance` | 2 | Phase 2 |
| 21 | Expense | `Features/Expense` | 3 | Phase 2 |
| 22 | Agent Gateway | `Features/AgentGateway` | 4 | Phase 1 |
| 23 | Dev Platform | `Features/DevPlatform` | 5 (P1) + 1 (P2) | Mixed |

**Total: 24 features, 176 tables (133 Phase 1 · 43 Phase 2)**

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

---

## Cross-Feature Communication

| Need | Mechanism |
|------|-----------|
| Read data from another feature | Inject `IApplicationDbContext` or `IRepository<T>` — query directly |
| Trigger side effect in another feature | Entity raises `IDomainEvent`; `DomainEventDispatchInterceptor` dispatches after save |
| React to another feature's event | `INotificationHandler<TEvent>` in `EventHandlers/` |
| Background processing | `IBackgroundJobService` (Hangfire) injected in handler |

No RabbitMQ. No IEventBus. No MassTransit. All communication is in-process.

---

## Developer Platform — Admin API

`ONEVO.Admin.Api` is a separate host inside `ONEVO.sln`. It is not a feature — it has no DbContext. All data access goes through `IApplicationDbContext` via the Application layer exactly like `ONEVO.Api`.

| Aspect | Detail |
|:-------|:-------|
| Host project | `ONEVO.Admin.Api` — separate `Program.cs` |
| JWT Issuer | `onevo-platform-admin` — never valid at `/api/v1/*` |
| Feature data | `Features/DevPlatform` — no TenantId on these entities |

---

## WMS — Consumed System

WMS is external. ONEVO communicates via HTTP bridge contracts only.

Full detail: [[backend/bridge-api-contracts|Bridge API Contracts]]
