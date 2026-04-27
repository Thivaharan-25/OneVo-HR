# Clean Architecture + CQRS — ONEVO Platform Design Spec

**Date:** 2026-04-27
**Status:** Approved
**Author:** Thivaharan
**Deadline:** 2026-05-31

---

## 1. Context & Why

The original ONEVO backend was designed as a **modular monolith** with 24 separate module projects, per-module DbContexts, RabbitMQ via MassTransit for cross-module async communication, and a transactional outbox per module. No code has been written yet.

The decision is to redesign to **Clean Architecture + CQRS** before writing a single line of code, for the following reasons:

- May 31 deadline makes the modular monolith too complex to deliver
- Microservice extraction is no longer a goal — removing the main justification for per-module DbContexts and RabbitMQ
- Clean Architecture is simpler, more testable, and faster to build
- CQRS with MediatR replaces all messaging infrastructure with in-process handlers

**What is dropped:**
- RabbitMQ + MassTransit
- Per-module transactional outbox
- 24 separate module `.csproj` files
- `IEventBus` abstraction
- Per-module `DbContext` (24 → 1)

---

## 2. Architecture Decision Summary

| Decision | Choice | Reason |
|---|---|---|
| Architecture pattern | Clean Architecture | Framework independence, testability, layer isolation |
| CQRS | MediatR (in-process) | No distributed systems overhead |
| Cross-feature events | MediatR `INotification` | Replaces RabbitMQ entirely |
| DbContext | Single `ApplicationDbContext` | No microservice extraction, single UoW, atomic transactions |
| Module structure | Feature folders within layers | Preserves logical grouping, maps to existing mental model |
| Agent app | Separate solution `ONEVO.Agent.sln` | Independent release cycle, ring-based deployment, security boundary |
| Phase 1 platform | Windows only | MacOS in Phase 2 |

---

## 3. Solution Structure

### ONEVO.sln (server-side)

```
ONEVO.sln
├── src/
│   ├── ONEVO.Domain/           Layer 1 — entities, domain events, value objects, enums, errors
│   ├── ONEVO.Application/      Layer 2 — CQRS handlers, interfaces, DTOs, validators, behaviors
│   ├── ONEVO.Infrastructure/   Layer 3 — EF Core, JWT, BCrypt, Redis, Hangfire, SignalR, S3
│   ├── ONEVO.Api/              Layer 4a — customer-facing ASP.NET Core host (/api/v1/*)
│   └── ONEVO.Admin.Api/        Layer 4b — developer console host (/admin/v1/*)
├── tests/
│   ├── ONEVO.Tests.Unit/
│   ├── ONEVO.Tests.Integration/
│   └── ONEVO.Tests.Architecture/
└── tools/
    └── ONEVO.DbMigrator/
```

### ONEVO.Agent.sln (desktop agent — separate repo)

```
ONEVO.Agent.sln
├── src/
│   ├── ONEVO.Agent.Core/           pure logic — no OS dependencies
│   ├── ONEVO.Agent.Windows/        Windows tray app + capture implementations
│   └── ONEVO.Agent.Infrastructure/ HTTP client to ONEVO.Api
└── tests/
    └── ONEVO.Agent.Tests.Unit/
```

### Strict Dependency Rule (enforced by ArchUnitNET)

```
ONEVO.Api / ONEVO.Admin.Api
        ↓ (references)
ONEVO.Application  ←  ONEVO.Infrastructure
        ↓
ONEVO.Domain

FORBIDDEN:
  Application → Infrastructure    (Application defines interfaces, never implements)
  Domain → anything               (Domain has zero external dependencies)
```

---

## 4. Layer 1 — ONEVO.Domain

Contains pure business entities and rules. No framework dependencies. No EF attributes (configured via Fluent API in Infrastructure).

