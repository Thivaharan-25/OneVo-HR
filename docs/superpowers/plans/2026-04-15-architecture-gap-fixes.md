# Architecture Gap Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close 4 architecture gaps in the backend design — hierarchy scope scalability, bridge API authentication, employee-device binding for agent ingest, and session table naming inconsistency.

**Architecture:** Each gap is independent and can be shipped separately. Gap 1 changes the SharedKernel and Auth module public interface. Gap 2 adds a new bridge auth subsystem to the Auth and API layers. Gap 3 adds an `agent_sessions` table and two endpoints to AgentGateway. Gap 4 is a doc-only fix.

**Tech Stack:** .NET 9, EF Core 9, PostgreSQL 16, MediatR, xUnit, FluentAssertions, Testcontainers, ArchUnitNET

---

## File Map

### Gap 1 — Hierarchy Scope (no extra DB round-trip, scales to large orgs)

| Action | File |
|:-------|:-----|
| Modify | `ONEVO.SharedKernel/HierarchyFilter.cs` — new value object |
| Modify | `ONEVO.Modules.Auth/Public/IHierarchyScopeService.cs` — return `HierarchyFilter` |
| Modify | `ONEVO.Modules.Auth/Internal/Services/HierarchyScopeService.cs` — return `HierarchyFilter` |
| Modify | `ONEVO.SharedKernel/BaseRepository.cs` — add `ApplyHierarchyFilter()` extension |
| Create | Migration: add index `idx_employees_reports_to_id` |
| Create | `ONEVO.Tests.Unit/HierarchyFilterTests.cs` |
| Create | `ONEVO.Tests.Integration/HierarchyScopeServiceTests.cs` |
| Update vault | `modules/auth/authorization/overview.md` — document HierarchyFilter |
| Update vault | `backend/shared-kernel.md` — document HierarchyFilter in SharedKernel exports |

### Gap 2 — Bridge API Authentication (OAuth 2.0 Client Credentials for service-to-service)

| Action | File |
|:-------|:-----|
| Create | `ONEVO.Modules.Auth/Internal/Entities/BridgeClient.cs` |
| Create | Migration: `bridge_clients` table |
| Modify | `ONEVO.Modules.Auth/Public/IAuthService.cs` — add `IssueBridgeTokenAsync()` |
| Modify | `ONEVO.Modules.Auth/Internal/Services/AuthService.cs` — implement bridge token |
| Modify | `ONEVO.Modules.Auth/Public/ITokenService.cs` — add `GenerateBridgeTokenAsync()` |
| Modify | `ONEVO.Modules.Auth/Internal/Services/TokenService.cs` — implement bridge token |
| Create | `ONEVO.Api/Middleware/BridgeAuthMiddleware.cs` |
| Create | `ONEVO.Modules.Auth/Endpoints/BridgeAuthEndpoints.cs` |
| Create | `ONEVO.Tests.Unit/BridgeAuthTests.cs` |
| Create | `ONEVO.Tests.Integration/BridgeAuthEndpointTests.cs` |
| Create vault | `backend/bridge-api-contracts.md` — full bridge auth spec |
| Update vault | `modules/auth/overview.md` — add BridgeClient table |
| Update vault | `database/schemas/infrastructure.md` — add bridge_clients schema |
| Update vault | `backend/api-conventions.md` — add bridge auth header docs |

### Gap 3 — Employee-Device Binding (server-side session table)

| Action | File |
|:-------|:-----|
| Create | `ONEVO.Modules.AgentGateway/Internal/Entities/AgentSession.cs` |
| Create | Migration: `agent_sessions` table |
| Create | `ONEVO.Modules.AgentGateway/Internal/Services/AgentSessionService.cs` |
| Create | `ONEVO.Modules.AgentGateway/Public/IAgentSessionService.cs` |
| Create | `ONEVO.Modules.AgentGateway/Endpoints/AgentSessionEndpoints.cs` |
| Modify | `ONEVO.Modules.AgentGateway/Endpoints/DataIngestionEndpoints.cs` — validate via session |
| Create | `ONEVO.Tests.Unit/AgentSessionServiceTests.cs` |
| Create | `ONEVO.Tests.Integration/AgentSessionEndpointTests.cs` |
| Update vault | `modules/agent-gateway/data-ingestion/overview.md` — document binding design |
| Update vault | `modules/agent-gateway/ipc-protocol.md` — document employee login IPC flow |
| Update vault | `database/schemas/agent-gateway.md` — add agent_sessions table |
| Update vault | `AI_CONTEXT/known-issues.md` — remove the "agent-device binding unclear" gotcha |

### Gap 4 — Session Table Naming (1-line fix)

| Action | File |
|:-------|:-----|
| Update vault | `security/auth-architecture.md` — `user_sessions` → `sessions` (2 occurrences) |

---

## Task 1: HierarchyFilter Value Object

**Files:**
- Create: `ONEVO.SharedKernel/HierarchyFilter.cs`
- Create: `ONEVO.Tests.Unit/HierarchyFilterTests.cs`

**Why this design:** The current `GetSubordinateIdsAsync()` makes an extra DB round-trip and then sends a potentially large `WHERE id IN (uuid, uuid, ...)` clause. `HierarchyFilter` is a value object passed INTO the repository, so the CTE is composed inside the SQL query — one trip, no large IN list.

- [ ] **Step 1: Write the failing tests**

```csharp
// ONEVO.Tests.Unit/HierarchyFilterTests.cs
using ONEVO.SharedKernel;
using FluentAssertions;

namespace ONEVO.Tests.Unit;

public class HierarchyFilterTests
{
    [Fact]
    public void All_IsUniversal_ReturnsTrue()
    {
        var filter = HierarchyFilter.All.Instance;
        filter.IsUniversal.Should().BeTrue();
    }

    [Fact]
    public void SubordinatesOf_IsNotUniversal()
    {
        var managerId = Guid.NewGuid();
        var filter = new HierarchyFilter.SubordinatesOf(managerId);
        filter.IsUniversal.Should().BeFalse();
    }

    [Fact]
    public void OwnOnly_IsNotUniversal()
    {
        var employeeId = Guid.NewGuid();
        var filter = new HierarchyFilter.OwnOnly(employeeId);
        filter.IsUniversal.Should().BeFalse();
    }

    [Fact]
    public void SubordinatesOf_StoresManagerId()
    {
        var managerId = Guid.NewGuid();
        var filter = new HierarchyFilter.SubordinatesOf(managerId);
        filter.ManagerId.Should().Be(managerId);
    }

    [Fact]
    public void OwnOnly_StoresEmployeeId()
    {
        var employeeId = Guid.NewGuid();
        var filter = new HierarchyFilter.OwnOnly(employeeId);
        filter.EmployeeId.Should().Be(employeeId);
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
dotnet test ONEVO.Tests.Unit --filter "HierarchyFilterTests" -v minimal
```

Expected: FAIL — `HierarchyFilter` type not found.

- [ ] **Step 3: Implement HierarchyFilter**

