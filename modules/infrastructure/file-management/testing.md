# File Management — Testing

**Module:** Infrastructure
**Feature:** File Management
**Location:** `tests/ONEVO.Tests.Unit/Modules/Infrastructure/FileServiceTests.cs`

---

## Unit Tests

```csharp
public class FileServiceTests
{
    private readonly Mock<IFileRepository> _repoMock = new();
    private readonly FileService _sut;

    [Fact]
    public async Task Upload_stores_metadata_and_blob()
    {
        // Arrange
        // ... setup mocks for upload stores metadata and blob

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // File record created
    }

    [Fact]
    public async Task File_too_large_returns_413()
    {
        // Arrange
        // ... setup mocks for file too large returns 413

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 413 returned
    }

    [Fact]
    public async Task Invalid_content_type_rejected()
    {
        // Arrange
        // ... setup mocks for invalid content type rejected

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 422 returned
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Upload stores metadata and blob | Unit | File record created |
| File too large returns 413 | Unit | 413 returned |
| Invalid content type rejected | Unit | 422 returned |

## Related

- [[file-management|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