```
ONEVO.Domain/
├── Common/
│   ├── BaseEntity.cs               Id (UUID v7), TenantId, CreatedAt, UpdatedAt,
│   │                               CreatedById, IsDeleted, List<IDomainEvent> DomainEvents
│   ├── IDomainEvent.cs             : INotification (MediatR) — replaces IEventBus entirely
│   └── ValueObject.cs              abstract base, equality by value
├── Enums/
│   ├── EmploymentType.cs
│   ├── EmploymentStatus.cs
│   ├── ApprovalStatus.cs
│   ├── Severity.cs
│   ├── WorkMode.cs
│   └── ... (all shared enums)
├── Errors/
│   ├── DomainException.cs
│   ├── NotFoundException.cs
│   └── ForbiddenException.cs
├── ValueObjects/
│   ├── Email.cs
│   ├── Money.cs
│   ├── PhoneNumber.cs
│   └── Address.cs
└── Features/                       24 feature folders — entities + domain events
    ├── Auth/
    │   ├── Entities/
    │   │   ├── User.cs
    │   │   ├── Role.cs
    │   │   ├── Permission.cs
    │   │   ├── UserRole.cs
    │   │   ├── RolePermission.cs
    │   │   ├── Session.cs
    │   │   ├── MfaToken.cs
    │   │   ├── AuditLog.cs
    │   │   └── PasswordResetToken.cs
    │   └── Events/
    │       ├── UserCreatedEvent.cs
    │       └── UserDeactivatedEvent.cs
    ├── InfrastructureModule/        (Tenants, Files, Countries) — named InfrastructureModule not Infrastructure to avoid collision with ONEVO.Infrastructure layer project
    │   ├── Entities/
    │   │   ├── Tenant.cs
    │   │   ├── TenantSubscription.cs
    │   │   ├── Country.cs
    │   │   └── FileStorage.cs
    │   └── Events/
    │       └── TenantCreatedEvent.cs
    ├── OrgStructure/
    │   ├── Entities/
    │   │   ├── LegalEntity.cs
    │   │   ├── Department.cs
    │   │   ├── JobFamily.cs
    │   │   ├── JobGrade.cs
    │   │   ├── Team.cs
    │   │   ├── CostCenter.cs
    │   │   ├── WorkLocation.cs
    │   │   ├── BusinessUnit.cs
    │   │   └── Division.cs
    │   └── Events/
    │       └── DepartmentCreatedEvent.cs
    ├── CoreHR/
    │   ├── Entities/
    │   │   ├── Employee.cs
    │   │   ├── EmployeeProfile.cs
    │   │   ├── SalaryHistory.cs
    │   │   ├── JobHistory.cs
    │   │   ├── Onboarding.cs
    │   │   ├── OnboardingTask.cs
    │   │   ├── Offboarding.cs
    │   │   ├── OffboardingTask.cs
    │   │   ├── EmergencyContact.cs
    │   │   ├── EmployeeDocument.cs
    │   │   ├── EmployeeBenefit.cs
    │   │   ├── EmployeeEquipment.cs
    │   │   └── EmploymentContract.cs
    │   └── Events/
    │       ├── EmployeeCreatedEvent.cs
    │       ├── EmployeeTerminatedEvent.cs
    │       └── EmployeeProfileUpdatedEvent.cs
    ├── Leave/
    │   ├── Entities/
    │   │   ├── LeaveType.cs
    │   │   ├── LeavePolicy.cs
    │   │   ├── LeaveEntitlement.cs
    │   │   ├── LeaveRequest.cs
    │   │   └── LeaveAdjustment.cs
    │   └── Events/
    │       ├── LeaveRequestSubmittedEvent.cs
    │       └── LeaveApprovedEvent.cs
    ├── Payroll/
    │   ├── Entities/
    │   │   ├── PayrollProvider.cs
    │   │   ├── PayrollRun.cs
    │   │   ├── PayrollLine.cs
    │   │   ├── TaxConfiguration.cs
    │   │   ├── Allowance.cs
    │   │   ├── Deduction.cs
    │   │   ├── PensionScheme.cs
    │   │   ├── BonusGrant.cs
    │   │   ├── SalaryComponent.cs
    │   │   ├── PayslipTemplate.cs
    │   │   └── PayrollAudit.cs
    │   └── Events/
    │       └── PayrollRunCompletedEvent.cs
    ├── Performance/
    │   ├── Entities/
    │   │   ├── ReviewCycle.cs
    │   │   ├── PerformanceReview.cs
    │   │   ├── Goal.cs
    │   │   ├── Feedback.cs
    │   │   ├── SuccessionPlan.cs
    │   │   ├── CompetencyFramework.cs
    │   │   └── RatingScale.cs
    │   └── Events/
    │       └── ReviewCompletedEvent.cs
    ├── Skills/
    │   ├── Entities/
    │   │   ├── SkillCategory.cs
    │   │   ├── Skill.cs
    │   │   ├── JobSkillRequirement.cs
    │   │   ├── EmployeeSkill.cs
    │   │   └── SkillValidationRequest.cs
    │   └── Events/
    │       └── SkillValidatedEvent.cs
    ├── Documents/
    │   ├── Entities/
    │   │   ├── Document.cs
    │   │   ├── DocumentVersion.cs
    │   │   ├── DocumentTemplate.cs
    │   │   ├── DocumentSignature.cs
    │   │   ├── DocumentCategory.cs
    │   │   └── DocumentAccessLog.cs
    │   └── Events/
    │       └── DocumentSignedEvent.cs
    ├── WorkforcePresence/
    │   ├── Entities/
    │   │   ├── Shift.cs
    │   │   ├── ShiftSchedule.cs
    │   │   ├── PresenceRecord.cs
    │   │   ├── BiometricDevice.cs
    │   │   ├── BiometricLog.cs
    │   │   ├── OvertimeEntry.cs
    │   │   ├── AttendanceCorrection.cs
    │   │   ├── ShiftSwapRequest.cs
    │   │   ├── GeoFenceZone.cs
    │   │   ├── ShiftRotation.cs
    │   │   ├── WorkScheduleTemplate.cs
    │   │   └── PresenceSummary.cs
    │   └── Events/
    │       ├── PresenceRecordedEvent.cs
    │       └── ShiftStartedEvent.cs
    ├── ActivityMonitoring/
    │   ├── Entities/
    │   │   ├── ActivitySnapshot.cs
    │   │   ├── AppUsageLog.cs
    │   │   ├── MeetingLog.cs
    │   │   ├── Screenshot.cs
    │   │   ├── BrowserActivityLog.cs
    │   │   ├── SystemEventLog.cs
    │   │   ├── ProductivityScore.cs
    │   │   ├── ActivityCategory.cs
    │   │   └── MonitoringSession.cs
    │   └── Events/
    │       └── SnapshotCapturedEvent.cs
    ├── IdentityVerification/
    │   ├── Entities/
    │   │   ├── VerificationRequest.cs
    │   │   ├── PhotoVerification.cs
    │   │   ├── BiometricMatch.cs
    │   │   ├── VerificationPolicy.cs
    │   │   ├── VerificationAudit.cs
    │   │   └── VerificationResult.cs
    │   └── Events/
    │       └── IdentityVerifiedEvent.cs
    ├── ExceptionEngine/
    │   ├── Entities/
    │   │   ├── AnomalyRule.cs
    │   │   ├── AnomalyAlert.cs
    │   │   ├── EscalationPolicy.cs
    │   │   ├── AlertAcknowledgement.cs
    │   │   └── RuleEvaluation.cs
    │   └── Events/
    │       └── AnomalyDetectedEvent.cs
    ├── DiscrepancyEngine/
    │   ├── Entities/
    │   │   ├── DiscrepancyEvent.cs
    │   │   └── WmsDailyTimeLog.cs
    │   └── Events/
    │       └── DiscrepancyFlaggedEvent.cs
    ├── ProductivityAnalytics/
    │   ├── Entities/
    │   │   ├── ProductivityReport.cs
    │   │   ├── ProductivityTrend.cs
    │   │   ├── WorkforceSnapshot.cs
    │   │   ├── AnalyticsDashboard.cs
    │   │   └── ReportExport.cs
    │   └── Events/
    │       └── ReportGeneratedEvent.cs
    ├── SharedPlatform/
    │   ├── Entities/
    │   │   ├── SsoProvider.cs
    │   │   ├── FeatureFlag.cs
    │   │   ├── TenantFeatureFlag.cs
    │   │   ├── Workflow.cs
    │   │   ├── WorkflowStep.cs
    │   │   ├── WorkflowInstance.cs
    │   │   ├── NotificationTemplate.cs
    │   │   └── NotificationChannel.cs
    │   └── Events/
    │       └── FeatureFlagChangedEvent.cs
    ├── Notifications/
    │   ├── Entities/
    │   │   ├── Notification.cs
    │   │   └── NotificationPreference.cs
    │   └── Events/
    │       └── NotificationCreatedEvent.cs
    ├── Configuration/
    │   ├── Entities/
    │   │   ├── TenantSetting.cs
    │   │   ├── IntegrationConfig.cs
    │   │   ├── MonitoringToggle.cs
    │   │   ├── WebhookConfig.cs
    │   │   ├── SmtpConfig.cs
    │   │   └── StorageConfig.cs
    │   └── Events/
    │       └── ConfigurationChangedEvent.cs
    ├── Calendar/
    │   ├── Entities/
    │   │   └── CalendarEvent.cs
    │   └── Events/
    │       └── CalendarEventCreatedEvent.cs
    ├── ReportingEngine/
    │   ├── Entities/
    │   │   ├── ScheduledReport.cs
    │   │   ├── ReportExecution.cs
    │   │   └── ReportTemplate.cs
    │   └── Events/
    │       └── ReportScheduledEvent.cs
    ├── Grievance/
    │   ├── Entities/
    │   │   ├── GrievanceCase.cs
    │   │   └── DisciplinaryAction.cs
    │   └── Events/
    │       └── GrievanceCaseFiled.cs
    ├── Expense/
    │   ├── Entities/
    │   │   ├── ExpenseCategory.cs
    │   │   ├── ExpenseClaim.cs
    │   │   └── ExpenseItem.cs
    │   └── Events/
    │       └── ExpenseClaimSubmittedEvent.cs
    ├── AgentGateway/
    │   ├── Entities/
    │   │   ├── RegisteredAgent.cs
    │   │   ├── AgentHeartbeat.cs
    │   │   ├── AgentPolicy.cs
    │   │   └── AgentIngestionLog.cs
    │   └── Events/
    │       └── AgentRegisteredEvent.cs
    └── DevPlatform/
        ├── Entities/
        │   ├── DevPlatformAccount.cs
        │   ├── DevPlatformSession.cs
        │   ├── AgentVersionRelease.cs
        │   ├── AgentDeploymentRing.cs
        │   └── AgentDeploymentRingAssignment.cs
        └── Events/
            └── AgentVersionPublishedEvent.cs
```

