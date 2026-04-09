# Recognitions — Testing

**Module:** Performance
**Feature:** Recognitions
**Location:** `tests/ONEVO.Tests.Unit/Modules/Performance/RecognitionServiceTests.cs`

---

## Unit Tests

```csharp
public class RecognitionServiceTests
{
    private readonly Mock<IRecognitionRepository> _repoMock = new();
    private readonly RecognitionService _sut;

    [Fact]
    public async Task Give_recognition_notifies_recipient()
    {
        // Arrange
        // ... setup mocks for give recognition notifies recipient

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Notification sent
    }

    [Fact]
    public async Task Self-recognition_rejected()
    {
        // Arrange
        // ... setup mocks for self-recognition rejected

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
| Give recognition notifies recipient | Unit | Notification sent |
| Self-recognition rejected | Unit | 400 returned |

## Related

- [[modules/performance/recognitions/overview|Recognitions Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
