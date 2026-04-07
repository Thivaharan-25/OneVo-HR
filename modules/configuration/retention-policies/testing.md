# Retention Policies — Testing

**Module:** Configuration
**Feature:** Retention Policies
**Location:** `tests/ONEVO.Tests.Unit/Modules/Configuration/RetentionPolicyServiceTests.cs`

---

## Unit Tests

```csharp
public class RetentionPolicyServiceTests
{
    private readonly Mock<IRetentionPolicyRepository> _repoMock = new();
    private readonly RetentionPolicyService _sut;

    [Fact]
    public async Task UpdateAsync_AuditLogsBelowMinimum_ReturnsFailure()
    {
        var command = new UpdateRetentionCommand { DataType = "audit_logs", RetentionDays = 30 };

        var result = await _sut.UpdateAsync(command, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("minimum");
    }

    [Fact]
    public async Task UpdateAsync_ValidPolicy_Updates()
    {
        var command = new UpdateRetentionCommand { DataType = "screenshots", RetentionDays = 60 };
        var result = await _sut.UpdateAsync(command, default);
        result.IsSuccess.Should().BeTrue();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Audit logs below 365 days | Unit | Validation failure |
| Valid screenshot retention | Unit | Policy updated |

## Related

- [[configuration/retention-policies/overview|Retention Policies Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
