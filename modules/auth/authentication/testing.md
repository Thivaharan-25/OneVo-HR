# Authentication — Testing

**Module:** Auth
**Feature:** Authentication
**Location:** `tests/ONEVO.Tests.Unit/Modules/Auth/AuthServiceTests.cs`

---

## Unit Tests

```csharp
public class AuthServiceTests
{
    private readonly Mock<IUserRepository> _userRepoMock = new();
    private readonly Mock<ITokenService> _tokenServiceMock = new();
    private readonly Mock<ISessionRepository> _sessionRepoMock = new();
    private readonly Mock<IRefreshTokenRepository> _refreshRepoMock = new();
    private readonly AuthService _sut;

    [Fact]
    public async Task LoginAsync_ValidCredentials_ReturnsTokenPair()
    {
        var user = CreateActiveUser();
        _userRepoMock.Setup(r => r.GetByEmailAsync(It.IsAny<string>(), It.IsAny<Guid>(), default)).ReturnsAsync(user);
        _tokenServiceMock.Setup(t => t.GenerateAccessTokenAsync(
            It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<List<string>>(), default)).ReturnsAsync("access-token");

        var result = await _sut.LoginAsync(new LoginCommand { Email = "test@onevo.com", Password = "valid" }, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.AccessToken.Should().NotBeEmpty();
    }

    [Fact]
    public async Task LoginAsync_InvalidPassword_ReturnsFailure()
    {
        var user = CreateActiveUser();
        _userRepoMock.Setup(r => r.GetByEmailAsync(It.IsAny<string>(), It.IsAny<Guid>(), default)).ReturnsAsync(user);

        var result = await _sut.LoginAsync(new LoginCommand { Email = "test@onevo.com", Password = "wrong" }, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Invalid credentials");
    }

    [Fact]
    public async Task LoginAsync_DisabledAccount_ReturnsForbidden()
    {
        var user = CreateActiveUser();
        user.IsActive = false;
        _userRepoMock.Setup(r => r.GetByEmailAsync(It.IsAny<string>(), It.IsAny<Guid>(), default)).ReturnsAsync(user);

        var result = await _sut.LoginAsync(new LoginCommand { Email = "test@onevo.com", Password = "valid" }, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("disabled");
    }

    [Fact]
    public async Task RefreshTokenAsync_RevokedToken_RevokesEntireChain()
    {
        var revokedToken = new RefreshToken { RevokedAt = DateTime.UtcNow };
        _refreshRepoMock.Setup(r => r.GetByHashAsync(It.IsAny<string>(), default)).ReturnsAsync(revokedToken);

        var result = await _sut.RefreshTokenAsync("some-token", default);

        result.IsSuccess.Should().BeFalse();
        _refreshRepoMock.Verify(r => r.RevokeChainAsync(It.IsAny<Guid>(), default), Times.Once);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Valid login | Unit | Token pair returned |
| Invalid password | Unit | Failure, generic message |
| Disabled account | Unit | Forbidden |
| MFA required | Unit | Returns MFA token |
| Refresh token reuse | Unit | Chain revoked |
| Account locked (5 failures) | Unit | 423 Locked |

## Related

- [[frontend/cross-cutting/authentication|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
