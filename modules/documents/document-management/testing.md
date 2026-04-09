# Document Management — Testing

**Module:** Documents
**Feature:** Document Management
**Location:** `tests/ONEVO.Tests.Unit/Modules/Documents/DocumentServiceTests.cs`

---

## Unit Tests

```csharp
public class DocumentServiceTests
{
    private readonly Mock<IDocumentRepository> _repoMock = new();
    private readonly DocumentService _sut;

    [Fact]
    public async Task Upload_creates_document_and_version()
    {
        // Arrange
        // ... setup mocks for upload creates document and version

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Version 1 created, is_current = true
    }

    [Fact]
    public async Task Download_logs_access()
    {
        // Arrange
        // ... setup mocks for download logs access

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Access log inserted
    }

    [Fact]
    public async Task File_upload_failure_rolls_back()
    {
        // Arrange
        // ... setup mocks for file upload failure rolls back

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // No document created
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Upload creates document and version | Unit | Version 1 created, is_current = true |
| Download logs access | Unit | Access log inserted |
| File upload failure rolls back | Unit | No document created |

## Related

- [[frontend/architecture/overview|Document Management Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
