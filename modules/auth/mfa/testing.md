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
        SetupValidEmailOtpChallenge();

        var result = await _sut.VerifyAsync(_userId, _validCode, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.AccessToken.Should().NotBeEmpty();
    }

    [Fact]
    public async Task VerifyAsync_InvalidCode_IncrementsAttempts()
    {
        SetupValidEmailOtpChallenge();

        var result = await _sut.VerifyAsync(_userId, "000000", default);

        result.IsSuccess.Should().BeFalse();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Valid email OTP code | Unit | Token pair returned |
| OTP delivery boundary called | Unit | Email/notification service receives send request |
| Expired OTP | Unit | Failure, requires resend |
| Invalid code | Unit | Failure, attempt incremented |
| MFA locked (3 attempts) | Unit | 423 Locked |
| MFA not enabled | Unit | 400 Bad Request |

## Related

- [[mfa|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
