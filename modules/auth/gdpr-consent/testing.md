# GDPR Consent — Testing

**Module:** Auth
**Feature:** GDPR Consent
**Location:** `tests/ONEVO.Tests.Unit/Modules/Auth/ConsentServiceTests.cs`

---

## Unit Tests

```csharp
public class ConsentServiceTests
{
    private readonly Mock<IGdprConsentRepository> _repoMock = new();
    private readonly Mock<IConfigurationService> _configMock = new();
    private readonly ConsentService _sut;

    [Fact]
    public async Task RecordAsync_MonitoringConsentWithdrawn_DisablesMonitoring()
    {
        var command = new RecordConsentCommand { ConsentType = "monitoring", Consented = false };

        await _sut.RecordAsync(command, default);

        _configMock.Verify(c => c.SetEmployeeOverrideAsync(
            It.Is<SetOverrideCommand>(o =>
                o.ActivityMonitoring == false &&
                o.ScreenshotCapture == false), default), Times.Once);
    }

    [Fact]
    public async Task HasConsentAsync_NoRecord_ReturnsFalse()
    {
        _repoMock.Setup(r => r.GetAsync(It.IsAny<Guid>(), "biometric", default)).ReturnsAsync((GdprConsentRecord?)null);

        var result = await _sut.HasConsentAsync(_userId, "biometric", default);

        result.Should().BeFalse();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Record monitoring consent | Unit | Consent saved |
| Withdraw monitoring | Unit | Monitoring disabled |
| Check biometric consent | Unit | Returns true/false |
| No consent record | Unit | Returns false |

## Related

- [[gdpr-consent|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
