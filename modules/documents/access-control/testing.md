# Access Control — Testing

**Module:** Documents
**Feature:** Access Control
**Location:** `tests/ONEVO.Tests.Unit/Modules/Documents/DocumentAccessServiceTests.cs`

---

## Unit Tests

```csharp
public class DocumentAccessServiceTests
{
    private readonly Mock<IDocumentAccessRepository> _repoMock = new();
    private readonly DocumentAccessService _sut;

    [Fact]
    public async Task Company_doc_accessible_by_all()
    {
        // Arrange
        // ... setup mocks for company doc accessible by all

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Access granted
    }

    [Fact]
    public async Task Employee_doc_denied_for_non-owner()
    {
        // Arrange
        // ... setup mocks for employee doc denied for non-owner

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 403 returned
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Company doc accessible by all | Unit | Access granted |
| Employee doc denied for non-owner | Unit | 403 returned |

## Related

- [[frontend/architecture/overview|Access Control Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
