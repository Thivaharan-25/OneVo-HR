# Reference Data — Testing

**Module:** Infrastructure
**Feature:** Reference Data
**Location:** `tests/ONEVO.Tests.Unit/Modules/Infrastructure/ReferenceDataServiceTests.cs`

---

## Unit Tests

```csharp
public class ReferenceDataServiceTests
{
    private readonly Mock<IReferenceDataRepository> _repoMock = new();
    private readonly ReferenceDataService _sut;

    [Fact]
    public async Task Get_countries_returns_cached_list()
    {
        // Arrange
        // ... setup mocks for get countries returns cached list

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Countries from cache
    }

    [Fact]
    public async Task Countries_not_tenant_scoped()
    {
        // Arrange
        // ... setup mocks for countries not tenant scoped

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // No tenant filter applied
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Get countries returns cached list | Unit | Countries from cache |
| Countries not tenant scoped | Unit | No tenant filter applied |

## Related

- [[modules/infrastructure/reference-data/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
