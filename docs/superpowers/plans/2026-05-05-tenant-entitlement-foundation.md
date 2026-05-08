# Tenant + Entitlement Foundation Implementation Plan

> **Superseded provisioning note:** This plan contains the older public self-signup and direct `adminPassword` implementation design. Current ONEVO guidance is operator-only tenant provisioning through `/admin/v1/tenants`: create provisioning draft, assign commercial terms/modules/settings/role templates, invite the tenant owner with a set-password link, then activate. Do not use this document as the source of truth for tenant creation flow, password handling, or production provisioning APIs.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build server-side module gates and tenant provisioning so the web app, IDE extension, and Developer Platform can resolve which modules and permissions a user has.

**Architecture:** A static `ModuleCatalog` defines all known module keys. A minimal `SubscriptionPlan` + `TenantSubscription` model links tenants to their plan's allowed modules. `ModuleEntitlementService` resolves active modules (plan âˆ© catalog Â± `FeatureAccessGrant` overrides); `IPermissionResolver` (already implemented in Task 2) resolves effective permissions. A single `GET /api/v1/me/entitlements` endpoint returns both for any consumer. `TenantProvisioningService` creates Tenant + LegalEntity + admin User + TenantSubscription in one transaction on public signup.

**Tech Stack:** .NET 9, EF Core 9 (InMemory for tests / Npgsql for prod), MediatR, FluentValidation, xUnit, WebApplicationFactory. Working directory for all `dotnet` commands: `C:\OneVo-HR\OneVo-backend`.

---

## Scope boundaries (do NOT build these)

- Full billing / Stripe / `plan_features` table â€” Task 5 (SharedPlatform)
- Org structure (departments, teams, employees) â€” DEV2 Task 1 (LegalEntity here is a minimal stub)
- Industry-profile monitoring toggle seeding â€” Task 6 (Configuration)
- DevPlatform Admin API HTTP controllers â€” Task 7 (only the service interface is built here)
- Workflow engine â€” Task 5

---

## File map

### Create
```
ONEVO.Domain/Modules/ModuleKey.cs
ONEVO.Domain/Modules/ModuleCatalog.cs
ONEVO.Domain/Features/InfrastructureModule/Events/TenantProvisioned.cs
ONEVO.Domain/Features/SharedPlatform/Entities/SubscriptionPlan.cs
ONEVO.Domain/Features/SharedPlatform/Entities/TenantSubscription.cs
ONEVO.Domain/Features/OrgStructure/Entities/LegalEntity.cs

ONEVO.Application/Features/InfrastructureModule/EntitlementErrors.cs
ONEVO.Application/Features/InfrastructureModule/Interfaces/IModuleEntitlementService.cs
ONEVO.Application/Features/InfrastructureModule/Interfaces/ITenantProvisioningService.cs
ONEVO.Application/Features/InfrastructureModule/DTOs/EntitlementDto.cs
ONEVO.Application/Features/InfrastructureModule/Commands/ProvisionTenant/ProvisionTenantCommand.cs
ONEVO.Application/Features/InfrastructureModule/Commands/ProvisionTenant/ProvisionTenantCommandHandler.cs
ONEVO.Application/Features/InfrastructureModule/Commands/ProvisionTenant/ProvisionTenantCommandValidator.cs
ONEVO.Application/Features/InfrastructureModule/Queries/GetMyEntitlements/GetMyEntitlementsQuery.cs
ONEVO.Application/Features/InfrastructureModule/Queries/GetMyEntitlements/GetMyEntitlementsQueryHandler.cs

ONEVO.Infrastructure/Persistence/Configurations/SharedPlatform/SubscriptionPlanConfiguration.cs
ONEVO.Infrastructure/Persistence/Configurations/SharedPlatform/TenantSubscriptionConfiguration.cs
ONEVO.Infrastructure/Persistence/Configurations/OrgStructure/LegalEntityConfiguration.cs
ONEVO.Infrastructure/Services/ModuleEntitlementService.cs
ONEVO.Infrastructure/Services/TenantProvisioningService.cs

ONEVO.Api/Controllers/InfrastructureModule/InfrastructureModuleController.cs
ONEVO.Api/Controllers/InfrastructureModule/EntitlementController.cs

tests/ONEVO.Tests.Unit/Entitlement/ModuleCatalogTests.cs
tests/ONEVO.Tests.Unit/Entitlement/ModuleEntitlementServiceTests.cs
tests/ONEVO.Tests.Integration/Entitlement/EntitlementTestFactory.cs
tests/ONEVO.Tests.Integration/Entitlement/TenantProvisioningTests.cs
tests/ONEVO.Tests.Integration/Entitlement/EntitlementEndpointTests.cs
tests/ONEVO.Tests.Integration/Entitlement/ModuleAssignmentTests.cs
```

### Modify
```
ONEVO.Domain/Features/InfrastructureModule/Entities/Tenant.cs          â€” add IndustryProfile, MarkProvisioned()
ONEVO.Application/Common/Interfaces/IApplicationDbContext.cs            â€” add 3 new DbSets
ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs                â€” add 3 new DbSets + query filters
ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/TenantConfiguration.cs  â€” add industry_profile column
ONEVO.Infrastructure/DependencyInjection.cs                             â€” register 2 new services
current-focus/DEV1.md                                                   â€” tick Task 3 checkboxes
```

---

## Task 1: ModuleCatalog Static Registry

**Files:**
- Create: `src/ONEVO.Domain/Modules/ModuleKey.cs`
- Create: `src/ONEVO.Domain/Modules/ModuleCatalog.cs`
- Test: `tests/ONEVO.Tests.Unit/Entitlement/ModuleCatalogTests.cs`

- [ ] **Step 1: Write the failing tests**

```csharp
// tests/ONEVO.Tests.Unit/Entitlement/ModuleCatalogTests.cs
using ONEVO.Domain.Modules;

namespace ONEVO.Tests.Unit.Entitlement;

public class ModuleCatalogTests
{
    [Fact]
    public void All_ContainsExpectedPhase1Modules()
    {
        Assert.Contains(ModuleKey.CoreHr, ModuleCatalog.All);
        Assert.Contains(ModuleKey.Leave, ModuleCatalog.All);
        Assert.Contains(ModuleKey.Calendar, ModuleCatalog.All);
        Assert.Contains(ModuleKey.WorkforcePresence, ModuleCatalog.All);
        Assert.Contains(ModuleKey.ActivityMonitoring, ModuleCatalog.All);
        Assert.Contains(ModuleKey.WorkSync, ModuleCatalog.All);
        Assert.Contains(ModuleKey.Notifications, ModuleCatalog.All);
        Assert.Contains(ModuleKey.IdeExtension, ModuleCatalog.All);
    }

    [Fact]
    public void All_HasNoDuplicates()
    {
        Assert.Equal(ModuleCatalog.All.Count, ModuleCatalog.All.Distinct().Count());
    }

    [Fact]
    public void IsKnown_ReturnsTrueForValidKey()
    {
        Assert.True(ModuleCatalog.IsKnown(ModuleKey.CoreHr));
        Assert.True(ModuleCatalog.IsKnown(ModuleKey.WorkSync));
    }

    [Fact]
    public void IsKnown_ReturnsFalseForUnknownKey()
    {
        Assert.False(ModuleCatalog.IsKnown("phantom_module"));
        Assert.False(ModuleCatalog.IsKnown(""));
    }
}
```

