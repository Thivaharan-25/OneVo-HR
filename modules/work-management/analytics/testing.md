# Insight & Analytics - Testing

**Phase:** Phase 2 - deferred
**Phase 1 Status:** Not active in current Phase 1 Work implementation; retained as future design reference.

**Module:** WorkSync
**Feature:** Insight & Analytics
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Analytics/`

---

## Unit Tests

```csharp
public class DashboardServiceTests
{
    [Fact]
    public async Task GetDashboards_ReturnsSharedAndOwn()
    {
        SetupDashboards(owned: 2, sharedViaIsShared: 1, sharedViaACL: 1);
        var result = await _sut.GetAccessibleAsync(_workspaceId, _userId, default);
        result.Value!.Should().HaveCount(4);
    }

    [Fact]
    public async Task GetDashboards_NotSharedNotOwned_Excluded()
    {
        SetupDashboard(isShared: false, ownedBy: Guid.NewGuid(), noACLEntry: true);
        var result = await _sut.GetAccessibleAsync(_workspaceId, _userId, default);
        result.Value!.Should().BeEmpty();
    }

    [Fact]
    public async Task QueueExport_ReturnsAccepted_WithExportId()
    {
        var result = await _sut.QueueExportAsync(_workspaceId, "task_report", "csv", _params, default);
        result.IsSuccess.Should().BeTrue();
        result.Value!.Status.Should().Be("queued");
        result.Value!.ExportId.Should().NotBeEmpty();
        _hangfireMock.Verify(h => h.Enqueue(It.IsAny<ProcessReportExportJob>()), Times.Once);
    }

    [Fact]
    public async Task ProcessExport_OnFailure_SetsStatusFailed()
    {
        _storageServiceMock.Setup(s => s.UploadAsync(It.IsAny<Stream>(), It.IsAny<string>(), default))
            .ThrowsAsync(new StorageException("Upload failed"));
        await _sut.ProcessExportAsync(_exportId, default);
        var export = await GetExportAsync(_exportId);
        export.Status.Should().Be("failed");
    }
}
```

## Integration Tests

```csharp
public class AnalyticsEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task DashboardNotShared_OtherUserCannotSee()
    {
        var dashboard = await CreatePrivateDashboardAsync();
        var response = await _otherUserClient.GetAsync($"/api/v1/workspaces/{_wsId}/dashboards");
        var dashboards = await response.Content.ReadFromJsonAsync<List<DashboardDto>>();
        dashboards!.Should().NotContain(d => d.Id == dashboard.Id);
    }

    [Fact]
    public async Task ExportReport_PollForReady()
    {
        var export = await QueueExportAsync("task_report", "csv");
        await TriggerProcessJobAsync(export.ExportId);
        var status = await GetExportStatusAsync(export.ExportId);
        status.Status.Should().Be("ready");
        status.DownloadUrl.Should().NotBeNullOrEmpty();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| is_shared = true - all workspace members see | Unit | Dashboard included |
| ACL share (user) - only target user sees | Unit | Dashboard included for target only |
| No share at all - excluded | Unit | Dashboard excluded |
| Queue export - Hangfire job enqueued | Unit | Job enqueued, status = queued |
| Export fails - status = failed | Unit | Status set to failed |
| Private dashboard invisible to others | Integration | Not in list |
| Export ready after processing | Integration | status = ready, download URL present |

## Related

- [[modules/work-management/analytics/overview|Analytics Overview]]
- [[modules/work-management/analytics/end-to-end-logic|Analytics Logic]]
