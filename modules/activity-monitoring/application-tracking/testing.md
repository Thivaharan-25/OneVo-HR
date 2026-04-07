# Application Tracking — Testing

**Module:** Activity Monitoring
**Feature:** Application Tracking
**Location:** `tests/ONEVO.Tests.Unit/Modules/ActivityMonitoring/ApplicationTrackingServiceTests.cs`

---

## Unit Tests

```csharp
public class ApplicationTrackingServiceTests
{
    private readonly Mock<IApplicationUsageRepository> _repoMock = new();
    private readonly Mock<IApplicationCategoryRepository> _categoryRepoMock = new();
    private readonly ApplicationTrackingService _sut;

    [Fact]
    public async Task GetAppUsageAsync_ReturnsGroupedByCategory()
    {
        var usage = new List<ApplicationUsage>
        {
            new() { ApplicationName = "Chrome", ApplicationCategory = "Browser", TotalSeconds = 3600 },
            new() { ApplicationName = "VS Code", ApplicationCategory = "IDE", TotalSeconds = 7200 }
        };
        _repoMock.Setup(r => r.GetByEmployeeDateAsync(It.IsAny<Guid>(), It.IsAny<DateOnly>(), default))
            .ReturnsAsync(usage);

        var result = await _sut.GetAppUsageAsync(_employeeId, DateOnly.FromDateTime(DateTime.Today), default);

        result.IsSuccess.Should().BeTrue();
        result.Value.Should().HaveCount(2);
        result.Value.First().TotalSeconds.Should().Be(7200); // sorted by time DESC
    }

    [Fact]
    public async Task CreateCategoryAsync_DuplicatePattern_ReturnsConflict()
    {
        _categoryRepoMock.Setup(r => r.ExistsByPatternAsync(It.IsAny<string>(), default)).ReturnsAsync(true);

        var result = await _sut.CreateCategoryAsync(new CreateCategoryCommand { ApplicationNamePattern = "*chrome*" }, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("already exists");
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Usage grouped by category | Unit | Correct grouping |
| Sorted by total_seconds DESC | Unit | Most-used first |
| Duplicate category pattern | Unit | 409 Conflict |
| No data for date | Unit | Empty list returned |

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[application-tracking/end-to-end-logic|Application Tracking — End-to-End Logic]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
- [[WEEK3-activity-monitoring]]