- [ ] **Step 2: Run â€” expect compile failure (types don't exist yet)**

```
dotnet test tests/ONEVO.Tests.Unit --filter Entitlement
```

Expected: Build error `The type or namespace name 'ModuleKey' could not be found`.

- [ ] **Step 3: Create ModuleKey.cs**

```csharp
// src/ONEVO.Domain/Modules/ModuleKey.cs
namespace ONEVO.Domain.Modules;

public static class ModuleKey
{
    public const string CoreHr              = "core_hr";
    public const string Leave               = "leave";
    public const string Calendar            = "calendar";
    public const string WorkforcePresence   = "workforce_presence";
    public const string ActivityMonitoring  = "activity_monitoring";
    public const string ExceptionEngine     = "exception_engine";
    public const string IdentityVerification = "identity_verification";
    public const string WorkSync            = "work_sync";
    public const string Notifications       = "notifications";
    public const string DataImport          = "data_import";
    public const string Skills              = "skills";
    public const string Configuration       = "configuration";
    public const string AgentGateway        = "agent_gateway";
    public const string IdeExtension        = "ide_extension";
}
```

- [ ] **Step 4: Create ModuleCatalog.cs**

```csharp
// src/ONEVO.Domain/Modules/ModuleCatalog.cs
namespace ONEVO.Domain.Modules;

public static class ModuleCatalog
{
    private static readonly HashSet<string> _all = new(StringComparer.Ordinal)
    {
        ModuleKey.CoreHr,
        ModuleKey.Leave,
        ModuleKey.Calendar,
        ModuleKey.WorkforcePresence,
        ModuleKey.ActivityMonitoring,
        ModuleKey.ExceptionEngine,
        ModuleKey.IdentityVerification,
        ModuleKey.WorkSync,
        ModuleKey.Notifications,
        ModuleKey.DataImport,
        ModuleKey.Skills,
        ModuleKey.Configuration,
        ModuleKey.AgentGateway,
        ModuleKey.IdeExtension,
    };

    public static IReadOnlyCollection<string> All => _all;

    public static bool IsKnown(string key) => _all.Contains(key);
}
```

- [ ] **Step 5: Run â€” expect all 4 tests pass**

```
dotnet test tests/ONEVO.Tests.Unit --filter Entitlement
```

Expected: `4 passed, 0 failed`.

- [ ] **Step 6: Commit**

```
git add src/ONEVO.Domain/Modules/ tests/ONEVO.Tests.Unit/Entitlement/ModuleCatalogTests.cs
git commit -m "feat(entitlement): add ModuleKey constants and ModuleCatalog registry"
```

---

## Task 2: Domain Entities

**Files:**
- Create: `src/ONEVO.Domain/Features/InfrastructureModule/Events/TenantProvisioned.cs`
- Create: `src/ONEVO.Domain/Features/SharedPlatform/Entities/SubscriptionPlan.cs`
- Create: `src/ONEVO.Domain/Features/SharedPlatform/Entities/TenantSubscription.cs`
- Create: `src/ONEVO.Domain/Features/OrgStructure/Entities/LegalEntity.cs`
- Modify: `src/ONEVO.Domain/Features/InfrastructureModule/Entities/Tenant.cs`
- Test: `tests/ONEVO.Tests.Unit/Entitlement/TenantProvisioningDomainTests.cs`

- [ ] **Step 1: Write the failing unit test for Tenant.MarkProvisioned**

```csharp
// tests/ONEVO.Tests.Unit/Entitlement/TenantProvisioningDomainTests.cs
using ONEVO.Domain.Features.InfrastructureModule.Entities;
using ONEVO.Domain.Features.InfrastructureModule.Events;

namespace ONEVO.Tests.Unit.Entitlement;

public class TenantProvisioningDomainTests
{
    [Fact]
    public void Tenant_Create_SetsProvisioningStatus()
    {
        var tenant = Tenant.Create("Acme Corp", "acme-corp", "office_it");

        Assert.Equal("provisioning", tenant.Status);
        Assert.False(tenant.IsActive);
        Assert.Equal("office_it", tenant.IndustryProfile);
        Assert.Equal("acme-corp", tenant.Slug);
    }

    [Fact]
    public void Tenant_MarkProvisioned_SetsActiveAndRaisesEvent()
    {
        var planId = Guid.NewGuid();
        var tenant = Tenant.Create("Acme Corp", "acme-corp", "retail");

        tenant.MarkProvisioned(planId);

        Assert.Equal("active", tenant.Status);
        Assert.True(tenant.IsActive);
        Assert.Equal(planId, tenant.SubscriptionPlanId);
        Assert.NotNull(tenant.ActivatedAt);

        var evt = Assert.Single(tenant.DomainEvents);
        var provisioned = Assert.IsType<TenantProvisioned>(evt);
        Assert.Equal(tenant.Id, provisioned.TenantId);
        Assert.Equal("acme-corp", provisioned.Slug);
        Assert.Equal("retail", provisioned.IndustryProfile);
    }

    [Fact]
    public void Tenant_Create_SlugIsLowercased()
    {
        var tenant = Tenant.Create("Acme Corp", "ACME-CORP", "office_it");
        Assert.Equal("acme-corp", tenant.Slug);
    }
}
```

- [ ] **Step 2: Run â€” expect compile failure**

```
dotnet test tests/ONEVO.Tests.Unit --filter Entitlement
```

Expected: Build errors for `TenantProvisioned`, `IndustryProfile`, `MarkProvisioned`.

- [ ] **Step 3: Create TenantProvisioned domain event**

```csharp
// src/ONEVO.Domain/Features/InfrastructureModule/Events/TenantProvisioned.cs
using ONEVO.Domain.Common;

namespace ONEVO.Domain.Features.InfrastructureModule.Events;

public record TenantProvisioned(
    Guid TenantId,
    string Slug,
    string IndustryProfile
) : IDomainEvent;
```

- [ ] **Step 4: Update Tenant.cs â€” add IndustryProfile and MarkProvisioned**

Replace the full file content:

```csharp
// src/ONEVO.Domain/Features/InfrastructureModule/Entities/Tenant.cs
using ONEVO.Domain.Common;
using ONEVO.Domain.Features.InfrastructureModule.Events;

namespace ONEVO.Domain.Features.InfrastructureModule.Entities;

public class Tenant : PlatformEntity
{
    public string Name { get; private set; } = string.Empty;
    public string Slug { get; private set; } = string.Empty;
    public string Status { get; private set; } = "provisioning";
    public string IndustryProfile { get; private set; } = "office_it";
    public Guid? SubscriptionPlanId { get; private set; }
    public string? PrimaryDomain { get; private set; }
    public bool IsActive { get; private set; }
    public DateTimeOffset? SuspendedAt { get; private set; }
    public DateTimeOffset? ActivatedAt { get; private set; }

    private Tenant() { }

    public static Tenant Create(string name, string slug, string industryProfile = "office_it")
        => new()
        {
            Id = Guid.NewGuid(),
            Name = name,
            Slug = slug.ToLowerInvariant(),
            IndustryProfile = industryProfile,
            Status = "provisioning",
            IsActive = false,
            CreatedAt = DateTimeOffset.UtcNow
        };

    public void MarkProvisioned(Guid planId)
    {
        Status = "active";
        IsActive = true;
        SubscriptionPlanId = planId;
        ActivatedAt = DateTimeOffset.UtcNow;
        PublishEvent(new TenantProvisioned(Id, Slug, IndustryProfile));
    }
}
```

- [ ] **Step 5: Create SubscriptionPlan entity**

```csharp
// src/ONEVO.Domain/Features/SharedPlatform/Entities/SubscriptionPlan.cs
using ONEVO.Domain.Common;

namespace ONEVO.Domain.Features.SharedPlatform.Entities;

public class SubscriptionPlan : PlatformEntity
{
    public string Name { get; private set; } = string.Empty;
    public string Code { get; private set; } = string.Empty;
    public string[] AllowedModules { get; private set; } = [];
    public bool IsActive { get; private set; } = true;

    private SubscriptionPlan() { }

    public static SubscriptionPlan Create(string name, string code, string[] allowedModules)
        => new()
        {
            Id = Guid.NewGuid(),
            Name = name,
            Code = code.ToLowerInvariant(),
            AllowedModules = allowedModules,
            IsActive = true,
            CreatedAt = DateTimeOffset.UtcNow
        };
}
```

- [ ] **Step 6: Create TenantSubscription entity**

```csharp
// src/ONEVO.Domain/Features/SharedPlatform/Entities/TenantSubscription.cs
using ONEVO.Domain.Common;
using ONEVO.Domain.Features.SharedPlatform.Entities;

namespace ONEVO.Domain.Features.SharedPlatform.Entities;

public class TenantSubscription : BaseEntity
{
    public Guid PlanId { get; private set; }
    public string Status { get; private set; } = "trialing";
    public DateOnly? PeriodStart { get; private set; }
    public DateOnly? PeriodEnd { get; private set; }

    // EF navigation â€” loaded via Include()
    public SubscriptionPlan Plan { get; private set; } = null!;

    private TenantSubscription() { }

    public static TenantSubscription Create(Guid tenantId, Guid planId, Guid createdById)
        => new()
        {
            Id = Guid.NewGuid(),
            TenantId = tenantId,
            PlanId = planId,
            Status = "trialing",
            CreatedById = createdById,
            CreatedAt = DateTimeOffset.UtcNow
        };
}
```

- [ ] **Step 7: Create LegalEntity minimal stub**

```csharp
// src/ONEVO.Domain/Features/OrgStructure/Entities/LegalEntity.cs
// NOTE: Minimal stub. Dev 2 (DEV2.T1) extends with registration_number, address, etc.
using ONEVO.Domain.Common;

namespace ONEVO.Domain.Features.OrgStructure.Entities;

public class LegalEntity : BaseEntity
{
    public string Name { get; private set; } = string.Empty;
    public string? CountryCode { get; private set; }
    public bool IsDefault { get; private set; }

    private LegalEntity() { }

    public static LegalEntity Create(
        string name, Guid tenantId, Guid createdById, string? countryCode = null)
        => new()
        {
            Id = Guid.NewGuid(),
            TenantId = tenantId,
            Name = name,
            CountryCode = countryCode,
            IsDefault = true,
            CreatedById = createdById,
            CreatedAt = DateTimeOffset.UtcNow
        };
}
```

- [ ] **Step 8: Run unit tests â€” expect all 7 pass**

```
dotnet test tests/ONEVO.Tests.Unit --filter Entitlement
```

Expected: `7 passed, 0 failed`.

- [ ] **Step 9: Commit**

```
git add src/ONEVO.Domain/ tests/ONEVO.Tests.Unit/Entitlement/TenantProvisioningDomainTests.cs
git commit -m "feat(entitlement): add SubscriptionPlan, TenantSubscription, LegalEntity entities and TenantProvisioned event"
```

---

## Task 3: EF Configurations + DbContext Update

**Files:**
- Create: `src/ONEVO.Infrastructure/Persistence/Configurations/SharedPlatform/SubscriptionPlanConfiguration.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Configurations/SharedPlatform/TenantSubscriptionConfiguration.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Configurations/OrgStructure/LegalEntityConfiguration.cs`
- Modify: `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/TenantConfiguration.cs`
- Modify: `src/ONEVO.Application/Common/Interfaces/IApplicationDbContext.cs`
- Modify: `src/ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs`

- [ ] **Step 1: Add new DbSets to IApplicationDbContext**

Open `src/ONEVO.Application/Common/Interfaces/IApplicationDbContext.cs` and add 3 using directives + 3 DbSet properties. The full updated file:

```csharp
// src/ONEVO.Application/Common/Interfaces/IApplicationDbContext.cs
using Microsoft.EntityFrameworkCore;
using ONEVO.Domain.Features.Auth.Entities;
using ONEVO.Domain.Features.InfrastructureModule.Entities;
using ONEVO.Domain.Features.OrgStructure.Entities;
using ONEVO.Domain.Features.SharedPlatform.Entities;

namespace ONEVO.Application.Common.Interfaces;

public interface IApplicationDbContext
{
    DbSet<Country> Countries { get; }
    DbSet<Tenant> Tenants { get; }
    DbSet<User> Users { get; }
    DbSet<FileRecord> FileRecords { get; }

    // Auth
    DbSet<Role> Roles { get; }
    DbSet<UserRole> UserRoles { get; }
    DbSet<Permission> Permissions { get; }
    DbSet<RolePermission> RolePermissions { get; }
    DbSet<RefreshToken> RefreshTokens { get; }
    DbSet<Session> Sessions { get; }
    DbSet<UserMfa> UserMfas { get; }
    DbSet<MfaRecoveryCode> MfaRecoveryCodes { get; }
    DbSet<UserPermissionOverride> UserPermissionOverrides { get; }
    DbSet<FeatureAccessGrant> FeatureAccessGrants { get; }
    DbSet<AuditLog> AuditLogs { get; }
    DbSet<GdprConsentRecord> GdprConsentRecords { get; }

    // SharedPlatform (Task 3 â€” Task 5 adds the rest)
    DbSet<SubscriptionPlan> SubscriptionPlans { get; }
    DbSet<TenantSubscription> TenantSubscriptions { get; }

    // OrgStructure stub (Dev 2 extends)
    DbSet<LegalEntity> LegalEntities { get; }
}
```

- [ ] **Step 2: Add new DbSets and query filters to ApplicationDbContext**

Replace only the relevant sections in `src/ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs`. The full updated file:

```csharp
// src/ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs
using Microsoft.EntityFrameworkCore;
using ONEVO.Application.Common.Interfaces;
using ONEVO.Domain.Common;
using ONEVO.Domain.Features.Auth.Entities;
using ONEVO.Domain.Features.InfrastructureModule.Entities;
using ONEVO.Domain.Features.OrgStructure.Entities;
using ONEVO.Domain.Features.SharedPlatform.Entities;

namespace ONEVO.Infrastructure.Persistence;

public class ApplicationDbContext : DbContext, IApplicationDbContext, IUnitOfWork
{
    private readonly ICurrentUserService? _currentUserService;

    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options,
        ICurrentUserService? currentUserService)
        : base(options)
    {
        _currentUserService = currentUserService;
    }

    public DbSet<Country> Countries => Set<Country>();
    public DbSet<Tenant> Tenants => Set<Tenant>();
    public DbSet<User> Users => Set<User>();
    public DbSet<FileRecord> FileRecords => Set<FileRecord>();

    public DbSet<Role> Roles => Set<Role>();
    public DbSet<UserRole> UserRoles => Set<UserRole>();
    public DbSet<Permission> Permissions => Set<Permission>();
    public DbSet<RolePermission> RolePermissions => Set<RolePermission>();
    public DbSet<RefreshToken> RefreshTokens => Set<RefreshToken>();
    public DbSet<Session> Sessions => Set<Session>();
    public DbSet<UserMfa> UserMfas => Set<UserMfa>();
    public DbSet<MfaRecoveryCode> MfaRecoveryCodes => Set<MfaRecoveryCode>();
    public DbSet<UserPermissionOverride> UserPermissionOverrides => Set<UserPermissionOverride>();
    public DbSet<FeatureAccessGrant> FeatureAccessGrants => Set<FeatureAccessGrant>();
    public DbSet<AuditLog> AuditLogs => Set<AuditLog>();
    public DbSet<GdprConsentRecord> GdprConsentRecords => Set<GdprConsentRecord>();

    // SharedPlatform (minimal â€” Task 5 adds the rest)
    public DbSet<SubscriptionPlan> SubscriptionPlans => Set<SubscriptionPlan>();
    public DbSet<TenantSubscription> TenantSubscriptions => Set<TenantSubscription>();

    // OrgStructure stub (Dev 2 extends)
    public DbSet<LegalEntity> LegalEntities => Set<LegalEntity>();

    private Guid? CurrentTenantId => _currentUserService?.TenantId;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(ApplicationDbContext).Assembly);

        // â”€â”€ Existing tenant-scoped query filters â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        modelBuilder.Entity<User>().HasQueryFilter(
            u => !u.IsDeleted && (CurrentTenantId == null || u.TenantId == CurrentTenantId.GetValueOrDefault()));
        modelBuilder.Entity<FileRecord>().HasQueryFilter(
            f => !f.IsDeleted && (CurrentTenantId == null || f.TenantId == CurrentTenantId.GetValueOrDefault()));
        modelBuilder.Entity<Role>().HasQueryFilter(
            r => !r.IsDeleted && (CurrentTenantId == null || r.TenantId == CurrentTenantId.GetValueOrDefault()));
        modelBuilder.Entity<UserPermissionOverride>().HasQueryFilter(
            o => !o.IsDeleted && (CurrentTenantId == null || o.TenantId == CurrentTenantId.GetValueOrDefault()));
        modelBuilder.Entity<FeatureAccessGrant>().HasQueryFilter(
            g => !g.IsDeleted && (CurrentTenantId == null || g.TenantId == CurrentTenantId.GetValueOrDefault()));
        modelBuilder.Entity<GdprConsentRecord>().HasQueryFilter(
            g => !g.IsDeleted && (CurrentTenantId == null || g.TenantId == CurrentTenantId.GetValueOrDefault()));
        modelBuilder.Entity<Session>().HasQueryFilter(
            s => CurrentTenantId == null || s.TenantId == CurrentTenantId.GetValueOrDefault());
        modelBuilder.Entity<UserMfa>().HasQueryFilter(
            m => CurrentTenantId == null || m.TenantId == CurrentTenantId.GetValueOrDefault());

        // â”€â”€ New Task 3 query filters â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        // TenantSubscription: tenant-scoped, no soft-delete
        modelBuilder.Entity<TenantSubscription>().HasQueryFilter(
            ts => CurrentTenantId == null || ts.TenantId == CurrentTenantId.GetValueOrDefault());
        // LegalEntity: tenant-scoped, soft-delete
        modelBuilder.Entity<LegalEntity>().HasQueryFilter(
            le => !le.IsDeleted && (CurrentTenantId == null || le.TenantId == CurrentTenantId.GetValueOrDefault()));

        base.OnModelCreating(modelBuilder);
    }
}
```

- [ ] **Step 3: Create SubscriptionPlanConfiguration**

```csharp
// src/ONEVO.Infrastructure/Persistence/Configurations/SharedPlatform/SubscriptionPlanConfiguration.cs
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using ONEVO.Domain.Features.SharedPlatform.Entities;

namespace ONEVO.Infrastructure.Persistence.Configurations.SharedPlatform;

public class SubscriptionPlanConfiguration : IEntityTypeConfiguration<SubscriptionPlan>
{
    public void Configure(EntityTypeBuilder<SubscriptionPlan> builder)
    {
        builder.ToTable("subscription_plans");
        builder.HasKey(x => x.Id);
        builder.Property(x => x.Id).HasColumnName("id");
        builder.Property(x => x.Name).HasColumnName("name").HasMaxLength(100).IsRequired();
        builder.Property(x => x.Code).HasColumnName("code").HasMaxLength(20).IsRequired();
        builder.Property(x => x.IsActive).HasColumnName("is_active");
        builder.Property(x => x.CreatedAt).HasColumnName("created_at");
        builder.Property(x => x.UpdatedAt).HasColumnName("updated_at");
        builder.Property(x => x.IsDeleted).HasColumnName("is_deleted");

        builder.Property(x => x.AllowedModules)
            .HasColumnName("allowed_modules")
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, (JsonSerializerOptions?)null),
                v => JsonSerializer.Deserialize<string[]>(v, (JsonSerializerOptions?)null)
                     ?? Array.Empty<string>());

        builder.HasIndex(x => x.Code).IsUnique();
    }
}
```

- [ ] **Step 4: Create TenantSubscriptionConfiguration**

```csharp
// src/ONEVO.Infrastructure/Persistence/Configurations/SharedPlatform/TenantSubscriptionConfiguration.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using ONEVO.Domain.Features.SharedPlatform.Entities;

namespace ONEVO.Infrastructure.Persistence.Configurations.SharedPlatform;

public class TenantSubscriptionConfiguration : IEntityTypeConfiguration<TenantSubscription>
{
    public void Configure(EntityTypeBuilder<TenantSubscription> builder)
    {
        builder.ToTable("tenant_subscriptions");
        builder.HasKey(x => x.Id);
        builder.Property(x => x.Id).HasColumnName("id");
        builder.Property(x => x.TenantId).HasColumnName("tenant_id");
        builder.Property(x => x.PlanId).HasColumnName("plan_id");
        builder.Property(x => x.Status).HasColumnName("status").HasMaxLength(20);
        builder.Property(x => x.PeriodStart).HasColumnName("current_period_start");
        builder.Property(x => x.PeriodEnd).HasColumnName("current_period_end");
        builder.Property(x => x.CreatedById).HasColumnName("created_by_id");
        builder.Property(x => x.CreatedAt).HasColumnName("created_at");
        builder.Property(x => x.UpdatedAt).HasColumnName("updated_at");
        builder.Property(x => x.IsDeleted).HasColumnName("is_deleted");

        builder.HasOne(ts => ts.Plan)
            .WithMany()
            .HasForeignKey(ts => ts.PlanId)
            .OnDelete(DeleteBehavior.Restrict);
    }
}
```

- [ ] **Step 5: Create LegalEntityConfiguration**

```csharp
// src/ONEVO.Infrastructure/Persistence/Configurations/OrgStructure/LegalEntityConfiguration.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using ONEVO.Domain.Features.OrgStructure.Entities;

namespace ONEVO.Infrastructure.Persistence.Configurations.OrgStructure;

public class LegalEntityConfiguration : IEntityTypeConfiguration<LegalEntity>
{
    public void Configure(EntityTypeBuilder<LegalEntity> builder)
    {
        builder.ToTable("legal_entities");
        builder.HasKey(x => x.Id);
        builder.Property(x => x.Id).HasColumnName("id");
        builder.Property(x => x.TenantId).HasColumnName("tenant_id");
        builder.Property(x => x.Name).HasColumnName("name").HasMaxLength(200).IsRequired();
        builder.Property(x => x.CountryCode).HasColumnName("country_code").HasMaxLength(3);
        builder.Property(x => x.IsDefault).HasColumnName("is_default");
        builder.Property(x => x.CreatedById).HasColumnName("created_by_id");
        builder.Property(x => x.CreatedAt).HasColumnName("created_at");
        builder.Property(x => x.UpdatedAt).HasColumnName("updated_at");
        builder.Property(x => x.IsDeleted).HasColumnName("is_deleted");
    }
}
```

- [ ] **Step 6: Add industry_profile to TenantConfiguration**

Open `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/TenantConfiguration.cs` and add this property mapping inside `Configure()`, after the existing property mappings (before or after `IsActive` â€” anywhere in the method body):

```csharp
builder.Property(x => x.IndustryProfile)
    .HasColumnName("industry_profile")
    .HasMaxLength(30)
    .HasDefaultValue("office_it");
```

- [ ] **Step 7: Verify full solution builds**

```
dotnet build ONEVO.sln
```

Expected: `Build succeeded.` with 0 errors.

- [ ] **Step 8: Run all existing tests still pass**

```
dotnet test ONEVO.sln
```

Expected: All previously passing tests still pass.

- [ ] **Step 9: Commit**

```
git add src/ONEVO.Infrastructure/Persistence/ src/ONEVO.Application/Common/Interfaces/IApplicationDbContext.cs
git commit -m "feat(entitlement): add EF configurations for SubscriptionPlan, TenantSubscription, LegalEntity; add industry_profile to Tenant"
```

---

## Task 4: Generate Migration + Seed Default Plans

**Files:**
- Created by EF tooling: `src/ONEVO.Infrastructure/Persistence/Migrations/[timestamp]_EntitlementFoundation.cs`

- [ ] **Step 1: Generate the migration**

Run from `C:\OneVo-HR\OneVo-backend`:

```
dotnet ef migrations add EntitlementFoundation `
  --project src/ONEVO.Infrastructure `
  --startup-project src/ONEVO.Api `
  --output-dir Persistence/Migrations
```

Expected: `Build succeeded. Done. To undo this action, use 'ef migrations remove'.`

- [ ] **Step 2: Add seed data for default subscription plans**

Open the newly generated migration file (`20260505xxxxxx_EntitlementFoundation.cs`) and append these `InsertData` calls at the **end** of the `Up()` method, before the closing `}`:

```csharp
// Seed the three default subscription plans.
// IDs are fixed so cross-environment restores stay consistent.
migrationBuilder.InsertData(
    table: "subscription_plans",
    columns: ["id", "name", "code", "allowed_modules", "is_active", "is_deleted", "created_at"],
    values: new object[,]
    {
        {
            Guid.Parse("a0000000-0000-0000-0000-000000000001"),
            "Starter", "starter",
            "[\"core_hr\",\"leave\",\"workforce_presence\",\"notifications\",\"data_import\",\"skills\"]",
            true, false,
            new DateTimeOffset(2026, 5, 5, 0, 0, 0, TimeSpan.Zero)
        },
        {
            Guid.Parse("a0000000-0000-0000-0000-000000000002"),
            "Professional", "professional",
            "[\"core_hr\",\"leave\",\"calendar\",\"workforce_presence\",\"activity_monitoring\"," +
            "\"work_sync\",\"notifications\",\"data_import\",\"skills\",\"ide_extension\"]",
            true, false,
            new DateTimeOffset(2026, 5, 5, 0, 0, 0, TimeSpan.Zero)
        },
        {
            Guid.Parse("a0000000-0000-0000-0000-000000000003"),
            "Enterprise", "enterprise",
            "[\"core_hr\",\"leave\",\"calendar\",\"workforce_presence\",\"activity_monitoring\"," +
            "\"exception_engine\",\"identity_verification\",\"work_sync\",\"notifications\"," +
            "\"data_import\",\"skills\",\"configuration\",\"agent_gateway\",\"ide_extension\"]",
            true, false,
            new DateTimeOffset(2026, 5, 5, 0, 0, 0, TimeSpan.Zero)
        }
    });
