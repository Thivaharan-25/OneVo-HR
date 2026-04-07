# Tax Configuration — Testing

**Module:** Payroll
**Feature:** Tax Configuration
**Location:** `tests/ONEVO.Tests.Unit/Modules/Payroll/TaxConfigServiceTests.cs`

---

## Unit Tests

```csharp
public class TaxConfigServiceTests
{
    private readonly Mock<ITaxConfigRepository> _repoMock = new();
    private readonly TaxConfigService _sut;

    [Fact]
    public async Task Create_with_valid_brackets_succeeds()
    {
        // Arrange
        // ... setup mocks for create with valid brackets succeeds

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Config created
    }

    [Fact]
    public async Task Overlapping_brackets_rejected()
    {
        // Arrange
        // ... setup mocks for overlapping brackets rejected

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Validation failure
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create with valid brackets succeeds | Unit | Config created |
| Overlapping brackets rejected | Unit | Validation failure |

## Related

- [[payroll/tax-configuration/overview|Tax Configuration Overview]]
- [[testing/README|Testing Standards]]