---

## 5. Layer 2 — ONEVO.Application

Contains all business logic orchestration. Defines interfaces — never implements them. References only ONEVO.Domain.

```
ONEVO.Application/
├── Common/
│   ├── Behaviors/
│   │   ├── ValidationBehavior.cs           FluentValidation — runs first, throws before handler
│   │   ├── LoggingBehavior.cs              logs request name, user, tenant, duration
│   │   ├── PerformanceBehavior.cs          warns if handler exceeds 500ms
│   │   └── UnhandledExceptionBehavior.cs   final safety net
│   ├── Interfaces/
│   │   ├── IApplicationDbContext.cs        DbSet<T> properties — Application never touches EF directly
│   │   ├── IRepository.cs                  IRepository<T> generic — GetByIdAsync, GetAllAsync, AddAsync, Update, Delete
│   │   ├── IUnitOfWork.cs                  SaveChangesAsync(CancellationToken ct)
│   │   ├── ICurrentUser.cs                 UserId, TenantId, Permissions[]
│   │   ├── ICacheService.cs                Get/Set/Remove — L1+L2 abstraction
│   │   ├── IEncryptionService.cs           Encrypt/Decrypt — AES-256 for PII
│   │   ├── IEmailService.cs                SendAsync(to, subject, body, ct)
│   │   ├── IStorageService.cs              UploadAsync / DownloadAsync / DeleteAsync
│   │   ├── IDateTimeProvider.cs            UtcNow — testable DateTime
│   │   ├── IBackgroundJobService.cs        Enqueue / Schedule — Hangfire abstraction
│   │   ├── INotificationDispatcher.cs      PushAsync — SignalR abstraction
│   │   ├── ITokenService.cs                GenerateToken / ValidateToken
│   │   └── IPasswordHasher.cs              Hash / Verify — BCrypt abstraction
│   └── Models/
│       ├── Result.cs                       Result<T>, Error — no exceptions for business failures
│       ├── PagedRequest.cs                 Page, PageSize, SortBy, SortDirection
│       └── PagedResult.cs                  Items, TotalCount, Page, TotalPages
│
└── Features/                              24 feature folders
    └── {Feature}/
        ├── Commands/
        │   └── {UseCase}/
        │       ├── {UseCase}Command.cs         record : IRequest<Result<ResponseDto>>
        │       └── {UseCase}CommandHandler.cs  IRequestHandler<Command, Result<ResponseDto>>
        ├── Queries/
        │   └── {UseCase}/
        │       ├── {UseCase}Query.cs            record : IRequest<Result<ResponseDto>>
        │       └── {UseCase}QueryHandler.cs
        ├── DTOs/
        │   ├── Requests/                        HTTP request body models
        │   └── Responses/                       handler return types
        ├── Validators/
        │   └── {UseCase}Validator.cs            AbstractValidator<{UseCase}Command>
        └── EventHandlers/
            └── {EventName}Handler.cs            INotificationHandler<IDomainEvent>
```