```

Also add the corresponding `DeleteData` call in `Down()`:

```csharp
migrationBuilder.DeleteData(
    table: "subscription_plans",
    keyColumn: "id",
    keyValues: new object[]
    {
        Guid.Parse("a0000000-0000-0000-0000-000000000001"),
        Guid.Parse("a0000000-0000-0000-0000-000000000002"),
        Guid.Parse("a0000000-0000-0000-0000-000000000003")
    });
```

- [ ] **Step 3: Apply migration to local dev database**

```
dotnet ef database update `
  --project src/ONEVO.Infrastructure `
  --startup-project src/ONEVO.Api
```

Expected: `Applying migration '20260505xxxxxx_EntitlementFoundation'. Done.`

- [ ] **Step 4: Commit**

```
git add src/ONEVO.Infrastructure/Persistence/Migrations/
git commit -m "feat(entitlement): add EntitlementFoundation migration with subscription plan seed data"
```

---

## Task 5: ModuleEntitlementService (Read Path) + Unit Tests

**Files:**
- Create: `src/ONEVO.Application/Features/InfrastructureModule/EntitlementErrors.cs`
- Create: `src/ONEVO.Application/Features/InfrastructureModule/Interfaces/IModuleEntitlementService.cs`
- Create: `src/ONEVO.Infrastructure/Services/ModuleEntitlementService.cs`
- Modify: `src/ONEVO.Infrastructure/DependencyInjection.cs`
- Test: `tests/ONEVO.Tests.Unit/Entitlement/ModuleEntitlementServiceTests.cs`

- [ ] **Step 1: Write failing unit tests**

```csharp
// tests/ONEVO.Tests.Unit/Entitlement/ModuleEntitlementServiceTests.cs
using Microsoft.EntityFrameworkCore;
using ONEVO.Domain.Common;
using ONEVO.Domain.Features.Auth.Entities;
using ONEVO.Domain.Features.SharedPlatform.Entities;
using ONEVO.Domain.Modules;
using ONEVO.Infrastructure.Persistence;
using ONEVO.Infrastructure.Services;

