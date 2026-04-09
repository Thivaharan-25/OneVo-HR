# Templates — Testing

**Module:** Documents
**Feature:** Templates
**Location:** `tests/ONEVO.Tests.Unit/Modules/Documents/TemplateServiceTests.cs`

---

## Unit Tests

```csharp
public class TemplateServiceTests
{
    private readonly Mock<ITemplateRepository> _repoMock = new();
    private readonly TemplateService _sut;

    [Fact]
    public async Task Create_template_parses_variables()
    {
        // Arrange
        // ... setup mocks for create template parses variables

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Variables extracted
    }

    [Fact]
    public async Task Generate_document_renders_template()
    {
        // Arrange
        // ... setup mocks for generate document renders template

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Merge variables replaced
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create template parses variables | Unit | Variables extracted |
| Generate document renders template | Unit | Merge variables replaced |

## Related

- [[frontend/architecture/overview|Templates Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