**CQRS example (Leave feature):**

```
Features/Leave/
├── Commands/
│   ├── CreateLeaveRequest/
│   │   ├── CreateLeaveRequestCommand.cs
│   │   └── CreateLeaveRequestCommandHandler.cs
│   └── ApproveLeaveRequest/
│       ├── ApproveLeaveRequestCommand.cs
│       └── ApproveLeaveRequestCommandHandler.cs
├── Queries/
│   ├── GetLeaveBalance/
│   │   ├── GetLeaveBalanceQuery.cs
│   │   └── GetLeaveBalanceQueryHandler.cs
│   └── GetLeaveRequests/
│       ├── GetLeaveRequestsQuery.cs
│       └── GetLeaveRequestsQueryHandler.cs
├── DTOs/
│   ├── Requests/
│   │   └── CreateLeaveRequestDto.cs
│   └── Responses/
│       ├── LeaveRequestDto.cs
│       └── LeaveBalanceDto.cs
├── Validators/
│   └── CreateLeaveRequestValidator.cs
└── EventHandlers/
    └── LeaveApprovedEventHandler.cs       reacts when Leave publishes LeaveApprovedEvent
```

---

## 6. Layer 3 — ONEVO.Infrastructure

Implements all interfaces defined in Application. References Application + Domain.

