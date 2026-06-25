# Time Off Entitlements - Testing

**Module:** Time Off
**Feature:** Time Off Entitlements
**Location:** `tests/ONEVO.Tests.Unit/Modules/TimeOff/Entitlements/`

---

## Unit Tests

Focus entitlement tests on the minute-based model. Admin enters entitlement in hours/minutes; the system stores the canonical value in minutes.

```csharp
public class TimeOffEntitlementServiceTests
{
    private readonly Mock<ITimeOffEntitlementRepository> _entitlementRepo = new();
    private readonly Mock<ITimeOffPolicyRepository> _policyRepo = new();
    private readonly Mock<IEmployeeService> _employeeService = new();
    private readonly Mock<IScheduleResolver> _scheduleResolver = new();
    private readonly Mock<IBalanceAuditService> _auditService = new();
    private readonly TimeOffEntitlementService _sut;

    public TimeOffEntitlementServiceTests()
    {
        _sut = new TimeOffEntitlementService(
            _entitlementRepo.Object,
            _policyRepo.Object,
            _employeeService.Object,
            _scheduleResolver.Object,
            _auditService.Object);
    }

    [Fact]
    public async Task CalculateEntitlement_MinuteInput_StoresMinutesDirectly()
    {
        var employeeId = Guid.NewGuid();
        var timeOffTypeId = Guid.NewGuid();

        _policyRepo.Setup(x => x.GetActivePolicyAsync(employeeId, timeOffTypeId, It.IsAny<DateRange>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new TimeOffPolicy
            {
                EntitlementMinutes = 9600,
                AccrualMethod = "yearly"
            });

        var result = await _sut.CalculateEntitlementAsync(employeeId, timeOffTypeId, 2026, CancellationToken.None);

        result.IsSuccess.Should().BeTrue();
        result.Value.EntitlementMinutes.Should().Be(9600);
    }

    [Fact]
    public async Task CalculateEntitlement_PreviousPeriodHasRemaining_CarriesForwardUpToMinuteCap()
    {
        var employeeId = Guid.NewGuid();
        var timeOffTypeId = Guid.NewGuid();

        _policyRepo.Setup(x => x.GetActivePolicyAsync(employeeId, timeOffTypeId, It.IsAny<DateRange>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new TimeOffPolicy
            {
                EntitlementMinutes = 9600,
                CarryForwardAllowed = true,
                CarryForwardLimitMinutes = 2400
            });

        _entitlementRepo.Setup(x => x.GetPreviousPeriodAsync(employeeId, timeOffTypeId, It.IsAny<DateRange>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new TimeOffEntitlement { AvailableMinutes = 3840 });

        var result = await _sut.CalculateEntitlementAsync(employeeId, timeOffTypeId, 2026, CancellationToken.None);

        result.Value.CarriedForwardMinutes.Should().Be(2400);
        result.Value.EntitlementMinutes.Should().Be(12000);
    }

    [Fact]
    public async Task Rollover_RemainingExceedsMinuteCap_LogsForfeitureAudit()
    {
        var employeeId = Guid.NewGuid();
        var timeOffTypeId = Guid.NewGuid();
        var entitlement = new TimeOffEntitlement
        {
            EmployeeId = employeeId,
            TimeOffTypeId = timeOffTypeId,
            AvailableMinutes = 5760,
            PeriodYear = 2025
        };
        var policy = new TimeOffPolicy
        {
            CarryForwardAllowed = true,
            CarryForwardLimitMinutes = 2400,
            EntitlementMinutes = 9600
        };

        _entitlementRepo.Setup(x => x.GetAllForPeriodAsync(2025, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<TimeOffEntitlement> { entitlement });

        _policyRepo.Setup(x => x.GetActivePolicyAsync(employeeId, timeOffTypeId, It.IsAny<DateRange>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(policy);

        await _sut.ProcessPeriodRolloverAsync(2025, CancellationToken.None);

        _auditService.Verify(x => x.LogAsync(
            employeeId,
            timeOffTypeId,
            "forfeiture",
            -3360,
            It.Is<string>(s => s.Contains("forfeiture")),
            It.IsAny<CancellationToken>()), Times.Once);
    }
}
```

---

## Integration Tests

```csharp
public class TimeOffEntitlementEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _client;
    private readonly ONEVOWebFactory _factory;

    public TimeOffEntitlementEndpointTests(ONEVOWebFactory factory)
    {
        _factory = factory;
        _client = factory.CreateAuthenticatedClient(permission: "time_off:read");
    }

    [Fact]
    public async Task GetEntitlements_ValidEmployee_Returns200WithMinuteBalances()
    {
        var employeeId = await _factory.SeedEmployeeAsync(hireDate: new DateOnly(2024, 1, 15));
        await _factory.SeedTimeOffPolicyAsync(entitlementMinutes: 9600);
        await _factory.SeedTimeOffEntitlementAsync(employeeId, year: 2026, entitlementMinutes: 9600, usedMinutes: 1440);

        var response = await _client.GetAsync($"/api/v1/time-off/entitlements/{employeeId}?year=2026");

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var dto = await response.Content.ReadFromJsonAsync<TimeOffEntitlementDto>();
        dto!.EntitlementMinutes.Should().Be(9600);
        dto.UsedMinutes.Should().Be(1440);
        dto.AvailableMinutes.Should().Be(8160);
    }

    [Fact]
    public async Task GetEntitlements_NewHireMidYear_ReturnsProratedMinuteEntitlement()
    {
        var employeeId = await _factory.SeedEmployeeAsync(hireDate: new DateOnly(2026, 7, 1));
        await _factory.SeedTimeOffPolicyAsync(entitlementMinutes: 9600, prorationMethod: "calendar_days");

        var response = await _client.GetAsync($"/api/v1/time-off/entitlements/{employeeId}?year=2026");

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var dto = await response.Content.ReadFromJsonAsync<TimeOffEntitlementDto>();
        dto!.EntitlementMinutes.Should().BeInRange(4560, 5040);
    }
}
```

---

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Hour/minute input converts to minutes before persistence | Unit | `entitlement_minutes = policy.entitlement_minutes` |
| Mid-year hire, calendar proration | Unit | Prorated minutes by remaining calendar days / period days |
| Mid-year hire, working-time proration | Unit | Prorated minutes by remaining working days / total working days |
| Schedule changes mid-period | Unit | Entitlement uses date-effective schedule slices for duration calculation |
| Carry-forward capped at policy limit | Unit | `carried_forward_minutes = MIN(available_minutes, carry_forward_limit_minutes)` |
| Carry-forward disabled | Unit | `carried_forward_minutes = 0` |
| Carry-forward expired | Unit | `carried_forward_minutes = 0` |
| Rollover logs forfeiture | Unit | Audit entry with `change_type = 'forfeiture'` and negative `minutes_changed` |
| Rollover creates next-period entitlement | Unit | New `time_off_entitlements` row for target period |
| No applicable policy for employee | Unit | Returns `NO_APPLICABLE_POLICY` error |
| Employee not found | Unit | Returns `EMPLOYEE_NOT_FOUND` error |
| GET entitlements returns 200 | Integration | HTTP 200 with minute balances |
| GET entitlements for unknown employee | Integration | HTTP 404 |
| GET entitlements without permission | Integration | HTTP 403 |
| Monthly accrual increments minutes | Unit | `entitlement_minutes += annual_entitlement_minutes / 12` per month |
| Idempotent rollover | Unit | Skips without duplicate entitlement |

## Related

- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
