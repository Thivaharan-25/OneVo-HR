# Data Ingestion — Testing

**Module:** Agent Gateway
**Feature:** Data Ingestion
**Location:** `tests/ONEVO.Tests.Unit/Modules/AgentGateway/DataIngestionServiceTests.cs`

---

## Unit Tests

```csharp
public class DataIngestionServiceTests
{
    private readonly Mock<IActivityRawBufferRepository> _bufferRepoMock = new();
    private readonly DataIngestionService _sut;

    [Fact]
    public async Task IngestAsync_ValidPayload_InsertsToRawBuffer()
    {
        var payload = CreateValidPayload(batchSize: 3);

        var result = await _sut.IngestAsync(_deviceId, payload, default);

        result.IsSuccess.Should().BeTrue();
        _bufferRepoMock.Verify(r => r.InsertBatchAsync(
            It.Is<List<ActivityRawBuffer>>(b => b.Count == 3), default), Times.Once);
    }

    [Fact]
    public async Task IngestAsync_EmptyBatch_ReturnsValidationError()
    {
        var payload = new IngestionPayload { Batch = new List<BatchItem>() };

        var result = await _sut.IngestAsync(_deviceId, payload, default);

        result.IsSuccess.Should().BeFalse();
    }

    [Fact]
    public async Task IngestAsync_TimestampTooOld_ReturnsValidationError()
    {
        var payload = CreateValidPayload();
        payload.Timestamp = DateTime.UtcNow.AddDays(-2);

        var result = await _sut.IngestAsync(_deviceId, payload, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("timestamp");
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Valid 3-item batch | Unit | 3 rows inserted to buffer |
| Empty batch | Unit | Validation error |
| Timestamp > 24h old | Unit | Validation error |
| Payload > 1MB | Unit | 413 error |
| Rate limit exceeded | Integration | 429 returned |

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[modules/agent-gateway/data-ingestion/end-to-end-logic|Data Ingestion — End-to-End Logic]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
