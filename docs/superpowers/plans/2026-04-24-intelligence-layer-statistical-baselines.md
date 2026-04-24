# Intelligence Layer — Statistical Baselines + AI Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace flat absolute thresholds in the Discrepancy Engine and Exception Engine with per-employee statistical baselines (rolling 30-day avg + σ), and add a lightweight AI narrative enrichment layer on critical discrepancy alerts only.

**Architecture:** Each engine gains a daily baseline computation job that pre-computes per-employee rolling statistics into dedicated tables. The severity/exception evaluation then uses z-score-relative thresholds when sufficient baseline data exists, falling back to absolute thresholds for new employees. AI enrichment fires as an event handler on `DiscrepancyCriticalDetected` only — never in the core evaluation loop.

**Tech Stack:** .NET 9 / C# 13, Entity Framework Core 9, Hangfire 1.8.x, PostgreSQL 16, xUnit + Moq + FluentAssertions, Anthropic.SDK (NuGet), MediatR

---

> **Phase independence:** Phase 1, Phase 2, and Phase 3 can each be shipped independently. Phases 1 and 2 have no dependency on each other. Phase 3 depends only on the `DiscrepancyCriticalDetected` event that already exists in Phase 1.

---

## File Map

### Phase 1 — Discrepancy Engine: Statistical Baselines

**This repo (docs to create/update):**
- Create: `modules/discrepancy-engine/statistical-baselines/overview.md`
- Modify: `modules/discrepancy-engine/overview.md`
- Modify: `database/schemas/discrepancy-engine.md`

**Backend files to create:**
- `src/Modules/DiscrepancyEngine/Domain/EmployeeDiscrepancyBaseline.cs`
- `src/Modules/DiscrepancyEngine/Features/Baselines/IDiscrepancyBaselineRepository.cs`
- `src/Modules/DiscrepancyEngine/Features/Baselines/DiscrepancyBaselineRepository.cs`
- `src/Modules/DiscrepancyEngine/Features/Baselines/BaselineComputationService.cs`
- `src/Modules/DiscrepancyEngine/Jobs/ComputeDiscrepancyBaselinesJob.cs`
- `src/Infrastructure/Migrations/YYYYMMDD_AddDiscrepancyBaselines.cs`
- `tests/Modules/DiscrepancyEngine.Tests/Baselines/BaselineComputationServiceTests.cs`
- `tests/Modules/DiscrepancyEngine.Tests/Jobs/DiscrepancyEngineJobBaselineTests.cs`

**Backend files to modify:**
- `src/Modules/DiscrepancyEngine/Domain/DiscrepancyEvent.cs` — add `ZScore`, `BaselineAvgMinutes`, `BaselineStddevMinutes`, `SeverityMethod`
- `src/Modules/DiscrepancyEngine/Jobs/DiscrepancyEngineJob.cs` — inject baseline, pass to severity calc
- `src/Modules/DiscrepancyEngine/Infrastructure/DiscrepancyEngineDbContext.cs` — add `EmployeeDiscrepancyBaselines` DbSet
- `src/Infrastructure/Startup/HangfireJobRegistration.cs` — register `ComputeDiscrepancyBaselinesJob`

### Phase 2 — Exception Engine: Baseline-Relative Thresholds

**This repo (docs to create/update):**
- Create: `modules/exception-engine/activity-baselines/overview.md`
- Modify: `modules/exception-engine/overview.md`

**Backend files to create:**
- `src/Modules/ExceptionEngine/Domain/EmployeeActivityBaseline.cs`
- `src/Modules/ExceptionEngine/Features/Baselines/IActivityBaselineRepository.cs`
- `src/Modules/ExceptionEngine/Features/Baselines/ActivityBaselineRepository.cs` — follows exact same SQL aggregate pattern as `DiscrepancyBaselineRepository` (Task 1.3), parameterized by `metric` column on `activity_daily_summary`
- `src/Modules/ExceptionEngine/Features/Baselines/ComputeActivityBaselinesJob.cs`
- `src/Modules/ExceptionEngine/Features/Evaluation/BaselineRuleEvaluator.cs`
- `src/Infrastructure/Migrations/YYYYMMDD_AddActivityBaselines.cs`
- `tests/Modules/ExceptionEngine.Tests/Baselines/ActivityBaselineRepositoryTests.cs`
- `tests/Modules/ExceptionEngine.Tests/Evaluation/BaselineRuleEvaluatorTests.cs`

**Backend files to modify:**
- `src/Modules/ExceptionEngine/Domain/RuleCondition.cs` — add `BaselineRelative` operator fields
- `src/Modules/ExceptionEngine/Features/Evaluation/RuleEvaluationService.cs` — inject `BaselineRuleEvaluator`
- `src/Modules/ExceptionEngine/Infrastructure/ExceptionEngineDbContext.cs` — add `EmployeeActivityBaselines` DbSet
- `src/Infrastructure/Startup/HangfireJobRegistration.cs` — register `ComputeActivityBaselinesJob`

### Phase 3 — AI Notification Enrichment

**This repo (docs to create):**
- Create: `modules/discrepancy-engine/notification-enrichment/overview.md`

**Backend files to create:**
- `src/Modules/DiscrepancyEngine/Features/Enrichment/IDiscrepancyEnrichmentService.cs`
- `src/Modules/DiscrepancyEngine/Features/Enrichment/IAnthropicInsightProvider.cs` — thin wrapper interface over `AnthropicClient` for testability
- `src/Modules/DiscrepancyEngine/Features/Enrichment/AnthropicInsightProvider.cs` — real implementation wrapping `AnthropicClient`
- `src/Modules/DiscrepancyEngine/Features/Enrichment/DiscrepancyEnrichmentService.cs` — depends on `IAnthropicInsightProvider`, not `AnthropicClient` directly
- `src/Modules/DiscrepancyEngine/Features/Enrichment/DiscrepancyEnrichmentHandler.cs`
- `tests/Modules/DiscrepancyEngine.Tests/Enrichment/DiscrepancyEnrichmentServiceTests.cs`

**Backend files to modify:**
- `src/Modules/Notifications/Domain/NotificationType.cs` — add `DiscrepancyAlertEnriched`
- `src/Infrastructure/Startup/ServiceRegistration.cs` — register enrichment service + handler, add `Anthropic.SDK`

---

## Phase 1: Discrepancy Engine — Statistical Baselines

### Task 1.1: Database Schema — Add `employee_discrepancy_baselines` table + new columns on `discrepancy_events`

**Files:**
- Modify: `database/schemas/discrepancy-engine.md`
- Create: `src/Infrastructure/Migrations/YYYYMMDD_AddDiscrepancyBaselines.cs`

- [ ] **Step 1: Update the schema doc**

Open `database/schemas/discrepancy-engine.md` and add a third table block after `wms_daily_time_logs`:

```markdown
## `employee_discrepancy_baselines`

Rolling per-employee statistical baseline for discrepancy severity calculation. Computed daily by `ComputeDiscrepancyBaselinesJob`. Requires minimum 5 samples before being used — new employees fall back to absolute thresholds automatically.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `computed_at` | `date` | The date this baseline was computed for |
| `window_days` | `int` | Rolling window (default 30) |
| `avg_unaccounted_minutes` | `decimal(8,2)` | Rolling average of unaccounted gap |
| `stddev_unaccounted_minutes` | `decimal(8,2)` | Rolling stddev of unaccounted gap |
| `sample_count` | `int` | Days with data in the window (< 5 → not used) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Index:** `(tenant_id, employee_id, computed_at)` UNIQUE
**Retention:** 90 days (small table, pruned by `CleanupOldBaselinesJob`)
```

Also append these columns to the `discrepancy_events` table block:

```markdown
| `z_score` | `decimal(8,2)` | Nullable. How many stddevs above baseline. Set when baseline data is available. |
| `baseline_avg_minutes` | `decimal(8,2)` | Nullable. Employee's 30-day avg at time of computation. |
| `baseline_stddev_minutes` | `decimal(8,2)` | Nullable. Employee's 30-day stddev at time of computation. |
| `severity_method` | `varchar(20)` | `absolute` (new employee, < 5 samples) or `baseline_relative` |
```

- [ ] **Step 2: Write the EF Core migration**

Create `src/Infrastructure/Migrations/YYYYMMDD_AddDiscrepancyBaselines.cs`:

```csharp
using Microsoft.EntityFrameworkCore.Migrations;

public partial class AddDiscrepancyBaselines : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.CreateTable(
            name: "employee_discrepancy_baselines",
            columns: table => new
            {
                id = table.Column<Guid>(nullable: false, defaultValueSql: "gen_random_uuid()"),
                tenant_id = table.Column<Guid>(nullable: false),
                employee_id = table.Column<Guid>(nullable: false),
                computed_at = table.Column<DateOnly>(nullable: false),
                window_days = table.Column<int>(nullable: false, defaultValue: 30),
                avg_unaccounted_minutes = table.Column<decimal>(precision: 8, scale: 2, nullable: false),
                stddev_unaccounted_minutes = table.Column<decimal>(precision: 8, scale: 2, nullable: false),
                sample_count = table.Column<int>(nullable: false),
                created_at = table.Column<DateTimeOffset>(nullable: false, defaultValueSql: "NOW()"),
                updated_at = table.Column<DateTimeOffset>(nullable: false, defaultValueSql: "NOW()")
            },
            constraints: table =>
            {
                table.PrimaryKey("PK_employee_discrepancy_baselines", x => x.id);
                table.ForeignKey("FK_discrepancy_baselines_tenants", x => x.tenant_id, "tenants", "id");
                table.ForeignKey("FK_discrepancy_baselines_employees", x => x.employee_id, "employees", "id");
            });

        migrationBuilder.CreateIndex(
            name: "IX_employee_discrepancy_baselines_unique",
            table: "employee_discrepancy_baselines",
            columns: new[] { "tenant_id", "employee_id", "computed_at" },
            unique: true);

        // Add columns to discrepancy_events
        migrationBuilder.AddColumn<decimal>(
            name: "z_score", table: "discrepancy_events",
            precision: 8, scale: 2, nullable: true);
        migrationBuilder.AddColumn<decimal>(
            name: "baseline_avg_minutes", table: "discrepancy_events",
            precision: 8, scale: 2, nullable: true);
        migrationBuilder.AddColumn<decimal>(
            name: "baseline_stddev_minutes", table: "discrepancy_events",
            precision: 8, scale: 2, nullable: true);
        migrationBuilder.AddColumn<string>(
            name: "severity_method", table: "discrepancy_events",
            maxLength: 20, nullable: false, defaultValue: "absolute");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable(name: "employee_discrepancy_baselines");
        migrationBuilder.DropColumn(name: "z_score", table: "discrepancy_events");
        migrationBuilder.DropColumn(name: "baseline_avg_minutes", table: "discrepancy_events");
        migrationBuilder.DropColumn(name: "baseline_stddev_minutes", table: "discrepancy_events");
        migrationBuilder.DropColumn(name: "severity_method", table: "discrepancy_events");
    }
}
```

