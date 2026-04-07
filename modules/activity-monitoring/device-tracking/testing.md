# Device Tracking — Testing

**Module:** Activity Monitoring
**Feature:** Device Tracking
**Location:** `tests/ONEVO.Tests.Unit/Modules/ActivityMonitoring/DeviceTrackingServiceTests.cs`

---

## Unit Tests

```csharp
public class DeviceTrackingServiceTests
{
    private readonly Mock<IDeviceTrackingRepository> _repoMock = new();
    private readonly Mock<IDeviceSessionRepository> _sessionRepoMock = new();
    private readonly DeviceTrackingService _sut;

    [Fact]
    public async Task ProcessDeviceDataAsync_WithSessions_CalculatesLaptopMinutes()
    {
        var sessions = new List<DeviceSession>
        {
            new() { ActiveMinutes = 50, IdleMinutes = 10 },
            new() { ActiveMinutes = 40, IdleMinutes = 20 }
        };
        _sessionRepoMock.Setup(r => r.GetByEmployeeDateAsync(It.IsAny<Guid>(), It.IsAny<DateOnly>(), default))
            .ReturnsAsync(sessions);

        await _sut.ProcessDeviceDataAsync(_employeeId, DateOnly.FromDateTime(DateTime.Today), default);

        _repoMock.Verify(r => r.UpsertAsync(
            It.Is<DeviceTracking>(d => d.LaptopActiveMinutes == 90), default), Times.Once);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Sessions aggregated to laptop minutes | Unit | Correct sum |
| No sessions for day | Unit | No tracking row |
| Multiple devices summed | Unit | Combined total |

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[device-tracking/end-to-end-logic|Device Tracking — End-to-End Logic]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
- [[WEEK3-activity-monitoring]]
