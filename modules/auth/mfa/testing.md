# MFA — Testing

**Module:** Auth
**Feature:** Multi-Factor Authentication
**Location:** `tests/ONEVO.Tests.Unit/Modules/Auth/MfaServiceTests.cs`

---

## Unit Tests

```csharp
public class MfaServiceTests
{
    private readonly Mock<IMfaRepository> _mfaRepoMock = new();
    private readonly Mock<ITokenService> _tokenServiceMock = new();
    private readonly MfaService _sut;

    [Fact]
    public async Task VerifyAsync_ValidCode_ReturnsTokenPair()
    {
        SetupValidTotpSecret();

        var result = await _sut.VerifyAsync(_userId, _validCode, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.AccessToken.Should().NotBeEmpty();
    }

    [Fact]
    public async Task VerifyAsync_InvalidCode_IncrementsAttempts()
    {
        SetupValidTotpSecret();

        var result = await _sut.VerifyAsync(_userId, "000000", default);

        result.IsSuccess.Should().BeFalse();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Valid TOTP code | Unit | Token pair returned |
| Invalid code | Unit | Failure, attempt incremented |
| MFA locked (5 attempts) | Unit | 423 Locked |
| MFA not enabled | Unit | 400 Bad Request |

## Related

- [[mfa|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