namespace ONEVO.Tests.Unit.Entitlement;

public class ModuleEntitlementServiceTests
{
    private static ApplicationDbContext CreateDb(string name)
    {
        var opts = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(name)
            .Options;
        return new ApplicationDbContext(opts, null);
    }

    private static void SetId<T>(T entity, Guid id) where T : class
        => typeof(T).GetProperty("Id")!.SetValue(entity, id);

    [Fact]
    public async Task GetActiveModules_ReturnsPlanModules_WhenNoGrants()
    {
        await using var db = CreateDb(nameof(GetActiveModules_ReturnsPlanModules_WhenNoGrants));
        var tenantId = Guid.NewGuid();
        var planId = Guid.NewGuid();

        var plan = SubscriptionPlan.Create("Starter", "starter",
            [ModuleKey.CoreHr, ModuleKey.Leave, ModuleKey.WorkSync]);
        SetId(plan, planId);
        db.SubscriptionPlans.Add(plan);
        db.TenantSubscriptions.Add(TenantSubscription.Create(tenantId, planId, Guid.Empty));
        await db.SaveChangesAsync();

        var svc = new ModuleEntitlementService(db);
        var result = await svc.GetActiveModulesAsync(tenantId, CancellationToken.None);

        Assert.Equal(3, result.Count);
        Assert.Contains(ModuleKey.CoreHr, result);
        Assert.Contains(ModuleKey.Leave, result);
        Assert.Contains(ModuleKey.WorkSync, result);
    }

    [Fact]
    public async Task GetActiveModules_ExcludesModuleDisabledByTenantGrant()
    {
        await using var db = CreateDb(nameof(GetActiveModules_ExcludesModuleDisabledByTenantGrant));
        var tenantId = Guid.NewGuid();
        var planId = Guid.NewGuid();

        var plan = SubscriptionPlan.Create("Starter", "starter",
            [ModuleKey.CoreHr, ModuleKey.Leave]);
        SetId(plan, planId);
        db.SubscriptionPlans.Add(plan);
        db.TenantSubscriptions.Add(TenantSubscription.Create(tenantId, planId, Guid.Empty));
        db.FeatureAccessGrants.Add(
            FeatureAccessGrant.Create("tenant", tenantId, ModuleKey.Leave, false, tenantId, Guid.Empty));
        await db.SaveChangesAsync();

        var svc = new ModuleEntitlementService(db);
        var result = await svc.GetActiveModulesAsync(tenantId, CancellationToken.None);

        Assert.Single(result);
        Assert.Contains(ModuleKey.CoreHr, result);
        Assert.DoesNotContain(ModuleKey.Leave, result);
    }

    [Fact]
    public async Task GetActiveModules_AddsModuleEnabledByTenantGrant_BeyondPlan()
    {
        await using var db = CreateDb(nameof(GetActiveModules_AddsModuleEnabledByTenantGrant_BeyondPlan));
        var tenantId = Guid.NewGuid();
        var planId = Guid.NewGuid();

        var plan = SubscriptionPlan.Create("Starter", "starter", [ModuleKey.CoreHr]);
        SetId(plan, planId);
        db.SubscriptionPlans.Add(plan);
        db.TenantSubscriptions.Add(TenantSubscription.Create(tenantId, planId, Guid.Empty));
        db.FeatureAccessGrants.Add(
            FeatureAccessGrant.Create("tenant", tenantId, ModuleKey.WorkSync, true, tenantId, Guid.Empty));
        await db.SaveChangesAsync();

        var svc = new ModuleEntitlementService(db);
        var result = await svc.GetActiveModulesAsync(tenantId, CancellationToken.None);

        Assert.Equal(2, result.Count);
        Assert.Contains(ModuleKey.CoreHr, result);
        Assert.Contains(ModuleKey.WorkSync, result);
    }

    [Fact]
    public async Task GetActiveModules_IgnoresUnknownModuleKeysFromPlan()
    {
        await using var db = CreateDb(nameof(GetActiveModules_IgnoresUnknownModuleKeysFromPlan));
        var tenantId = Guid.NewGuid();
        var planId = Guid.NewGuid();

        var plan = SubscriptionPlan.Create("Custom", "custom",
            [ModuleKey.CoreHr, "legacy_module_xyz"]);
        SetId(plan, planId);
        db.SubscriptionPlans.Add(plan);
        db.TenantSubscriptions.Add(TenantSubscription.Create(tenantId, planId, Guid.Empty));
        await db.SaveChangesAsync();

        var svc = new ModuleEntitlementService(db);
        var result = await svc.GetActiveModulesAsync(tenantId, CancellationToken.None);

        Assert.Single(result);
        Assert.Contains(ModuleKey.CoreHr, result);
        Assert.DoesNotContain("legacy_module_xyz", result);
    }
}
```

- [ ] **Step 2: Run â€” expect compile failure (interface + service don't exist)**

```
dotnet test tests/ONEVO.Tests.Unit --filter ModuleEntitlement
```

Expected: Build error `The type or namespace name 'ModuleEntitlementService' could not be found`.

- [ ] **Step 3: Create EntitlementErrors**

```csharp
// src/ONEVO.Application/Features/InfrastructureModule/EntitlementErrors.cs
using ONEVO.Application.Common.Models;

namespace ONEVO.Application.Features.InfrastructureModule;

public static class EntitlementErrors
{
    public static readonly Error SlugTaken =
        new("Entitlement.SlugTaken", "A tenant with this slug already exists.");

    public static readonly Error PlanNotFound =
        new("Entitlement.PlanNotFound", "The specified subscription plan was not found or is inactive.");

    public static readonly Error TenantNotFound =
        new("Entitlement.TenantNotFound", "Tenant not found.");
}
```

- [ ] **Step 4: Create IModuleEntitlementService**

```csharp
// src/ONEVO.Application/Features/InfrastructureModule/Interfaces/IModuleEntitlementService.cs
namespace ONEVO.Application.Features.InfrastructureModule.Interfaces;

public interface IModuleEntitlementService
{
    /// <summary>Resolves active modules: plan allowedModules Â± tenant-level FeatureAccessGrant overrides.</summary>
    Task<List<string>> GetActiveModulesAsync(Guid tenantId, CancellationToken ct);