```
ONEVO.Infrastructure/
├── Persistence/
│   ├── ApplicationDbContext.cs             single DbContext — all 176 tables
│   │                                       global query filters: TenantId + IsDeleted
│   ├── ApplicationDbContextFactory.cs      IDesignTimeDbContextFactory for migrations
│   ├── Migrations/                         ONE migration set for entire solution
│   ├── Interceptors/
│   │   ├── AuditableEntityInterceptor.cs   auto-sets CreatedAt, UpdatedAt, CreatedById
│   │   ├── SoftDeleteInterceptor.cs        converts Delete → IsDeleted=true
│   │   └── DomainEventDispatchInterceptor.cs  collects DomainEvents post-save → IPublisher
│   ├── Configurations/                     IEntityTypeConfiguration<T> per entity
│   │   ├── Auth/
│   │   │   ├── UserConfiguration.cs
│   │   │   └── ... (9 configs)
│   │   ├── OrgStructure/   CoreHR/   Leave/  ... (24 feature folders, 176 configs total)
│   ├── Repositories/
│   │   └── GenericRepository.cs            IRepository<T> — tenant-filtered, soft-delete aware
│   └── UnitOfWork.cs                       wraps ApplicationDbContext.SaveChangesAsync
│
├── Identity/
│   ├── JwtTokenService.cs                  ValidateLifetime=true, ClockSkew=Zero, key from env
│   ├── CurrentUserService.cs               reads UserId+TenantId+Permissions from HttpContext JWT
│   ├── PasswordHasher.cs                   BCrypt.Net-Next WorkFactor=12
│   └── PermissionService.cs               RBAC permission evaluation
│
├── Caching/
│   ├── RedisCacheService.cs                ICacheService — L1 in-memory + L2 Redis
│   └── CacheKeys.cs                        centralized key naming constants
│
├── BackgroundJobs/
│   ├── HangfireConfiguration.cs            PostgreSQL storage, server setup
│   ├── Queues.cs                           Critical / High / Default / Low / Batch
│   └── BackgroundJobService.cs             IBackgroundJobService implementation
│
├── RealTime/
│   ├── SignalRNotificationDispatcher.cs    INotificationDispatcher — pushes to SignalR hubs
│   └── HubRegistration.cs                 registers all hubs at startup
│
├── Email/
│   └── SmtpEmailService.cs                IEmailService implementation
│
├── Storage/
│   └── BlobStorageService.cs              IStorageService — Azure Blob / S3
│
├── Security/
│   └── AesEncryptionService.cs            IEncryptionService — AES-256-GCM for PII fields
│
├── ExternalServices/
│   └── WmsBridgeClient.cs                HTTP client for WMS bridge webhooks
│
└── DependencyInjection.cs                 services.AddInfrastructure(config)
```

---

## 7. Layer 4a — ONEVO.Api

Customer-facing host. Thin controllers only — no business logic.

```
ONEVO.Api/
├── Controllers/                    one controller per feature, all thin
│   ├── Auth/AuthController.cs
│   ├── OrgStructure/OrgStructureController.cs
│   ├── CoreHR/EmployeesController.cs
│   ├── Leave/LeaveController.cs
│   ├── Payroll/PayrollController.cs
│   ├── Performance/PerformanceController.cs
│   ├── Skills/SkillsController.cs
│   ├── Documents/DocumentsController.cs
│   ├── WorkforcePresence/WorkforcePresenceController.cs
│   ├── ActivityMonitoring/ActivityMonitoringController.cs
│   ├── IdentityVerification/IdentityVerificationController.cs
│   ├── ExceptionEngine/ExceptionEngineController.cs
│   ├── ProductivityAnalytics/ProductivityAnalyticsController.cs
│   ├── Notifications/NotificationsController.cs
│   ├── Configuration/ConfigurationController.cs
│   ├── Calendar/CalendarController.cs
│   ├── Grievance/GrievanceController.cs
│   ├── Expense/ExpenseController.cs
│   └── AgentGateway/AgentGatewayController.cs
├── Hubs/
│   ├── WorkforceLiveHub.cs
│   ├── ExceptionAlertsHub.cs
│   ├── NotificationsHub.cs
│   └── AgentStatusHub.cs
├── Middleware/
│   ├── TenantResolutionMiddleware.cs   extracts TenantId from JWT → ICurrentUser
│   ├── PermissionMiddleware.cs         evaluates RequirePermission attributes
│   └── ExceptionHandlerMiddleware.cs   RFC 7807 Problem Details — all unhandled exceptions
├── Filters/
│   └── RequirePermissionAttribute.cs
└── Program.cs                         calls services.AddApplication() + services.AddInfrastructure()
```