- [ ] **Step 3: Run migration to verify it applies cleanly**

```bash
dotnet ef database update --project src/ONEVO.Infrastructure --startup-project src/ONEVO.Api
```

Expected: `Done.` with no errors.

- [ ] **Step 4: Commit**

```bash
git add database/schemas/discrepancy-engine.md
git add src/Infrastructure/Migrations/YYYYMMDD_AddDiscrepancyBaselines.cs
git commit -m "feat(discrepancy): add employee_discrepancy_baselines schema and migration"
```

---

### Task 1.2: Domain Entity — `EmployeeDiscrepancyBaseline`

**Files:**
- Create: `src/Modules/DiscrepancyEngine/Domain/EmployeeDiscrepancyBaseline.cs`
- Modify: `src/Modules/DiscrepancyEngine/Domain/DiscrepancyEvent.cs`
- Modify: `src/Modules/DiscrepancyEngine/Infrastructure/DiscrepancyEngineDbContext.cs`

- [ ] **Step 1: Write the failing test**

Create `tests/Modules/DiscrepancyEngine.Tests/Baselines/BaselineComputationServiceTests.cs`:

```csharp
using FluentAssertions;
using ONEVO.Modules.DiscrepancyEngine.Domain;
using Xunit;

namespace ONEVO.Modules.DiscrepancyEngine.Tests.Baselines;

public class EmployeeDiscrepancyBaselineTests
{
    [Fact]
    public void IsUsable_ReturnsFalse_WhenSampleCountBelowMinimum()
    {
        var baseline = new EmployeeDiscrepancyBaseline
        {
            SampleCount = 4,
            StddevUnaccountedMinutes = 15m
        };

        baseline.IsUsable().Should().BeFalse();
    }

    [Fact]
    public void IsUsable_ReturnsFalse_WhenStddevIsZero()
    {
        var baseline = new EmployeeDiscrepancyBaseline
        {
            SampleCount = 10,
            StddevUnaccountedMinutes = 0m
        };

        baseline.IsUsable().Should().BeFalse();
    }

    [Fact]
    public void IsUsable_ReturnsTrue_WhenSufficientSamplesAndNonZeroStddev()
    {
        var baseline = new EmployeeDiscrepancyBaseline
        {
            SampleCount = 5,
            StddevUnaccountedMinutes = 12.5m
        };

        baseline.IsUsable().Should().BeTrue();
    }

    [Theory]
    [InlineData(60, 30, 15, 2.0)]    // (60-30)/15 = 2.0
    [InlineData(30, 30, 15, 0.0)]    // exactly at mean
    [InlineData(0, 30, 15, -2.0)]    // below mean
    public void ComputeZScore_ReturnsCorrectValue(
        decimal unaccounted, decimal avg, decimal stddev, double expectedZ)
    {
        var baseline = new EmployeeDiscrepancyBaseline
        {
            AvgUnaccountedMinutes = avg,
            StddevUnaccountedMinutes = stddev,
            SampleCount = 10
        };

        var zScore = baseline.ComputeZScore(unaccounted);

        zScore.Should().BeApproximately((decimal)expectedZ, 0.01m);
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "EmployeeDiscrepancyBaselineTests" -v
```

Expected: FAIL — `EmployeeDiscrepancyBaseline` type not found.

- [ ] **Step 3: Create the domain entity**

Create `src/Modules/DiscrepancyEngine/Domain/EmployeeDiscrepancyBaseline.cs`:

```csharp
namespace ONEVO.Modules.DiscrepancyEngine.Domain;

public class EmployeeDiscrepancyBaseline
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public Guid TenantId { get; init; }
    public Guid EmployeeId { get; init; }
    public DateOnly ComputedAt { get; init; }
    public int WindowDays { get; init; } = 30;
    public decimal AvgUnaccountedMinutes { get; init; }
    public decimal StddevUnaccountedMinutes { get; init; }
    public int SampleCount { get; init; }
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;

    // Minimum 5 samples AND non-zero stddev required for statistical validity
    public bool IsUsable() => SampleCount >= 5 && StddevUnaccountedMinutes > 0;

    public decimal ComputeZScore(decimal unaccountedMinutes) =>
        (unaccountedMinutes - AvgUnaccountedMinutes) / StddevUnaccountedMinutes;
}
```

- [ ] **Step 4: Add new fields to `DiscrepancyEvent`**

Open `src/Modules/DiscrepancyEngine/Domain/DiscrepancyEvent.cs` and add:

```csharp
// Add after existing Severity property:
public decimal? ZScore { get; set; }
public decimal? BaselineAvgMinutes { get; set; }
public decimal? BaselineStddevMinutes { get; set; }
public string SeverityMethod { get; set; } = "absolute"; // "absolute" | "baseline_relative"
```

- [ ] **Step 5: Register in DbContext**

Open `src/Modules/DiscrepancyEngine/Infrastructure/DiscrepancyEngineDbContext.cs` and add:

```csharp
public DbSet<EmployeeDiscrepancyBaseline> EmployeeDiscrepancyBaselines => Set<EmployeeDiscrepancyBaseline>();
```

And add EF configuration (in `OnModelCreating` or a separate `IEntityTypeConfiguration`):

```csharp
builder.Entity<EmployeeDiscrepancyBaseline>(e =>
{
    e.ToTable("employee_discrepancy_baselines");
    e.HasKey(x => x.Id);
    e.Property(x => x.Id).HasColumnName("id");
    e.Property(x => x.TenantId).HasColumnName("tenant_id").IsRequired();
    e.Property(x => x.EmployeeId).HasColumnName("employee_id").IsRequired();
    e.Property(x => x.ComputedAt).HasColumnName("computed_at").IsRequired();
    e.Property(x => x.WindowDays).HasColumnName("window_days").HasDefaultValue(30);
    e.Property(x => x.AvgUnaccountedMinutes).HasColumnName("avg_unaccounted_minutes")
        .HasPrecision(8, 2).IsRequired();
    e.Property(x => x.StddevUnaccountedMinutes).HasColumnName("stddev_unaccounted_minutes")
        .HasPrecision(8, 2).IsRequired();
    e.Property(x => x.SampleCount).HasColumnName("sample_count").IsRequired();
    e.Property(x => x.CreatedAt).HasColumnName("created_at");
    e.Property(x => x.UpdatedAt).HasColumnName("updated_at");
    e.HasIndex(x => new { x.TenantId, x.EmployeeId, x.ComputedAt }).IsUnique();
});
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "EmployeeDiscrepancyBaselineTests" -v
```

Expected: All 5 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add src/Modules/DiscrepancyEngine/Domain/EmployeeDiscrepancyBaseline.cs
git add src/Modules/DiscrepancyEngine/Domain/DiscrepancyEvent.cs
git add src/Modules/DiscrepancyEngine/Infrastructure/DiscrepancyEngineDbContext.cs
git add tests/Modules/DiscrepancyEngine.Tests/Baselines/BaselineComputationServiceTests.cs
git commit -m "feat(discrepancy): add EmployeeDiscrepancyBaseline entity and domain logic"
```

---

### Task 1.3: Repository — `IDiscrepancyBaselineRepository` + `DiscrepancyBaselineRepository`

**Files:**
- Create: `src/Modules/DiscrepancyEngine/Features/Baselines/IDiscrepancyBaselineRepository.cs`
- Create: `src/Modules/DiscrepancyEngine/Features/Baselines/DiscrepancyBaselineRepository.cs`

- [ ] **Step 1: Write the failing tests**

Add to `tests/Modules/DiscrepancyEngine.Tests/Baselines/BaselineComputationServiceTests.cs`:

```csharp
// Integration test — requires a test database
public class DiscrepancyBaselineRepositoryTests : IAsyncLifetime
{
    private readonly DiscrepancyEngineDbContext _db;

    public DiscrepancyBaselineRepositoryTests()
    {
        // Use test DB configured via appsettings.Test.json or TestContainers
        var options = new DbContextOptionsBuilder<DiscrepancyEngineDbContext>()
            .UseNpgsql(TestConfig.ConnectionString)
            .Options;
        _db = new DiscrepancyEngineDbContext(options);
    }

    [Fact]
    public async Task ComputeRawBaselinesAsync_ReturnsCorrectStats()
    {
        var tenantId = Guid.NewGuid();
        var employeeId = Guid.NewGuid();
        var today = DateOnly.FromDateTime(DateTime.UtcNow);

        // Seed 10 discrepancy events with known unaccounted_minutes
        await SeedDiscrepancyEvents(tenantId, employeeId, today,
            unaccountedValues: new[] { 30, 45, 60, 15, 90, 20, 55, 70, 40, 35 });

        var repo = new DiscrepancyBaselineRepository(_db);
        var results = await repo.ComputeRawBaselinesAsync(tenantId, today, windowDays: 30, CancellationToken.None);

        var baseline = results.Single(r => r.EmployeeId == employeeId);
        baseline.SampleCount.Should().Be(10);
        baseline.AvgUnaccountedMinutes.Should().BeApproximately(46.0m, 1m);
        baseline.IsUsable().Should().BeTrue();
    }

    [Fact]
    public async Task GetLatestBaselineAsync_ReturnsNull_WhenNoBaseline()
    {
        var repo = new DiscrepancyBaselineRepository(_db);
        var result = await repo.GetLatestBaselineAsync(Guid.NewGuid(), Guid.NewGuid(), CancellationToken.None);

        result.Should().BeNull();
    }

    public Task InitializeAsync() => _db.Database.EnsureCreatedAsync();
    public Task DisposeAsync() => _db.DisposeAsync().AsTask();

