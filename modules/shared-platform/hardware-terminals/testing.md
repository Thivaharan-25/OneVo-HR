# Hardware Terminals — Testing

**Module:** Shared Platform
**Feature:** Hardware Terminals
**Location:** `tests/ONEVO.Tests.Unit/Modules/SharedPlatform/HardwareTerminalServiceTests.cs`

---

## Unit Tests

```csharp
public class HardwareTerminalServiceTests
{
    private readonly Mock<IHardwareTerminalRepository> _repoMock = new();
    private readonly HardwareTerminalService _sut;

    [Fact]
    public async Task Register_terminal_encrypts_API_key()
    {
        // Arrange
        // ... setup mocks for register terminal encrypts api key

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Key encrypted
    }

    [Fact]
    public async Task Offline_terminal_detected()
    {
        // Arrange
        // ... setup mocks for offline terminal detected

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Alert generated
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Register terminal encrypts API key | Unit | Key encrypted |
| Offline terminal detected | Unit | Alert generated |

## Related

- [[modules/shared-platform/hardware-terminals/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