## 7b. Layer 4b — ONEVO.Admin.Api

Developer console host. Same pattern — thin controllers calling Application layer.

```
ONEVO.Admin.Api/
├── Controllers/
│   ├── TenantsController.cs
│   ├── FeatureFlagsController.cs
│   ├── AgentVersionsController.cs
│   ├── AuditController.cs
│   ├── SystemConfigController.cs
│   └── ApiKeysController.cs              Phase 2
├── Middleware/
│   └── PlatformAdminAuthMiddleware.cs    validates iss: onevo-platform-admin
├── Policies/
│   ├── PlatformAdminPolicy.cs            30-min TTL
│   └── ImpersonationOnlyPolicy.cs        15-min TTL
└── Program.cs
```

---

## 8. Security Implementation

### Password Hashing
- Library: `BCrypt.Net-Next`
- WorkFactor: **12** (non-negotiable)
- Interface: `IPasswordHasher` in Application
- Implementation: `PasswordHasher.cs` in Infrastructure/Identity

### JWT
- `ValidateLifetime = true`
- `ClockSkew = TimeSpan.Zero` — no grace window
- `SecretKey` — environment variable only, **never** in `appsettings.json`
- Three issuers: `onevo-customer`, `onevo-platform-admin`, `onevo-agent`
- Tokens from one issuer are **never valid** at endpoints requiring another issuer

### PII Encryption
- Algorithm: AES-256-GCM
- Interface: `IEncryptionService` in Application
- Implementation: `AesEncryptionService.cs` in Infrastructure/Security
- Applied via EF Core value converters on columns: NIC, passport number, bank account, salary details, biometric hashes
- Encryption key: Azure Key Vault in production, environment variable in dev

### Multi-Tenancy
- `TenantResolutionMiddleware` reads `tenant_id` claim from JWT → sets `ICurrentUser`
- `ApplicationDbContext` injects `ICurrentUser` and applies global query filters:
  - `HasQueryFilter(x => x.TenantId == _currentUser.TenantId)`
  - `HasQueryFilter(x => !x.IsDeleted)`
- DevPlatform entities have **no TenantId** — platform-level only, no tenant filter applied

### RBAC
- `[RequirePermission("leave:approve")]` on controller endpoints
- `PermissionMiddleware` reads `Permissions[]` from JWT claims
- 403 → `ExceptionHandlerMiddleware` → RFC 7807 Problem Details response

### Global Exception Handling (RFC 7807)

| Exception type | HTTP status | Notes |
|---|---|---|
| `NotFoundException` | 404 | Resource not found |
| `ForbiddenException` | 403 | Insufficient permissions |
| `ValidationException` | 422 | FluentValidation errors array |
| `DomainException` | 422 | Business rule violation |
| `System.Exception` | 500 | Logs full stack, returns safe message |

---

## 9. CQRS Pipeline

Request travels through MediatR behaviors in this exact order:

```
HTTP Request
    ↓
[1] ValidationBehavior        — FluentValidation, returns 422 before handler if invalid
    ↓
[2] LoggingBehavior           — logs command name, UserId, TenantId, timestamp
    ↓
[3] PerformanceBehavior       — logs warning if elapsed > 500ms
    ↓
[4] UnhandledExceptionBehavior — catches any unhandled exception, re-throws for middleware
    ↓
Handler (Command or Query)
    ↓
IUnitOfWork.SaveChangesAsync(ct)
    ↓
AuditableEntityInterceptor    — sets CreatedAt/UpdatedAt/CreatedById
SoftDeleteInterceptor         — converts hard deletes to IsDeleted=true
DomainEventDispatchInterceptor — collects domain events → IPublisher.Publish() in-process
    ↓
Result<T> → Controller → HTTP Response
```

### CancellationToken Rule
Every handler, repository call, and external HTTP call must accept and pass `CancellationToken ct`. No exceptions.

### Result Pattern
Handlers never throw for business failures — they return `Result<T>`:
```
Result<T>.Success(value)       — happy path
Result<T>.Failure(error)       — business rule failure, maps to 422
```
Only infrastructure failures (DB down, network) throw exceptions caught by middleware.

---

## 10. Domain Events (replaces RabbitMQ entirely)

### Pattern
1. Entity method raises business action (e.g. `LeaveRequest.Approve()`)
2. Method adds event to `DomainEvents` list on `BaseEntity`
3. `IUnitOfWork.SaveChangesAsync()` persists the DB change
4. `DomainEventDispatchInterceptor` collects all `DomainEvents` from tracked entities
5. Dispatches each via `IPublisher.Publish(event, ct)` (MediatR in-process)
6. `INotificationHandler<LeaveApprovedEvent>` in any feature's `EventHandlers/` reacts

