# Project Management — Testing

**Module:** WorkSync
**Feature:** Project Management
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Projects/`

---

## Unit Tests

```csharp
public class ProjectServiceTests
{
    [Fact]
    public async Task CreateProject_DuplicateIdentifier_ReturnsFailure()
    {
        SetupExistingIdentifier("TASK", _workspaceId);
        var result = await _sut.CreateAsync(_commandWithIdentifier("TASK"), default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("IDENTIFIER_TAKEN");
    }

    [Fact]
    public async Task ArchiveProject_WithActiveSprint_ReturnsFailure()
    {
        SetupActiveSprintInProject(_projectId);
        var result = await _sut.ArchiveAsync(_projectId, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Complete active sprint first");
    }

    [Fact]
    public async Task TransferOwnership_UpdatesBothMemberships()
    {
        SetupOwner(_projectId, _currentOwnerId);
        await _sut.TransferOwnershipAsync(_projectId, _newOwnerId, default);
        _memberRepoMock.Verify(r => r.UpdateRoleAsync(_projectId, _currentOwnerId, "Admin", default), Times.Once);
        _memberRepoMock.Verify(r => r.UpdateRoleAsync(_projectId, _newOwnerId, "Owner", default), Times.Once);
    }

    [Fact]
    public async Task AddMember_NotWorkspaceMember_ReturnsFailure()
    {
        SetupUserNotInWorkspace(_userId, _workspaceId);
        var result = await _sut.AddMemberAsync(_projectId, _userId, "Member", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("workspace member");
    }
}
```

## Integration Tests

```csharp
public class ProjectEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task CreateProject_OwnerAutomaticallyAdded()
    {
        var project = await CreateProjectAsync("Payroll App");
        var members = await GetMembersAsync(project.Id);
        members.Should().Contain(m => m.UserId == _callerId && m.Role == "Owner");
    }

    [Fact]
    public async Task TenantIsolation_CannotAccessOtherTenantProjects()
    {
        var foreignProject = await CreateProjectInOtherTenantAsync();
        var response = await _client.GetAsync($"/api/v1/projects/{foreignProject.Id}");
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Duplicate project identifier | Unit | IDENTIFIER_TAKEN |
| Archive with active sprint | Unit | Failure |
| Transfer ownership swaps roles | Unit | Both membership rows updated |
| Add non-workspace member | Unit | Failure |
| Creator auto-added as Owner | Integration | Owner member present |
| Tenant isolation | Integration | 404 for foreign project |

## Related

- [[modules/work-management/projects/overview|Projects Overview]]
- [[modules/work-management/projects/end-to-end-logic|Projects Logic]]
