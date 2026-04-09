# Exception Rules — Testing

**Module:** Exception Engine
**Feature:** Exception Rules
**Location:** `tests/ONEVO.Tests.Unit/Modules/ExceptionEngine/ExceptionRuleServiceTests.cs`

---

## Unit Tests

```csharp
public class ExceptionRuleServiceTests
{
    private readonly Mock<IExceptionRuleRepository> _repoMock = new();
    private readonly ExceptionRuleService _sut;

    [Fact]
    public async Task Create_rule_with_valid_threshold_json_succeeds()
    {
        // Arrange
        // ... setup mocks for create rule with valid threshold_json succeeds

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Rule created
    }

    [Fact]
    public async Task Invalid_threshold_json_returns_validation_error()
    {
        // Arrange
        // ... setup mocks for invalid threshold_json returns validation error

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 422 returned
    }

    [Fact]
    public async Task Invalid_rule_type_rejected()
    {
        // Arrange
        // ... setup mocks for invalid rule_type rejected

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 422 returned
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create rule with valid threshold_json succeeds | Unit | Rule created |
| Invalid threshold_json returns validation error | Unit | 422 returned |
| Invalid rule_type rejected | Unit | 422 returned |

## Related

- [[frontend/architecture/overview|Exception Rules Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