    /// <summary>
    /// Replaces tenant module assignments (used by DevPlatform).
    /// Writes FeatureAccessGrant records (GranteeType="tenant") and saves.
    /// </summary>
    Task SetTenantModulesAsync(
        Guid tenantId, IEnumerable<string> moduleKeys,
        Guid setByUserId, CancellationToken ct);
}
```

- [ ] **Step 5: Create ModuleEntitlementService (read path only â€” write path in Task 8)**

```csharp
// src/ONEVO.Infrastructure/Services/ModuleEntitlementService.cs
using Microsoft.EntityFrameworkCore;
using ONEVO.Application.Common.Interfaces;
using ONEVO.Application.Features.InfrastructureModule.Interfaces;
using ONEVO.Domain.Features.Auth.Entities;
using ONEVO.Domain.Modules;

namespace ONEVO.Infrastructure.Services;

public class ModuleEntitlementService : IModuleEntitlementService
{
    private readonly IApplicationDbContext _db;

    public ModuleEntitlementService(IApplicationDbContext db) => _db = db;

    public async Task<List<string>> GetActiveModulesAsync(Guid tenantId, CancellationToken ct)
    {
        // 1. Get plan's allowed modules
        var sub = await _db.TenantSubscriptions
            .Include(ts => ts.Plan)
            .Where(ts => ts.TenantId == tenantId && ts.Status != "cancelled")
            .OrderByDescending(ts => ts.CreatedAt)
            .FirstOrDefaultAsync(ct);

        var active = new HashSet<string>(
            (sub?.Plan.AllowedModules ?? []).Where(ModuleCatalog.IsKnown),
            StringComparer.Ordinal);

        // 2. Apply tenant-level FeatureAccessGrant overrides
        var grants = await _db.FeatureAccessGrants
            .IgnoreQueryFilters()
            .Where(g => !g.IsDeleted && g.GranteeType == "tenant" && g.GranteeId == tenantId)
            .ToListAsync(ct);

        foreach (var g in grants)
        {
            if (g.IsEnabled && ModuleCatalog.IsKnown(g.Module)) active.Add(g.Module);
            else active.Remove(g.Module);
        }

        return [.. active];
    }

    public Task SetTenantModulesAsync(
        Guid tenantId, IEnumerable<string> moduleKeys,
        Guid setByUserId, CancellationToken ct)
        => throw new NotImplementedException("Implemented in Task 8.");
}
```

- [ ] **Step 6: Register IModuleEntitlementService in DI**

Open `src/ONEVO.Infrastructure/DependencyInjection.cs` and add this line in the `AddInfrastructure` method, after the `// Auth services` block:

```csharp
// Entitlement services
services.AddScoped<IModuleEntitlementService, ModuleEntitlementService>();
```

Also add the using: `using ONEVO.Application.Features.InfrastructureModule.Interfaces;`

- [ ] **Step 7: Run â€” expect all 4 unit tests pass**

```
dotnet test tests/ONEVO.Tests.Unit --filter ModuleEntitlement
```

Expected: `4 passed, 0 failed`.

- [ ] **Step 8: Commit**

```
git add src/ONEVO.Application/Features/InfrastructureModule/ `
        src/ONEVO.Infrastructure/Services/ModuleEntitlementService.cs `
        src/ONEVO.Infrastructure/DependencyInjection.cs `
        tests/ONEVO.Tests.Unit/Entitlement/ModuleEntitlementServiceTests.cs
git commit -m "feat(entitlement): add IModuleEntitlementService with active-module resolution"
```

---

## Task 6: Tenant Provisioning + POST /api/v1/tenants

**Files:**
- Create: `src/ONEVO.Application/Features/InfrastructureModule/Interfaces/ITenantProvisioningService.cs`
- Create: `src/ONEVO.Application/Features/InfrastructureModule/Commands/ProvisionTenant/ProvisionTenantCommand.cs`
- Create: `src/ONEVO.Application/Features/InfrastructureModule/Commands/ProvisionTenant/ProvisionTenantCommandHandler.cs`
- Create: `src/ONEVO.Application/Features/InfrastructureModule/Commands/ProvisionTenant/ProvisionTenantCommandValidator.cs`
- Create: `src/ONEVO.Infrastructure/Services/TenantProvisioningService.cs`
- Create: `src/ONEVO.Api/Controllers/InfrastructureModule/InfrastructureModuleController.cs`
- Modify: `src/ONEVO.Infrastructure/DependencyInjection.cs`
- Test: `tests/ONEVO.Tests.Integration/Entitlement/EntitlementTestFactory.cs`
- Test: `tests/ONEVO.Tests.Integration/Entitlement/TenantProvisioningTests.cs`

- [ ] **Step 1: Create the integration test factory**

```csharp
// tests/ONEVO.Tests.Integration/Entitlement/EntitlementTestFactory.cs
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.Extensions.DependencyInjection;
using ONEVO.Application.Features.Auth.Interfaces;
using ONEVO.Domain.Features.SharedPlatform.Entities;
using ONEVO.Domain.Modules;
using ONEVO.Infrastructure.Persistence;
using ONEVO.Tests.Integration.Auth;   // reuses FakePasswordService

namespace ONEVO.Tests.Integration.Entitlement;

public class EntitlementTestFactory : WebApplicationFactory<Program>
{
    private readonly string _dbName = $"EntitlementTest_{Guid.NewGuid()}";

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Development");
        builder.ConfigureServices(services =>
        {
            var toRemove = services
                .Where(d => d.ServiceType == typeof(DbContextOptions<ApplicationDbContext>)
                         || d.ServiceType == typeof(IDbContextOptionsConfiguration<ApplicationDbContext>))
                .ToList();
            foreach (var d in toRemove) services.Remove(d);

            services.AddDbContext<ApplicationDbContext>((_, opt) =>
                opt.UseInMemoryDatabase(_dbName));

            var pwDescriptor = services.SingleOrDefault(d => d.ServiceType == typeof(IPasswordService));
            if (pwDescriptor is not null) services.Remove(pwDescriptor);
            services.AddScoped<IPasswordService, FakePasswordService>();
        });
    }

    public async Task SeedDefaultPlansAsync()
    {
        using var scope = Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

        if (await db.SubscriptionPlans.AnyAsync()) return;

        var starterModules = new[]
        {
            ModuleKey.CoreHr, ModuleKey.Leave, ModuleKey.WorkforcePresence,
            ModuleKey.Notifications, ModuleKey.DataImport, ModuleKey.Skills
        };
        db.SubscriptionPlans.Add(SubscriptionPlan.Create("Starter", "starter", starterModules));
        db.SubscriptionPlans.Add(SubscriptionPlan.Create("Professional", "professional",
            [.. starterModules, ModuleKey.Calendar, ModuleKey.WorkSync,
             ModuleKey.ActivityMonitoring, ModuleKey.IdeExtension]));
        db.SubscriptionPlans.Add(SubscriptionPlan.Create("Enterprise", "enterprise",
            [.. ModuleCatalog.All]));

        await db.SaveChangesAsync();
    }
}
```

- [ ] **Step 2: Write failing provisioning integration tests**

```csharp
// tests/ONEVO.Tests.Integration/Entitlement/TenantProvisioningTests.cs
using System.Net;
using System.Net.Http.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using ONEVO.Infrastructure.Persistence;

namespace ONEVO.Tests.Integration.Entitlement;

public class TenantProvisioningTests : IAsyncLifetime
{
    private readonly EntitlementTestFactory _factory = new();
    private HttpClient _client = null!;

    public async Task InitializeAsync()
    {
        _client = _factory.CreateClient();
        await _factory.SeedDefaultPlansAsync();
    }

    public Task DisposeAsync() { _factory.Dispose(); return Task.CompletedTask; }

    [Fact]
    public async Task ProvisionTenant_ValidRequest_Creates_Tenant_LegalEntity_User_Subscription()
    {
        var response = await _client.PostAsJsonAsync("/api/v1/tenants", new
        {
            companyName = "Acme Corp",
            slug = "acme-corp",
            adminEmail = "admin@acme.com",
            adminFirstName = "John",
            adminLastName = "Doe",
            adminPassword = "SecurePass123!",
            planCode = "starter",
            industryProfile = "office_it"
        });

        var body = await response.Content.ReadAsStringAsync();
        Assert.True(response.StatusCode == HttpStatusCode.Created,
            $"Expected 201 but got {response.StatusCode}. Body: {body}");

        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

        var tenant = await db.Tenants.IgnoreQueryFilters()
            .FirstOrDefaultAsync(t => t.Slug == "acme-corp");
        Assert.NotNull(tenant);
        Assert.Equal("active", tenant!.Status);
        Assert.True(tenant.IsActive);
        Assert.Equal("office_it", tenant.IndustryProfile);

        var legal = await db.LegalEntities.IgnoreQueryFilters()
            .FirstOrDefaultAsync(le => le.TenantId == tenant.Id);
        Assert.NotNull(legal);
        Assert.True(legal!.IsDefault);

        var user = await db.Users.IgnoreQueryFilters()
            .FirstOrDefaultAsync(u => u.Email == "admin@acme.com");
        Assert.NotNull(user);
        Assert.Equal(tenant.Id, user!.TenantId);

        var sub = await db.TenantSubscriptions.IgnoreQueryFilters()
            .FirstOrDefaultAsync(s => s.TenantId == tenant.Id);
        Assert.NotNull(sub);
        Assert.Equal("trialing", sub!.Status);
    }

    [Fact]
    public async Task ProvisionTenant_DuplicateSlug_Returns422()
    {
        await _client.PostAsJsonAsync("/api/v1/tenants", new
        {
            companyName = "First", slug = "dup-slug",
            adminEmail = "a@a.com", adminFirstName = "A", adminLastName = "B",
            adminPassword = "SecurePass123!", planCode = "starter", industryProfile = "office_it"
        });

        var response = await _client.PostAsJsonAsync("/api/v1/tenants", new
        {
            companyName = "Second", slug = "dup-slug",
            adminEmail = "b@b.com", adminFirstName = "C", adminLastName = "D",
            adminPassword = "SecurePass123!", planCode = "starter", industryProfile = "office_it"
        });

        Assert.Equal(HttpStatusCode.UnprocessableEntity, response.StatusCode);
    }

    [Fact]
    public async Task ProvisionTenant_InvalidPlanCode_Returns422()
    {
        var response = await _client.PostAsJsonAsync("/api/v1/tenants", new
        {
            companyName = "Test", slug = "test-bad-plan",
            adminEmail = "admin@test.com", adminFirstName = "A", adminLastName = "B",
            adminPassword = "SecurePass123!", planCode = "nonexistent", industryProfile = "office_it"
        });

        Assert.Equal(HttpStatusCode.UnprocessableEntity, response.StatusCode);
    }

