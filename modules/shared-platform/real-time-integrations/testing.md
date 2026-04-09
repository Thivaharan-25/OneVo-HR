# Real-Time Integrations — Testing

**Module:** Shared Platform
**Feature:** Real-Time Integrations
**Location:** `tests/ONEVO.Tests.Unit/Modules/SharedPlatform/IntegrationServiceTests.cs`

---

## Unit Tests

```csharp
public class IntegrationServiceTests
{
    private readonly Mock<IIntegrationRepository> _repoMock = new();
    private readonly IntegrationService _sut;

    [Fact]
    public async Task Create_API_key_returns_plaintext_once()
    {
        // Arrange
        // ... setup mocks for create api key returns plaintext once

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Key shown once
    }

    [Fact]
    public async Task Webhook_delivery_retries_on_failure()
    {
        // Arrange
        // ... setup mocks for webhook delivery retries on failure

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 3 retries with backoff
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create API key returns plaintext once | Unit | Key shown once |
| Webhook delivery retries on failure | Unit | 3 retries with backoff |

## Related

- [[modules/shared-platform/real-time-integrations/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