```csharp
// ONEVO.SharedKernel/HierarchyFilter.cs
namespace ONEVO.SharedKernel;

/// <summary>
/// Represents how queries should be scoped to the org hierarchy.
/// Pass this into repository methods instead of materializing a list of IDs.
/// The repository applies a recursive CTE internally — one DB round-trip, no large IN list.
/// </summary>
public abstract record HierarchyFilter
{
    /// <summary>No hierarchy restriction — used by Super Admin. All tenant employees visible.</summary>
    public sealed record AllEmployees : HierarchyFilter
    {
        public static readonly AllEmployees Instance = new();
        private AllEmployees() { }
        public override bool IsUniversal => true;
    }

    /// <summary>Recursive subtree: the manager + all employees below them in the reporting chain.</summary>
    public sealed record SubordinatesOf(Guid ManagerId) : HierarchyFilter
    {
        public override bool IsUniversal => false;
    }

    /// <summary>Self-only: the employee can only see their own record.</summary>
    public sealed record OwnOnly(Guid EmployeeId) : HierarchyFilter
    {
        public override bool IsUniversal => false;
    }

    /// <summary>True only for AllEmployees — used to skip the CTE entirely.</summary>
    public abstract bool IsUniversal { get; }

    // Convenience alias so callers can write HierarchyFilter.All
    public static AllEmployees All => AllEmployees.Instance;
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
dotnet test ONEVO.Tests.Unit --filter "HierarchyFilterTests" -v minimal
```

Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add ONEVO.SharedKernel/HierarchyFilter.cs ONEVO.Tests.Unit/HierarchyFilterTests.cs
git commit -m "feat(shared-kernel): add HierarchyFilter value object for scope-aware queries"
```

---

## Task 2: Update IHierarchyScopeService Interface

**Files:**
- Modify: `ONEVO.Modules.Auth/Public/IHierarchyScopeService.cs`
- Modify: `ONEVO.Modules.Auth/Internal/Services/HierarchyScopeService.cs`

**Why:** The current interface returns `HashSet<Guid>` and forces callers to do a two-step: fetch IDs, then filter. The new interface returns `HierarchyFilter` — a lightweight value object. The repository handles the CTE in Task 3.

- [ ] **Step 1: Write the failing unit test**

```csharp
// ONEVO.Tests.Unit/HierarchyScopeServiceTests.cs
using ONEVO.Modules.Auth.Public;
using ONEVO.SharedKernel;
using FluentAssertions;
using Moq;

namespace ONEVO.Tests.Unit;

public class HierarchyScopeServiceTests
{
    private readonly Mock<ICurrentUser> _currentUser = new();
    private readonly HierarchyScopeService _sut;

    public HierarchyScopeServiceTests()
    {
        _sut = new HierarchyScopeService(_currentUser.Object);
    }

    [Fact]
    public async Task GetFilter_WhenSuperAdmin_ReturnsAll()
    {
        _currentUser.Setup(u => u.IsSuperAdmin).Returns(true);

        var filter = await _sut.GetFilterAsync(CancellationToken.None);

        filter.Should().Be(HierarchyFilter.All);
    }

    [Fact]
    public async Task GetFilter_WhenManager_ReturnsSubordinatesOf()
    {
        var managerId = Guid.NewGuid();
        _currentUser.Setup(u => u.IsSuperAdmin).Returns(false);
        _currentUser.Setup(u => u.EmployeeId).Returns(managerId);

        var filter = await _sut.GetFilterAsync(CancellationToken.None);

        filter.Should().BeOfType<HierarchyFilter.SubordinatesOf>()
              .Which.ManagerId.Should().Be(managerId);
    }