    private async Task SeedDiscrepancyEvents(Guid tenantId, Guid employeeId,
        DateOnly baseDate, int[] unaccountedValues)
    {
        for (int i = 0; i < unaccountedValues.Length; i++)
        {
            _db.DiscrepancyEvents.Add(new DiscrepancyEvent
            {
                TenantId = tenantId,
                EmployeeId = employeeId,
                Date = baseDate.AddDays(-i - 1),
                UnaccountedMinutes = unaccountedValues[i],
                HrActiveMinutes = 480,
                WmsLoggedMinutes = 480 - unaccountedValues[i],
                CalendarMinutes = 0,
                Severity = "low",
                ThresholdMinutes = 60
            });
        }
        await _db.SaveChangesAsync();
    }
}
```

- [ ] **Step 2: Run to verify fail**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "DiscrepancyBaselineRepositoryTests" -v
```

Expected: FAIL — `DiscrepancyBaselineRepository` not found.

- [ ] **Step 3: Define the interface**

Create `src/Modules/DiscrepancyEngine/Features/Baselines/IDiscrepancyBaselineRepository.cs`:

```csharp
namespace ONEVO.Modules.DiscrepancyEngine.Features.Baselines;

public interface IDiscrepancyBaselineRepository
{
    /// <summary>
    /// Runs the rolling window SQL aggregate for all employees in a tenant.
    /// Returns raw compute results — caller is responsible for upserting.
    /// </summary>
    Task<IReadOnlyList<EmployeeDiscrepancyBaseline>> ComputeRawBaselinesAsync(
        Guid tenantId, DateOnly date, int windowDays, CancellationToken ct);

    Task UpsertBatchAsync(
        IReadOnlyList<EmployeeDiscrepancyBaseline> baselines, CancellationToken ct);

    Task<EmployeeDiscrepancyBaseline?> GetLatestBaselineAsync(
        Guid tenantId, Guid employeeId, CancellationToken ct);
}
```

- [ ] **Step 4: Implement the repository**

Create `src/Modules/DiscrepancyEngine/Features/Baselines/DiscrepancyBaselineRepository.cs`:

```csharp
using Dapper; // or raw EF SQL — use whichever the project uses for raw queries
using Microsoft.EntityFrameworkCore;
using ONEVO.Modules.DiscrepancyEngine.Domain;
using ONEVO.Modules.DiscrepancyEngine.Infrastructure;

namespace ONEVO.Modules.DiscrepancyEngine.Features.Baselines;

public class DiscrepancyBaselineRepository : IDiscrepancyBaselineRepository
{
    private readonly DiscrepancyEngineDbContext _db;

    public DiscrepancyBaselineRepository(DiscrepancyEngineDbContext db) => _db = db;

    public async Task<IReadOnlyList<EmployeeDiscrepancyBaseline>> ComputeRawBaselinesAsync(
        Guid tenantId, DateOnly date, int windowDays, CancellationToken ct)
    {
        var windowStart = date.AddDays(-windowDays);

        // Use raw SQL for the aggregate — EF cannot express STDDEV easily
        var results = await _db.Database.SqlQueryRaw<BaselineRawResult>(
            """
            SELECT
                employee_id,
                AVG(unaccounted_minutes)::DECIMAL(8,2) AS avg_unaccounted_minutes,
                COALESCE(STDDEV(unaccounted_minutes), 0)::DECIMAL(8,2) AS stddev_unaccounted_minutes,
                COUNT(*)::INT AS sample_count
            FROM discrepancy_events
            WHERE tenant_id = {0}
              AND date >= {1}
              AND date < {2}
            GROUP BY employee_id
            HAVING COUNT(*) >= 1
            """,
            tenantId, windowStart, date
        ).ToListAsync(ct);

        return results.Select(r => new EmployeeDiscrepancyBaseline
        {
            TenantId = tenantId,
            EmployeeId = r.EmployeeId,
            ComputedAt = date,
            WindowDays = windowDays,
            AvgUnaccountedMinutes = r.AvgUnaccountedMinutes,
            StddevUnaccountedMinutes = r.StddevUnaccountedMinutes,
            SampleCount = r.SampleCount
        }).ToList();
    }

    public async Task UpsertBatchAsync(
        IReadOnlyList<EmployeeDiscrepancyBaseline> baselines, CancellationToken ct)
    {
        foreach (var baseline in baselines)
        {
            var existing = await _db.EmployeeDiscrepancyBaselines
                .FirstOrDefaultAsync(b =>
                    b.TenantId == baseline.TenantId &&
                    b.EmployeeId == baseline.EmployeeId &&
                    b.ComputedAt == baseline.ComputedAt, ct);

            if (existing is null)
                _db.EmployeeDiscrepancyBaselines.Add(baseline);
            else
            {
                existing = existing with
                {
                    AvgUnaccountedMinutes = baseline.AvgUnaccountedMinutes,
                    StddevUnaccountedMinutes = baseline.StddevUnaccountedMinutes,
                    SampleCount = baseline.SampleCount,
                    UpdatedAt = DateTimeOffset.UtcNow
                };
                _db.EmployeeDiscrepancyBaselines.Update(existing);
            }
        }

        await _db.SaveChangesAsync(ct);
    }

    public async Task<EmployeeDiscrepancyBaseline?> GetLatestBaselineAsync(
        Guid tenantId, Guid employeeId, CancellationToken ct) =>
        await _db.EmployeeDiscrepancyBaselines
            .Where(b => b.TenantId == tenantId && b.EmployeeId == employeeId)
            .OrderByDescending(b => b.ComputedAt)
            .FirstOrDefaultAsync(ct);

    // Internal projection type for raw SQL result
    private record BaselineRawResult(
        Guid EmployeeId,
        decimal AvgUnaccountedMinutes,
        decimal StddevUnaccountedMinutes,
        int SampleCount);
}
```

- [ ] **Step 5: Run tests**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "DiscrepancyBaselineRepositoryTests" -v
```

Expected: All 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/Modules/DiscrepancyEngine/Features/Baselines/
git add tests/Modules/DiscrepancyEngine.Tests/Baselines/
git commit -m "feat(discrepancy): add IDiscrepancyBaselineRepository with rolling SQL aggregate"
```

---

### Task 1.4: Job — `ComputeDiscrepancyBaselinesJob`

**Files:**
- Create: `src/Modules/DiscrepancyEngine/Jobs/ComputeDiscrepancyBaselinesJob.cs`
- Modify: `src/Infrastructure/Startup/HangfireJobRegistration.cs`

- [ ] **Step 1: Write failing test**

Create `tests/Modules/DiscrepancyEngine.Tests/Jobs/DiscrepancyEngineJobBaselineTests.cs`:

```csharp
using FluentAssertions;
using Moq;
using ONEVO.Modules.DiscrepancyEngine.Domain;
using ONEVO.Modules.DiscrepancyEngine.Features.Baselines;
using ONEVO.Modules.DiscrepancyEngine.Jobs;
using Xunit;

namespace ONEVO.Modules.DiscrepancyEngine.Tests.Jobs;

public class ComputeDiscrepancyBaselinesJobTests
{
    private readonly Mock<IDiscrepancyBaselineRepository> _baselineRepo = new();

    [Fact]
    public async Task RunAsync_ComputesAndUpsertsBaselinesForTenant()
    {
        var tenantId = Guid.NewGuid();
        var today = DateOnly.FromDateTime(DateTime.UtcNow);

        var computedBaselines = new List<EmployeeDiscrepancyBaseline>
        {
            new() { TenantId = tenantId, EmployeeId = Guid.NewGuid(),
                    ComputedAt = today, AvgUnaccountedMinutes = 45m,
                    StddevUnaccountedMinutes = 12m, SampleCount = 10 }
        };

        _baselineRepo
            .Setup(r => r.ComputeRawBaselinesAsync(tenantId, today, 30, It.IsAny<CancellationToken>()))
            .ReturnsAsync(computedBaselines);

        var job = new ComputeDiscrepancyBaselinesJob(_baselineRepo.Object);
        await job.RunAsync(tenantId, today, CancellationToken.None);

        _baselineRepo.Verify(r =>
            r.UpsertBatchAsync(computedBaselines, It.IsAny<CancellationToken>()),
            Times.Once);
    }

    [Fact]
    public async Task RunAsync_SkipsUpsert_WhenNoBaselineData()
    {
        var tenantId = Guid.NewGuid();
        var today = DateOnly.FromDateTime(DateTime.UtcNow);

        _baselineRepo
            .Setup(r => r.ComputeRawBaselinesAsync(tenantId, today, 30, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<EmployeeDiscrepancyBaseline>());

        var job = new ComputeDiscrepancyBaselinesJob(_baselineRepo.Object);
        await job.RunAsync(tenantId, today, CancellationToken.None);

        _baselineRepo.Verify(r =>
            r.UpsertBatchAsync(It.IsAny<IReadOnlyList<EmployeeDiscrepancyBaseline>>(),
                It.IsAny<CancellationToken>()),
            Times.Never);
    }
}
```

- [ ] **Step 2: Run to verify fail**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "ComputeDiscrepancyBaselinesJobTests" -v
```

Expected: FAIL.

- [ ] **Step 3: Implement the job**

Create `src/Modules/DiscrepancyEngine/Jobs/ComputeDiscrepancyBaselinesJob.cs`:

```csharp
using ONEVO.Modules.DiscrepancyEngine.Features.Baselines;

namespace ONEVO.Modules.DiscrepancyEngine.Jobs;

public class ComputeDiscrepancyBaselinesJob
{
    private readonly IDiscrepancyBaselineRepository _baselineRepo;

    public ComputeDiscrepancyBaselinesJob(IDiscrepancyBaselineRepository baselineRepo) =>
        _baselineRepo = baselineRepo;

    // Called by Hangfire: daily at 10:00 PM (30 min before DiscrepancyEngineJob)
    public async Task RunAsync(Guid tenantId, DateOnly date, CancellationToken ct)
    {
        var baselines = await _baselineRepo.ComputeRawBaselinesAsync(tenantId, date, windowDays: 30, ct);

        if (!baselines.Any())
            return;

        await _baselineRepo.UpsertBatchAsync(baselines, ct);
    }
}
```

- [ ] **Step 4: Register the Hangfire job**

Open `src/Infrastructure/Startup/HangfireJobRegistration.cs` and add:

```csharp
// Daily at 10:00 PM — runs BEFORE DiscrepancyEngineJob (10:30 PM)
// Per-tenant: enqueued in a loop by a master scheduler job, same pattern as DiscrepancyEngineJob
RecurringJob.AddOrUpdate<ComputeDiscrepancyBaselinesJob>(
    "compute-discrepancy-baselines",
    job => job.RunAsync(Guid.Empty, DateOnly.FromDateTime(DateTime.UtcNow), CancellationToken.None),
    "0 22 * * *",  // 10:00 PM daily
    new RecurringJobOptions { TimeZone = TimeZoneInfo.Utc, QueueName = "default" });