    [Fact]
    public async Task ProvisionTenant_InvalidSlugFormat_Returns422()
    {
        var response = await _client.PostAsJsonAsync("/api/v1/tenants", new
        {
            companyName = "Test", slug = "HAS SPACES",
            adminEmail = "admin@test.com", adminFirstName = "A", adminLastName = "B",
            adminPassword = "SecurePass123!", planCode = "starter", industryProfile = "office_it"
        });

        Assert.Equal(HttpStatusCode.UnprocessableEntity, response.StatusCode);
    }
}
```

- [ ] **Step 3: Run â€” expect compile failure (controller + commands don't exist)**

```
dotnet test tests/ONEVO.Tests.Integration --filter Entitlement
```

Expected: Build errors.

- [ ] **Step 4: Create ITenantProvisioningService**

```csharp
// src/ONEVO.Application/Features/InfrastructureModule/Interfaces/ITenantProvisioningService.cs
using ONEVO.Application.Common.Models;

namespace ONEVO.Application.Features.InfrastructureModule.Interfaces;

public interface ITenantProvisioningService
{
    Task<Result<ProvisionTenantResult>> ProvisionAsync(
        ProvisionTenantInput input, CancellationToken ct);
}

public record ProvisionTenantInput(
    string CompanyName, string Slug,
    string AdminEmail, string AdminFirstName, string AdminLastName,
    string AdminPassword, Guid PlanId, string IndustryProfile);

public record ProvisionTenantResult(Guid TenantId, Guid AdminUserId);
```

- [ ] **Step 5: Create ProvisionTenantCommand**

```csharp
// src/ONEVO.Application/Features/InfrastructureModule/Commands/ProvisionTenant/ProvisionTenantCommand.cs
using MediatR;
using ONEVO.Application.Common.Models;
using ONEVO.Application.Features.InfrastructureModule.Interfaces;

namespace ONEVO.Application.Features.InfrastructureModule.Commands.ProvisionTenant;

public record ProvisionTenantCommand(
    string CompanyName,
    string Slug,
    string AdminEmail,
    string AdminFirstName,
    string AdminLastName,
    string AdminPassword,
    string PlanCode,
    string IndustryProfile
) : IRequest<Result<ProvisionTenantResult>>;
```

- [ ] **Step 6: Create ProvisionTenantCommandValidator**

```csharp
// src/ONEVO.Application/Features/InfrastructureModule/Commands/ProvisionTenant/ProvisionTenantCommandValidator.cs
using FluentValidation;

namespace ONEVO.Application.Features.InfrastructureModule.Commands.ProvisionTenant;

public class ProvisionTenantCommandValidator : AbstractValidator<ProvisionTenantCommand>
{
    private static readonly string[] ValidProfiles =
        ["office_it", "manufacturing", "retail", "healthcare", "custom"];

    public ProvisionTenantCommandValidator()
    {
        RuleFor(x => x.CompanyName).NotEmpty().MaximumLength(200);

        RuleFor(x => x.Slug)
            .NotEmpty()
            .MaximumLength(100)
            .Matches("^[a-z0-9-]+$")
            .WithMessage("Slug must contain only lowercase letters, numbers, and hyphens.");

        RuleFor(x => x.AdminEmail).NotEmpty().EmailAddress().MaximumLength(255);

        RuleFor(x => x.AdminFirstName).NotEmpty().MaximumLength(100);
        RuleFor(x => x.AdminLastName).NotEmpty().MaximumLength(100);

        RuleFor(x => x.AdminPassword)
            .NotEmpty()
            .MinimumLength(12)
            .WithMessage("Admin password must be at least 12 characters.");

        RuleFor(x => x.PlanCode).NotEmpty();

        RuleFor(x => x.IndustryProfile)
            .Must(p => ValidProfiles.Contains(p))
            .WithMessage($"IndustryProfile must be one of: {string.Join(", ", ValidProfiles)}.");
    }
}
```

- [ ] **Step 7: Create ProvisionTenantCommandHandler**

```csharp
// src/ONEVO.Application/Features/InfrastructureModule/Commands/ProvisionTenant/ProvisionTenantCommandHandler.cs
using MediatR;
using Microsoft.EntityFrameworkCore;
using ONEVO.Application.Common.Interfaces;
using ONEVO.Application.Common.Models;
using ONEVO.Application.Features.InfrastructureModule.Interfaces;

namespace ONEVO.Application.Features.InfrastructureModule.Commands.ProvisionTenant;

public class ProvisionTenantCommandHandler
    : IRequestHandler<ProvisionTenantCommand, Result<ProvisionTenantResult>>
{
    private readonly IApplicationDbContext _db;
    private readonly ITenantProvisioningService _provisioning;

    public ProvisionTenantCommandHandler(
        IApplicationDbContext db, ITenantProvisioningService provisioning)
    {
        _db = db;
        _provisioning = provisioning;
    }

    public async Task<Result<ProvisionTenantResult>> Handle(
        ProvisionTenantCommand request, CancellationToken ct)
    {
        var slugNorm = request.Slug.ToLowerInvariant();

        var slugExists = await _db.Tenants
            .IgnoreQueryFilters()
            .AnyAsync(t => t.Slug == slugNorm, ct);

        if (slugExists)
            return Result<ProvisionTenantResult>.Failure(EntitlementErrors.SlugTaken);

        var plan = await _db.SubscriptionPlans
            .FirstOrDefaultAsync(p => p.Code == request.PlanCode && p.IsActive, ct);

        if (plan is null)
            return Result<ProvisionTenantResult>.Failure(EntitlementErrors.PlanNotFound);

        return await _provisioning.ProvisionAsync(
            new ProvisionTenantInput(
                request.CompanyName, slugNorm,
                request.AdminEmail, request.AdminFirstName, request.AdminLastName,
                request.AdminPassword, plan.Id, request.IndustryProfile),
            ct);
    }
}
```

- [ ] **Step 8: Create TenantProvisioningService**

```csharp
// src/ONEVO.Infrastructure/Services/TenantProvisioningService.cs
using ONEVO.Application.Common.Interfaces;
using ONEVO.Application.Common.Models;
using ONEVO.Application.Features.Auth.Interfaces;
using ONEVO.Application.Features.InfrastructureModule.Interfaces;
using ONEVO.Domain.Features.InfrastructureModule.Entities;
using ONEVO.Domain.Features.OrgStructure.Entities;
using ONEVO.Domain.Features.SharedPlatform.Entities;

namespace ONEVO.Infrastructure.Services;

public class TenantProvisioningService : ITenantProvisioningService
{
    private readonly IApplicationDbContext _db;
    private readonly IUnitOfWork _uow;
    private readonly IPasswordService _pwd;

    public TenantProvisioningService(
        IApplicationDbContext db, IUnitOfWork uow, IPasswordService pwd)
    {
        _db = db;
        _uow = uow;
        _pwd = pwd;
    }

    public async Task<Result<ProvisionTenantResult>> ProvisionAsync(
        ProvisionTenantInput input, CancellationToken ct)
    {
        var tenant = Tenant.Create(input.CompanyName, input.Slug, input.IndustryProfile);
        _db.Tenants.Add(tenant);

        var legal = LegalEntity.Create(input.CompanyName, tenant.Id, Guid.Empty);
        _db.LegalEntities.Add(legal);

        var admin = User.Create(
            input.AdminEmail, _pwd.Hash(input.AdminPassword),
            input.AdminFirstName, input.AdminLastName,
            tenant.Id, Guid.Empty);
        _db.Users.Add(admin);

        var sub = TenantSubscription.Create(tenant.Id, input.PlanId, admin.Id);
        _db.TenantSubscriptions.Add(sub);

        // Finalise â€” raises TenantProvisioned domain event (dispatched after save)
        tenant.MarkProvisioned(input.PlanId);

        await _uow.SaveChangesAsync(ct);

        return Result<ProvisionTenantResult>.Success(
            new ProvisionTenantResult(tenant.Id, admin.Id));
    }
}
```

- [ ] **Step 9: Create InfrastructureModuleController**

```csharp
// src/ONEVO.Api/Controllers/InfrastructureModule/InfrastructureModuleController.cs
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ONEVO.Application.Features.InfrastructureModule.Commands.ProvisionTenant;
using ONEVO.Application.Features.InfrastructureModule.Interfaces;

namespace ONEVO.Api.Controllers.InfrastructureModule;

[ApiController]
[Route("api/v1")]
public class InfrastructureModuleController : ControllerBase
{
    private readonly ISender _sender;

    public InfrastructureModuleController(ISender sender) => _sender = sender;

    /// <summary>Public self-signup. Creates tenant, legal entity, admin user, and subscription.</summary>
    [HttpPost("tenants")]
    [AllowAnonymous]
    [ProducesResponseType(typeof(ProvisionTenantResult), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status422UnprocessableEntity)]
    public async Task<IActionResult> ProvisionTenant(
        [FromBody] ProvisionTenantRequest request, CancellationToken ct)
    {
        var result = await _sender.Send(
            new ProvisionTenantCommand(
                request.CompanyName, request.Slug,
                request.AdminEmail, request.AdminFirstName, request.AdminLastName,
                request.AdminPassword, request.PlanCode,
                request.IndustryProfile ?? "office_it"),
            ct);

        if (result.IsFailure)
            return UnprocessableEntity(new { result.Error.Code, result.Error.Message });

        return CreatedAtAction(nameof(ProvisionTenant), result.Value);
    }

    public record ProvisionTenantRequest(
        string CompanyName,
        string Slug,
        string AdminEmail,
        string AdminFirstName,
        string AdminLastName,
        string AdminPassword,
        string PlanCode,
        string? IndustryProfile);
}
```

- [ ] **Step 10: Register ITenantProvisioningService in DI**

In `src/ONEVO.Infrastructure/DependencyInjection.cs`, add inside `AddInfrastructure()` after the entitlement services line:

```csharp
services.AddScoped<ITenantProvisioningService, TenantProvisioningService>();
```

- [ ] **Step 11: Run â€” expect all 4 provisioning tests pass**

```
dotnet test tests/ONEVO.Tests.Integration --filter "Entitlement&ProvisionTenant"
```

Expected: `4 passed, 0 failed`.

- [ ] **Step 12: Run full test suite to catch regressions**

```
dotnet test ONEVO.sln
```

Expected: All tests pass.

- [ ] **Step 13: Commit**

```
git add src/ tests/ONEVO.Tests.Integration/Entitlement/
git commit -m "feat(entitlement): add TenantProvisioningService, ProvisionTenantCommand, and POST /api/v1/tenants"
```

---

## Task 7: Entitlement DTO + GET /api/v1/me/entitlements

**Files:**
- Create: `src/ONEVO.Application/Features/InfrastructureModule/DTOs/EntitlementDto.cs`
- Create: `src/ONEVO.Application/Features/InfrastructureModule/Queries/GetMyEntitlements/GetMyEntitlementsQuery.cs`
- Create: `src/ONEVO.Application/Features/InfrastructureModule/Queries/GetMyEntitlements/GetMyEntitlementsQueryHandler.cs`
- Create: `src/ONEVO.Api/Controllers/InfrastructureModule/EntitlementController.cs`
- Test: `tests/ONEVO.Tests.Integration/Entitlement/EntitlementEndpointTests.cs`

- [ ] **Step 1: Write failing integration tests**

```csharp
// tests/ONEVO.Tests.Integration/Entitlement/EntitlementEndpointTests.cs
using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;

