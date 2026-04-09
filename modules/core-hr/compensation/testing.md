# Compensation — Testing

**Module:** Core HR
**Feature:** Compensation
**Location:** `tests/ONEVO.Tests.Unit/Modules/CoreHR/CompensationServiceTests.cs`

---

## Unit Tests

```csharp
public class CompensationServiceTests
{
    private readonly Mock<ICompensationRepository> _repoMock = new();
    private readonly CompensationService _sut;

    [Fact]
    public async Task Update_salary_creates_history_record()
    {
        // Arrange
        // ... setup mocks for update salary creates history record

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // History row inserted
    }

    [Fact]
    public async Task Get_salary_history_returns_ordered_by_date()
    {
        // Arrange
        // ... setup mocks for get salary history returns ordered by date

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Descending order
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Update salary creates history record | Unit | History row inserted |
| Get salary history returns ordered by date | Unit | Descending order |

## Related

- [[modules/core-hr/compensation/overview|Compensation Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
