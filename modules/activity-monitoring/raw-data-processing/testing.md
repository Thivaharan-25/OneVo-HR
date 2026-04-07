# Raw Data Processing — Testing

**Module:** Activity Monitoring
**Feature:** Raw Data Processing
**Location:** `tests/ONEVO.Tests.Unit/Modules/ActivityMonitoring/RawDataProcessorTests.cs`

---

## Unit Tests

```csharp
public class RawDataProcessorTests
{
    private readonly Mock<IActivityRawBufferRepository> _bufferRepoMock = new();
    private readonly Mock<IActivitySnapshotRepository> _snapshotRepoMock = new();
    private readonly Mock<IConfigurationService> _configMock = new();
    private readonly Mock<IAgentGatewayService> _agentServiceMock = new();
    private readonly RawDataProcessor _sut;

    [Fact]
    public async Task ProcessBatchAsync_ValidPayload_CreatesSnapshots()
    {
        SetupAgentWithEmployee();
        SetupMonitoringEnabled();
        var rawRows = CreateValidRawRows(count: 5);
        _bufferRepoMock.Setup(r => r.GetUnprocessedAsync(It.IsAny<int>(), default)).ReturnsAsync(rawRows);

        await _sut.ProcessBatchAsync(default);

        _snapshotRepoMock.Verify(r => r.InsertBatchAsync(
            It.Is<List<ActivitySnapshot>>(s => s.Count == 5), default), Times.Once);
    }

    [Fact]
    public async Task ProcessBatchAsync_MonitoringDisabled_SkipsProcessing()
    {
        SetupAgentWithEmployee();
        SetupMonitoringDisabled();
        var rawRows = CreateValidRawRows(count: 5);
        _bufferRepoMock.Setup(r => r.GetUnprocessedAsync(It.IsAny<int>(), default)).ReturnsAsync(rawRows);

        await _sut.ProcessBatchAsync(default);

        _snapshotRepoMock.Verify(r => r.InsertBatchAsync(
            It.IsAny<List<ActivitySnapshot>>(), default), Times.Never);
    }

    [Fact]
    public async Task ProcessBatchAsync_MalformedPayload_SkipsAndLogs()
    {
        SetupAgentWithEmployee();
        SetupMonitoringEnabled();
        var rawRows = CreateMalformedRawRows();
        _bufferRepoMock.Setup(r => r.GetUnprocessedAsync(It.IsAny<int>(), default)).ReturnsAsync(rawRows);

        await _sut.ProcessBatchAsync(default);

        _snapshotRepoMock.Verify(r => r.InsertBatchAsync(
            It.Is<List<ActivitySnapshot>>(s => s.Count == 0), default), Times.Once);
    }

    [Fact]
    public void ComputeIntensityScore_MaxValues_CapsAt100()
    {
        var score = RawDataProcessor.ComputeIntensityScore(keyboardEvents: 9999, mouseEvents: 9999);

        score.Should().Be(100m);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Valid payload with 5 snapshots | Unit | 5 snapshots created |
| Monitoring disabled for employee | Unit | No snapshots created |
| Malformed JSON payload | Unit | Skipped, logged warning |
| Intensity score > 100 capped | Unit | Score = 100 |
| Unknown agent device_id | Unit | Batch skipped |
| Window title hashed (SHA-256) | Unit | Raw title never stored |

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[raw-data-processing/end-to-end-logic|Raw Data Processing — End-to-End Logic]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
- [[WEEK3-activity-monitoring]]
