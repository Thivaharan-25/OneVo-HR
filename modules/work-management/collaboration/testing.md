# Collaboration — Testing

**Module:** WorkSync
**Feature:** Collaboration
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Collaboration/`

---

## Unit Tests

```csharp
public class DocumentServiceTests
{
    [Fact]
    public async Task UploadVersion_ToApprovedDocument_ReturnsFailure()
    {
        var doc = new Document { Status = "approved", LockedAt = DateTime.UtcNow };
        _docRepoMock.Setup(r => r.GetByIdAsync(doc.Id, default)).ReturnsAsync(doc);
        var result = await _sut.UploadVersionAsync(doc.Id, _fileCommand, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("DOCUMENT_LOCKED");
    }

    [Fact]
    public async Task ApproveDocument_SetsAllLockFieldsAtomically()
    {
        var doc = new Document { Status = "in_review" };
        var approval = new DocumentApproval { Status = "pending", DocumentId = doc.Id };
        _approvalRepoMock.Setup(r => r.GetByIdAsync(approval.Id, default)).ReturnsAsync(approval);
        _docRepoMock.Setup(r => r.GetByIdAsync(doc.Id, default)).ReturnsAsync(doc);

        await _sut.ApproveAsync(approval.Id, _approverId, default);

        doc.Status.Should().Be("approved");
        doc.LockedAt.Should().NotBeNull();
        doc.LockedBy.Should().Be(_approverId);
        doc.ApprovedVersionId.Should().NotBeEmpty();
    }

    [Fact]
    public async Task VersionNumber_AutoIncrementsPerDocument()
    {
        SetupExistingVersions(docId: _docId, maxVersion: 3);
        var result = await _sut.UploadVersionAsync(_docId, _fileCommand, default);
        result.Value!.VersionNumber.Should().Be(4);
    }

    [Fact]
    public async Task UnlockDocument_ClearsAllLockFields()
    {
        var doc = new Document { Status = "approved", LockedAt = DateTime.UtcNow, LockedBy = _userId };
        await _sut.UnlockAsync(doc.Id, default);
        doc.Status.Should().Be("draft");
        doc.LockedAt.Should().BeNull();
        doc.LockedBy.Should().BeNull();
        doc.ApprovedVersionId.Should().BeNull();
    }
}

public class WikiPageServiceTests
{
    [Fact]
    public async Task UpdatePage_WithCyclicParent_ReturnsFailure()
    {
        // page A → parent B → parent C → trying to set C's parent to A (cycle)
        SetupAncestorChain(new[] { "B", "C" }, targetPageId: "A");
        var result = await _sut.UpdateParentAsync("C", parentId: "A", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("CYCLE_DETECTED");
    }
}
```

## Integration Tests

```csharp
public class DocumentEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task FullApprovalFlow_LocksThenUnlocks()
    {
        var doc = await CreateDocumentAsync();
        await UploadVersionAsync(doc.Id);
        var approval = await SubmitForApprovalAsync(doc.Id);
        await ApproveAsync(approval.Id);
        var locked = await GetDocumentAsync(doc.Id);
        locked.Status.Should().Be("approved");
        locked.LockedAt.Should().NotBeNull();

        await UnlockAsync(doc.Id); // admin action
        var unlocked = await GetDocumentAsync(doc.Id);
        unlocked.Status.Should().Be("draft");
        unlocked.LockedAt.Should().BeNull();
    }

    [Fact]
    public async Task UploadToLockedDocument_Returns403()
    {
        var doc = await CreateApprovedDocumentAsync();
        var response = await UploadVersionRawAsync(doc.Id);
        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Upload to approved (locked) document | Unit + Integration | DOCUMENT_LOCKED / 403 |
| Approve sets all 4 lock fields atomically | Unit | All fields set in one transaction |
| version_number auto-increments per document | Unit | version = max + 1 |
| Unlock clears all lock fields | Unit | status = draft, lock fields null |
| Wiki cycle detection | Unit | CYCLE_DETECTED |
| Full approval + unlock cycle | Integration | Document locked then unlocked |

## Related

- [[modules/work-management/collaboration/overview|Collaboration Overview]]
- [[modules/work-management/collaboration/end-to-end-logic|Collaboration Logic]]
