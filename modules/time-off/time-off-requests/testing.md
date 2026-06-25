# Time Off Requests - Testing

**Module:** Time Off
**Feature:** Time Off Requests
**Location:** `tests/ONEVO.Tests.Unit/Modules/TimeOff/TimeOffRequestServiceTests.cs`

---

## Unit Tests

```csharp
public class TimeOffRequestServiceTests
{
    private readonly Mock<ITimeOffRequestRepository> _repoMock = new();
    private readonly Mock<ITimeOffEntitlementRepository> _entitlementRepoMock = new();
    private readonly Mock<ITimeOffCalculationService> _calculationServiceMock = new();
    private readonly Mock<ICalendarConflictService> _conflictServiceMock = new();
    private readonly TimeOffRequestService _sut;

    [Fact]
    public async Task SubmitRequestAsync_WithSufficientMinuteBalance_ReturnsSuccess()
    {
        SetupEntitlement(availableMinutes: 7200);
        SetupNoOverlaps();
        SetupNoConflicts();
        _calculationServiceMock.Setup(x => x.CalculateDurationMinutesAsync(It.IsAny<CreateTimeOffRequestCommand>(), default))
            .ReturnsAsync(1440);

        var command = new CreateTimeOffRequestCommand
        {
            TimeOffTypeId = _annualTypeId,
            StartDate = DateOnly.FromDateTime(DateTime.Today.AddDays(7)),
            EndDate = DateOnly.FromDateTime(DateTime.Today.AddDays(9)),
            RequestDurationMinutes = 1440,
            Reason = "Vacation"
        };

        var result = await _sut.SubmitRequestAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Status.Should().Be("pending");
        result.Value.RequestDurationMinutes.Should().Be(1440);
    }

    [Fact]
    public async Task SubmitRequestAsync_WithInsufficientMinuteBalance_ReturnsFailure()
    {
        SetupEntitlement(availableMinutes: 240);
        _calculationServiceMock.Setup(x => x.CalculateDurationMinutesAsync(It.IsAny<CreateTimeOffRequestCommand>(), default))
            .ReturnsAsync(960);

        var result = await _sut.SubmitRequestAsync(_longLeaveCommand, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Insufficient");
    }

    [Fact]
    public async Task SubmitRequestAsync_WithOverlap_ReturnsConflict()
    {
        SetupEntitlement(availableMinutes: 7200);
        _repoMock.Setup(r => r.HasOverlappingAsync(
                It.IsAny<Guid>(), It.IsAny<DateOnly>(), It.IsAny<DateOnly>(), default))
            .ReturnsAsync(true);

        var result = await _sut.SubmitRequestAsync(_validCommand, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Overlapping");
    }

    [Fact]
    public async Task SubmitRequestAsync_WithCalendarConflicts_SucceedsWithWarnings()
    {
        SetupEntitlement(availableMinutes: 7200);
        SetupNoOverlaps();
        _calculationServiceMock.Setup(x => x.CalculateDurationMinutesAsync(It.IsAny<CreateTimeOffRequestCommand>(), default))
            .ReturnsAsync(480);
        _conflictServiceMock.Setup(s => s.GetConflictsForDateRangeAsync(
                It.IsAny<Guid>(), It.IsAny<DateOnly>(), It.IsAny<DateOnly>(), default))
            .ReturnsAsync(Result.Success(new TimeOffConflictSummaryDto { HasConflicts = true }));

        var result = await _sut.SubmitRequestAsync(_validCommand, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.ConflictSnapshotJson.Should().NotBeNull();
    }

    [Fact]
    public async Task ApproveAsync_UpdatesMinuteBalanceAndPublishesEvent()
    {
        var request = new TimeOffRequest { Status = "pending", RequestDurationMinutes = 1440, DeductionMinutes = 0 };
        _repoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync(request);
        var entitlement = new TimeOffEntitlement { UsedMinutes = 2400, AvailableMinutes = 7200 };
        _entitlementRepoMock.Setup(r => r.GetAsync(
                It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<int>(), default))
            .ReturnsAsync(entitlement);

        var result = await _sut.ApproveAsync(request.Id, default);

        result.IsSuccess.Should().BeTrue();
        request.DeductionMinutes.Should().Be(1440);
        entitlement.UsedMinutes.Should().Be(3840);
        entitlement.AvailableMinutes.Should().Be(5760);
    }

    [Fact]
    public async Task CancelAsync_WhenApproved_ReversesMinuteDeduction()
    {
        var request = new TimeOffRequest { Status = "approved", DeductionMinutes = 1440 };
        _repoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync(request);
        var entitlement = new TimeOffEntitlement { UsedMinutes = 3840, AvailableMinutes = 5760 };

        await _sut.CancelAsync(request.Id, default);

        entitlement.UsedMinutes.Should().Be(2400);
        entitlement.AvailableMinutes.Should().Be(7200);
    }
}
```

## Integration Tests

```csharp
public class TimeOffRequestEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task FullFlow_Submit_Approve_VerifyMinuteBalance()
    {
        var submit = new
        {
            TimeOffTypeId = _annualTypeId,
            StartDate = "2026-04-20",
            EndDate = "2026-04-22",
            RequestDurationMinutes = 1440,
            Reason = "Vacation"
        };

        var submitResp = await _employeeClient.PostAsJsonAsync("/api/v1/time-off/requests", submit);
        submitResp.StatusCode.Should().Be(HttpStatusCode.Created);
        var request = await submitResp.Content.ReadFromJsonAsync<TimeOffRequestDto>();
        request!.RequestDurationMinutes.Should().BeGreaterThan(0);

        var approveResp = await _managerClient.PutAsync($"/api/v1/time-off/requests/{request.Id}/approve", null);
        approveResp.StatusCode.Should().Be(HttpStatusCode.OK);

        var entitlement = await _employeeClient.GetFromJsonAsync<TimeOffEntitlementDto>(
            $"/api/v1/time-off/entitlements/{_employeeId}");
        entitlement!.UsedMinutes.Should().BeGreaterThan(0);
    }

    [Fact]
    public async Task Submit_WithInsufficientBalance_Returns422()
    {
        var submit = new { TimeOffTypeId = _annualTypeId, StartDate = "2026-01-01", EndDate = "2026-12-31", RequestDurationMinutes = 124800 };
        var response = await _employeeClient.PostAsJsonAsync("/api/v1/time-off/requests", submit);
        response.StatusCode.Should().Be(HttpStatusCode.UnprocessableEntity);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Submit duration-based request with sufficient minute balance | Unit | Success, status = pending |
| Submit with insufficient minute balance | Unit | Failure unless policy allows over-balance/unpaid behavior |
| Submit with overlapping dates/times | Unit | Failure |
| Submit with calendar conflicts | Unit | Success + conflict snapshot |
| Exceeds maximum consecutive minutes | Unit | Failure |
| Approve pending request | Unit | `used_minutes` increments and `deduction_minutes` is captured |
| Approve already-approved | Unit | Failure |
| Cancel approved request | Unit | `deduction_minutes` is restored on cancellation |
| Full submit-approve flow | Integration | Minute balance correctly updated |
| Tenant isolation | Integration | Cannot see other tenant requests |

## Related

- [[modules/time-off/time-off-requests/overview|Time Off Requests Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
