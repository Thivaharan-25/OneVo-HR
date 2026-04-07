# Integrations — Testing

**Module:** Configuration
**Feature:** Integrations
**Location:** `tests/ONEVO.Tests.Unit/Modules/Configuration/IntegrationServiceTests.cs`

---

## Unit Tests

```csharp
public class IntegrationServiceTests
{
    private readonly Mock<IIntegrationConnectionRepository> _repoMock = new();
    private readonly Mock<IEncryptionService> _encryptionMock = new();
    private readonly IntegrationService _sut;

    [Fact]
    public async Task CreateAsync_ValidIntegration_EncryptsCredentials()
    {
        var command = new CreateIntegrationCommand { IntegrationType = "stripe" };

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        _encryptionMock.Verify(e => e.EncryptAsync(It.IsAny<string>(), default), Times.Once);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create integration | Unit | Credentials encrypted |
| Unknown type | Unit | 422 error |
| Duplicate type | Unit | 409 Conflict |

## Related

- [[configuration/integrations/overview|Integrations Overview]]
- [[testing/README|Testing Standards]]
