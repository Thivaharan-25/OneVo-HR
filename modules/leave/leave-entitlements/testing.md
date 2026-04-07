# Leave Entitlements — Testing

**Module:** Leave  
**Feature:** Leave Entitlements  
**Location:** `tests/ONEVO.Tests.Unit/Modules/Leave/Entitlements/`

---

## Unit Tests

```csharp
public class LeaveEntitlementServiceTests
{
    private readonly Mock<ILeaveEntitlementRepository> _entitlementRepo = new();
    private readonly Mock<ILeavePolicyRepository> _policyRepo = new();
    private readonly Mock<IEmployeeService> _employeeService = new();
    private readonly Mock<IBalanceAuditService> _auditService = new();
    private readonly LeaveEntitlementService _sut;

    public LeaveEntitlementServiceTests()
    {
        _sut = new LeaveEntitlementService(
            _entitlementRepo.Object,
            _policyRepo.Object,
            _employeeService.Object,
            _auditService.Object);
    }

    // --- Proration Tests ---

    [Fact]
    public async Task CalculateEntitlement_NewHireMidYear_ProratesByCalendarDays()
    {
        // Arrange
        var employeeId = Guid.NewGuid();
        var leaveTypeId = Guid.NewGuid();
        var hireDate = new DateOnly(2026, 7, 1); // mid-year

        _employeeService.Setup(x => x.GetByIdAsync(employeeId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(Result.Ok(new EmployeeDto { Id = employeeId, HireDate = hireDate, CountryId = Guid.NewGuid(), JobLevelId = Guid.NewGuid() }));

        _policyRepo.Setup(x => x.GetActivePolicyAsync(leaveTypeId, It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LeavePolicy { AnnualEntitlementDays = 20m, ProrrationMethod = "calendar_days", CarryForwardMaxDays = 5m });

        _entitlementRepo.Setup(x => x.GetByEmployeeAndYearAsync(employeeId, 2025, It.IsAny<CancellationToken>()))
            .ReturnsAsync((LeaveEntitlement?)null);

        // Act
        var result = await _sut.CalculateEntitlementAsync(employeeId, leaveTypeId, 2026, CancellationToken.None);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.Value.TotalDays.Should().BeApproximately(10.0m, 0.5m); // ~184/365 * 20
    }

    [Fact]
    public async Task CalculateEntitlement_FullYearEmployee_NoProration()
    {
        // Arrange
        var employeeId = Guid.NewGuid();
        var leaveTypeId = Guid.NewGuid();

        _employeeService.Setup(x => x.GetByIdAsync(employeeId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(Result.Ok(new EmployeeDto { Id = employeeId, HireDate = new DateOnly(2024, 3, 1), CountryId = Guid.NewGuid(), JobLevelId = Guid.NewGuid() }));

        _policyRepo.Setup(x => x.GetActivePolicyAsync(It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LeavePolicy { AnnualEntitlementDays = 20m, ProrrationMethod = "calendar_days", CarryForwardMaxDays = 5m });

        _entitlementRepo.Setup(x => x.GetByEmployeeAndYearAsync(employeeId, 2025, It.IsAny<CancellationToken>()))
            .ReturnsAsync((LeaveEntitlement?)null);

        // Act
        var result = await _sut.CalculateEntitlementAsync(employeeId, leaveTypeId, 2026, CancellationToken.None);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.Value.TotalDays.Should().Be(20.0m);
    }

    // --- Carry-Forward Tests ---

    [Fact]
    public async Task CalculateEntitlement_PreviousYearHasRemaining_CarriesForwardUpToCap()
    {
        // Arrange
        var employeeId = Guid.NewGuid();
        var leaveTypeId = Guid.NewGuid();

        _employeeService.Setup(x => x.GetByIdAsync(employeeId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(Result.Ok(new EmployeeDto { Id = employeeId, HireDate = new DateOnly(2023, 1, 1), CountryId = Guid.NewGuid(), JobLevelId = Guid.NewGuid() }));

        _policyRepo.Setup(x => x.GetActivePolicyAsync(It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LeavePolicy { AnnualEntitlementDays = 20m, CarryForwardMaxDays = 5m, CarryForwardExpiryMonths = 3 });

        _entitlementRepo.Setup(x => x.GetByEmployeeAndYearAsync(employeeId, 2025, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LeaveEntitlement { RemainingDays = 8m }); // 8 remaining, cap is 5

        // Act
        var result = await _sut.CalculateEntitlementAsync(employeeId, leaveTypeId, 2026, CancellationToken.None);

        // Assert
        result.Value.CarriedForwardDays.Should().Be(5m); // capped at 5
        result.Value.TotalDays.Should().Be(25m); // 20 + 5
    }

    [Fact]
    public async Task CalculateEntitlement_CarryForwardExpired_ZeroCarryForward()
    {
        // Arrange
        var employeeId = Guid.NewGuid();
        var leaveTypeId = Guid.NewGuid();

        _employeeService.Setup(x => x.GetByIdAsync(employeeId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(Result.Ok(new EmployeeDto { Id = employeeId, HireDate = new DateOnly(2023, 1, 1) }));

        _policyRepo.Setup(x => x.GetActivePolicyAsync(It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LeavePolicy { AnnualEntitlementDays = 20m, CarryForwardMaxDays = 5m, CarryForwardExpiryMonths = 0 });

        // Act
        var result = await _sut.CalculateEntitlementAsync(employeeId, leaveTypeId, 2026, CancellationToken.None);

        // Assert
        result.Value.CarriedForwardDays.Should().Be(0m);
    }

    // --- Forfeiture Tests ---

    [Fact]
    public async Task YearEndRollover_RemainingExceedsCap_LogsForfeitureAudit()
    {
        // Arrange
        var employeeId = Guid.NewGuid();
        var leaveTypeId = Guid.NewGuid();
        var entitlement = new LeaveEntitlement { EmployeeId = employeeId, LeaveTypeId = leaveTypeId, RemainingDays = 12m, Year = 2025 };
        var policy = new LeavePolicy { CarryForwardMaxDays = 5m, AnnualEntitlementDays = 20m };

        _entitlementRepo.Setup(x => x.GetAllForYearAsync(2025, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<LeaveEntitlement> { entitlement });

        _policyRepo.Setup(x => x.GetActivePolicyAsync(leaveTypeId, It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(policy);

        // Act
        await _sut.ProcessYearEndRolloverAsync(2025, CancellationToken.None);

        // Assert — forfeiture of 7 days (12 - 5)
        _auditService.Verify(x => x.LogAsync(
            employeeId, leaveTypeId, "forfeiture", -7m,
            It.Is<string>(s => s.Contains("forfeiture")),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    // --- Error Tests ---

    [Fact]
    public async Task CalculateEntitlement_NoPolicyFound_ReturnsFailure()
    {
        // Arrange
        _employeeService.Setup(x => x.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(Result.Ok(new EmployeeDto { HireDate = new DateOnly(2024, 1, 1) }));

        _policyRepo.Setup(x => x.GetActivePolicyAsync(It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((LeavePolicy?)null);

        // Act
        var result = await _sut.CalculateEntitlementAsync(Guid.NewGuid(), Guid.NewGuid(), 2026, CancellationToken.None);

        // Assert
        result.IsFailure.Should().BeTrue();
        result.Error.Code.Should().Be("NO_APPLICABLE_POLICY");
    }

    [Fact]
    public async Task CalculateEntitlement_EmployeeNotFound_ReturnsFailure()
    {
        // Arrange
        _employeeService.Setup(x => x.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(Result.Fail<EmployeeDto>("EMPLOYEE_NOT_FOUND"));

        // Act
        var result = await _sut.CalculateEntitlementAsync(Guid.NewGuid(), Guid.NewGuid(), 2026, CancellationToken.None);

        // Assert
        result.IsFailure.Should().BeTrue();
        result.Error.Code.Should().Be("EMPLOYEE_NOT_FOUND");
    }
}
```

