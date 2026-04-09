# Succession Planning — Testing

**Module:** Performance
**Feature:** Succession Planning
**Location:** `tests/ONEVO.Tests.Unit/Modules/Performance/SuccessionServiceTests.cs`

---

## Unit Tests

```csharp
public class SuccessionServiceTests
{
    private readonly Mock<ISuccessionRepository> _repoMock = new();
    private readonly SuccessionService _sut;

    [Fact]
    public async Task Create_plan_links_successor()
    {
        // Arrange
        // ... setup mocks for create plan links successor

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Plan created
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create plan links successor | Unit | Plan created |

## Related

- [[database/performance|Performance Module]]
- [[modules/performance/succession-planning/end-to-end-logic|Succession Planning — End-to-End Logic]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
- Performance task file (deferred to Phase 2)
