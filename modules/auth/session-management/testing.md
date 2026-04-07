# Session Management — Testing

**Module:** Auth
**Feature:** Session Management
**Location:** `tests/ONEVO.Tests.Unit/Modules/Auth/SessionServiceTests.cs`

---

## Unit Tests

```csharp
public class SessionServiceTests
{
    private readonly Mock<ISessionRepository> _sessionRepoMock = new();
    private readonly Mock<IRefreshTokenRepository> _refreshRepoMock = new();
    private readonly SessionService _sut;

    [Fact]
    public async Task LogoutAsync_RevokesSessionAndTokens()
    {
        var session = new Session { Id = _sessionId, IsRevoked = false };
        _sessionRepoMock.Setup(r => r.GetByIdAsync(_sessionId, default)).ReturnsAsync(session);

        await _sut.LogoutAsync(_sessionId, _userId, default);

        session.IsRevoked.Should().BeTrue();
        _refreshRepoMock.Verify(r => r.RevokeAllForUserAsync(_userId, default), Times.Once);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Logout revokes session | Unit | Session marked revoked |
| Logout revokes refresh tokens | Unit | All tokens revoked |
| Expired session rejected | Unit | 401 returned |

## Related

- [[session-management|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