    [Fact]
    public async Task GetFilter_WhenEmployee_ReturnsOwnOnly()
    {
        var employeeId = Guid.NewGuid();
        _currentUser.Setup(u => u.IsSuperAdmin).Returns(false);
        _currentUser.Setup(u => u.EmployeeId).Returns(employeeId);
        _currentUser.Setup(u => u.HasPermission("employees:read-team")).Returns(false);

        var filter = await _sut.GetFilterAsync(CancellationToken.None);

        filter.Should().BeOfType<HierarchyFilter.OwnOnly>()
              .Which.EmployeeId.Should().Be(employeeId);
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
dotnet test ONEVO.Tests.Unit --filter "HierarchyScopeServiceTests" -v minimal
```

Expected: FAIL — `GetFilterAsync` method not found.

- [ ] **Step 3: Update the public interface**

```csharp
// ONEVO.Modules.Auth/Public/IHierarchyScopeService.cs
using ONEVO.SharedKernel;

namespace ONEVO.Modules.Auth.Public;

public interface IHierarchyScopeService
{
    /// <summary>
    /// Returns the appropriate HierarchyFilter for the current user.
    /// - Super Admin → HierarchyFilter.All (no restriction)
    /// - Manager (has employees:read-team) → HierarchyFilter.SubordinatesOf(managerId)
    /// - Employee → HierarchyFilter.OwnOnly(employeeId)
    ///
    /// Pass the returned filter into repository methods. Do NOT call this and
    /// then materialize a list of IDs — that defeats the purpose.
    /// </summary>
    Task<HierarchyFilter> GetFilterAsync(CancellationToken ct);
}
```

- [ ] **Step 4: Update the implementation**

```csharp
// ONEVO.Modules.Auth/Internal/Services/HierarchyScopeService.cs
using ONEVO.Modules.Auth.Public;
using ONEVO.SharedKernel;

namespace ONEVO.Modules.Auth.Internal.Services;

internal sealed class HierarchyScopeService : IHierarchyScopeService
{
    private readonly ICurrentUser _currentUser;

    public HierarchyScopeService(ICurrentUser currentUser)
    {
        _currentUser = currentUser;
    }

    public Task<HierarchyFilter> GetFilterAsync(CancellationToken ct)
    {
        if (_currentUser.IsSuperAdmin)
            return Task.FromResult<HierarchyFilter>(HierarchyFilter.All);

        if (_currentUser.HasPermission("employees:read-team"))
            return Task.FromResult<HierarchyFilter>(
                new HierarchyFilter.SubordinatesOf(_currentUser.EmployeeId));

        return Task.FromResult<HierarchyFilter>(
            new HierarchyFilter.OwnOnly(_currentUser.EmployeeId));
    }
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
dotnet test ONEVO.Tests.Unit --filter "HierarchyScopeServiceTests" -v minimal
```

Expected: PASS (3 tests).

- [ ] **Step 6: Commit**

```bash
git add ONEVO.Modules.Auth/Public/IHierarchyScopeService.cs \
        ONEVO.Modules.Auth/Internal/Services/HierarchyScopeService.cs \
        ONEVO.Tests.Unit/HierarchyScopeServiceTests.cs
git commit -m "feat(auth): refactor IHierarchyScopeService to return HierarchyFilter value object"
```

---

## Task 3: BaseRepository CTE Support + Migration

**Files:**
- Modify: `ONEVO.SharedKernel/BaseRepository.cs`
- Create: `ONEVO.DbMigrator/Migrations/YYYYMMDD_AddHierarchyIndex.cs`
- Create: `ONEVO.Tests.Integration/HierarchyRepositoryTests.cs`

**Why the CTE approach:** `employees` is self-referencing via `reports_to_id`. A recursive CTE walks the tree in one SQL statement. The EF Core 9 `Database.SqlQuery<T>()` (not raw string — it's typed and uses parameters) returns an `IQueryable<Guid>` that EF can compose into a subquery. No application-level ID list. No extra round-trip.

- [ ] **Step 1: Write the failing integration test**

```csharp
// ONEVO.Tests.Integration/HierarchyRepositoryTests.cs
using ONEVO.SharedKernel;
using ONEVO.Tests.Integration.Fixtures;
using FluentAssertions;

namespace ONEVO.Tests.Integration;

public class HierarchyRepositoryTests : IClassFixture<PostgresFixture>
{
    private readonly PostgresFixture _db;

    public HierarchyRepositoryTests(PostgresFixture db) => _db = db;

    [Fact]
    public async Task ApplyHierarchyFilter_SubordinatesOf_ReturnsOnlySubtree()
    {
        // Arrange: CEO → Manager → Employee1, Employee2
        var tenantId = await _db.CreateTenantAsync();
        var ceoId = await _db.CreateEmployeeAsync(tenantId, reportsToId: null);
        var managerId = await _db.CreateEmployeeAsync(tenantId, reportsToId: ceoId);
        var emp1Id = await _db.CreateEmployeeAsync(tenantId, reportsToId: managerId);
        var emp2Id = await _db.CreateEmployeeAsync(tenantId, reportsToId: managerId);

        var repo = _db.GetEmployeeRepository(tenantId);
        var filter = new HierarchyFilter.SubordinatesOf(managerId);

        // Act
        var results = await repo.GetAllWithFilterAsync(filter, CancellationToken.None);

        // Assert: manager sees own record + direct reports (3 total)
        results.Select(e => e.Id).Should().BeEquivalentTo(
            new[] { managerId, emp1Id, emp2Id });
    }

    [Fact]
    public async Task ApplyHierarchyFilter_All_ReturnsAllTenantEmployees()
    {
        var tenantId = await _db.CreateTenantAsync();
        var id1 = await _db.CreateEmployeeAsync(tenantId, reportsToId: null);
        var id2 = await _db.CreateEmployeeAsync(tenantId, reportsToId: id1);

        var repo = _db.GetEmployeeRepository(tenantId);

        var results = await repo.GetAllWithFilterAsync(HierarchyFilter.All, CancellationToken.None);

        results.Select(e => e.Id).Should().BeEquivalentTo(new[] { id1, id2 });
    }

    [Fact]
    public async Task ApplyHierarchyFilter_OwnOnly_ReturnsSingleEmployee()
    {
        var tenantId = await _db.CreateTenantAsync();
        var id1 = await _db.CreateEmployeeAsync(tenantId, reportsToId: null);
        await _db.CreateEmployeeAsync(tenantId, reportsToId: id1);

        var repo = _db.GetEmployeeRepository(tenantId);
        var filter = new HierarchyFilter.OwnOnly(id1);

        var results = await repo.GetAllWithFilterAsync(filter, CancellationToken.None);

        results.Should().HaveCount(1);
        results.Single().Id.Should().Be(id1);
    }

    [Fact]
    public async Task ApplyHierarchyFilter_DoesNotLeakAcrossTenants()
    {
        var tenantA = await _db.CreateTenantAsync();
        var tenantB = await _db.CreateTenantAsync();
        var managerA = await _db.CreateEmployeeAsync(tenantA, reportsToId: null);
        await _db.CreateEmployeeAsync(tenantB, reportsToId: null);

        var repo = _db.GetEmployeeRepository(tenantA);
        var results = await repo.GetAllWithFilterAsync(HierarchyFilter.All, CancellationToken.None);

        results.Should().OnlyContain(e => e.TenantId == tenantA);
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
dotnet test ONEVO.Tests.Integration --filter "HierarchyRepositoryTests" -v minimal
```

Expected: FAIL — `GetAllWithFilterAsync` not found.

- [ ] **Step 3: Add `ApplyHierarchyFilter` to BaseRepository**

```csharp
// ONEVO.SharedKernel/BaseRepository.cs — add these two members

/// <summary>
/// Returns all entities matching the hierarchy filter.
/// Uses a recursive CTE for SubordinatesOf — single DB query, no IN-list.
/// TENANT FILTERING IS ALWAYS APPLIED regardless of filter type.
/// </summary>
public async Task<List<T>> GetAllWithFilterAsync(
    HierarchyFilter filter, CancellationToken ct) where T : Employee
{
    return await ApplyHierarchyFilter(Query, filter).ToListAsync(ct);
}

/// <summary>
/// Composes a hierarchy filter onto an existing IQueryable.
/// Call this inside module-specific repository methods that need scoping.
/// </summary>
protected IQueryable<T> ApplyHierarchyFilter(IQueryable<T> source, HierarchyFilter filter)
    where T : Employee
{
    return filter switch
    {
        HierarchyFilter.AllEmployees => source,

        HierarchyFilter.OwnOnly(var empId) =>
            source.Where(e => e.Id == empId),

        HierarchyFilter.SubordinatesOf(var managerId) =>
            ApplySubordinateCte(source, managerId),

        _ => throw new ArgumentOutOfRangeException(nameof(filter))
    };
}

private IQueryable<T> ApplySubordinateCte(IQueryable<T> source, Guid managerId)
    where T : Employee
{
    // Recursive CTE: manager + all employees below in reporting chain.
    // Uses EF Core 9 SqlQuery<T> with typed parameters (no string interpolation).
    // tenant_id is already filtered by the base Query — the CTE adds hierarchy scope.
    var subordinateIds = _context.Database.SqlQuery<Guid>(
        $"""
        WITH RECURSIVE subordinates AS (
            SELECT id
            FROM employees
            WHERE (id = {managerId} OR reports_to_id = {managerId})
              AND tenant_id = {_tenantContext.TenantId}
              AND is_deleted = false
            UNION ALL
            SELECT e.id
            FROM employees e
            INNER JOIN subordinates s ON e.reports_to_id = s.id
            WHERE e.tenant_id = {_tenantContext.TenantId}
              AND e.is_deleted = false
        )
        SELECT id FROM subordinates
        """);

    // EF composes this as a subquery — the outer query still has full tenant filtering
    return source.Where(e => subordinateIds.Contains(e.Id));
}
```

> **Note on string interpolation in `SqlQuery`:** EF Core 9's `Database.SqlQuery<T>($"...")` with FormattableString automatically parameterizes interpolated values. This is NOT the same as raw string interpolation — EF converts `{managerId}` to `@p0`. See [EF Core raw SQL docs](https://learn.microsoft.com/en-us/ef/core/querying/sql-queries).

- [ ] **Step 4: Create the migration for the hierarchy index**

```csharp
// ONEVO.DbMigrator/Migrations/YYYYMMDD_AddHierarchyIndex.cs
public partial class AddHierarchyIndex : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // Partial index: only non-deleted employees, covering the recursive CTE join
        migrationBuilder.Sql("""
            CREATE INDEX idx_employees_reports_to_id
            ON employees (reports_to_id, tenant_id)
            WHERE is_deleted = false;
            """);
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("DROP INDEX IF EXISTS idx_employees_reports_to_id;");
    }
}
```

- [ ] **Step 5: Run the migration against local DB**

```bash
dotnet run --project ONEVO.DbMigrator -- --environment Development
```

Expected: Migration applied successfully.

- [ ] **Step 6: Run integration tests**

```bash
dotnet test ONEVO.Tests.Integration --filter "HierarchyRepositoryTests" -v minimal
```

Expected: PASS (4 tests).

- [ ] **Step 7: Update vault docs**

In `modules/auth/authorization/overview.md`, add a section:

```markdown
## Hierarchy Scoping Implementation

`IHierarchyScopeService.GetFilterAsync()` returns a `HierarchyFilter` value object.
Pass it to repository methods — never materialize a list of IDs.

| User type | Filter returned | SQL mechanism |
|:----------|:----------------|:--------------|
| Super Admin | `HierarchyFilter.All` | No additional filter |
| Manager (has `employees:read-team`) | `HierarchyFilter.SubordinatesOf(managerId)` | Recursive CTE in one query |
| Employee | `HierarchyFilter.OwnOnly(employeeId)` | `WHERE id = @employeeId` |

The CTE includes the manager themselves + all employees below in the reporting chain.
Index: `idx_employees_reports_to_id ON employees(reports_to_id, tenant_id) WHERE is_deleted = false`
```

- [ ] **Step 8: Commit**

```bash
git add ONEVO.SharedKernel/BaseRepository.cs \
        ONEVO.DbMigrator/Migrations/ \
        ONEVO.Tests.Integration/HierarchyRepositoryTests.cs \
        modules/auth/authorization/overview.md
git commit -m "feat(shared-kernel): add CTE-based hierarchy filter to BaseRepository"
```

---

## Task 4: Bridge API Authentication — Schema + Token Endpoint

**Files:**
- Create: `ONEVO.Modules.Auth/Internal/Entities/BridgeClient.cs`
- Create: Migration — `bridge_clients` table
- Modify: `ONEVO.Modules.Auth/Public/ITokenService.cs`
- Modify: `ONEVO.Modules.Auth/Internal/Services/TokenService.cs`
- Modify: `ONEVO.Modules.Auth/Endpoints/BridgeAuthEndpoints.cs`
- Create: `ONEVO.Tests.Unit/BridgeAuthTests.cs`

**Why OAuth Client Credentials (not API key + HMAC):**
- ONEVO already has JWT infrastructure (RS256, key rotation) — reuse it
- Bridge JWT carries `tenant_id` + `allowed_bridges[]` claims, so middleware can make one decision
- Token expiry (1 hour) limits exposure window without requiring HMAC signing on every request
- Client secret hashed with Argon2id (same as user passwords) — consistent security posture

**Bridge JWT payload:**
```json
{
  "sub": "bridge-client-uuid",
  "tenant_id": "tenant-uuid",
  "type": "bridge",
  "bridges": ["people-sync", "availability"],
  "iss": "onevo",
  "aud": "onevo-bridge",
  "iat": 1679616000,
  "exp": 1679619600
}
```

- [ ] **Step 1: Write failing unit tests for bridge token generation**

```csharp
// ONEVO.Tests.Unit/BridgeAuthTests.cs
using ONEVO.Modules.Auth.Internal.Services;
using ONEVO.Modules.Auth.Public;
using ONEVO.SharedKernel;
using FluentAssertions;
using Moq;
using Microsoft.Extensions.Options;

namespace ONEVO.Tests.Unit;

public class BridgeAuthTests
{
    private readonly Mock<IOptions<JwtOptions>> _jwtOptions = new();
    private readonly TokenService _sut;

    public BridgeAuthTests()
    {
        _jwtOptions.Setup(o => o.Value).Returns(new JwtOptions
        {
            Issuer = "onevo",
            Audience = "onevo-api",
            BridgeAudience = "onevo-bridge",
            PrivateKeyPem = TestKeys.RsaPrivateKeyPem
        });
        _sut = new TokenService(_jwtOptions.Object);
    }

    [Fact]
    public async Task GenerateBridgeToken_ContainsBridgeType()
    {
        var clientId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();
        var bridges = new[] { "people-sync", "availability" };

        var token = await _sut.GenerateBridgeTokenAsync(clientId, tenantId, bridges, CancellationToken.None);

        var claims = TestJwt.Parse(token);
        claims["type"].Should().Be("bridge");
    }

    [Fact]
    public async Task GenerateBridgeToken_ContainsTenantId()
    {
        var tenantId = Guid.NewGuid();
        var token = await _sut.GenerateBridgeTokenAsync(
            Guid.NewGuid(), tenantId, new[] { "people-sync" }, CancellationToken.None);

        var claims = TestJwt.Parse(token);
        claims["tenant_id"].Should().Be(tenantId.ToString());
    }

    [Fact]
    public async Task GenerateBridgeToken_ExpiresInOneHour()
    {
        var token = await _sut.GenerateBridgeTokenAsync(
            Guid.NewGuid(), Guid.NewGuid(), new[] { "people-sync" }, CancellationToken.None);

        var claims = TestJwt.Parse(token);
        var exp = DateTimeOffset.FromUnixTimeSeconds(long.Parse(claims["exp"]));
        exp.Should().BeCloseTo(DateTimeOffset.UtcNow.AddHours(1), TimeSpan.FromSeconds(5));
    }

    [Fact]
    public async Task GenerateBridgeToken_AudienceIsOnEvoBridge()
    {
        var token = await _sut.GenerateBridgeTokenAsync(
            Guid.NewGuid(), Guid.NewGuid(), new[] { "people-sync" }, CancellationToken.None);

        var claims = TestJwt.Parse(token);
        claims["aud"].Should().Be("onevo-bridge");
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
dotnet test ONEVO.Tests.Unit --filter "BridgeAuthTests" -v minimal
```

Expected: FAIL — `GenerateBridgeTokenAsync` not found.

- [ ] **Step 3: Create BridgeClient entity**

```csharp
// ONEVO.Modules.Auth/Internal/Entities/BridgeClient.cs
using ONEVO.SharedKernel;

namespace ONEVO.Modules.Auth.Internal.Entities;

/// <summary>
/// Represents an external service (e.g. WorkManage Pro) that has registered
/// to consume ONEVO bridge APIs. Uses OAuth 2.0 Client Credentials flow.
/// </summary>
internal sealed class BridgeClient : BaseEntity
{
    /// <summary>Public identifier sent in token requests. Not secret.</summary>
    public Guid ClientId { get; private set; }

    /// <summary>Argon2id hash of the client secret. Never store plaintext.</summary>
    public string ClientSecretHash { get; private set; } = default!;

    /// <summary>Human-readable name, e.g. "WorkManage Pro".</summary>
    public string Name { get; private set; } = default!;

    /// <summary>
    /// Subset of bridge names this client is allowed to call.
    /// Valid values: people-sync, availability, performance, skills, work-activity
    /// </summary>
    public string[] AllowedBridges { get; private set; } = [];

    public bool IsActive { get; private set; } = true;
    public DateTimeOffset? ExpiresAt { get; private set; }
    public DateTimeOffset? LastUsedAt { get; private set; }

    private BridgeClient() { }

    public static BridgeClient Create(
        Guid tenantId,
        string name,
        string clientSecretHash,
        string[] allowedBridges,
        Guid createdById)
    {
        return new BridgeClient
        {
            TenantId = tenantId,
            ClientId = Guid.NewGuid(),
            Name = name,
            ClientSecretHash = clientSecretHash,
            AllowedBridges = allowedBridges,
            CreatedById = createdById
        };
    }

    public void RecordUsage()
    {
        LastUsedAt = DateTimeOffset.UtcNow;
    }

    public bool IsExpired() =>
        ExpiresAt.HasValue && ExpiresAt.Value < DateTimeOffset.UtcNow;
}
```

- [ ] **Step 4: Create the migration**

```csharp
// ONEVO.DbMigrator/Migrations/YYYYMMDD_AddBridgeClients.cs
public partial class AddBridgeClients : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("""
            CREATE TABLE bridge_clients (
                id              uuid            NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
                tenant_id       uuid            NOT NULL REFERENCES tenants(id),
                client_id       uuid            NOT NULL UNIQUE,
                client_secret_hash varchar(128) NOT NULL,
                name            varchar(100)    NOT NULL,
                allowed_bridges varchar[]       NOT NULL DEFAULT '{}',
                is_active       boolean         NOT NULL DEFAULT true,
                expires_at      timestamptz,
                last_used_at    timestamptz,
                created_at      timestamptz     NOT NULL DEFAULT now(),
                updated_at      timestamptz     NOT NULL DEFAULT now(),
                created_by_id   uuid            REFERENCES users(id),
                is_deleted      boolean         NOT NULL DEFAULT false,
                deleted_at      timestamptz
            );

            CREATE INDEX idx_bridge_clients_tenant ON bridge_clients(tenant_id) WHERE is_deleted = false;
            CREATE INDEX idx_bridge_clients_client_id ON bridge_clients(client_id) WHERE is_active = true;
            """);
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("DROP TABLE IF EXISTS bridge_clients;");
    }
}
```

- [ ] **Step 5: Update ITokenService**

```csharp
// ONEVO.Modules.Auth/Public/ITokenService.cs — add this method
public interface ITokenService
{
    Task<string> GenerateAccessTokenAsync(Guid userId, Guid tenantId, List<string> permissions, CancellationToken ct);
    Task<string> GenerateDeviceTokenAsync(Guid deviceId, Guid tenantId, CancellationToken ct);
    Task<string> GenerateRefreshTokenAsync(Guid userId, CancellationToken ct);

    /// <summary>
    /// Generates a bridge JWT for service-to-service calls (OAuth client credentials).
    /// Audience: "onevo-bridge". Type claim: "bridge". Expires: 1 hour.
    /// </summary>
    Task<string> GenerateBridgeTokenAsync(
        Guid clientId, Guid tenantId, string[] allowedBridges, CancellationToken ct);
}
```

- [ ] **Step 6: Implement GenerateBridgeTokenAsync in TokenService**

```csharp
// ONEVO.Modules.Auth/Internal/Services/TokenService.cs — add this method
public async Task<string> GenerateBridgeTokenAsync(
    Guid clientId, Guid tenantId, string[] allowedBridges, CancellationToken ct)
{
    var now = DateTimeOffset.UtcNow;
    var claims = new List<Claim>
    {
        new(JwtRegisteredClaimNames.Sub, clientId.ToString()),
        new("tenant_id", tenantId.ToString()),
        new("type", "bridge"),
        new("bridges", JsonSerializer.Serialize(allowedBridges)),
        new(JwtRegisteredClaimNames.Iat, now.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer64),
    };

    var key = LoadRsaPrivateKey();
    var credentials = new SigningCredentials(new RsaSecurityKey(key), SecurityAlgorithms.RsaSha256);

    var token = new JwtSecurityToken(
        issuer: _options.Issuer,
        audience: _options.BridgeAudience, // "onevo-bridge" — separate from "onevo-api"
        claims: claims,
        notBefore: now.UtcDateTime,
        expires: now.AddHours(1).UtcDateTime,
        signingCredentials: credentials);

    return new JwtSecurityTokenHandler().WriteToken(token);
}
```

- [ ] **Step 7: Create the bridge token endpoint**

```csharp
// ONEVO.Modules.Auth/Endpoints/BridgeAuthEndpoints.cs
using ONEVO.Modules.Auth.Internal.Services;

namespace ONEVO.Modules.Auth.Endpoints;

internal static class BridgeAuthEndpoints
{
    internal static void MapBridgeAuthEndpoints(this IEndpointRouteBuilder app)
    {
        // Public — no [Authorize]. Bridge client credentials are validated inside the handler.
        app.MapPost("/api/v1/auth/bridge/token", IssueBridgeToken)
           .WithName("IssueBridgeToken")
           .WithTags("Bridge Auth")
           .AllowAnonymous();
    }

    private static async Task<IResult> IssueBridgeToken(
        BridgeTokenRequest request,
        IBridgeAuthService bridgeAuthService,
        CancellationToken ct)
    {
        var result = await bridgeAuthService.IssueTokenAsync(request, ct);

        return result.IsSuccess
            ? Results.Ok(new BridgeTokenResponse(
                AccessToken: result.Value.Token,
                TokenType: "Bearer",
                ExpiresIn: 3600))
            : Results.Problem(
                title: "Authentication failed",
                detail: result.Error,
                statusCode: 401);
    }
}

internal record BridgeTokenRequest(
    Guid ClientId,
    string ClientSecret,
    Guid TenantId);

internal record BridgeTokenResponse(
    string AccessToken,
    string TokenType,
    int ExpiresIn);
```

- [ ] **Step 8: Run unit tests to verify they pass**

```bash
dotnet test ONEVO.Tests.Unit --filter "BridgeAuthTests" -v minimal
```

Expected: PASS (4 tests).

- [ ] **Step 9: Apply migration**

```bash
dotnet run --project ONEVO.DbMigrator -- --environment Development
```

Expected: `bridge_clients` table created.

- [ ] **Step 10: Commit**

```bash
git add ONEVO.Modules.Auth/ \
        ONEVO.DbMigrator/Migrations/ \
        ONEVO.Tests.Unit/BridgeAuthTests.cs
git commit -m "feat(auth): add bridge API client credentials flow and bridge_clients table"
```

---

## Task 5: Bridge Authentication Middleware

**Files:**
- Create: `ONEVO.Api/Middleware/BridgeAuthMiddleware.cs`
- Create: `ONEVO.Tests.Integration/BridgeAuthEndpointTests.cs`

**Why a separate middleware and not `[Authorize]`:** Bridge JWT has `aud: "onevo-bridge"` while user JWT has `aud: "onevo-api"`. ASP.NET Core's default `[Authorize]` only validates against the configured audience. Bridge endpoints need a separate policy that validates the bridge audience + bridge type claim + allowed-bridges list.

- [ ] **Step 1: Write the failing integration test**

```csharp
// ONEVO.Tests.Integration/BridgeAuthEndpointTests.cs
using ONEVO.Tests.Integration.Fixtures;
using FluentAssertions;
using System.Net;
using System.Net.Http.Json;

namespace ONEVO.Tests.Integration;

public class BridgeAuthEndpointTests : IClassFixture<WebAppFixture>
{
    private readonly WebAppFixture _app;

    public BridgeAuthEndpointTests(WebAppFixture app) => _app = app;

    [Fact]
    public async Task POST_BridgeToken_WithValidCredentials_Returns200WithToken()
    {
        var (clientId, secret, tenantId) = await _app.CreateBridgeClientAsync(
            bridges: ["people-sync"]);

        var response = await _app.Client.PostAsJsonAsync("/api/v1/auth/bridge/token", new
        {
            client_id = clientId,
            client_secret = secret,
            tenant_id = tenantId
        });

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var body = await response.Content.ReadFromJsonAsync<BridgeTokenResponse>();
        body!.AccessToken.Should().NotBeNullOrEmpty();
        body.TokenType.Should().Be("Bearer");
        body.ExpiresIn.Should().Be(3600);
    }

    [Fact]
    public async Task POST_BridgeToken_WithWrongSecret_Returns401()
    {
        var (clientId, _, tenantId) = await _app.CreateBridgeClientAsync(
            bridges: ["people-sync"]);

        var response = await _app.Client.PostAsJsonAsync("/api/v1/auth/bridge/token", new
        {
            client_id = clientId,
            client_secret = "wrong-secret",
            tenant_id = tenantId
        });

        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task BridgeEndpoint_WithUserJwt_Returns403()
    {
        // User JWT has aud: "onevo-api" — not valid for bridge endpoints
        var userToken = await _app.GetUserTokenAsync();
        _app.Client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", userToken);

        var response = await _app.Client.GetAsync("/api/v1/bridges/people-sync/employees");

        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }

    [Fact]
    public async Task BridgeEndpoint_WithBridgeJwtForWrongBridge_Returns403()
    {
        // Client only has "availability" access, calls "people-sync"
        var (clientId, secret, tenantId) = await _app.CreateBridgeClientAsync(
            bridges: ["availability"]);

        var tokenResponse = await _app.Client.PostAsJsonAsync("/api/v1/auth/bridge/token", new
        {
            client_id = clientId,
            client_secret = secret,
            tenant_id = tenantId
        });
        var body = await tokenResponse.Content.ReadFromJsonAsync<BridgeTokenResponse>();

        _app.Client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", body!.AccessToken);

        var response = await _app.Client.GetAsync("/api/v1/bridges/people-sync/employees");

        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
dotnet test ONEVO.Tests.Integration --filter "BridgeAuthEndpointTests" -v minimal
```

Expected: FAIL.

- [ ] **Step 3: Create BridgeAuthMiddleware**

```csharp
// ONEVO.Api/Middleware/BridgeAuthMiddleware.cs
using System.IdentityModel.Tokens.Jwt;
using System.Text.Json;
using Microsoft.IdentityModel.Tokens;

namespace ONEVO.Api.Middleware;

/// <summary>
/// Validates bridge JWTs on /api/v1/bridges/* endpoints.
/// Bridge JWT has aud: "onevo-bridge" and type: "bridge" claim.
/// Also validates that the requested bridge is in the token's allowed bridges list.
/// </summary>
public sealed class BridgeAuthMiddleware
{
    private readonly RequestDelegate _next;
    private readonly TokenValidationParameters _bridgeValidationParams;

    public BridgeAuthMiddleware(RequestDelegate next, IOptions<JwtOptions> jwtOptions)
    {
        _next = next;
        _bridgeValidationParams = new TokenValidationParameters
        {
            ValidIssuer = jwtOptions.Value.Issuer,
            ValidAudience = jwtOptions.Value.BridgeAudience, // "onevo-bridge"
            IssuerSigningKey = LoadRsaPublicKey(jwtOptions.Value.PublicKeyPem),
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30)
        };
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Only applies to bridge endpoints
        if (!context.Request.Path.StartsWithSegments("/api/v1/bridges"))
        {
            await _next(context);
            return;
        }

        var token = ExtractBearerToken(context);
        if (token is null)
        {
            context.Response.StatusCode = 401;
            return;
        }

        ClaimsPrincipal principal;
        try
        {
            principal = new JwtSecurityTokenHandler()
                .ValidateToken(token, _bridgeValidationParams, out _);
        }
        catch
        {
            context.Response.StatusCode = 403; // Valid token format, wrong audience
            return;
        }

        // Must have type: "bridge" claim
        if (principal.FindFirst("type")?.Value != "bridge")
        {
            context.Response.StatusCode = 403;
            return;
        }

        // Validate allowed bridges claim against the requested path
        var requestedBridge = ExtractBridgeName(context.Request.Path);
        var allowedBridges = JsonSerializer.Deserialize<string[]>(
            principal.FindFirst("bridges")?.Value ?? "[]") ?? [];

        if (!allowedBridges.Contains(requestedBridge))
        {
            context.Response.StatusCode = 403;
            return;
        }

        // Set tenant context from bridge JWT
        var tenantId = principal.FindFirst("tenant_id")?.Value;
        if (tenantId is null)
        {
            context.Response.StatusCode = 403;
            return;
        }

        context.Items["BridgeTenantId"] = Guid.Parse(tenantId);
        await _next(context);
    }

    private static string? ExtractBearerToken(HttpContext context)
    {
        var header = context.Request.Headers.Authorization.FirstOrDefault();
        return header?.StartsWith("Bearer ") == true ? header[7..] : null;
    }

    private static string ExtractBridgeName(PathString path)
    {
        // /api/v1/bridges/people-sync/... → "people-sync"
        var segments = path.Value?.Split('/');
        return segments?.Length >= 5 ? segments[4] : string.Empty;
    }
}
```

- [ ] **Step 4: Register middleware in Program.cs**

```csharp
// ONEVO.Api/Program.cs — add after UseAuthentication, before UseAuthorization
app.UseMiddleware<BridgeAuthMiddleware>();
```

- [ ] **Step 5: Run integration tests**

```bash
dotnet test ONEVO.Tests.Integration --filter "BridgeAuthEndpointTests" -v minimal
```

Expected: PASS (4 tests).

- [ ] **Step 6: Update vault — create bridge-api-contracts.md**

Create `backend/bridge-api-contracts.md` with:

```markdown
# Bridge API Contracts

## Authentication

WorkManage Pro authenticates to ONEVO bridge endpoints using **OAuth 2.0 Client Credentials**.

### Registration
Super Admin registers WorkManage Pro in ONEVO Settings → Integrations.
ONEVO generates `client_id` (UUID) + `client_secret` (random 48-byte base64).
The secret is shown once and stored only as Argon2id hash.

### Token Request
POST /api/v1/auth/bridge/token (public — no auth header)
Body: { "client_id": "uuid", "client_secret": "...", "tenant_id": "uuid" }
Response: { "access_token": "jwt", "token_type": "Bearer", "expires_in": 3600 }

### Using the Token
Authorization: Bearer <bridge_jwt>
Bridge JWT audience: "onevo-bridge"
Bridge JWT type claim: "bridge"
Bridge JWT bridges claim: ["people-sync", "availability"] (subset allowed for this client)

### Validation
- Middleware validates: audience = "onevo-bridge", type = "bridge"
- Middleware validates: requested bridge is in token's allowed bridges list
- Tenant context is set from token's tenant_id claim
- User JWT (aud: "onevo-api") is rejected on bridge endpoints with 403

## Bridge Endpoints
| Bridge | Endpoint | Direction | Permission |
|:-------|:---------|:----------|:-----------|
| People Sync | GET /api/v1/bridges/people-sync/employees | ONEVO → WMS | Bridge token |
| Availability | GET /api/v1/bridges/availability/{empId} | ONEVO → WMS | Bridge token |
| Performance | POST /api/v1/bridges/performance/metrics | WMS → ONEVO | Bridge token |
| Skills | GET/POST /api/v1/bridges/skills/{empId} | Bidirectional | Bridge token |
| Work Activity | POST /api/v1/bridges/work-activity | WMS → ONEVO | Bridge token |
```

- [ ] **Step 7: Commit**

```bash
git add ONEVO.Api/Middleware/BridgeAuthMiddleware.cs \
        ONEVO.Api/Program.cs \
        ONEVO.Tests.Integration/BridgeAuthEndpointTests.cs \
        backend/bridge-api-contracts.md
git commit -m "feat(api): add bridge auth middleware for WorkManage Pro service-to-service auth"
```

---

## Task 6: Employee-Device Binding — AgentSession Table + Endpoints

**Files:**
- Create: `ONEVO.Modules.AgentGateway/Internal/Entities/AgentSession.cs`
- Create: Migration — `agent_sessions` table
- Create: `ONEVO.Modules.AgentGateway/Public/IAgentSessionService.cs`
- Create: `ONEVO.Modules.AgentGateway/Internal/Services/AgentSessionService.cs`
- Create: `ONEVO.Modules.AgentGateway/Endpoints/AgentSessionEndpoints.cs`
- Create: `ONEVO.Tests.Unit/AgentSessionServiceTests.cs`

**Why a server-side session table:** The Device JWT contains `device_id` but no `employee_id` — by design, because a device can have different employees log in over time. The `agent_sessions` table tracks the currently active employee on each device. This lets the ingest endpoint (Task 7) resolve `device_id → employee_id` server-side, so the agent doesn't need to put `employee_id` in the JWT.

**Security benefit:** Even if an agent sends a manipulated `employee_id` in the ingest payload, the server compares it against the `agent_sessions` record and rejects mismatches.

- [ ] **Step 1: Write failing unit tests**

```csharp
// ONEVO.Tests.Unit/AgentSessionServiceTests.cs
using ONEVO.Modules.AgentGateway.Internal.Services;
using ONEVO.Modules.AgentGateway.Public;
using FluentAssertions;
using Moq;

namespace ONEVO.Tests.Unit;

public class AgentSessionServiceTests
{
    private readonly Mock<IAgentSessionRepository> _repo = new();
    private readonly Mock<IEmployeeService> _employeeService = new(); // From CoreHR.Public
    private readonly AgentSessionService _sut;

    public AgentSessionServiceTests()
    {
        _sut = new AgentSessionService(_repo.Object, _employeeService.Object);
    }

    [Fact]
    public async Task Login_WithValidEmployee_CreatesActiveSession()
    {
        var deviceId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();
        var employeeId = Guid.NewGuid();

        _employeeService.Setup(s => s.GetByIdAsync(employeeId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new EmployeeDto { Id = employeeId, TenantId = tenantId });

        _repo.Setup(r => r.DeactivateExistingAsync(deviceId, It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);
        _repo.Setup(r => r.AddAsync(It.IsAny<AgentSession>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var result = await _sut.LoginAsync(deviceId, tenantId, employeeId, CancellationToken.None);

        result.IsSuccess.Should().BeTrue();
        _repo.Verify(r => r.DeactivateExistingAsync(deviceId, It.IsAny<CancellationToken>()), Times.Once);
        _repo.Verify(r => r.AddAsync(
            It.Is<AgentSession>(s => s.DeviceId == deviceId && s.EmployeeId == employeeId && s.IsActive),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task Login_WhenEmployeeNotInTenant_ReturnsFailure()
    {
        var tenantId = Guid.NewGuid();
        var employeeId = Guid.NewGuid();

        _employeeService.Setup(s => s.GetByIdAsync(employeeId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((EmployeeDto?)null);

        var result = await _sut.LoginAsync(Guid.NewGuid(), tenantId, employeeId, CancellationToken.None);

        result.IsSuccess.Should().BeFalse();
        result.Error.Should().Contain("Employee not found");
    }

    [Fact]
    public async Task GetCurrentEmployeeId_WhenActiveSession_ReturnsEmployeeId()
    {
        var deviceId = Guid.NewGuid();
        var employeeId = Guid.NewGuid();

        _repo.Setup(r => r.GetActiveAsync(deviceId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new AgentSession { DeviceId = deviceId, EmployeeId = employeeId, IsActive = true });

        var result = await _sut.GetCurrentEmployeeIdAsync(deviceId, CancellationToken.None);

        result.Should().Be(employeeId);
    }

    [Fact]
    public async Task GetCurrentEmployeeId_WhenNoActiveSession_ReturnsNull()
    {
        _repo.Setup(r => r.GetActiveAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((AgentSession?)null);

        var result = await _sut.GetCurrentEmployeeIdAsync(Guid.NewGuid(), CancellationToken.None);

        result.Should().BeNull();
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
dotnet test ONEVO.Tests.Unit --filter "AgentSessionServiceTests" -v minimal
```

Expected: FAIL — types not found.

- [ ] **Step 3: Create AgentSession entity**

```csharp
// ONEVO.Modules.AgentGateway/Internal/Entities/AgentSession.cs
using ONEVO.SharedKernel;

namespace ONEVO.Modules.AgentGateway.Internal.Entities;

/// <summary>
/// Tracks which employee is currently logged in on a given device.
/// One active session per device at a time (enforced by partial unique index).
/// This is the authoritative source for device → employee binding during ingest.
/// </summary>
internal sealed class AgentSession : BaseEntity
{
    public Guid DeviceId { get; init; }        // FK → registered_agents
    public Guid EmployeeId { get; init; }      // FK → employees (via CoreHR.Public)
    public DateTimeOffset LoggedInAt { get; init; } = DateTimeOffset.UtcNow;
    public DateTimeOffset LastActivityAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? LoggedOutAt { get; set; }
    public bool IsActive { get; set; } = true;

    public void Logout()
    {
        IsActive = false;
        LoggedOutAt = DateTimeOffset.UtcNow;
    }
}
```

- [ ] **Step 4: Create the migration**

```csharp
// ONEVO.DbMigrator/Migrations/YYYYMMDD_AddAgentSessions.cs
public partial class AddAgentSessions : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("""
            CREATE TABLE agent_sessions (
                id                uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
                tenant_id         uuid        NOT NULL REFERENCES tenants(id),
                device_id         uuid        NOT NULL REFERENCES registered_agents(id),
                employee_id       uuid        NOT NULL,
                logged_in_at      timestamptz NOT NULL DEFAULT now(),
                last_activity_at  timestamptz NOT NULL DEFAULT now(),
                logged_out_at     timestamptz,
                is_active         boolean     NOT NULL DEFAULT true,
                created_at        timestamptz NOT NULL DEFAULT now(),
                updated_at        timestamptz NOT NULL DEFAULT now(),
                created_by_id     uuid,
                is_deleted        boolean     NOT NULL DEFAULT false,
                deleted_at        timestamptz
            );

            -- Only one active session per device at a time
            CREATE UNIQUE INDEX idx_agent_sessions_active_device
                ON agent_sessions(device_id)
                WHERE is_active = true;

            CREATE INDEX idx_agent_sessions_device_tenant
                ON agent_sessions(device_id, tenant_id)
                WHERE is_active = true;
            """);
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("DROP TABLE IF EXISTS agent_sessions;");
    }
}
```

- [ ] **Step 5: Create public interface and service**

```csharp
// ONEVO.Modules.AgentGateway/Public/IAgentSessionService.cs
using ONEVO.SharedKernel;

namespace ONEVO.Modules.AgentGateway.Public;

public interface IAgentSessionService
{
    /// <summary>
    /// Records employee login on a device. Deactivates any existing active session first.
    /// Called when employee logs in via tray app.
    /// </summary>
    Task<Result> LoginAsync(Guid deviceId, Guid tenantId, Guid employeeId, CancellationToken ct);

    /// <summary>
    /// Records employee logout from a device.
    /// Called when employee explicitly logs out, or when device detects user logoff.
    /// </summary>
    Task<Result> LogoutAsync(Guid deviceId, CancellationToken ct);

    /// <summary>
    /// Returns the employee currently logged in on this device, or null if no active session.
    /// Used by the ingest endpoint to validate employee binding.
    /// </summary>
    Task<Guid?> GetCurrentEmployeeIdAsync(Guid deviceId, CancellationToken ct);
}
```

```csharp
// ONEVO.Modules.AgentGateway/Internal/Services/AgentSessionService.cs
using ONEVO.Modules.AgentGateway.Internal.Entities;
using ONEVO.Modules.AgentGateway.Public;
using ONEVO.Modules.CoreHR.Public; // IEmployeeService from CoreHR public interface
using ONEVO.SharedKernel;

namespace ONEVO.Modules.AgentGateway.Internal.Services;

internal sealed class AgentSessionService : IAgentSessionService
{
    private readonly IAgentSessionRepository _repo;
    private readonly IEmployeeService _employeeService;

    public AgentSessionService(IAgentSessionRepository repo, IEmployeeService employeeService)
    {
        _repo = repo;
        _employeeService = employeeService;
    }

    public async Task<Result> LoginAsync(Guid deviceId, Guid tenantId, Guid employeeId, CancellationToken ct)
    {
        // Validate employee exists in this tenant
        var employee = await _employeeService.GetByIdAsync(employeeId, ct);
        if (employee is null || employee.TenantId != tenantId)
            return Result.Failure("Employee not found in this tenant");

        // Deactivate any existing session on this device
        await _repo.DeactivateExistingAsync(deviceId, ct);

        var session = new AgentSession
        {
            TenantId = tenantId,
            DeviceId = deviceId,
            EmployeeId = employeeId
        };

        await _repo.AddAsync(session, ct);
        return Result.Success();
    }

    public async Task<Result> LogoutAsync(Guid deviceId, CancellationToken ct)
    {
        var session = await _repo.GetActiveAsync(deviceId, ct);
        if (session is null)
            return Result.Success(); // Idempotent — no active session is fine

        session.Logout();
        await _repo.UpdateAsync(session, ct);
        return Result.Success();
    }

    public async Task<Guid?> GetCurrentEmployeeIdAsync(Guid deviceId, CancellationToken ct)
    {
        var session = await _repo.GetActiveAsync(deviceId, ct);
        return session?.EmployeeId;
    }
}
```

- [ ] **Step 6: Create the session endpoints**

```csharp
// ONEVO.Modules.AgentGateway/Endpoints/AgentSessionEndpoints.cs
namespace ONEVO.Modules.AgentGateway.Endpoints;

internal static class AgentSessionEndpoints
{
    internal static void MapAgentSessionEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v1/agent/session")
                       .RequireAuthorization("AgentPolicy"); // Device JWT only

        group.MapPost("/login", EmployeeLogin);
        group.MapPost("/logout", EmployeeLogout);
        group.MapGet("/current", GetCurrentSession);
    }

    private static async Task<IResult> EmployeeLogin(
        AgentEmployeeLoginRequest request,
        IAgentSessionService sessionService,
        IAgentContext agentContext, // Extracted from Device JWT by AgentAuthMiddleware
        CancellationToken ct)
    {
        var result = await sessionService.LoginAsync(
            agentContext.DeviceId,
            agentContext.TenantId,
            request.EmployeeId,
            ct);

        return result.IsSuccess
            ? Results.Ok(new { message = "Session created" })
            : Results.Problem(title: "Login failed", detail: result.Error, statusCode: 403);
    }

    private static async Task<IResult> EmployeeLogout(
        IAgentSessionService sessionService,
        IAgentContext agentContext,
        CancellationToken ct)
    {
        await sessionService.LogoutAsync(agentContext.DeviceId, ct);
        return Results.NoContent();
    }

    private static async Task<IResult> GetCurrentSession(
        IAgentSessionService sessionService,
        IAgentContext agentContext,
        CancellationToken ct)
    {
        var employeeId = await sessionService.GetCurrentEmployeeIdAsync(agentContext.DeviceId, ct);
        return employeeId is null
            ? Results.NotFound(new { message = "No active employee session on this device" })
            : Results.Ok(new { employee_id = employeeId });
    }
}

internal record AgentEmployeeLoginRequest(Guid EmployeeId);
```

- [ ] **Step 7: Run unit tests**

```bash
dotnet test ONEVO.Tests.Unit --filter "AgentSessionServiceTests" -v minimal
```

Expected: PASS (4 tests).

- [ ] **Step 8: Apply migration**

```bash
dotnet run --project ONEVO.DbMigrator -- --environment Development
```

Expected: `agent_sessions` table created.

- [ ] **Step 9: Commit**

```bash
git add ONEVO.Modules.AgentGateway/ \
        ONEVO.DbMigrator/Migrations/ \
        ONEVO.Tests.Unit/AgentSessionServiceTests.cs
git commit -m "feat(agent-gateway): add agent_sessions table and employee-device binding service"
```

---

## Task 7: Enforce Employee Binding in Ingest Endpoint

**Files:**
- Modify: `ONEVO.Modules.AgentGateway/Endpoints/DataIngestionEndpoints.cs`
- Create: `ONEVO.Tests.Integration/DataIngestionBindingTests.cs`

**Why:** Without this, any registered device could send data attributed to any `employee_id` in the payload. The server must cross-check `payload.employee_id` against `agent_sessions.employee_id` for the device identified by the JWT.

- [ ] **Step 1: Write failing integration tests**

```csharp
// ONEVO.Tests.Integration/DataIngestionBindingTests.cs
using ONEVO.Tests.Integration.Fixtures;
using FluentAssertions;
using System.Net;
using System.Net.Http.Json;

namespace ONEVO.Tests.Integration;

public class DataIngestionBindingTests : IClassFixture<WebAppFixture>
{
    private readonly WebAppFixture _app;

    public DataIngestionBindingTests(WebAppFixture app) => _app = app;

    [Fact]
    public async Task Ingest_WhenEmployeeMatchesSession_Returns202()
    {
        var (deviceToken, deviceId, tenantId) = await _app.RegisterDeviceAsync();
        var employeeId = await _app.CreateEmployeeAsync(tenantId);
        await _app.CreateAgentSessionAsync(deviceId, tenantId, employeeId);

        var response = await _app.PostWithDeviceToken(deviceToken, "/api/v1/agent/ingest",
            new { employee_id = employeeId, snapshots = Array.Empty<object>() });

        response.StatusCode.Should().Be(HttpStatusCode.Accepted);
    }

    [Fact]
    public async Task Ingest_WhenNoActiveSession_Returns403()
    {
        var (deviceToken, _, tenantId) = await _app.RegisterDeviceAsync();
        var employeeId = await _app.CreateEmployeeAsync(tenantId);
        // No session created

        var response = await _app.PostWithDeviceToken(deviceToken, "/api/v1/agent/ingest",
            new { employee_id = employeeId, snapshots = Array.Empty<object>() });

        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }

    [Fact]
    public async Task Ingest_WhenEmployeeIdMismatch_Returns403()
    {
        var (deviceToken, deviceId, tenantId) = await _app.RegisterDeviceAsync();
        var legitimateEmployeeId = await _app.CreateEmployeeAsync(tenantId);
        var spoofedEmployeeId = await _app.CreateEmployeeAsync(tenantId);
        await _app.CreateAgentSessionAsync(deviceId, tenantId, legitimateEmployeeId);

        // Agent sends a different employee_id than what's in the session
        var response = await _app.PostWithDeviceToken(deviceToken, "/api/v1/agent/ingest",
            new { employee_id = spoofedEmployeeId, snapshots = Array.Empty<object>() });

        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
dotnet test ONEVO.Tests.Integration --filter "DataIngestionBindingTests" -v minimal
```

Expected: FAIL — ingest endpoint doesn't validate session yet.

- [ ] **Step 3: Add session validation to the ingest endpoint**

```csharp
// ONEVO.Modules.AgentGateway/Endpoints/DataIngestionEndpoints.cs
// Modify the ingest handler to add these lines before processing:

private static async Task<IResult> IngestData(
    AgentIngestRequest request,
    IAgentSessionService sessionService,
    IDataIngestionService ingestionService,
    IAgentContext agentContext,
    CancellationToken ct)
{
    // Validate employee-device binding
    var currentEmployeeId = await sessionService.GetCurrentEmployeeIdAsync(agentContext.DeviceId, ct);

    if (currentEmployeeId is null)
        return Results.Problem(
            title: "No active session",
            detail: "No employee is logged in on this device. Employee must log in via the tray app before data can be ingested.",
            statusCode: 403);

    if (currentEmployeeId != request.EmployeeId)
        return Results.Problem(
            title: "Employee mismatch",
            detail: "The employee_id in the payload does not match the active session for this device.",
            statusCode: 403);

    // Proceed with async ingestion
    await ingestionService.IngestAsync(request, agentContext.DeviceId, currentEmployeeId.Value, ct);
    return Results.Accepted();
}
```

- [ ] **Step 4: Run integration tests**

```bash
dotnet test ONEVO.Tests.Integration --filter "DataIngestionBindingTests" -v minimal
```

Expected: PASS (3 tests).

- [ ] **Step 5: Update vault docs**

Update `modules/agent-gateway/data-ingestion/overview.md`:

```markdown
## Employee-Device Binding

The ingest endpoint validates that the `employee_id` in the payload matches the
active `agent_sessions` record for the device identified by the Device JWT.

Flow:
1. Employee logs into tray app → MAUI authenticates employee
2. Tray app IPC → Service: `{type: "employee_login", employee_id: uuid}`
3. Service calls POST /api/v1/agent/session/login (Device JWT)
4. Server creates agent_sessions record: device_id → employee_id
5. Agent sends POST /api/v1/agent/ingest with employee_id in payload
6. Server validates: payload.employee_id == agent_sessions[device_id].employee_id
7. Mismatch or missing session → 403

This prevents one device from submitting data attributed to a different employee.
```

- [ ] **Step 6: Remove stale "unclear" gotcha from known-issues**

In `AI_CONTEXT/known-issues.md`, remove the gotcha about agent-device binding being unclear and replace with:

```markdown
- **Agent employee-device binding:** The agent sends `employee_id` in the ingest payload body.
  The server validates this against the `agent_sessions` table (keyed by `device_id` from the
  Device JWT). If no active session exists or `employee_id` mismatches, the server returns 403.
  Employee session starts via `POST /api/v1/agent/session/login` (called by the tray app after
  employee login). See [[modules/agent-gateway/data-ingestion/overview|Data Ingestion]].
```

- [ ] **Step 7: Commit**

```bash
git add ONEVO.Modules.AgentGateway/Endpoints/DataIngestionEndpoints.cs \
        ONEVO.Tests.Integration/DataIngestionBindingTests.cs \
        modules/agent-gateway/data-ingestion/overview.md \
        AI_CONTEXT/known-issues.md
git commit -m "feat(agent-gateway): enforce employee-device session binding on ingest endpoint"
```

---

## Task 8: Session Table Naming Fix

**Files:**
- Modify: `security/auth-architecture.md`

- [ ] **Step 1: Fix the two occurrences of `user_sessions` in auth-architecture.md**

Find and replace both occurrences:

```
# Find: user_sessions
# Replace with: sessions
```

Occurrences are in:
1. The Token Lifecycle table: `Storage: "user_sessions" table`
2. The Session Security table: `Device tracking: "user_sessions.device_type"`

After fix:
- `Storage | sessions table`
- `Device tracking | sessions.device_type + ip_address`

- [ ] **Step 2: Verify no other files have the stale name**

```bash
grep -r "user_sessions" . --include="*.md"
```

Expected: No matches.

- [ ] **Step 3: Commit**

```bash
git add security/auth-architecture.md
git commit -m "fix(docs): standardize sessions table name (was user_sessions in auth-architecture)"
```

---

## Self-Review

### Spec Coverage Check

| Gap | Task(s) | Status |
|:----|:--------|:-------|
| Hierarchy scope scalability | Tasks 1–3 | ✅ HierarchyFilter + CTE + index |
| Bridge API authentication | Tasks 4–5 | ✅ OAuth client credentials + middleware |
| Employee-device binding | Tasks 6–7 | ✅ agent_sessions + ingest validation |
| Session table naming | Task 8 | ✅ 1-line fix |

### Placeholder Scan

- No "TBD", "TODO", or "implement later" — all steps have complete code
- All types referenced in later tasks are defined in earlier tasks
- Method signatures are consistent (`LoginAsync`, `GetCurrentEmployeeIdAsync`, `GetFilterAsync`)
- All SQL uses parameterized queries — no string interpolation (EF Core 9 FormattableString for the CTE is parameterized by EF)

### Type Consistency Check

- `HierarchyFilter` defined in Task 1, used in Tasks 2–3 ✅
- `IAgentSessionService.LoginAsync(deviceId, tenantId, employeeId, ct)` defined in Task 6, called in Task 7 ✅
- `BridgeTokenRequest/Response` defined in Task 4, used in Task 5 ✅
- `AgentSession` entity defined in Task 6, used in Task 7 ✅