```

> **Note:** The master scheduler that fans out per-tenant follows the same pattern as the existing `DiscrepancyEngineJob` scheduler. Find that job, copy its fan-out logic, and use `ComputeDiscrepancyBaselinesJob` instead.

- [ ] **Step 5: Run tests**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "ComputeDiscrepancyBaselinesJobTests" -v
```

Expected: All 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/Modules/DiscrepancyEngine/Jobs/ComputeDiscrepancyBaselinesJob.cs
git add src/Infrastructure/Startup/HangfireJobRegistration.cs
git add tests/Modules/DiscrepancyEngine.Tests/Jobs/DiscrepancyEngineJobBaselineTests.cs
git commit -m "feat(discrepancy): add ComputeDiscrepancyBaselinesJob running daily at 10 PM"
```

---

### Task 1.5: Severity Calculation — Baseline-Relative Logic in `DiscrepancyEngineJob`

**Files:**
- Modify: `src/Modules/DiscrepancyEngine/Jobs/DiscrepancyEngineJob.cs`

- [ ] **Step 1: Write the failing tests**

Add to `tests/Modules/DiscrepancyEngine.Tests/Jobs/DiscrepancyEngineJobBaselineTests.cs`:

```csharp
public class DiscrepancySeverityCalculatorTests
{
    // Test the static severity calculation logic in isolation
    // by extracting it to a testable method

    [Fact]
    public void CalculateSeverity_UsesZScore_WhenBaselineIsUsable()
    {
        var baseline = new EmployeeDiscrepancyBaseline
        {
            AvgUnaccountedMinutes = 30m,
            StddevUnaccountedMinutes = 15m,
            SampleCount = 10
        };
        var threshold = new DiscrepancyThreshold { AcceptableGapMinutes = 60 };

        // zScore = (90 - 30) / 15 = 4.0 → critical
        var (severity, method) = DiscrepancySeverityCalculator.Calculate(
            unaccountedMinutes: 90, threshold, baseline);

        severity.Should().Be(DiscrepancySeverity.Critical);
        method.Should().Be("baseline_relative");
    }

    [Fact]
    public void CalculateSeverity_FallsBackToAbsolute_WhenBaselineNotUsable()
    {
        var baseline = new EmployeeDiscrepancyBaseline
        {
            SampleCount = 2,  // < 5 — not usable
            StddevUnaccountedMinutes = 15m
        };
        var threshold = new DiscrepancyThreshold { AcceptableGapMinutes = 60 };

        var (severity, method) = DiscrepancySeverityCalculator.Calculate(
            unaccountedMinutes: 45, threshold, baseline);

        severity.Should().Be(DiscrepancySeverity.Low); // 45 min → low in absolute
        method.Should().Be("absolute");
    }

    [Fact]
    public void CalculateSeverity_FallsBackToAbsolute_WhenNoBaseline()
    {
        var threshold = new DiscrepancyThreshold { AcceptableGapMinutes = 60 };

        var (severity, method) = DiscrepancySeverityCalculator.Calculate(
            unaccountedMinutes: 200, threshold, baseline: null);

        severity.Should().Be(DiscrepancySeverity.Critical); // 200 min → critical absolute
        method.Should().Be("absolute");
    }

    [Theory]
    [InlineData(0.9, "none")]     // z < 1.0
    [InlineData(1.2, "low")]      // 1.0 ≤ z < 1.5
    [InlineData(2.0, "high")]     // 1.5 ≤ z < 2.5
    [InlineData(3.0, "critical")] // z ≥ 2.5
    public void CalculateSeverity_ZScoreBrackets_AreCorrect(double zScore, string expectedSeverity)
    {
        // Set up baseline so that unaccounted = avg + zScore * stddev
        var avg = 30m;
        var stddev = 15m;
        var unaccounted = avg + (decimal)zScore * stddev;

        var baseline = new EmployeeDiscrepancyBaseline
        {
            AvgUnaccountedMinutes = avg,
            StddevUnaccountedMinutes = stddev,
            SampleCount = 10
        };
        var threshold = new DiscrepancyThreshold { AcceptableGapMinutes = 60 };

        var (severity, _) = DiscrepancySeverityCalculator.Calculate(unaccounted, threshold, baseline);

        severity.ToString().ToLower().Should().Be(expectedSeverity);
    }
}
```

- [ ] **Step 2: Run to verify fail**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "DiscrepancySeverityCalculatorTests" -v
```

Expected: FAIL — `DiscrepancySeverityCalculator` not found.

- [ ] **Step 3: Extract severity logic into a static calculator**

Create `src/Modules/DiscrepancyEngine/Features/Baselines/DiscrepancySeverityCalculator.cs`:

```csharp
using ONEVO.Modules.DiscrepancyEngine.Domain;

namespace ONEVO.Modules.DiscrepancyEngine.Features.Baselines;

public static class DiscrepancySeverityCalculator
{
    public static (DiscrepancySeverity Severity, string Method) Calculate(
        decimal unaccountedMinutes,
        DiscrepancyThreshold threshold,
        EmployeeDiscrepancyBaseline? baseline)
    {
        if (baseline is not null && baseline.IsUsable())
        {
            var zScore = baseline.ComputeZScore(unaccountedMinutes);
            var severity = zScore switch
            {
                < 1.0m => DiscrepancySeverity.None,
                >= 1.0m and < 1.5m => DiscrepancySeverity.Low,
                >= 1.5m and < 2.5m => DiscrepancySeverity.High,
                _ => DiscrepancySeverity.Critical
            };
            return (severity, "baseline_relative");
        }

        // Absolute fallback
        var absoluteSeverity = unaccountedMinutes switch
        {
            < 30 => DiscrepancySeverity.None,
            >= 30 and < 60 => DiscrepancySeverity.Low,
            >= 60 and < 180 => DiscrepancySeverity.High,
            _ => DiscrepancySeverity.Critical
        };
        return (absoluteSeverity, "absolute");
    }
}
```

- [ ] **Step 4: Wire into `DiscrepancyEngineJob.RunAsync`**

Open `src/Modules/DiscrepancyEngine/Jobs/DiscrepancyEngineJob.cs`. In the per-employee loop, after computing `unaccountedMinutes`, replace the existing `CalculateSeverity` call with:

```csharp
// Before: var severity = CalculateSeverity(unaccountedMinutes, threshold);

// After:
var baseline = await _baselineRepo.GetLatestBaselineAsync(tenantId, employee.Id, ct);
var (severity, severityMethod) = DiscrepancySeverityCalculator.Calculate(
    unaccountedMinutes, threshold, baseline);

// Then on the DiscrepancyEvent being upserted, add:
await _repository.UpsertDiscrepancyEventAsync(new DiscrepancyEvent
{
    // ... all existing fields ...
    Severity = severity.ToString().ToLower(),
    ZScore = baseline?.IsUsable() == true ? baseline.ComputeZScore(unaccountedMinutes) : null,
    BaselineAvgMinutes = baseline?.IsUsable() == true ? baseline.AvgUnaccountedMinutes : null,
    BaselineStddevMinutes = baseline?.IsUsable() == true ? baseline.StddevUnaccountedMinutes : null,
    SeverityMethod = severityMethod
}, ct);
```

Also inject `IDiscrepancyBaselineRepository` into the job's constructor.

- [ ] **Step 5: Run all Phase 1 tests**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/Modules/DiscrepancyEngine/Features/Baselines/DiscrepancySeverityCalculator.cs
git add src/Modules/DiscrepancyEngine/Jobs/DiscrepancyEngineJob.cs
git commit -m "feat(discrepancy): use z-score baseline severity with absolute fallback for new employees"
```

---

### Task 1.6: Update Module Docs

**Files:**
- Modify: `modules/discrepancy-engine/overview.md`
- Create: `modules/discrepancy-engine/statistical-baselines/overview.md`

- [ ] **Step 1: Create the statistical baselines feature doc**

Create `modules/discrepancy-engine/statistical-baselines/overview.md`:

```markdown
# Statistical Baselines

**Module:** Discrepancy Engine
**Feature:** Statistical Baselines

---

## Purpose

Pre-computes per-employee rolling 30-day statistics on `unaccounted_minutes` so the main `DiscrepancyEngineJob` can classify severity relative to that employee's personal norm rather than absolute thresholds. Reduces false positives for employees who systematically under-log (e.g., researchers, field roles) while catching genuine anomalies.

## How It Works

`ComputeDiscrepancyBaselinesJob` runs daily at 10:00 PM (30 minutes before `DiscrepancyEngineJob`). For each employee, it runs a rolling SQL aggregate over the past 30 days of `discrepancy_events`:

```sql
SELECT employee_id,
       AVG(unaccounted_minutes)::DECIMAL(8,2),
       STDDEV(unaccounted_minutes)::DECIMAL(8,2),
       COUNT(*)
FROM discrepancy_events
WHERE tenant_id = @tenantId AND date >= @windowStart AND date < @today
GROUP BY employee_id
```

Results are upserted into `employee_discrepancy_baselines`.

## Severity Calculation

`DiscrepancySeverityCalculator.Calculate()` applies:

| Condition | Method | Severity Brackets |
|:----------|:-------|:------------------|
| Baseline has ≥ 5 samples + stddev > 0 | `baseline_relative` (z-score) | z < 1.0 → none, 1.0–1.5 → low, 1.5–2.5 → high, ≥ 2.5 → critical |
| Baseline unavailable or < 5 samples | `absolute` (fallback) | < 30 min → none, 30–60 → low, 60–180 → high, ≥ 180 → critical |

## Hangfire Job

| Job | Schedule | Queue |
|:----|:---------|:------|
| `ComputeDiscrepancyBaselinesJob` | Daily 10:00 PM | Default |

## Key Rules