---

## Integration Tests

```csharp
public class LeaveEntitlementEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _client;
    private readonly ONEVOWebFactory _factory;

    public LeaveEntitlementEndpointTests(ONEVOWebFactory factory)
    {
        _factory = factory;
        _client = factory.CreateAuthenticatedClient(permission: "leave:read");
    }

    [Fact]
    public async Task GetEntitlements_ValidEmployee_Returns200WithEntitlements()
    {
        // Arrange
        var employeeId = await _factory.SeedEmployeeAsync(hireDate: new DateOnly(2024, 1, 15));
        await _factory.SeedLeavePolicyAsync(annualDays: 20m, carryForwardMax: 5m);
        await _factory.SeedLeaveEntitlementAsync(employeeId, year: 2026, totalDays: 20m, usedDays: 3m);

        // Act
        var response = await _client.GetAsync($"/api/v1/leave/entitlements/{employeeId}?year=2026");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var dto = await response.Content.ReadFromJsonAsync<LeaveEntitlementDto>();
        dto!.TotalDays.Should().Be(20m);
        dto.UsedDays.Should().Be(3m);
        dto.RemainingDays.Should().Be(17m);
    }

    [Fact]
    public async Task GetEntitlements_EmployeeNotFound_Returns404()
    {
        // Act
        var response = await _client.GetAsync($"/api/v1/leave/entitlements/{Guid.NewGuid()}?year=2026");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task GetEntitlements_NoPermission_Returns403()
    {
        // Arrange
        var client = _factory.CreateAuthenticatedClient(permission: "leave:none");

        // Act
        var response = await client.GetAsync($"/api/v1/leave/entitlements/{Guid.NewGuid()}?year=2026");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }

    [Fact]
    public async Task GetEntitlements_NewHireMidYear_CalculatesProratedEntitlement()
    {
        // Arrange
        var employeeId = await _factory.SeedEmployeeAsync(hireDate: new DateOnly(2026, 7, 1));
        await _factory.SeedLeavePolicyAsync(annualDays: 20m, prorrationMethod: "calendar_days");

        // Act
        var response = await _client.GetAsync($"/api/v1/leave/entitlements/{employeeId}?year=2026");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var dto = await response.Content.ReadFromJsonAsync<LeaveEntitlementDto>();
        dto!.TotalDays.Should().BeInRange(9.5m, 10.5m); // ~184/365 * 20
    }
}
```

