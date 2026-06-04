# Legal & Privacy Acceptance - Testing

**Module:** Auth
**Feature:** Legal & Privacy Acceptance
**Location:** `tests/ONEVO.Tests.Unit/Modules/Auth/LegalAcceptanceServiceTests.cs`

---

## Unit Tests

```csharp
public class LegalAcceptanceServiceTests
{
    private readonly Mock<ILegalAcceptanceRepository> _repoMock = new();
    private readonly Mock<IConfigurationService> _configMock = new();
    private readonly LegalAcceptanceService _sut;

    [Fact]
    public async Task RecordAsync_WorkPulseScreenshotNoticeMissing_DisablesScreenshotCollector()
    {
        var command = new RecordLegalDecisionCommand
        {
            DocumentType = "screenshot_notice",
            Decision = "declined",
            Source = "desktop-agent"
        };

        await _sut.RecordAsync(command, default);

        _configMock.Verify(c => c.SetEmployeeOverrideAsync(
            It.Is<SetOverrideCommand>(o =>
                o.ScreenshotCapture == false), default), Times.Once);
    }

    [Fact]
    public async Task HasRequiredDecisionAsync_NoRecord_ReturnsFalse()
    {
        _repoMock.Setup(r => r.GetAsync(It.IsAny<Guid>(), "biometric_photo_consent", default)).ReturnsAsync((LegalAcceptanceRecord?)null);

        var result = await _sut.HasRequiredDecisionAsync(_userId, "biometric_photo_consent", default);

        result.Should().BeFalse();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Record Terms acceptance | Unit | Versioned acceptance saved |
| Record Privacy Notice acknowledgement | Unit | Versioned acknowledgement saved |
| Missing WorkPulse screenshot notice | Unit | Screenshot collector disabled |
| Check biometric/photo consent | Unit | Returns true/false |
| No legal acceptance record | Unit | Returns false |

## Related

- [[Userflow/Auth-Access/gdpr-consent|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