namespace ONEVO.Tests.Integration.Entitlement;

public class EntitlementEndpointTests : IAsyncLifetime
{
    private readonly EntitlementTestFactory _factory = new();
    private HttpClient _client = null!;

    public async Task InitializeAsync()
    {
        _client = _factory.CreateClient();
        await _factory.SeedDefaultPlansAsync();
    }

    public Task DisposeAsync() { _factory.Dispose(); return Task.CompletedTask; }

    [Fact]
    public async Task GetEntitlements_Anonymous_Returns401()
    {
        var resp = await _client.GetAsync("/api/v1/me/entitlements");
        Assert.Equal(HttpStatusCode.Unauthorized, resp.StatusCode);
    }

    [Fact]
    public async Task GetEntitlements_AuthenticatedUser_ReturnsModulesAndPermissions()
    {
        // Provision a tenant
        await _client.PostAsJsonAsync("/api/v1/tenants", new
        {
            companyName = "Ent Test Corp", slug = "ent-test-corp",
            adminEmail = "admin@enttest.com", adminFirstName = "Jane", adminLastName = "Smith",
            adminPassword = "SecurePass123!", planCode = "starter", industryProfile = "office_it"
        });

        // Login
        var loginResp = await _client.PostAsJsonAsync("/api/v1/auth/login", new
        {
            tenantSlug = "ent-test-corp",
            email = "admin@enttest.com",
            password = "SecurePass123!"
        });
        Assert.Equal(HttpStatusCode.OK, loginResp.StatusCode);
        var login = await loginResp.Content.ReadFromJsonAsync<LoginResult>();
        _client.DefaultRequestHeaders.Authorization =
            // Browser web auth now uses HttpOnly cookie sessions; do not attach login.AccessToken.

        // Get entitlements
        var resp = await _client.GetAsync("/api/v1/me/entitlements");
        Assert.Equal(HttpStatusCode.OK, resp.StatusCode);

        var dto = await resp.Content.ReadFromJsonAsync<EntitlementResult>();
        Assert.NotNull(dto);
        Assert.NotEmpty(dto!.Modules);
        Assert.Contains("core_hr", dto.Modules);
        Assert.Contains("leave", dto.Modules);
        Assert.NotEmpty(dto.Permissions);
        Assert.NotNull(dto.Plan);
        Assert.Equal("starter", dto.Plan!.Code);
        Assert.NotEmpty(dto.Plan.AllowedModules);
    }

    [Fact]
    public async Task GetEntitlements_StarterPlan_DoesNotIncludeWorkSync()
    {
        await _client.PostAsJsonAsync("/api/v1/tenants", new
        {
            companyName = "Starter Only", slug = "starter-only",
            adminEmail = "admin@starter.com", adminFirstName = "A", adminLastName = "B",
            adminPassword = "SecurePass123!", planCode = "starter", industryProfile = "office_it"
        });

        var loginResp = await _client.PostAsJsonAsync("/api/v1/auth/login", new
        {
            tenantSlug = "starter-only",
            email = "admin@starter.com",
            password = "SecurePass123!"
        });
        var login = await loginResp.Content.ReadFromJsonAsync<LoginResult>();
        _client.DefaultRequestHeaders.Authorization =
            // Browser web auth now uses HttpOnly cookie sessions; do not attach login.AccessToken.

        var resp = await _client.GetAsync("/api/v1/me/entitlements");
        var dto = await resp.Content.ReadFromJsonAsync<EntitlementResult>();

        Assert.DoesNotContain("work_sync", dto!.Modules);
    }

    // â”€â”€ Local DTOs for response deserialization â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    private record LoginResult(bool Authenticated, bool MustChangePassword,
        string? ChangePasswordToken, bool MfaRequired, string? MfaPendingToken);

    private record EntitlementResult(
        Guid TenantId, Guid UserId,
        List<string> Modules, List<string> Permissions,
        PlanResult? Plan);

    private record PlanResult(string Code, List<string> AllowedModules);
}
```

- [ ] **Step 2: Run â€” expect compile failure (controller + query types don't exist)**

```
dotnet test tests/ONEVO.Tests.Integration --filter EntitlementEndpoint
```

Expected: Build errors.

- [ ] **Step 3: Create EntitlementDto**

```csharp
// src/ONEVO.Application/Features/InfrastructureModule/DTOs/EntitlementDto.cs
namespace ONEVO.Application.Features.InfrastructureModule.DTOs;

public record EntitlementDto(
    Guid TenantId,
    Guid UserId,
    List<string> Modules,
    List<string> Permissions,
    PlanDto? Plan);

public record PlanDto(string Code, List<string> AllowedModules);
```

- [ ] **Step 4: Create GetMyEntitlementsQuery**

```csharp
// src/ONEVO.Application/Features/InfrastructureModule/Queries/GetMyEntitlements/GetMyEntitlementsQuery.cs
using MediatR;
using ONEVO.Application.Common.Models;
using ONEVO.Application.Features.InfrastructureModule.DTOs;

namespace ONEVO.Application.Features.InfrastructureModule.Queries.GetMyEntitlements;

public record GetMyEntitlementsQuery : IRequest<Result<EntitlementDto>>;
```

- [ ] **Step 5: Create GetMyEntitlementsQueryHandler**

```csharp
// src/ONEVO.Application/Features/InfrastructureModule/Queries/GetMyEntitlements/GetMyEntitlementsQueryHandler.cs
using MediatR;
using Microsoft.EntityFrameworkCore;
using ONEVO.Application.Common.Interfaces;
using ONEVO.Application.Common.Models;
using ONEVO.Application.Features.Auth.Interfaces;
using ONEVO.Application.Features.InfrastructureModule.DTOs;
using ONEVO.Application.Features.InfrastructureModule.Interfaces;

namespace ONEVO.Application.Features.InfrastructureModule.Queries.GetMyEntitlements;

public class GetMyEntitlementsQueryHandler
    : IRequestHandler<GetMyEntitlementsQuery, Result<EntitlementDto>>
{
    private readonly ICurrentUserService _currentUser;
    private readonly IModuleEntitlementService _entitlement;
    private readonly IPermissionResolver _permissions;
    private readonly IApplicationDbContext _db;

    public GetMyEntitlementsQueryHandler(
        ICurrentUserService currentUser,
        IModuleEntitlementService entitlement,
        IPermissionResolver permissions,
        IApplicationDbContext db)
    {
        _currentUser = currentUser;
        _entitlement = entitlement;
        _permissions = permissions;
        _db = db;
    }

    public async Task<Result<EntitlementDto>> Handle(
        GetMyEntitlementsQuery request, CancellationToken ct)
    {
        var userId = _currentUser.UserId!.Value;
        var tenantId = _currentUser.TenantId!.Value;

        var modulesTask = _entitlement.GetActiveModulesAsync(tenantId, ct);
        var permissionsTask = _permissions.ResolveAsync(userId, tenantId, ct);

        await Task.WhenAll(modulesTask, permissionsTask);

        var sub = await _db.TenantSubscriptions
            .Include(ts => ts.Plan)
            .Where(ts => ts.TenantId == tenantId && ts.Status != "cancelled")
            .OrderByDescending(ts => ts.CreatedAt)
            .FirstOrDefaultAsync(ct);

        var planDto = sub is null
            ? null
            : new PlanDto(sub.Plan.Code, sub.Plan.AllowedModules.ToList());

        return Result<EntitlementDto>.Success(new EntitlementDto(
            tenantId, userId,
            modulesTask.Result,
            permissionsTask.Result,
            planDto));
    }
}
```

- [ ] **Step 6: Create EntitlementController**

```csharp
// src/ONEVO.Api/Controllers/InfrastructureModule/EntitlementController.cs
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ONEVO.Application.Features.InfrastructureModule.DTOs;
using ONEVO.Application.Features.InfrastructureModule.Queries.GetMyEntitlements;

namespace ONEVO.Api.Controllers.InfrastructureModule;

[ApiController]
[Route("api/v1/me")]
[Authorize]
public class EntitlementController : ControllerBase
{
    private readonly ISender _sender;

    public EntitlementController(ISender sender) => _sender = sender;