1. **Minimum 5 samples required** before baseline is used. New employees always use absolute thresholds.
2. **Zero stddev is treated as unusable** — prevents division-by-zero and handles employees with perfectly consistent patterns.
3. **Results are per-tenant, per-employee** — one baseline row per employee per day.
```

- [ ] **Step 2: Add feature reference to module overview**

Open `modules/discrepancy-engine/overview.md` and add to the Features section:

```markdown
- [[modules/discrepancy-engine/statistical-baselines/overview|Statistical Baselines]] — Per-employee rolling baseline computation and z-score severity classification
```

And add to Hangfire Jobs table:

```markdown
| `ComputeDiscrepancyBaselinesJob` | Daily 10:00 PM | Default | Compute rolling 30-day avg+stddev per employee |
```

- [ ] **Step 3: Commit**

```bash
git add modules/discrepancy-engine/
git commit -m "docs(discrepancy): document statistical baseline feature and update overview"
```

---

## Phase 2: Exception Engine — Baseline-Relative Thresholds

### Task 2.1: Database Schema — `employee_activity_baselines`

**Files:**
- Create: `modules/exception-engine/activity-baselines/overview.md`
- Create: `src/Infrastructure/Migrations/YYYYMMDD_AddActivityBaselines.cs`

- [ ] **Step 1: Write the migration**

Create `src/Infrastructure/Migrations/YYYYMMDD_AddActivityBaselines.cs`:

```csharp
public partial class AddActivityBaselines : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.CreateTable(
            name: "employee_activity_baselines",
            columns: table => new
            {
                id = table.Column<Guid>(nullable: false, defaultValueSql: "gen_random_uuid()"),
                tenant_id = table.Column<Guid>(nullable: false),
                employee_id = table.Column<Guid>(nullable: false),
                metric = table.Column<string>(maxLength: 50, nullable: false),
                computed_at = table.Column<DateOnly>(nullable: false),
                window_days = table.Column<int>(nullable: false, defaultValue: 30),
                avg_value = table.Column<decimal>(precision: 10, scale: 2, nullable: false),
                stddev_value = table.Column<decimal>(precision: 10, scale: 2, nullable: false),
                sample_count = table.Column<int>(nullable: false),
                created_at = table.Column<DateTimeOffset>(nullable: false, defaultValueSql: "NOW()")
            },
            constraints: table =>
            {
                table.PrimaryKey("PK_employee_activity_baselines", x => x.id);
                table.ForeignKey("FK_activity_baselines_tenants", x => x.tenant_id, "tenants", "id");
                table.ForeignKey("FK_activity_baselines_employees", x => x.employee_id, "employees", "id");
            });

        migrationBuilder.CreateIndex(
            name: "IX_employee_activity_baselines_unique",
            table: "employee_activity_baselines",
            columns: new[] { "tenant_id", "employee_id", "metric", "computed_at" },
            unique: true);
    }

    protected override void Down(MigrationBuilder migrationBuilder) =>
        migrationBuilder.DropTable("employee_activity_baselines");
}
```

- [ ] **Step 2: Run migration**

```bash
dotnet ef database update --project src/ONEVO.Infrastructure --startup-project src/ONEVO.Api
```

Expected: `Done.`

- [ ] **Step 3: Commit**

```bash
git add src/Infrastructure/Migrations/YYYYMMDD_AddActivityBaselines.cs
git commit -m "feat(exceptions): add employee_activity_baselines migration"
```

---

### Task 2.2: Domain — `EmployeeActivityBaseline` + Extended `RuleCondition`

**Files:**
- Create: `src/Modules/ExceptionEngine/Domain/EmployeeActivityBaseline.cs`
- Modify: `src/Modules/ExceptionEngine/Domain/RuleCondition.cs`

- [ ] **Step 1: Write failing tests**

Create `tests/Modules/ExceptionEngine.Tests/Baselines/ActivityBaselineTests.cs`:

```csharp
using FluentAssertions;
using ONEVO.Modules.ExceptionEngine.Domain;
using Xunit;

public class EmployeeActivityBaselineTests
{
    [Theory]
    [InlineData(4, false)]   // < 5 samples
    [InlineData(5, true)]    // exactly 5
    [InlineData(20, true)]   // well above threshold
    public void IsUsable_RespectsMinimumSampleCount(int sampleCount, bool expected)
    {
        var baseline = new EmployeeActivityBaseline
        {
            SampleCount = sampleCount,
            StddevValue = 10m
        };

        baseline.IsUsable().Should().Be(expected);
    }

    [Fact]
    public void IsUsable_ReturnsFalse_WhenStddevIsZero()
    {
        var baseline = new EmployeeActivityBaseline { SampleCount = 10, StddevValue = 0m };
        baseline.IsUsable().Should().BeFalse();
    }

    [Fact]
    public void ComputeThreshold_ReturnsAvgPlusSigmaMultiple()
    {
        var baseline = new EmployeeActivityBaseline
        {
            AvgValue = 60m,
            StddevValue = 20m,
            SampleCount = 10
        };

        // 60 + (2.0 * 20) = 100
        baseline.ComputeThreshold(sigmaMultiplier: 2.0m).Should().Be(100m);
    }
}

public class RuleConditionBaselineTests
{
    [Fact]
    public void IsBaselineRelative_ReturnsTrue_WhenOperatorIsBaselineRelative()
    {
        var condition = new RuleCondition
        {
            Metric = "idle_minutes",
            Operator = "baseline_relative",
            SigmaMultiplier = 2.0m,
            FallbackAbsoluteThreshold = 180m
        };

        condition.IsBaselineRelative().Should().BeTrue();
    }
}
```

- [ ] **Step 2: Run to verify fail**

```bash
dotnet test tests/Modules/ExceptionEngine.Tests --filter "ActivityBaselineTests" -v
```

Expected: FAIL.

- [ ] **Step 3: Create domain entity**

Create `src/Modules/ExceptionEngine/Domain/EmployeeActivityBaseline.cs`:

```csharp
namespace ONEVO.Modules.ExceptionEngine.Domain;

public class EmployeeActivityBaseline
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public Guid TenantId { get; init; }
    public Guid EmployeeId { get; init; }
    public string Metric { get; init; } = string.Empty; // "idle_minutes", "active_minutes", etc.
    public DateOnly ComputedAt { get; init; }
    public int WindowDays { get; init; } = 30;
    public decimal AvgValue { get; init; }
    public decimal StddevValue { get; init; }
    public int SampleCount { get; init; }
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.UtcNow;

    public bool IsUsable() => SampleCount >= 5 && StddevValue > 0;

    public decimal ComputeThreshold(decimal sigmaMultiplier) =>
        AvgValue + (sigmaMultiplier * StddevValue);
}
```

- [ ] **Step 4: Extend `RuleCondition`**

Open `src/Modules/ExceptionEngine/Domain/RuleCondition.cs` and add:

```csharp
// New properties — backward compatible, default null
public decimal? SigmaMultiplier { get; init; }          // e.g. 2.0 — used when Operator = "baseline_relative"
public decimal? FallbackAbsoluteThreshold { get; init; } // used if baseline not usable

public bool IsBaselineRelative() => Operator == "baseline_relative";
```

- [ ] **Step 5: Run tests**

```bash
dotnet test tests/Modules/ExceptionEngine.Tests --filter "ActivityBaselineTests" -v
```

Expected: All 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/Modules/ExceptionEngine/Domain/
git add tests/Modules/ExceptionEngine.Tests/Baselines/ActivityBaselineTests.cs
git commit -m "feat(exceptions): add EmployeeActivityBaseline entity and baseline_relative operator"
```

---

### Task 2.3: `BaselineRuleEvaluator`

**Files:**
- Create: `src/Modules/ExceptionEngine/Features/Evaluation/BaselineRuleEvaluator.cs`
- Create: `tests/Modules/ExceptionEngine.Tests/Evaluation/BaselineRuleEvaluatorTests.cs`

- [ ] **Step 1: Write the failing tests**

Create `tests/Modules/ExceptionEngine.Tests/Evaluation/BaselineRuleEvaluatorTests.cs`:

```csharp
using FluentAssertions;
using ONEVO.Modules.ExceptionEngine.Domain;
using ONEVO.Modules.ExceptionEngine.Features.Evaluation;
using Xunit;

public class BaselineRuleEvaluatorTests
{
    [Fact]
    public async Task EvaluateAsync_UsesBaselineThreshold_WhenBaselineUsable()
    {
        // avg=60, stddev=20, sigma=2.0 → threshold=100
        var baseline = new EmployeeActivityBaseline
        {
            Metric = "idle_minutes",
            AvgValue = 60m, StddevValue = 20m, SampleCount = 10
        };
        var condition = new RuleCondition
        {
            Metric = "idle_minutes",
            Operator = "baseline_relative",
            SigmaMultiplier = 2.0m,
            FallbackAbsoluteThreshold = 180m
        };
        var metrics = new DailyActivityMetrics { TotalIdleMinutes = 120m }; // 120 > 100

        var evaluator = new BaselineRuleEvaluator();
        var result = await evaluator.EvaluateAsync(condition, metrics, baseline, CancellationToken.None);

        result.Should().BeTrue();
    }

    [Fact]
    public async Task EvaluateAsync_UsesFallbackThreshold_WhenBaselineNotUsable()
    {
        var baseline = new EmployeeActivityBaseline
        {
            Metric = "idle_minutes",
            AvgValue = 60m, StddevValue = 20m, SampleCount = 3 // not usable
        };
        var condition = new RuleCondition
        {
            Metric = "idle_minutes",
            Operator = "baseline_relative",
            SigmaMultiplier = 2.0m,
            FallbackAbsoluteThreshold = 180m
        };
        // 120 < 180 fallback threshold
        var metrics = new DailyActivityMetrics { TotalIdleMinutes = 120m };

        var evaluator = new BaselineRuleEvaluator();
        var result = await evaluator.EvaluateAsync(condition, metrics, baseline, CancellationToken.None);

        result.Should().BeFalse();
    }

    [Fact]
    public async Task EvaluateAsync_UsesFallbackThreshold_WhenBaselineIsNull()
    {
        var condition = new RuleCondition
        {
            Metric = "idle_minutes",
            Operator = "baseline_relative",
            SigmaMultiplier = 2.0m,
            FallbackAbsoluteThreshold = 60m
        };
        var metrics = new DailyActivityMetrics { TotalIdleMinutes = 90m }; // 90 > 60

        var evaluator = new BaselineRuleEvaluator();
        var result = await evaluator.EvaluateAsync(condition, metrics, null, CancellationToken.None);

        result.Should().BeTrue();
    }

    [Theory]
    [InlineData("idle_minutes", 120, true)]       // gt absolute
    [InlineData("idle_minutes", 60, false)]        // equal — not strictly greater
    [InlineData("active_minutes", 200, true)]
    [InlineData("intensity_avg", 30, false)]
    public async Task EvaluateAsync_AbsoluteGt_EvaluatesCorrectly(
        string metric, decimal value, bool expected)
    {
        var condition = new RuleCondition
        {
            Metric = metric,
            Operator = "gt",
            Threshold = 100m
        };
        var metrics = new DailyActivityMetrics
        {
            TotalIdleMinutes = metric == "idle_minutes" ? value : 0,
            TotalActiveMinutes = metric == "active_minutes" ? value : 0,
            IntensityAvg = metric == "intensity_avg" ? value : 0
        };

        var evaluator = new BaselineRuleEvaluator();
        var result = await evaluator.EvaluateAsync(condition, metrics, null, CancellationToken.None);

        result.Should().Be(expected);
    }
}
```

