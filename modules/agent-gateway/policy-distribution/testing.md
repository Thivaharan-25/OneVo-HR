# Policy Distribution — Testing

**Module:** Agent Gateway
**Feature:** Policy Distribution
**Location:** `tests/ONEVO.Tests.Unit/Modules/AgentGateway/AgentPolicyServiceTests.cs`

---

## Unit Tests

```csharp
public class AgentPolicyServiceTests
{
    private readonly Mock<IRegisteredAgentRepository> _agentRepoMock = new();
    private readonly Mock<IConfigurationService> _configMock = new();
    private readonly AgentPolicyService _sut;

    [Fact]
    public async Task GetPolicyAsync_WithEmployeeOverride_MergesCorrectly()
    {
        SetupAgentWithEmployee();
        _configMock.Setup(c => c.GetMonitoringTogglesAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(Result.Success(new MonitoringTogglesDto { ScreenshotCapture = true }));
        _configMock.Setup(c => c.GetEmployeeOverrideAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(Result.Success(new EmployeeMonitoringOverrideDto { ScreenshotCapture = false }));

        var result = await _sut.GetPolicyAsync(_deviceId, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.ScreenshotCapture.Should().BeFalse(); // override wins
    }

    [Fact]
    public async Task GetPolicyAsync_NoEmployee_ReturnsTenantDefaults()
    {
        SetupAgentWithoutEmployee();
        _configMock.Setup(c => c.GetMonitoringTogglesAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(Result.Success(new MonitoringTogglesDto { ActivityMonitoring = true }));

        var result = await _sut.GetPolicyAsync(_deviceId, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.ActivityMonitoring.Should().BeTrue();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Employee override wins over tenant | Unit | Override value used |
| No employee linked | Unit | Tenant defaults returned |
| Agent revoked | Unit | 401 returned |
| Null override inherits tenant | Unit | Tenant value used |

## Related

- [[agent-gateway|Agent Gateway Module]]
- [[policy-distribution/end-to-end-logic|Policy Distribution — End-to-End Logic]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
- [[WEEK1-shared-platform]]