    /// <summary>Returns active modules and effective permissions for the authenticated user.</summary>
    [HttpGet("entitlements")]
    [ProducesResponseType(typeof(EntitlementDto), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetMyEntitlements(CancellationToken ct)
    {
        var result = await _sender.Send(new GetMyEntitlementsQuery(), ct);

        if (result.IsFailure)
            return StatusCode(500, new { result.Error.Code, result.Error.Message });

        return Ok(result.Value);
    }
}
```

- [ ] **Step 7: Run â€” expect all 3 endpoint tests pass**

```
dotnet test tests/ONEVO.Tests.Integration --filter EntitlementEndpoint
```

Expected: `3 passed, 0 failed`.

- [ ] **Step 8: Run full test suite**

```
dotnet test ONEVO.sln
```

Expected: All tests pass.

- [ ] **Step 9: Commit**

```
git add src/ tests/ONEVO.Tests.Integration/Entitlement/EntitlementEndpointTests.cs
git commit -m "feat(entitlement): add GET /api/v1/me/entitlements returning modules, permissions, and plan info"
```

---

## Task 8: SetTenantModulesAsync Write Path + DevPlatform Assignment Tests

**Files:**
- Modify: `src/ONEVO.Infrastructure/Services/ModuleEntitlementService.cs`
- Test: `tests/ONEVO.Tests.Integration/Entitlement/ModuleAssignmentTests.cs`

- [ ] **Step 1: Write failing module assignment tests**

```csharp
// tests/ONEVO.Tests.Integration/Entitlement/ModuleAssignmentTests.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using ONEVO.Application.Features.InfrastructureModule.Interfaces;
using ONEVO.Domain.Features.InfrastructureModule.Entities;
using ONEVO.Domain.Features.SharedPlatform.Entities;
using ONEVO.Domain.Modules;
using ONEVO.Infrastructure.Persistence;

namespace ONEVO.Tests.Integration.Entitlement;

public class ModuleAssignmentTests : IAsyncLifetime
{
    private readonly EntitlementTestFactory _factory = new();

    public async Task InitializeAsync() => await _factory.SeedDefaultPlansAsync();
    public Task DisposeAsync() { _factory.Dispose(); return Task.CompletedTask; }

    private static void SetId<T>(T entity, Guid id) where T : class
        => typeof(T).GetProperty("Id")!.SetValue(entity, id);

    private async Task<(Guid tenantId, IModuleEntitlementService svc, ApplicationDbContext db)>
        SetupTenantWithPlanAsync(IServiceScope scope, string planCode)
    {
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        var svc = scope.ServiceProvider.GetRequiredService<IModuleEntitlementService>();

        var tenantId = Guid.NewGuid();
        var plan = await db.SubscriptionPlans.FirstAsync(p => p.Code == planCode);

        var tenant = Tenant.Create("Module Test Corp", $"mod-test-{Guid.NewGuid():N}", "office_it");
        SetId(tenant, tenantId);
        tenant.MarkProvisioned(plan.Id);
        db.Tenants.Add(tenant);
        db.TenantSubscriptions.Add(TenantSubscription.Create(tenantId, plan.Id, Guid.Empty));
        await db.SaveChangesAsync();

        return (tenantId, svc, db);
    }

    [Fact]
    public async Task SetTenantModules_RemovesModulesNotInSet_AndAddsModulesBeyondPlan()
    {
        using var scope = _factory.Services.CreateScope();
        var (tenantId, svc, db) = await SetupTenantWithPlanAsync(scope, "starter");
        // Starter has: core_hr, leave, workforce_presence, notifications, data_import, skills

        // Request: keep core_hr, remove leave, add work_sync (beyond plan)
        await svc.SetTenantModulesAsync(
            tenantId,
            [ModuleKey.CoreHr, ModuleKey.WorkSync],
            Guid.Empty,
            CancellationToken.None);

        var active = await svc.GetActiveModulesAsync(tenantId, CancellationToken.None);

        Assert.Contains(ModuleKey.CoreHr, active);
        Assert.Contains(ModuleKey.WorkSync, active);
        Assert.DoesNotContain(ModuleKey.Leave, active);
        Assert.DoesNotContain(ModuleKey.WorkforcePresence, active);
    }

    [Fact]
    public async Task SetTenantModules_CalledTwice_SecondCallWins()
    {
        using var scope = _factory.Services.CreateScope();
        var (tenantId, svc, _) = await SetupTenantWithPlanAsync(scope, "starter");

        await svc.SetTenantModulesAsync(
            tenantId, [ModuleKey.CoreHr, ModuleKey.WorkSync], Guid.Empty, CancellationToken.None);

        await svc.SetTenantModulesAsync(
            tenantId, [ModuleKey.CoreHr, ModuleKey.Leave], Guid.Empty, CancellationToken.None);

        var active = await svc.GetActiveModulesAsync(tenantId, CancellationToken.None);

        Assert.Contains(ModuleKey.CoreHr, active);
        Assert.Contains(ModuleKey.Leave, active);
        Assert.DoesNotContain(ModuleKey.WorkSync, active);
    }

    [Fact]
    public async Task SetTenantModules_IgnoresUnknownModuleKeys()
    {
        using var scope = _factory.Services.CreateScope();
        var (tenantId, svc, _) = await SetupTenantWithPlanAsync(scope, "starter");

        await svc.SetTenantModulesAsync(
            tenantId, [ModuleKey.CoreHr, "phantom_module"], Guid.Empty, CancellationToken.None);

        var active = await svc.GetActiveModulesAsync(tenantId, CancellationToken.None);

        Assert.Contains(ModuleKey.CoreHr, active);
        Assert.DoesNotContain("phantom_module", active);
    }
}
```

- [ ] **Step 2: Run â€” expect 3 failures (NotImplementedException)**

```
dotnet test tests/ONEVO.Tests.Integration --filter ModuleAssignment
```

Expected: `3 failed` with `NotImplementedException`.

- [ ] **Step 3: Implement SetTenantModulesAsync in ModuleEntitlementService**

Replace the `SetTenantModulesAsync` method placeholder with the full implementation:

```csharp
public async Task SetTenantModulesAsync(
    Guid tenantId, IEnumerable<string> moduleKeys,
    Guid setByUserId, CancellationToken ct)
{
    var requested = new HashSet<string>(
        moduleKeys.Where(ModuleCatalog.IsKnown),
        StringComparer.Ordinal);

    // Soft-delete all existing tenant-level grants for this tenant
    var existing = await _db.FeatureAccessGrants
        .IgnoreQueryFilters()
        .Where(g => !g.IsDeleted && g.GranteeType == "tenant" && g.GranteeId == tenantId)
        .ToListAsync(ct);

    foreach (var g in existing)
        g.IsDeleted = true;

    // Resolve current plan modules
    var planModules = await GetPlanModulesAsync(tenantId, ct);

    // Write override grants only where the requested set diverges from the plan
    foreach (var module in ModuleCatalog.All)
    {
        var inPlan = planModules.Contains(module);
        var inRequested = requested.Contains(module);

        if (inRequested && !inPlan)
        {
            // Enable beyond plan
            _db.FeatureAccessGrants.Add(
                FeatureAccessGrant.Create("tenant", tenantId, module, true, tenantId, setByUserId));
        }
        else if (!inRequested && inPlan)
        {
            // Disable module that plan includes
            _db.FeatureAccessGrants.Add(
                FeatureAccessGrant.Create("tenant", tenantId, module, false, tenantId, setByUserId));
        }
        // If both match, no override grant is needed
    }

    // IApplicationDbContext is also IUnitOfWork â€” cast to save
    if (_db is IUnitOfWork uow)
        await uow.SaveChangesAsync(ct);
}

private async Task<HashSet<string>> GetPlanModulesAsync(Guid tenantId, CancellationToken ct)
{
    var sub = await _db.TenantSubscriptions
        .Include(ts => ts.Plan)
        .Where(ts => ts.TenantId == tenantId && ts.Status != "cancelled")
        .OrderByDescending(ts => ts.CreatedAt)
        .FirstOrDefaultAsync(ct);

    return new HashSet<string>(
        (sub?.Plan.AllowedModules ?? []).Where(ModuleCatalog.IsKnown),
        StringComparer.Ordinal);
}
```

Also add the required using at the top of `ModuleEntitlementService.cs`:

```csharp
using ONEVO.Application.Common.Interfaces;
using ONEVO.Domain.Features.Auth.Entities;
```

(`FeatureAccessGrant` is in `ONEVO.Domain.Features.Auth.Entities` â€” already in scope from the read path.)

- [ ] **Step 4: Run â€” expect all 3 tests pass**

```
dotnet test tests/ONEVO.Tests.Integration --filter ModuleAssignment
```

Expected: `3 passed, 0 failed`.

- [ ] **Step 5: Run full test suite**

```
dotnet test ONEVO.sln --filter Entitlement
```

Expected: All entitlement tests pass.

- [ ] **Step 6: Commit**

```
git add src/ONEVO.Infrastructure/Services/ModuleEntitlementService.cs `
        tests/ONEVO.Tests.Integration/Entitlement/ModuleAssignmentTests.cs
git commit -m "feat(entitlement): implement SetTenantModulesAsync for DevPlatform module assignment"
```

---

## Task 9: Final Verification + DEV1.md Update

- [ ] **Step 1: Run the full verification command for Task 3**

```
dotnet test ONEVO.sln --filter Entitlement
```

Expected: All entitlement tests pass (unit + integration).

- [ ] **Step 2: Run the full suite**

```
dotnet test ONEVO.sln
```

Expected: All tests pass with 0 failures.

- [ ] **Step 3: Build production configuration**

```
dotnet build ONEVO.sln -c Release
```

Expected: `Build succeeded.`

- [ ] **Step 4: Update DEV1.md â€” tick all Task 3 checkboxes**

Open `current-focus/DEV1.md`. In the **Task 3: Tenant + Entitlement Foundation** section, change each `- [ ]` to `- [x]`:

```markdown
- [x] Tenant provisioning creates baseline tenant, legal entity, admin user, and subscription record.
- [x] Module entitlement service resolves active modules from subscription, feature grants, and module registry.
- [x] Permissions service can return effective permissions for a user and tenant.
- [x] Entitlement DTO supports web and IDE consumers.
- [x] Developer Platform provisioning can set tenant modules through the same entitlement/module registry.
- [x] Tests cover active module resolution, permission inheritance, and module assignment.
```

Also update **Current Unfinished Task** from `Task 2 - Tenant Auth + RBAC` to `Task 5 - Shared Platform Core + Workflow Engine`.

- [ ] **Step 5: Final commit**

```
git add current-focus/DEV1.md
git commit -m "docs(dev1): mark Task 3 Tenant + Entitlement Foundation complete"
```

---

## Self-Review Checklist

**Spec coverage:**
| AC | Task |
|---|---|
| Tenant provisioning creates baseline tenant, legal entity, admin user, and subscription record | Task 6 |
| Module entitlement service resolves active modules from subscription, feature grants, and module registry | Task 5 |
| Permissions service returns effective permissions (reuses IPermissionResolver from Task 2) | Task 7 handler |
| Entitlement DTO supports web and IDE consumers (single DTO, single endpoint) | Task 7 |
| DevPlatform can set tenant modules through same entitlement/module registry | Task 8 |
| Tests cover active module resolution, permission inheritance, and module assignment | Tasks 5, 7, 8 |

**Type consistency across tasks:**
- `ModuleKey.*` constants defined in Task 1 â€” used unchanged in Tasks 5, 6, 7, 8
- `ProvisionTenantResult` defined in Task 6 `ITenantProvisioningService.cs` â€” returned by handler and controller
- `EntitlementDto` / `PlanDto` defined in Task 7 â€” returned by handler and controller
- `IModuleEntitlementService.SetTenantModulesAsync` signature defined in Task 5 â€” implemented in Task 8
- `FeatureAccessGrant.Create("tenant", ...)` pattern â€” used identically in Tasks 5 (read path) and 8 (write path)
- `IgnoreQueryFilters()` used consistently everywhere tenant-level grants are read cross-tenant

**Placeholder scan:** None found â€” every step contains complete, compilable code.