- [ ] **Step 2: Run to verify fail**

```bash
dotnet test tests/Modules/ExceptionEngine.Tests --filter "BaselineRuleEvaluatorTests" -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `BaselineRuleEvaluator`**

Create `src/Modules/ExceptionEngine/Features/Evaluation/BaselineRuleEvaluator.cs`:

```csharp
using ONEVO.Modules.ExceptionEngine.Domain;

namespace ONEVO.Modules.ExceptionEngine.Features.Evaluation;

public class BaselineRuleEvaluator
{
    public Task<bool> EvaluateAsync(
        RuleCondition condition,
        DailyActivityMetrics metrics,
        EmployeeActivityBaseline? baseline,
        CancellationToken ct)
    {
        var rawValue = GetMetricValue(metrics, condition.Metric);

        if (condition.IsBaselineRelative())
        {
            decimal threshold;
            if (baseline is not null && baseline.IsUsable() && condition.SigmaMultiplier.HasValue)
                threshold = baseline.ComputeThreshold(condition.SigmaMultiplier.Value);
            else
                threshold = condition.FallbackAbsoluteThreshold
                    ?? throw new InvalidOperationException(
                        $"Rule condition for metric '{condition.Metric}' requires FallbackAbsoluteThreshold when baseline is unavailable.");

            return Task.FromResult(rawValue > threshold);
        }

        var result = condition.Operator switch
        {
            "gt" => rawValue > condition.Threshold,
            "lt" => rawValue < condition.Threshold,
            "gte" => rawValue >= condition.Threshold,
            "lte" => rawValue <= condition.Threshold,
            _ => throw new ArgumentException($"Unknown operator: {condition.Operator}")
        };

        return Task.FromResult(result);
    }

    private static decimal GetMetricValue(DailyActivityMetrics metrics, string metric) =>
        metric switch
        {
            "idle_minutes" => metrics.TotalIdleMinutes,
            "active_minutes" => metrics.TotalActiveMinutes,
            "intensity_avg" => metrics.IntensityAvg,
            "keyboard_total" => metrics.KeyboardTotal,
            "mouse_total" => metrics.MouseTotal,
            _ => throw new ArgumentException($"Unknown metric: {metric}")
        };
}
```

- [ ] **Step 4: Run all Phase 2 tests**

```bash
dotnet test tests/Modules/ExceptionEngine.Tests -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/Modules/ExceptionEngine/Features/Evaluation/BaselineRuleEvaluator.cs
git add tests/Modules/ExceptionEngine.Tests/Evaluation/BaselineRuleEvaluatorTests.cs
git commit -m "feat(exceptions): add BaselineRuleEvaluator with sigma-relative and absolute fallback"
```

---

### Task 2.4: `ComputeActivityBaselinesJob` + Inject into Rule Evaluation

**Files:**
- Create: `src/Modules/ExceptionEngine/Features/Baselines/ComputeActivityBaselinesJob.cs`
- Modify: `src/Modules/ExceptionEngine/Features/Evaluation/RuleEvaluationService.cs`
- Modify: `src/Infrastructure/Startup/HangfireJobRegistration.cs`

- [ ] **Step 1: Write the failing test**

Create `tests/Modules/ExceptionEngine.Tests/Baselines/ActivityBaselineRepositoryTests.cs`:

```csharp
using FluentAssertions;
using Moq;
using ONEVO.Modules.ExceptionEngine.Domain;
using ONEVO.Modules.ExceptionEngine.Features.Baselines;
using Xunit;

public class ComputeActivityBaselinesJobTests
{
    private readonly Mock<IActivityBaselineRepository> _repo = new();

    [Fact]
    public async Task RunAsync_ComputesBaselinesForAllTrackedMetrics()
    {
        var tenantId = Guid.NewGuid();
        var today = DateOnly.FromDateTime(DateTime.UtcNow);
        var metrics = new[] { "idle_minutes", "active_minutes", "intensity_avg" };

        foreach (var metric in metrics)
        {
            _repo.Setup(r => r.ComputeRawBaselinesAsync(tenantId, metric, today, 30, It.IsAny<CancellationToken>()))
                 .ReturnsAsync(new List<EmployeeActivityBaseline>());
        }

        var job = new ComputeActivityBaselinesJob(_repo.Object);
        await job.RunAsync(tenantId, today, CancellationToken.None);

        foreach (var metric in metrics)
        {
            _repo.Verify(r =>
                r.ComputeRawBaselinesAsync(tenantId, metric, today, 30, It.IsAny<CancellationToken>()),
                Times.Once);
        }
    }
}
```

- [ ] **Step 2: Run to verify fail**

```bash
dotnet test tests/Modules/ExceptionEngine.Tests --filter "ComputeActivityBaselinesJobTests" -v
```

Expected: FAIL.

- [ ] **Step 3: Define `IActivityBaselineRepository`**

Create `src/Modules/ExceptionEngine/Features/Baselines/IActivityBaselineRepository.cs`:

```csharp
namespace ONEVO.Modules.ExceptionEngine.Features.Baselines;

public interface IActivityBaselineRepository
{
    Task<IReadOnlyList<EmployeeActivityBaseline>> ComputeRawBaselinesAsync(
        Guid tenantId, string metric, DateOnly date, int windowDays, CancellationToken ct);

    Task UpsertBatchAsync(IReadOnlyList<EmployeeActivityBaseline> baselines, CancellationToken ct);

    Task<EmployeeActivityBaseline?> GetLatestBaselineAsync(
        Guid tenantId, Guid employeeId, string metric, CancellationToken ct);
}
```

- [ ] **Step 4: Implement the job**

Create `src/Modules/ExceptionEngine/Features/Baselines/ComputeActivityBaselinesJob.cs`:

```csharp
namespace ONEVO.Modules.ExceptionEngine.Features.Baselines;

public class ComputeActivityBaselinesJob
{
    // All metrics that exception rules can reference as baseline_relative
    private static readonly string[] TrackedMetrics =
        ["idle_minutes", "active_minutes", "intensity_avg", "keyboard_total", "mouse_total"];

    private readonly IActivityBaselineRepository _repo;

    public ComputeActivityBaselinesJob(IActivityBaselineRepository repo) => _repo = repo;

    // Called by Hangfire: daily at 9:45 PM (before exception engine evaluation)
    public async Task RunAsync(Guid tenantId, DateOnly date, CancellationToken ct)
    {
        foreach (var metric in TrackedMetrics)
        {
            var baselines = await _repo.ComputeRawBaselinesAsync(tenantId, metric, date, windowDays: 30, ct);

            if (baselines.Any())
                await _repo.UpsertBatchAsync(baselines, ct);
        }
    }
}
```

- [ ] **Step 5: Inject `BaselineRuleEvaluator` into `RuleEvaluationService`**

Open `src/Modules/ExceptionEngine/Features/Evaluation/RuleEvaluationService.cs`. In the method that evaluates an individual rule condition, add:

```csharp
// In EvaluateRuleAsync or EvaluateConditionAsync, when handling a condition:

if (condition.IsBaselineRelative())
{
    // Look up the latest pre-computed baseline for this employee + metric
    var baseline = await _baselineRepo.GetLatestBaselineAsync(
        tenantId, employeeId, condition.Metric, ct);

    return await _baselineEvaluator.EvaluateAsync(condition, metrics, baseline, ct);
}

// For non-baseline-relative conditions, use the existing evaluator unchanged
```

Inject `IActivityBaselineRepository` and `BaselineRuleEvaluator` via constructor.

- [ ] **Step 6: Register jobs**

Open `src/Infrastructure/Startup/HangfireJobRegistration.cs` and add:

```csharp
// 9:45 PM — before exception engine evaluation
RecurringJob.AddOrUpdate<ComputeActivityBaselinesJob>(
    "compute-activity-baselines",
    job => job.RunAsync(Guid.Empty, DateOnly.FromDateTime(DateTime.UtcNow), CancellationToken.None),
    "45 21 * * *",
    new RecurringJobOptions { TimeZone = TimeZoneInfo.Utc, QueueName = "default" });
```

- [ ] **Step 7: Run all tests**

```bash
dotnet test tests/Modules/ExceptionEngine.Tests -v
```

Expected: All tests PASS.

- [ ] **Step 8: Commit**

```bash
git add src/Modules/ExceptionEngine/Features/Baselines/
git add src/Modules/ExceptionEngine/Features/Evaluation/RuleEvaluationService.cs
git add src/Infrastructure/Startup/HangfireJobRegistration.cs
git add tests/Modules/ExceptionEngine.Tests/Baselines/ActivityBaselineRepositoryTests.cs
git commit -m "feat(exceptions): add ComputeActivityBaselinesJob and wire BaselineRuleEvaluator into rule evaluation"
```

---

## Phase 3: AI Notification Enrichment

> **Prerequisite:** Phase 1 must be deployed so `DiscrepancyCriticalDetected` events are firing. Phase 2 is independent.

### Task 3.1: Add `Anthropic.SDK` and notification type

**Files:**
- Modify: `src/Modules/Notifications/Domain/NotificationType.cs`
- Modify: `src/Infrastructure/Startup/ServiceRegistration.cs`

- [ ] **Step 1: Add the Anthropic SDK**

```bash
dotnet add src/ONEVO.Modules.DiscrepancyEngine package Anthropic.SDK
```

Expected: package added to `.csproj`, no build errors.

- [ ] **Step 2: Add notification type**

Open `src/Modules/Notifications/Domain/NotificationType.cs` and add:

```csharp
DiscrepancyAlertEnriched  // Manager notification with AI-generated narrative context
```

- [ ] **Step 3: Commit**

```bash
git add src/ONEVO.Modules.DiscrepancyEngine/
git add src/Modules/Notifications/Domain/NotificationType.cs
git commit -m "feat(enrichment): add Anthropic.SDK dependency and DiscrepancyAlertEnriched notification type"
```

---

### Task 3.2: `DiscrepancyEnrichmentService`

**Files:**
- Create: `src/Modules/DiscrepancyEngine/Features/Enrichment/IDiscrepancyEnrichmentService.cs`
- Create: `src/Modules/DiscrepancyEngine/Features/Enrichment/DiscrepancyEnrichmentService.cs`
- Create: `tests/Modules/DiscrepancyEngine.Tests/Enrichment/DiscrepancyEnrichmentServiceTests.cs`

- [ ] **Step 1: Write failing tests**

Create `tests/Modules/DiscrepancyEngine.Tests/Enrichment/DiscrepancyEnrichmentServiceTests.cs`:

```csharp
using FluentAssertions;
using Moq;
using ONEVO.Modules.DiscrepancyEngine.Features.Enrichment;
using ONEVO.Modules.DiscrepancyEngine.Public;
using ONEVO.Modules.Notifications;
using Xunit;

