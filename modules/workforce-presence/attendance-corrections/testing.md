# Attendance Corrections — Testing

**Module:** Workforce Presence
**Feature:** Attendance Corrections
**Location:** `tests/ONEVO.Tests.Unit/Modules/WorkforcePresence/CorrectionServiceTests.cs`

---

## Unit Tests

```csharp
public class CorrectionServiceTests
{
    private readonly Mock<ICorrectionRepository> _repoMock = new();
    private readonly CorrectionService _sut;

    [Fact]
    public async Task Submit_correction_triggers_re-reconciliation()
    {
        // Arrange
        // ... setup mocks for submit correction triggers re-reconciliation

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Presence session updated
    }

    [Fact]
    public async Task Correction_logs_audit_trail()
    {
        // Arrange
        // ... setup mocks for correction logs audit trail

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Original and corrected values stored
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Submit correction triggers re-reconciliation | Unit | Presence session updated |
| Correction logs audit trail | Unit | Original and corrected values stored |

## Related

- [[attendance-corrections|Attendance Corrections Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