### Cross-feature event wiring example
```
Leave feature publishes:         LeaveApprovedEvent
WorkforcePresence handles:       LeaveApprovedEventHandler.cs → marks shift absent
Payroll handles:                 LeaveApprovedEventHandler.cs → creates deduction entry
```
Both handlers live in their respective feature's `EventHandlers/` folder under Application.

### What is gone
- `IEventBus` — deleted
- `IntegrationEvent` base class — deleted
- `MassTransit` — not installed
- `IConsumer<T>` — deleted
- Per-module `OutboxMessage.cs` — deleted
- Per-module `OutboxProcessor.cs` — deleted
- RabbitMQ exchange/queue topology — deleted

---

## 11. ONEVO Agent Architecture (separate solution)

### Why separate solution
- Independent release cycle — server deploys daily, agent uses ring-based rollout to thousands of machines
- `agent_version_releases` + `agent_deployment_rings` tables in DevPlatform exist to manage this
- Security boundary — agent binary on employee machines must not contain server internals
- Phase 2: add `ONEVO.Agent.Mac/` without touching server solution

### Solution structure

```
ONEVO.Agent.sln
├── src/
│   ├── ONEVO.Agent.Core/
│   │   ├── Capture/
│   │   │   ├── IScreenshotCapture.cs
│   │   │   ├── IAppUsageCapture.cs
│   │   │   └── IBrowserActivityCapture.cs
│   │   ├── Sync/
│   │   │   ├── IAgentApiClient.cs         POSTs snapshots to AgentGateway
│   │   │   └── IOfflineQueue.cs           buffers data when network unavailable
│   │   ├── Policy/
│   │   │   └── AgentPolicy.cs             capture rules fetched from server
│   │   └── Models/
│   │       ├── ActivitySnapshot.cs
│   │       ├── AppUsageRecord.cs
│   │       └── HeartbeatPayload.cs
│   │
│   ├── ONEVO.Agent.Windows/
│   │   ├── Capture/
│   │   │   ├── WindowsScreenshotCapture.cs      GDI+ / PrintWindow API
│   │   │   ├── WindowsAppUsageCapture.cs         GetForegroundWindow + Process API
│   │   │   └── WindowsBrowserCapture.cs
│   │   ├── Tray/
│   │   │   ├── SystemTrayIcon.cs                 NotifyIcon
│   │   │   └── TrayContextMenu.cs
│   │   ├── Storage/
│   │   │   └── SQLiteOfflineQueue.cs             local queue — survives network drops
│   │   ├── AutoUpdate/
│   │   │   └── AgentUpdater.cs                   polls AgentGateway for new version ring
│   │   └── Program.cs                            .NET Worker Service host
│   │
│   └── ONEVO.Agent.Infrastructure/
│       ├── AgentApiClient.cs                     HTTP client → ONEVO.Api AgentGateway endpoints
│       ├── AgentAuthService.cs                   machine token auth (provisioned at IT install)
│       └── PolicySyncService.cs                  GETs capture policy from AgentGateway
│
└── tests/
    └── ONEVO.Agent.Tests.Unit/
```

### Agent auth flow
1. IT admin provisions a machine token via `AgentGateway` endpoint
2. Token stored in Windows Credential Manager (not registry, not plain file)
3. Agent uses token for all API calls — `iss: onevo-agent`
4. Token is tenant-scoped — identifies which employee machine this is

---

## 12. Complete File Change Plan

### DELETE — 5 files

```
backend/messaging/README.md
backend/messaging/error-handling.md
backend/messaging/event-catalog.md
backend/messaging/module-event-matrix.md
backend/messaging/exchange-topology.md
```

### FULL REWRITE — 5 files

```
backend/folder-structure.md              4-layer Clean Architecture + ONEVO.Agent.sln
backend/module-catalog.md                feature folders, updated solution structure
backend/module-boundaries.md             layer dependency rules + ArchUnitNET
backend/shared-kernel.md                 ONEVO.Domain layer documentation
AI_CONTEXT/project-context.md           updated architecture description
```

### PARTIAL UPDATE — Backend (8 files)

```
backend/README.md
backend/api-conventions.md
backend/bridge-api-contracts.md         remove RabbitMQ, HTTP-only bridge remains
backend/notification-system.md          remove IEventBus, in-process domain events
backend/real-time.md                    remove module project refs
backend/external-integrations.md
backend/monitoring-data-flow.md
backend/search-architecture.md
```

### PARTIAL UPDATE — Developer Platform (8 files)

