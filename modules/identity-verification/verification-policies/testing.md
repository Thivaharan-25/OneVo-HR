# Verification Policies — Testing

**Module:** Identity Verification
**Feature:** Verification Policies
**Location:** `tests/ONEVO.Tests.Unit/Modules/IdentityVerification/VerificationPolicyServiceTests.cs`

---

## Unit Tests

```csharp
public class VerificationPolicyServiceTests
{
    private readonly Mock<IVerificationPolicyRepository> _repoMock = new();
    private readonly VerificationPolicyService _sut;

    [Fact]
    public async Task Update_policy_validates_threshold_range()
    {
        // Arrange
        // ... setup mocks for update policy validates threshold range

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 0-100 enforced
    }

    [Fact]
    public async Task Get_policy_returns_tenant_config()
    {
        // Arrange
        // ... setup mocks for get policy returns tenant config

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Policy returned
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Update policy validates threshold range | Unit | 0-100 enforced |
| Get policy returns tenant config | Unit | Policy returned |

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[modules/identity-verification/verification-policies/end-to-end-logic|Verification Policies — End-to-End Logic]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
