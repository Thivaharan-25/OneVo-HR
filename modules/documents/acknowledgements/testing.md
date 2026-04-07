# Acknowledgements — Testing

**Module:** Documents
**Feature:** Acknowledgements
**Location:** `tests/ONEVO.Tests.Unit/Modules/Documents/AcknowledgementServiceTests.cs`

---

## Unit Tests

```csharp
public class AcknowledgementServiceTests
{
    private readonly Mock<IAcknowledgementRepository> _repoMock = new();
    private readonly AcknowledgementService _sut;

    [Fact]
    public async Task Acknowledge_creates_record_with_IP()
    {
        // Arrange
        // ... setup mocks for acknowledge creates record with ip

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Record with IP address
    }

    [Fact]
    public async Task Already_acknowledged_returns_error()
    {
        // Arrange
        // ... setup mocks for already acknowledged returns error

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 400 returned
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Acknowledge creates record with IP | Unit | Record with IP address |
| Already acknowledged returns error | Unit | 400 returned |

## Related

- [[documents/acknowledgements/overview|Acknowledgements Overview]]
- [[testing/README|Testing Standards]]
