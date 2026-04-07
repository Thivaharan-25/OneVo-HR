# Qualifications — Testing

**Module:** Core HR
**Feature:** Qualifications
**Location:** `tests/ONEVO.Tests.Unit/Modules/CoreHR/QualificationServiceTests.cs`

---

## Unit Tests

```csharp
public class QualificationServiceTests
{
    private readonly Mock<IQualificationRepository> _repoMock = new();
    private readonly QualificationService _sut;

    [Fact]
    public async Task Add_qualification_with_document_uploads_file()
    {
        // Arrange
        // ... setup mocks for add qualification with document uploads file

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // File uploaded, ID stored
    }

    [Fact]
    public async Task Add_work_history_creates_record()
    {
        // Arrange
        // ... setup mocks for add work history creates record

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // History inserted
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Add qualification with document uploads file | Unit | File uploaded, ID stored |
| Add work history creates record | Unit | History inserted |

## Related

- [[qualifications|Qualifications Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