public class DiscrepancyEnrichmentServiceTests
{
    private readonly Mock<IDiscrepancyEngineService> _discrepancyService = new();
    private readonly Mock<INotificationService> _notifications = new();
    private readonly Mock<IAnthropicInsightProvider> _anthropic = new();  // testable wrapper, not concrete AnthropicClient

    [Fact]
    public async Task EnrichAndNotifyAsync_SendsEnrichedNotification_WhenHistoryExists()
    {
        var employeeId = Guid.NewGuid();
        var managerId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();

        _discrepancyService
            .Setup(s => s.GetDiscrepanciesForRangeAsync(
                employeeId, It.IsAny<DateOnly>(), It.IsAny<DateOnly>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<DiscrepancyEventDto>
            {
                new() { Severity = "critical", UnaccountedMinutes = 200 },
                new() { Severity = "high", UnaccountedMinutes = 120 }
            });

        _anthropic
            .Setup(a => a.GetInsightAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync("This employee has had 2 elevated discrepancies in the past 30 days.");

        Notification? sentNotification = null;
        _notifications
            .Setup(n => n.SendAsync(It.IsAny<Notification>(), It.IsAny<CancellationToken>()))
            .Callback<Notification, CancellationToken>((n, _) => sentNotification = n)
            .Returns(Task.CompletedTask);

        var service = new DiscrepancyEnrichmentService(
            _discrepancyService.Object, _anthropic.Object, _notifications.Object);

        await service.EnrichAndNotifyAsync(employeeId, managerId, tenantId,
            DiscrepancySeverity.Critical, unaccountedMinutes: 240, CancellationToken.None);

        sentNotification.Should().NotBeNull();
        sentNotification!.Type.Should().Be(NotificationType.DiscrepancyAlertEnriched);
        sentNotification.RecipientId.Should().Be(managerId);
    }

    [Fact]
    public async Task EnrichAndNotifyAsync_UsesDefaultMessage_WhenNoHistory()
    {
        var employeeId = Guid.NewGuid();

        _discrepancyService
            .Setup(s => s.GetDiscrepanciesForRangeAsync(
                employeeId, It.IsAny<DateOnly>(), It.IsAny<DateOnly>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<DiscrepancyEventDto>());

        // Anthropic should NOT be called when there's no history
        _anthropic.Verify(a =>
            a.GetInsightAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Never);

        Notification? sentNotification = null;
        _notifications
            .Setup(n => n.SendAsync(It.IsAny<Notification>(), It.IsAny<CancellationToken>()))
            .Callback<Notification, CancellationToken>((n, _) => sentNotification = n);

        var service = new DiscrepancyEnrichmentService(
            _discrepancyService.Object, _anthropic.Object, _notifications.Object);

        await service.EnrichAndNotifyAsync(Guid.NewGuid(), Guid.NewGuid(), Guid.NewGuid(),
            DiscrepancySeverity.Critical, 240, CancellationToken.None);

        sentNotification!.Type.Should().Be(NotificationType.DiscrepancyAlertEnriched);
    }
}
```

- [ ] **Step 2: Run to verify fail**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "DiscrepancyEnrichmentServiceTests" -v
```

Expected: FAIL.

- [ ] **Step 3: Define interfaces**

Create `src/Modules/DiscrepancyEngine/Features/Enrichment/IAnthropicInsightProvider.cs`:

```csharp
namespace ONEVO.Modules.DiscrepancyEngine.Features.Enrichment;

/// <summary>Thin wrapper over AnthropicClient to keep DiscrepancyEnrichmentService testable.</summary>
public interface IAnthropicInsightProvider
{
    Task<string> GetInsightAsync(string prompt, CancellationToken ct);
}
```

Create `src/Modules/DiscrepancyEngine/Features/Enrichment/AnthropicInsightProvider.cs`:

```csharp
using Anthropic.SDK;
using Anthropic.SDK.Messaging;

namespace ONEVO.Modules.DiscrepancyEngine.Features.Enrichment;

public class AnthropicInsightProvider : IAnthropicInsightProvider
{
    private readonly AnthropicClient _client;
    private const string SystemPrompt =
        "You are an HR analytics assistant providing neutral, factual workforce insights to managers. Never be accusatory. Focus on data patterns only.";

    public AnthropicInsightProvider(AnthropicClient client) => _client = client;

    public async Task<string> GetInsightAsync(string prompt, CancellationToken ct)
    {
        var response = await _client.Messages.GetClaudeMessageAsync(
            new MessageParameters
            {
                Model = AnthropicModels.Claude3Sonnet,
                MaxTokens = 300,
                System = [new SystemMessage { Text = SystemPrompt }],
                Messages = [new Message
                {
                    Role = RoleType.User,
                    Content = [new TextContent { Text = prompt }]
                }]
            }, ct);

        return response.Message.ToString();
    }
}
```

Create `src/Modules/DiscrepancyEngine/Features/Enrichment/IDiscrepancyEnrichmentService.cs`:

```csharp
namespace ONEVO.Modules.DiscrepancyEngine.Features.Enrichment;

public interface IDiscrepancyEnrichmentService
{
    Task EnrichAndNotifyAsync(
        Guid employeeId,
        Guid managerId,
        Guid tenantId,
        DiscrepancySeverity severity,
        int unaccountedMinutes,
        CancellationToken ct);
}
```

- [ ] **Step 4: Implement the service**

Create `src/Modules/DiscrepancyEngine/Features/Enrichment/DiscrepancyEnrichmentService.cs`:

```csharp
using ONEVO.Modules.DiscrepancyEngine.Public;
using ONEVO.Modules.Notifications;

namespace ONEVO.Modules.DiscrepancyEngine.Features.Enrichment;

public class DiscrepancyEnrichmentService : IDiscrepancyEnrichmentService
{
    private readonly IDiscrepancyEngineService _discrepancyService;
    private readonly IAnthropicInsightProvider _anthropic;  // interface, not concrete SDK type
    private readonly INotificationService _notifications;

    public DiscrepancyEnrichmentService(
        IDiscrepancyEngineService discrepancyService,
        IAnthropicInsightProvider anthropic,
        INotificationService notifications)
    {
        _discrepancyService = discrepancyService;
        _anthropic = anthropic;
        _notifications = notifications;
    }

    public async Task EnrichAndNotifyAsync(
        Guid employeeId, Guid managerId, Guid tenantId,
        DiscrepancySeverity severity, int unaccountedMinutes, CancellationToken ct)
    {
        var today = DateOnly.FromDateTime(DateTime.UtcNow);
        var history = await _discrepancyService.GetDiscrepanciesForRangeAsync(
            employeeId, today.AddDays(-30), today.AddDays(-1), ct);

        string insight;
        if (history.Count == 0)
        {
            insight = "No prior discrepancy history for this employee. This is the first detected event.";
        }
        else
        {
            var prompt = BuildPrompt(history, severity, unaccountedMinutes);
            insight = await CallClaudeAsync(prompt, ct);
        }

        await _notifications.SendAsync(new Notification
        {
            RecipientId = managerId,
            Type = NotificationType.DiscrepancyAlertEnriched,
            Data = new
            {
                EmployeeId = employeeId,
                Severity = severity.ToString().ToLower(),
                UnaccountedMinutes = unaccountedMinutes,
                Insight = insight
            }
        }, ct);
    }

    private string BuildPrompt(
        IReadOnlyList<DiscrepancyEventDto> history,
        DiscrepancySeverity severity,
        int unaccountedMinutes)
    {
        var criticalCount = history.Count(h => h.Severity == "critical");
        var highCount = history.Count(h => h.Severity == "high");
        var avgUnaccounted = (int)history.Average(h => h.UnaccountedMinutes);

        return $"""
            An employee has a {severity} discrepancy alert today with {unaccountedMinutes} unaccounted minutes.

            Past 30 days:
            - Critical events: {criticalCount}
            - High events: {highCount}
            - Average unaccounted minutes: {avgUnaccounted}

            Provide a 2-3 sentence neutral, factual insight for the manager.
            Do not be accusatory. Note whether this is a pattern or an anomaly.
            """;
    }

    private Task<string> CallClaudeAsync(string prompt, CancellationToken ct) =>
        _anthropic.GetInsightAsync(prompt, ct);  // delegates to IAnthropicInsightProvider
}
```

- [ ] **Step 5: Run tests**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "DiscrepancyEnrichmentServiceTests" -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/Modules/DiscrepancyEngine/Features/Enrichment/
git add tests/Modules/DiscrepancyEngine.Tests/Enrichment/
git commit -m "feat(enrichment): add DiscrepancyEnrichmentService with Claude narrative context"
```

---

### Task 3.3: Event Handler — `DiscrepancyEnrichmentHandler`

**Files:**
- Create: `src/Modules/DiscrepancyEngine/Features/Enrichment/DiscrepancyEnrichmentHandler.cs`
- Modify: `src/Infrastructure/Startup/ServiceRegistration.cs`

- [ ] **Step 1: Write failing test**

Add to `tests/Modules/DiscrepancyEngine.Tests/Enrichment/DiscrepancyEnrichmentServiceTests.cs`:

```csharp
public class DiscrepancyEnrichmentHandlerTests
{
    [Fact]
    public async Task Handle_InvokesEnrichmentService_OnCriticalEvent()
    {
        var enrichmentService = new Mock<IDiscrepancyEnrichmentService>();
        var handler = new DiscrepancyEnrichmentHandler(enrichmentService.Object);

        var domainEvent = new DiscrepancyCriticalDetected(
            EmployeeId: Guid.NewGuid(),
            ManagerId: Guid.NewGuid(),
            TenantId: Guid.NewGuid(),
            UnaccountedMinutes: 250,
            Date: DateOnly.FromDateTime(DateTime.UtcNow));

        await handler.Handle(domainEvent, CancellationToken.None);

        enrichmentService.Verify(s =>
            s.EnrichAndNotifyAsync(
                domainEvent.EmployeeId, domainEvent.ManagerId, domainEvent.TenantId,
                DiscrepancySeverity.Critical, domainEvent.UnaccountedMinutes,
                It.IsAny<CancellationToken>()),
            Times.Once);
    }
}
```

- [ ] **Step 2: Run to verify fail**

```bash
dotnet test tests/Modules/DiscrepancyEngine.Tests --filter "DiscrepancyEnrichmentHandlerTests" -v
```

Expected: FAIL.

- [ ] **Step 3: Implement the handler**

Create `src/Modules/DiscrepancyEngine/Features/Enrichment/DiscrepancyEnrichmentHandler.cs`:

```csharp
using MediatR;
using ONEVO.Modules.DiscrepancyEngine.Domain.Events;

namespace ONEVO.Modules.DiscrepancyEngine.Features.Enrichment;

public class DiscrepancyEnrichmentHandler : INotificationHandler<DiscrepancyCriticalDetected>
{
    private readonly IDiscrepancyEnrichmentService _enrichmentService;

    public DiscrepancyEnrichmentHandler(IDiscrepancyEnrichmentService enrichmentService) =>
        _enrichmentService = enrichmentService;

    public async Task Handle(DiscrepancyCriticalDetected notification, CancellationToken ct) =>
        await _enrichmentService.EnrichAndNotifyAsync(
            notification.EmployeeId,
            notification.ManagerId,
            notification.TenantId,
            DiscrepancySeverity.Critical,
            notification.UnaccountedMinutes,
            ct);
}
```

- [ ] **Step 4: Register in DI**

Open `src/Infrastructure/Startup/ServiceRegistration.cs` and add:

```csharp
// Anthropic client — concrete SDK type registered as singleton (one HTTP client)
builder.Services.AddSingleton(new AnthropicClient(
    builder.Configuration["Anthropic:ApiKey"]
        ?? throw new InvalidOperationException("Anthropic:ApiKey is required")));

// Thin wrapper registered as the interface the service depends on
builder.Services.AddSingleton<IAnthropicInsightProvider, AnthropicInsightProvider>();

builder.Services.AddScoped<IDiscrepancyEnrichmentService, DiscrepancyEnrichmentService>();
// Handler auto-registered by MediatR assembly scan — no manual registration needed
```

Also add to `appsettings.json`:

```json
{
  "Anthropic": {
    "ApiKey": ""
  }
}
```

And to `appsettings.Production.json` (or Railway env vars):

```
ANTHROPIC__APIKEY=<your-api-key>
```

- [ ] **Step 5: Run all tests**

```bash
dotnet test tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/Modules/DiscrepancyEngine/Features/Enrichment/DiscrepancyEnrichmentHandler.cs
git add src/Infrastructure/Startup/ServiceRegistration.cs
git add tests/Modules/DiscrepancyEngine.Tests/Enrichment/
git commit -m "feat(enrichment): wire DiscrepancyEnrichmentHandler into MediatR event pipeline"
```

---

### Task 3.4: Create enrichment feature doc

**Files:**
- Create: `modules/discrepancy-engine/notification-enrichment/overview.md`

- [ ] **Step 1: Write the doc**

Create `modules/discrepancy-engine/notification-enrichment/overview.md`:

```markdown
# Notification Enrichment

**Module:** Discrepancy Engine
**Feature:** AI Notification Enrichment

---

## Purpose

When a `DiscrepancyCriticalDetected` event fires, this feature enriches the manager notification with a 2-3 sentence neutral AI-generated insight using the employee's 30-day discrepancy history as context. It does NOT participate in detection or severity classification — those remain deterministic.

## What It Does

1. `DiscrepancyEnrichmentHandler` receives `DiscrepancyCriticalDetected` via MediatR
2. Fetches 30-day discrepancy history for the employee
3. If no history: sends a default "first event" message (no AI call)
4. If history exists: makes a single Claude API call (max 300 tokens) to generate neutral narrative
5. Sends a `DiscrepancyAlertEnriched` notification to the manager

## Key Rules

- **AI is NOT in the detection loop.** Claude is called AFTER severity is already classified.
- **Only fires on `critical` severity.** Low/high alerts use the existing non-enriched path.
- **No AI call if no history.** Prevents meaningless insights and saves cost for new employees.
- **Model:** `claude-sonnet-4-6` (cost-efficient at 300 tokens max)
- **System prompt enforces:** neutral tone, no accusation, pattern-focused

## Event Flow

```
DiscrepancyEngineJob publishes DiscrepancyCriticalDetected
    → DiscrepancyEnrichmentHandler.Handle()
        → IDiscrepancyEnrichmentService.EnrichAndNotifyAsync()
            → IDiscrepancyEngineService.GetDiscrepanciesForRangeAsync() (30-day history)
            → AnthropicClient.Messages.GetClaudeMessageAsync() (if history exists)
            → INotificationService.SendAsync(DiscrepancyAlertEnriched)
```

## Configuration

Set `ANTHROPIC__APIKEY` in Railway environment variables (never commit to source).
```

- [ ] **Step 2: Commit**

```bash
git add modules/discrepancy-engine/notification-enrichment/overview.md
git commit -m "docs(enrichment): document AI notification enrichment architecture and rules"
```

---

## Final Verification

- [ ] **Run full test suite**

```bash
dotnet test tests/ --logger "console;verbosity=detailed"
```

Expected: All tests pass, no skipped.

- [ ] **Build the full solution**

```bash
dotnet build src/ONEVO.sln --configuration Release
```

Expected: 0 errors, 0 warnings.

- [ ] **Run architecture tests**

```bash
dotnet test tests/ONEVO.Architecture.Tests -v
```

Expected: Module boundary checks pass — DiscrepancyEngine does not reference ExceptionEngine internals, etc.

- [ ] **Final commit and tag**

```bash
git tag v-intelligence-layer-complete
git push origin HEAD --tags
```

---

## Summary of All Files Changed

### This repo (documentation):
| Action | Path |
|:-------|:-----|
| Modify | `database/schemas/discrepancy-engine.md` |
| Create | `modules/discrepancy-engine/statistical-baselines/overview.md` |
| Modify | `modules/discrepancy-engine/overview.md` |
| Create | `modules/exception-engine/activity-baselines/overview.md` |
| Modify | `modules/exception-engine/overview.md` |
| Create | `modules/discrepancy-engine/notification-enrichment/overview.md` |

### Backend (implementation):
| Action | Path |
|:-------|:-----|
| Create | `src/Modules/DiscrepancyEngine/Domain/EmployeeDiscrepancyBaseline.cs` |
| Modify | `src/Modules/DiscrepancyEngine/Domain/DiscrepancyEvent.cs` |
| Create | `src/Modules/DiscrepancyEngine/Features/Baselines/IDiscrepancyBaselineRepository.cs` |
| Create | `src/Modules/DiscrepancyEngine/Features/Baselines/DiscrepancyBaselineRepository.cs` |
| Create | `src/Modules/DiscrepancyEngine/Features/Baselines/DiscrepancySeverityCalculator.cs` |
| Create | `src/Modules/DiscrepancyEngine/Jobs/ComputeDiscrepancyBaselinesJob.cs` |
| Modify | `src/Modules/DiscrepancyEngine/Jobs/DiscrepancyEngineJob.cs` |
| Modify | `src/Modules/DiscrepancyEngine/Infrastructure/DiscrepancyEngineDbContext.cs` |
| Create | `src/Modules/ExceptionEngine/Domain/EmployeeActivityBaseline.cs` |
| Modify | `src/Modules/ExceptionEngine/Domain/RuleCondition.cs` |
| Create | `src/Modules/ExceptionEngine/Features/Baselines/IActivityBaselineRepository.cs` |
| Create | `src/Modules/ExceptionEngine/Features/Baselines/ActivityBaselineRepository.cs` |
| Create | `src/Modules/ExceptionEngine/Features/Baselines/ComputeActivityBaselinesJob.cs` |
| Create | `src/Modules/ExceptionEngine/Features/Evaluation/BaselineRuleEvaluator.cs` |
| Modify | `src/Modules/ExceptionEngine/Features/Evaluation/RuleEvaluationService.cs` |
| Modify | `src/Modules/ExceptionEngine/Infrastructure/ExceptionEngineDbContext.cs` |
| Create | `src/Modules/DiscrepancyEngine/Features/Enrichment/IAnthropicInsightProvider.cs` |
| Create | `src/Modules/DiscrepancyEngine/Features/Enrichment/AnthropicInsightProvider.cs` |
| Create | `src/Modules/DiscrepancyEngine/Features/Enrichment/IDiscrepancyEnrichmentService.cs` |
| Create | `src/Modules/DiscrepancyEngine/Features/Enrichment/DiscrepancyEnrichmentService.cs` |
| Create | `src/Modules/DiscrepancyEngine/Features/Enrichment/DiscrepancyEnrichmentHandler.cs` |
| Modify | `src/Modules/Notifications/Domain/NotificationType.cs` |
| Modify | `src/Infrastructure/Startup/HangfireJobRegistration.cs` |
| Modify | `src/Infrastructure/Startup/ServiceRegistration.cs` |
| Create | `src/Infrastructure/Migrations/YYYYMMDD_AddDiscrepancyBaselines.cs` |
| Create | `src/Infrastructure/Migrations/YYYYMMDD_AddActivityBaselines.cs` |
| Create | `tests/Modules/DiscrepancyEngine.Tests/Baselines/BaselineComputationServiceTests.cs` |
| Create | `tests/Modules/DiscrepancyEngine.Tests/Jobs/DiscrepancyEngineJobBaselineTests.cs` |
| Create | `tests/Modules/ExceptionEngine.Tests/Baselines/ActivityBaselineTests.cs` |
| Create | `tests/Modules/ExceptionEngine.Tests/Baselines/ActivityBaselineRepositoryTests.cs` |
| Create | `tests/Modules/ExceptionEngine.Tests/Evaluation/BaselineRuleEvaluatorTests.cs` |
| Create | `tests/Modules/DiscrepancyEngine.Tests/Enrichment/DiscrepancyEnrichmentServiceTests.cs` |
