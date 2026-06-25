# Resource Management - Testing

**Module:** WorkSync
**Feature:** Resource Management
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Resources/`

---

## Unit Tests

```csharp
public class ResourceServiceTests
{
    [Fact]
    public async Task CreateAllocation_OverAllocation_EmitsWarning()
    {
        SetupExistingAllocation(_userId, percentage: 80, overlappingDates: true);
        var result = await _sut.CreateAllocationAsync(
            _projectId, _userId, 30, _startDate, _endDate, default);
        result.IsSuccess.Should().BeTrue(); // not a hard block
        _eventPublisherMock.Verify(p =>
            p.PublishAsync(It.IsAny<ResourceOverAllocatedEvent>(), default), Times.Once);
    }

    [Fact]
    public async Task CreateAllocation_UserNotInWorkspace_ReturnsFailure()
    {
        SetupUserNotInWorkspace(_userId, _workspaceId);
        var result = await _sut.CreateAllocationAsync(
            _projectId, _userId, 50, _startDate, _endDate, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("workspace member");
    }

    [Fact]
    public async Task CalculateAvailability_SubtractsTimeOffHours()
    {
        SetupContractedHours(_userId, hoursPerDay: 8);
        SetupNoOverrides(_userId);
        SetupTimeOffHours(_userId, leaveHours: 40, inPeriod: (_startDate, _endDate));
        var workingDays = 20; // assume 4 working weeks
        var availability = await _sut.GetAvailabilityAsync(_userId, _startDate, _endDate, default);
        availability.AvailableHours.Should().Be((workingDays * 8) - 40); // 120 hours
    }

    [Fact]
    public async Task AvailabilityOverride_TakesPrecedenceOverContract()
    {
        SetupContractedHours(_userId, hoursPerDay: 8);
        SetupOverride(_userId, availableHoursPerDay: 4, _startDate, _endDate);
        var availability = await _sut.GetAvailabilityAsync(_userId, _startDate, _endDate, default);
        availability.HoursPerDay.Should().Be(4); // override wins
    }
}
```

## Test Scenarios

Time Off remains stored and calculated in minutes. Resource Management converts approved Time Off minutes into derived capacity hours only for planning calculations.

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Over-allocation (> 100%) emits warning | Unit | Success + warning event |
| User not in workspace | Unit | Failure |
| Availability subtracts derived Time Off capacity hours | Unit | Approved Time Off minutes are converted to derived hours before capacity calculation |
| Override takes precedence | Unit | Override hours used |
| Allocation percentage 0 | Unit | Validation failure |

## Related

- [[modules/work-management/resources/overview|Resources Overview]]
- [[modules/work-management/resources/end-to-end-logic|Resources Logic]]
