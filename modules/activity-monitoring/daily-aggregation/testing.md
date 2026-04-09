# Daily Aggregation — Testing

**Module:** Activity Monitoring
**Feature:** Daily Aggregation
**Location:** `tests/ONEVO.Tests.Unit/Modules/ActivityMonitoring/DailyAggregationServiceTests.cs`

---

## Unit Tests

```csharp
public class DailyAggregationServiceTests
{
    private readonly Mock<IActivitySnapshotRepository> _snapshotRepoMock = new();
    private readonly Mock<IMeetingSessionRepository> _meetingRepoMock = new();
    private readonly Mock<IActivityDailySummaryRepository> _summaryRepoMock = new();
    private readonly DailyAggregationService _sut;

    [Fact]
    public async Task AggregateAsync_WithSnapshots_CalculatesCorrectTotals()
    {
        var snapshots = new List<ActivitySnapshot>
        {
            new() { ActiveSeconds = 120, IdleSeconds = 30, IntensityScore = 80, KeyboardEventsCount = 100, MouseEventsCount = 50 },
            new() { ActiveSeconds = 140, IdleSeconds = 10, IntensityScore = 90, KeyboardEventsCount = 120, MouseEventsCount = 60 }
        };
        _snapshotRepoMock.Setup(r => r.GetByEmployeeDateAsync(It.IsAny<Guid>(), It.IsAny<DateOnly>(), default))
            .ReturnsAsync(snapshots);

        await _sut.AggregateAsync(_tenantId, DateOnly.FromDateTime(DateTime.Today), default);

        _summaryRepoMock.Verify(r => r.UpsertAsync(
            It.Is<ActivityDailySummary>(s =>
                s.TotalActiveMinutes == 4 && // (120+140)/60
                s.IntensityAvg == 85m &&
                s.KeyboardTotal == 220), default), Times.Once);
    }

    [Fact]
    public async Task AggregateAsync_NoData_SkipsEmployee()
    {
        _snapshotRepoMock.Setup(r => r.GetByEmployeeDateAsync(It.IsAny<Guid>(), It.IsAny<DateOnly>(), default))
            .ReturnsAsync(new List<ActivitySnapshot>());

        await _sut.AggregateAsync(_tenantId, DateOnly.FromDateTime(DateTime.Today), default);

        _summaryRepoMock.Verify(r => r.UpsertAsync(It.IsAny<ActivityDailySummary>(), default), Times.Never);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Multiple snapshots aggregated | Unit | Correct totals |
| No snapshot data | Unit | No summary created |
| Active percentage computed | Unit | active / (active + idle) * 100 |
| UPSERT on conflict | Unit | Existing summary updated |

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring Module]]
- [[modules/activity-monitoring/daily-aggregation/end-to-end-logic|Daily Aggregation — End-to-End Logic]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]]
