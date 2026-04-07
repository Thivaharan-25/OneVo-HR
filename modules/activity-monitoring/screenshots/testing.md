# Screenshots — Testing

**Module:** Activity Monitoring
**Feature:** Screenshots
**Location:** `tests/ONEVO.Tests.Unit/Modules/ActivityMonitoring/ScreenshotServiceTests.cs`

---

## Unit Tests

```csharp
public class ScreenshotServiceTests
{
    private readonly Mock<IScreenshotRepository> _repoMock = new();
    private readonly Mock<IFileService> _fileServiceMock = new();
    private readonly Mock<IConfigurationService> _configMock = new();
    private readonly ScreenshotService _sut;

    [Fact]
    public async Task ProcessScreenshotAsync_Enabled_StoresMetadata()
    {
        SetupScreenshotEnabled();
        _fileServiceMock.Setup(f => f.UploadFileAsync(It.IsAny<Stream>(), It.IsAny<string>(), It.IsAny<string>(), default))
            .ReturnsAsync(Result.Success(new FileRecordDto { Id = Guid.NewGuid() }));

        var result = await _sut.ProcessScreenshotAsync(_payload, default);

        result.IsSuccess.Should().BeTrue();
        _repoMock.Verify(r => r.InsertAsync(It.IsAny<Screenshot>(), default), Times.Once);
    }

    [Fact]
    public async Task ProcessScreenshotAsync_Disabled_SkipsProcessing()
    {
        SetupScreenshotDisabled();

        var result = await _sut.ProcessScreenshotAsync(_payload, default);

        _fileServiceMock.Verify(f => f.UploadFileAsync(
            It.IsAny<Stream>(), It.IsAny<string>(), It.IsAny<string>(), default), Times.Never);
    }

    [Fact]
    public async Task GetScreenshotUrlAsync_NotFound_Returns404()
    {
        _repoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), default)).ReturnsAsync((Screenshot?)null);

        var result = await _sut.GetScreenshotUrlAsync(Guid.NewGuid(), default);

        result.IsSuccess.Should().BeFalse();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Screenshot enabled | Unit | File uploaded, metadata stored |
| Screenshot disabled | Unit | Skipped |
| Screenshot not found | Unit | 404 |
| Blob upload failure | Unit | Retried, then failure |

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[screenshots/end-to-end-logic|Screenshots — End-to-End Logic]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
- [[WEEK3-activity-monitoring]]
