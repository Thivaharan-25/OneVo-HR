# Agent Registration — Testing

**Module:** Agent Gateway
**Feature:** Agent Registration
**Location:** `tests/ONEVO.Tests.Unit/Modules/AgentGateway/AgentRegistrationServiceTests.cs`

---

## Unit Tests

```csharp
public class AgentRegistrationServiceTests
{
    private readonly Mock<IRegisteredAgentRepository> _repoMock = new();
    private readonly Mock<ITokenService> _tokenServiceMock = new();
    private readonly Mock<IConfigurationService> _configMock = new();
    private readonly AgentRegistrationService _sut;

    [Fact]
    public async Task RegisterAsync_NewDevice_CreatesAgentAndReturnsJwt()
    {
        _repoMock.Setup(r => r.GetByDeviceIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync((RegisteredAgent?)null);
        _tokenServiceMock.Setup(t => t.GenerateDeviceTokenAsync(It.IsAny<Guid>(), It.IsAny<Guid>(), default))
            .ReturnsAsync("device-jwt-token");

        var result = await _sut.RegisterAsync(_validCommand, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.DeviceJwt.Should().Be("device-jwt-token");
        _repoMock.Verify(r => r.InsertAsync(It.IsAny<RegisteredAgent>(), default), Times.Once);
    }

    [Fact]
    public async Task RegisterAsync_RevokedDevice_ReturnsForbidden()
    {
        var revokedAgent = new RegisteredAgent { Status = "revoked" };
        _repoMock.Setup(r => r.GetByDeviceIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync(revokedAgent);

        var result = await _sut.RegisterAsync(_validCommand, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("revoked");
    }

    [Fact]
    public async Task RegisterAsync_ExistingActiveDevice_ReturnsExistingWithNewJwt()
    {
        var activeAgent = new RegisteredAgent { Status = "active", Id = Guid.NewGuid() };
        _repoMock.Setup(r => r.GetByDeviceIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync(activeAgent);
        _tokenServiceMock.Setup(t => t.GenerateDeviceTokenAsync(It.IsAny<Guid>(), It.IsAny<Guid>(), default))
            .ReturnsAsync("new-jwt");

        var result = await _sut.RegisterAsync(_validCommand, default);

        result.IsSuccess.Should().BeTrue();
        _repoMock.Verify(r => r.InsertAsync(It.IsAny<RegisteredAgent>(), default), Times.Never);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| New device registration | Unit | Agent created, JWT returned |
| Revoked device | Unit | 403 Forbidden |
| Existing active device | Unit | Existing agent returned with new JWT |
| Missing required fields | Unit | Validation failure |

## Related

- [[agent-registration|Agent Registration Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