```
developer-platform/overview.md
developer-platform/system-design.md
developer-platform/auth.md
developer-platform/database/schema.md           single ApplicationDbContext
developer-platform/backend/admin-api-layer.md   remove module project refs
developer-platform/backend/api-contracts.md
developer-platform/modules/agent-version-manager/overview.md
developer-platform/modules/app-catalog-manager/overview.md
```

### PARTIAL UPDATE — Module feature docs (24 files)

Keep all domain/feature content. Update only code structure sections — remove `Internal/`, `Public/`, per-module DbContext. Replace with feature folder path.

```
modules/infrastructure/overview.md       → Application/Features/InfrastructureModule/
modules/auth/overview.md                 → Application/Features/Auth/
modules/org-structure/overview.md        → Application/Features/OrgStructure/
modules/core-hr/overview.md              → Application/Features/CoreHR/
modules/leave/overview.md                → Application/Features/Leave/
modules/payroll/overview.md              → Application/Features/Payroll/
modules/performance/overview.md          → Application/Features/Performance/
modules/skills/overview.md               → Application/Features/Skills/
modules/documents/overview.md            → Application/Features/Documents/
modules/workforce-presence/overview.md   → Application/Features/WorkforcePresence/
modules/activity-monitoring/overview.md  → Application/Features/ActivityMonitoring/
modules/identity-verification/overview.md → Application/Features/IdentityVerification/
modules/exception-engine/overview.md     → Application/Features/ExceptionEngine/
modules/discrepancy-engine/overview.md   → Application/Features/DiscrepancyEngine/
modules/productivity-analytics/overview.md → Application/Features/ProductivityAnalytics/
modules/shared-platform/overview.md      → Application/Features/SharedPlatform/
modules/notifications/overview.md        → Application/Features/Notifications/
modules/configuration/overview.md        → Application/Features/Configuration/
modules/calendar/overview.md             → Application/Features/Calendar/
modules/reporting-engine/overview.md     → Application/Features/ReportingEngine/
modules/grievance/overview.md            → Application/Features/Grievance/
modules/expense/overview.md              → Application/Features/Expense/
modules/agent-gateway/overview.md        → Application/Features/AgentGateway/
modules/dev-platform/overview.md         → Application/Features/DevPlatform/
```

### SUPERSEDE — 1 ADR

```
docs/decisions/ADR-001-per-module-database-and-event-bus.md
  → Add status header: "Superseded by ADR-002 and ADR-003 on 2026-04-27"
```

### CREATE NEW — Architecture docs (8 files)

```
backend/clean-architecture-overview.md
backend/layer-guide/domain-layer.md
backend/layer-guide/application-layer.md
backend/layer-guide/infrastructure-layer.md
backend/layer-guide/webapi-layer.md
backend/security.md
backend/cqrs-patterns.md
backend/domain-events.md
```

### CREATE NEW — Agent docs (2 files)

```
backend/agent/overview.md
backend/agent/windows-agent.md
```

### CREATE NEW — ADRs (2 files)

```
docs/decisions/ADR-002-clean-architecture-cqrs.md
docs/decisions/ADR-003-single-applicationdbcontext.md
```

### File change summary

| Action | Count |
|---|---|
| DELETE | 5 |
| FULL REWRITE | 5 |
| PARTIAL UPDATE | 40 |
| CREATE NEW | 12 |
| **Total affected** | **62** |

---

## 13. Tests

```
ONEVO.Tests.Unit/
  Features/
    Leave/
      Commands/ApproveLeaveRequestCommandHandlerTests.cs
      Queries/GetLeaveBalanceQueryHandlerTests.cs
    CoreHR/ Auth/ ... (per feature)

ONEVO.Tests.Integration/
  Features/ (real DB via Testcontainers — Postgres + Redis)

ONEVO.Tests.Architecture/
  LayerDependencyTests.cs    ArchUnitNET rules:
    Domain has no outgoing references
    Application references only Domain
    Infrastructure references Application + Domain
    WebApi references Application + Infrastructure (DI wiring only)
    No circular dependencies
```

---

## 14. NuGet Packages

### ONEVO.Domain
- `MediatR` (IDomainEvent : INotification)

### ONEVO.Application
- `MediatR`
- `FluentValidation`
- `FluentValidation.DependencyInjectionExtensions`

### ONEVO.Infrastructure
- `Microsoft.EntityFrameworkCore`
- `Npgsql.EntityFrameworkCore.PostgreSQL`
- `BCrypt.Net-Next`
- `Microsoft.AspNetCore.Authentication.JwtBearer`
- `StackExchange.Redis`
- `Hangfire.PostgreSql`
- `Microsoft.AspNetCore.SignalR`

### REMOVED (no longer needed)
- `MassTransit`
- `MassTransit.RabbitMQ`
- `MassTransit.EntityFrameworkCore` (outbox)