---

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Full-year employee gets full entitlement | Unit | `total_days = annual_entitlement_days` (no proration) |
| Mid-year hire, calendar_days proration | Unit | Prorated by remaining calendar days / 365 |
| Mid-year hire, working_days proration | Unit | Prorated by remaining working days / total working days |
| Carry-forward capped at policy max | Unit | `carried_forward_days = MIN(remaining, cap)` |
| Carry-forward expired | Unit | `carried_forward_days = 0` |
| Year-end rollover logs forfeiture | Unit | Audit entry with `change_type = 'forfeiture'` |
| Year-end rollover creates new year entitlement | Unit | New `leave_entitlements` row for next year |
| No applicable policy for employee | Unit | Returns `NO_APPLICABLE_POLICY` error |
| Employee not found | Unit | Returns `EMPLOYEE_NOT_FOUND` error |
| GET entitlements returns 200 | Integration | HTTP 200, correct totals |
| GET entitlements for unknown employee | Integration | HTTP 404 |
| GET entitlements without permission | Integration | HTTP 403 |
| GET entitlements for mid-year hire | Integration | Prorated total calculated on first access |
| Monthly accrual increments total_days | Unit | `total_days += annual / 12` per month |
| Idempotent rollover (already created) | Unit | Skips without error |

## Related

- [[leave-entitlements|Leave Entitlements Overview]]
- [[testing/README|Testing Standards]]
