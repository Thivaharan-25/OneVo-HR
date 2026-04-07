# Compliance & Governance — Testing

**Module:** Shared Platform
**Feature:** Compliance & Governance
**Location:** `tests/ONEVO.Tests.Unit/Modules/SharedPlatform/ComplianceServiceTests.cs`

---

## Unit Tests

```csharp
public class ComplianceServiceTests
{
    private readonly Mock<IComplianceRepository> _repoMock = new();
    private readonly ComplianceService _sut;

    [Fact]
    public async Task Legal_hold_prevents_deletion()
    {
        // Arrange
        // ... setup mocks for legal hold prevents deletion

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Purge job skips held data
    }

    [Fact]
    public async Task GDPR_export_collects_all_user_data()
    {
        // Arrange
        // ... setup mocks for gdpr export collects all user data

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // ZIP file generated
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Legal hold prevents deletion | Unit | Purge job skips held data |
| GDPR export collects all user data | Unit | ZIP file generated |

## Related

- [[compliance-governance|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
