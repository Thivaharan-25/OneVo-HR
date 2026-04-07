# Feature Flags — Testing

**Module:** Shared Platform
**Feature:** Feature Flags
**Location:** `tests/ONEVO.Tests.Unit/Modules/SharedPlatform/FeatureFlagServiceTests.cs`

---

## Unit Tests

```csharp
public class FeatureFlagServiceTests
{
    private readonly Mock<IFeatureFlagRepository> _repoMock = new();
    private readonly FeatureFlagService _sut;

    [Fact]
    public async Task Check_flag_returns_cached_value()
    {
        // Arrange
        // ... setup mocks for check flag returns cached value

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Redis cache hit
    }

    [Fact]
    public async Task Toggle_invalidates_cache()
    {
        // Arrange
        // ... setup mocks for toggle invalidates cache

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Cache cleared
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Check flag returns cached value | Unit | Redis cache hit |
| Toggle invalidates cache | Unit | Cache cleared |

## Related

- [[feature-flags|Overview]]
- [[testing/README|Testing Standards]]
