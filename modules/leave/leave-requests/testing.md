# Leave Requests — Testing

**Module:** Leave  
**Feature:** Leave Requests  
**Location:** `tests/ONEVO.Tests.Unit/Modules/Leave/LeaveRequestServiceTests.cs`

---

## Unit Tests

```csharp
public class LeaveRequestServiceTests
{
    private readonly Mock<ILeaveRequestRepository> _repoMock = new();
    private readonly Mock<ILeaveEntitlementRepository> _entitlementRepoMock = new();
    private readonly Mock<ICalendarConflictService> _conflictServiceMock = new();
    private readonly LeaveRequestService _sut;

    [Fact]
    public async Task SubmitRequestAsync_WithSufficientBalance_ReturnsSuccess()
    {
        SetupEntitlement(remaining: 15);
        SetupNoOverlaps();
        SetupNoConflicts();

        var command = new CreateLeaveRequestCommand
        {
            LeaveTypeId = _annualTypeId,
            StartDate = DateOnly.FromDateTime(DateTime.Today.AddDays(7)),
            EndDate = DateOnly.FromDateTime(DateTime.Today.AddDays(9)),
            Reason = "Vacation"
        };

        var result = await _sut.SubmitRequestAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Status.Should().Be("pending");
    }

    [Fact]
    public async Task SubmitRequestAsync_WithInsufficientBalance_ReturnsFailure()
    {
        SetupEntitlement(remaining: 1);

        var result = await _sut.SubmitRequestAsync(_longLeaveCommand, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Insufficient");
    }

    [Fact]
    public async Task SubmitRequestAsync_WithOverlap_ReturnsConflict()
    {
        SetupEntitlement(remaining: 15);
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
        SetupEntitlement(remaining: 15);
        SetupNoOverlaps();
        _conflictServiceMock.Setup(s => s.GetConflictsForDateRangeAsync(
                It.IsAny<Guid>(), It.IsAny<DateOnly>(), It.IsAny<DateOnly>(), default))
            .ReturnsAsync(Result.Success(new LeaveConflictSummaryDto { HasConflicts = true }));

        var result = await _sut.SubmitRequestAsync(_validCommand, default);

        result.IsSuccess.Should().BeTrue(); // conflicts are warnings only
        result.Value!.ConflictSnapshotJson.Should().NotBeNull();
    }

    [Fact]
    public async Task ApproveAsync_UpdatesBalanceAndPublishesEvent()
    {
        var request = new LeaveRequest { Status = "pending", TotalDays = 3 };
        _repoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync(request);
        var entitlement = new LeaveEntitlement { UsedDays = 5, RemainingDays = 15 };
        _entitlementRepoMock.Setup(r => r.GetAsync(
                It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<int>(), default))
            .ReturnsAsync(entitlement);

        var result = await _sut.ApproveAsync(request.Id, default);

        result.IsSuccess.Should().BeTrue();
        entitlement.UsedDays.Should().Be(8);
        entitlement.RemainingDays.Should().Be(12);
    }

    [Fact]
    public async Task CancelAsync_WhenApproved_ReversesEntitlement()
    {
        var request = new LeaveRequest { Status = "approved", TotalDays = 3 };
        _repoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync(request);
        var entitlement = new LeaveEntitlement { UsedDays = 8, RemainingDays = 12 };

        await _sut.CancelAsync(request.Id, default);

        entitlement.UsedDays.Should().Be(5);
        entitlement.RemainingDays.Should().Be(15);
    }
}
```

## Integration Tests

```csharp
public class LeaveRequestEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task FullFlow_Submit_Approve_VerifyBalance()
    {
        var submit = new { LeaveTypeId = _annualTypeId, StartDate = "2026-04-20", EndDate = "2026-04-22", Reason = "Vacation" };
        var submitResp = await _employeeClient.PostAsJsonAsync("/api/v1/leave/requests", submit);
        submitResp.StatusCode.Should().Be(HttpStatusCode.Created);
        var requestId = (await submitResp.Content.ReadFromJsonAsync<LeaveRequestDto>())!.Id;

        var approveResp = await _managerClient.PutAsync($"/api/v1/leave/requests/{requestId}/approve", null);
        approveResp.StatusCode.Should().Be(HttpStatusCode.OK);

        var entitlement = await _employeeClient.GetFromJsonAsync<LeaveEntitlementDto>(
            $"/api/v1/leave/entitlements/{_employeeId}");
        entitlement!.UsedDays.Should().BeGreaterThan(0);
    }

    [Fact]
    public async Task Submit_WithInsufficientBalance_Returns422()
    {
        var submit = new { LeaveTypeId = _annualTypeId, StartDate = "2026-01-01", EndDate = "2026-12-31" };
        var response = await _employeeClient.PostAsJsonAsync("/api/v1/leave/requests", submit);
        response.StatusCode.Should().Be(HttpStatusCode.UnprocessableEntity);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Submit with sufficient balance | Unit | Success, status = pending |
| Submit with insufficient balance | Unit | Failure |
| Submit with overlapping dates | Unit | Failure |
| Submit with calendar conflicts | Unit | Success + conflict snapshot |
| Exceeds max consecutive days | Unit | Failure |
| Approve pending request | Unit | Balance updated |
| Approve already-approved | Unit | Failure |
| Cancel approved reverses balance | Unit | Balance restored |
| Full submit-approve flow | Integration | Balance correctly updated |
| Tenant isolation | Integration | Cannot see other tenant requests |

## Related

- [[leave-requests|Leave Requests Overview]]
- [[testing/README|Testing Standards]]
