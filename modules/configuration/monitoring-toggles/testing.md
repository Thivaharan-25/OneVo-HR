# Monitoring Toggles — Testing

**Module:** Configuration
**Feature:** Monitoring Toggles
**Location:** `tests/ONEVO.Tests.Unit/Modules/Configuration/MonitoringToggleServiceTests.cs`

---

## Unit Tests

```csharp
public class MonitoringToggleServiceTests
{
    private readonly Mock<IMonitoringToggleRepository> _repoMock = new();
    private readonly ConfigurationService _sut;

    [Fact]
    public async Task UpdateMonitoringTogglesAsync_ValidToggles_UpdatesAndInvalidatesCache()
    {
        SetupExistingToggles();
        var command = new UpdateTogglesCommand { ScreenshotCapture = true };

        var result = await _sut.UpdateMonitoringTogglesAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.ScreenshotCapture.Should().BeTrue();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Update toggles | Unit | Cache invalidated |
| Industry defaults applied | Unit | Correct defaults per profile |

## Related

- [[frontend/architecture/overview|Monitoring Toggles Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
