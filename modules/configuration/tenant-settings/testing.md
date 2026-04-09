# Tenant Settings — Testing

**Module:** Configuration
**Feature:** Tenant Settings
**Location:** `tests/ONEVO.Tests.Unit/Modules/Configuration/TenantSettingsServiceTests.cs`

---

## Unit Tests

```csharp
public class TenantSettingsServiceTests
{
    private readonly Mock<ITenantSettingsRepository> _repoMock = new();
    private readonly ConfigurationService _sut;

    [Fact]
    public async Task GetTenantSettingsAsync_ExistingTenant_ReturnsSettings()
    {
        _repoMock.Setup(r => r.GetByTenantAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(new TenantSettings { Timezone = "Asia/Colombo" });

        var result = await _sut.GetTenantSettingsAsync(default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Timezone.Should().Be("Asia/Colombo");
    }

    [Fact]
    public async Task UpdateTenantSettingsAsync_InvalidTimezone_ReturnsFailure()
    {
        var command = new UpdateSettingsCommand { Timezone = "Invalid/Zone" };
        var result = await _sut.UpdateTenantSettingsAsync(command, default);
        result.IsSuccess.Should().BeFalse();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Get existing settings | Unit | Settings returned |
| Invalid timezone | Unit | Validation failure |
| Settings auto-created for new tenant | Unit | Defaults applied |

## Related

- [[frontend/architecture/overview|Tenant Settings Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
