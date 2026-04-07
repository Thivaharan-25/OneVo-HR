# Heartbeat Monitoring — Testing

**Module:** Agent Gateway
**Feature:** Heartbeat Monitoring
**Location:** `tests/ONEVO.Tests.Unit/Modules/AgentGateway/AgentHeartbeatServiceTests.cs`

---

## Unit Tests

```csharp
public class AgentHeartbeatServiceTests
{
    private readonly Mock<IRegisteredAgentRepository> _repoMock = new();
    private readonly Mock<IAgentHealthLogRepository> _healthRepoMock = new();
    private readonly Mock<IDomainEventPublisher> _eventPublisher = new();
    private readonly AgentHeartbeatService _sut;

    [Fact]
    public async Task ProcessHeartbeatAsync_ValidPayload_UpdatesLastHeartbeat()
    {
        var agent = new RegisteredAgent { Id = _agentId, Status = "active" };
        _repoMock.Setup(r => r.GetByDeviceIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync(agent);

        await _sut.ProcessHeartbeatAsync(_deviceId, _validPayload, default);

        agent.LastHeartbeatAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
    }

    [Fact]
    public async Task ProcessHeartbeatAsync_TamperDetected_PublishesEvent()
    {
        var agent = new RegisteredAgent { Id = _agentId, Status = "active" };
        _repoMock.Setup(r => r.GetByDeviceIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync(agent);
        var payload = new HeartbeatPayload { TamperDetected = true };

        await _sut.ProcessHeartbeatAsync(_deviceId, payload, default);

        _eventPublisher.Verify(e => e.PublishAsync(
            It.IsAny<AgentTamperDetectedEvent>(), default), Times.Once);
    }

    [Fact]
    public async Task DetectOfflineAsync_AgentOffline5Min_PublishesHeartbeatLost()
    {
        var offlineAgents = new List<RegisteredAgent>
        {
            new() { Id = _agentId, LastHeartbeatAt = DateTime.UtcNow.AddMinutes(-6) }
        };
        _repoMock.Setup(r => r.GetOfflineAgentsAsync(It.IsAny<TimeSpan>(), default)).ReturnsAsync(offlineAgents);

        await _sut.DetectOfflineAsync(default);

        _eventPublisher.Verify(e => e.PublishAsync(
            It.IsAny<AgentHeartbeatLostEvent>(), default), Times.Once);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Valid heartbeat | Unit | Timestamp updated |
| Tamper detected | Unit | Event published |
| Agent offline > 5 min | Unit | HeartbeatLost event |
| Unknown device_id | Unit | 401 returned |

## Related

- [[agent-gateway|Agent Gateway Module]]
- [[heartbeat-monitoring/end-to-end-logic|Heartbeat Monitoring — End-to-End Logic]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
- [[WEEK1-shared-platform]]
