# Backend Folder Structure Design: ONEVO.sln

**Date:** 2026-05-02  
**Status:** Approved  

---

## Goal

Scaffold the full `ONEVO.sln` backend as a real, buildable .NET 9 solution at `C:\ONEVO-Backend\` using the `dotnet` CLI. All 38 feature folders created across Domain, Application, and Infrastructure layers.

---

## Solution Root

```
C:\ONEVO-Backend\
├── ONEVO.sln
├── src/
├── tests/
└── tools/
```

---

## Projects (9 total)

| Project | Type | Path | References |
|:--------|:-----|:-----|:-----------|
| `ONEVO.Domain` | classlib | `src/ONEVO.Domain` | — |
| `ONEVO.Application` | classlib | `src/ONEVO.Application` | Domain |
| `ONEVO.Infrastructure` | classlib | `src/ONEVO.Infrastructure` | Application |
| `ONEVO.Api` | webapi | `src/ONEVO.Api` | Infrastructure, Application |
| `ONEVO.Admin.Api` | webapi | `src/ONEVO.Admin.Api` | Infrastructure, Application |
| `ONEVO.Tests.Unit` | xunit | `tests/ONEVO.Tests.Unit` | Application |
| `ONEVO.Tests.Integration` | xunit | `tests/ONEVO.Tests.Integration` | Infrastructure |
| `ONEVO.Tests.Architecture` | xunit | `tests/ONEVO.Tests.Architecture` | Domain, Application, Infrastructure |
| `ONEVO.DbMigrator` | console | `tools/ONEVO.DbMigrator` | Infrastructure |

---

## Feature Folders (38 total)

All features get:
- **Domain:** `Features/{Feature}/Entities/` + `Features/{Feature}/Events/`
- **Application:** `Features/{Feature}/Commands/` + `Queries/` + `DTOs/Requests/` + `DTOs/Responses/` + `Validators/` + `EventHandlers/`
- **Infrastructure:** `Persistence/Configurations/{Feature}/`

### Pillar 1 — HR Management

| Folder | Notes |
|:-------|:------|
| `Auth` | |
| `InfrastructureModule` | Named to avoid clash with `ONEVO.Infrastructure` project |
| `OrgStructure` | |
| `CoreHR` | |
| `Leave` | |
| `Payroll` | Phase 2 |
| `Performance` | Phase 2 |
| `Skills` | Mixed Phase 1/2 |
| `Documents` | Phase 2 |

### Pillar 2 — Workforce Intelligence

| Folder | Notes |
|:-------|:------|
| `WorkforcePresence` | |
| `ActivityMonitoring` | |
| `DiscrepancyEngine` | |
| `IdentityVerification` | |
| `ExceptionEngine` | |
| `ProductivityAnalytics` | |

### Pillar 3 — WorkSync

| Folder | Notes |
|:-------|:------|
| `WMFoundation` | WorkSync workspaces, workspace_members (5 tables) |
| `Projects` | |
| `Tasks` | |
| `Planning` | |
| `OKR` | |
| `Time` | |
| `Resources` | |
| `Chat` | |
| `ChatAI` | Standalone add-on |
| `Collaboration` | |
| `WorkSyncAnalytics` | Renamed to avoid future clash |
| `WorkSyncIntegrations` | Renamed to avoid clash with `Integrations/MicrosoftTeams` |

### Shared Foundation

| Folder | Notes |
|:-------|:------|
| `SharedPlatform` | 35 tables — tenants, billing, webhooks, feature flags, Teams accounts |
| `Notifications` | No own tables — handlers only |
| `Configuration` | |
| `Calendar` | |
| `ReportingEngine` | Phase 2 |
| `Grievance` | Phase 2 |
| `Expense` | Phase 2 |
| `AgentGateway` | |
| `DevPlatform` | |
| `Integrations/MicrosoftTeams` | Nested under Integrations namespace |
| `IDEExtension` | |

---

## Infrastructure Extras

Beyond the per-feature EF configurations, Infrastructure also gets:

```
ONEVO.Infrastructure/
├── Persistence/
│   ├── ApplicationDbContext.cs
│   ├── Interceptors/
│   │   ├── AuditInterceptor.cs         # writes audit_logs — no Application handler
│   │   └── DomainEventDispatchInterceptor.cs
│   ├── Configurations/{Feature}/       # per-feature EF Fluent API configs
│   └── Migrations/
├── Services/
│   ├── Email/SmtpEmailService.cs
│   ├── Storage/BlobStorageService.cs
│   ├── Security/AesEncryptionService.cs
│   └── RealTime/
│       ├── SignalRNotificationDispatcher.cs
│       ├── IDEHubService.cs
│       └── HubRegistration.cs
└── DependencyInjection.cs
```

---

## Domain Common

```
ONEVO.Domain/
├── Common/
│   ├── BaseEntity.cs
│   ├── IDomainEvent.cs
│   └── ValueObject.cs
├── Enums/
├── Errors/
│   ├── DomainException.cs
│   ├── NotFoundException.cs
│   └── ForbiddenException.cs
└── ValueObjects/
    ├── Email.cs
    ├── Money.cs
    ├── PhoneNumber.cs
    └── Address.cs
```

---

## Application Common

```
ONEVO.Application/
└── Common/
    ├── Behaviors/
    │   ├── ValidationBehavior.cs
    │   ├── LoggingBehavior.cs
    │   ├── PerformanceBehavior.cs
    │   └── UnhandledExceptionBehavior.cs
    ├── Interfaces/
    │   ├── IApplicationDbContext.cs
    │   ├── IRepository.cs
    │   ├── IUnitOfWork.cs
    │   ├── ICurrentUser.cs
    │   ├── ICacheService.cs
    │   ├── IEncryptionService.cs
    │   ├── IEmailService.cs
    │   ├── IStorageService.cs
    │   ├── IDateTimeProvider.cs
    │   ├── IBackgroundJobService.cs
    │   ├── INotificationDispatcher.cs
    │   ├── ITokenService.cs
    │   ├── IPasswordHasher.cs
    │   └── IIDEHubService.cs
    └── Models/
        ├── Result.cs
        ├── PagedRequest.cs
        └── PagedResult.cs
```

---

## API Hosts

```
ONEVO.Api/
├── Controllers/           # One per feature, thin
├── Hubs/
│   ├── WorkforceLiveHub.cs
│   ├── ExceptionAlertsHub.cs
│   ├── NotificationsHub.cs
│   └── AgentStatusHub.cs
├── Middleware/
│   ├── TenantResolutionMiddleware.cs
│   └── ExceptionHandlingMiddleware.cs
└── Program.cs

ONEVO.Admin.Api/
├── Controllers/
├── Middleware/
└── Program.cs
```

---

## Decisions

- **No `WorkManagement/` parent folder** — all WorkSync features flat, same level as HR features
- **`WMFoundation`** — WorkSync workspace bootstrap tables, not to be confused with SharedPlatform
- **`WorkSyncAnalytics` / `WorkSyncIntegrations`** — prefixed to avoid namespace collisions
- **`SharedPlatform` is a Feature folder** — has real use cases (webhooks, billing, tenant settings); audit logging lives in `Infrastructure/Persistence/Interceptors/` only
- **`ONEVO.Agent.sln` is separate** — not part of this scaffold
