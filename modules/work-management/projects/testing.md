# Project Management - Testing

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
        SetupExistingIdentifier("TASK", _tenantId);
        var result = await _sut.CreateAsync(_commandWithIdentifier("TASK"), default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("IDENTIFIER_TAKEN");
    }

    [Fact]
    public async Task CreateProject_AddsCreatorAsAdmin()
    {
        var result = await _sut.CreateAsync(_validCommand, default);
        result.IsSuccess.Should().BeTrue();
        _memberRepoMock.Verify(r => r.AddAsync(
            It.Is<ProjectMember>(m => m.UserId == _callerId && m.Role == "admin"),
            default),
            Times.Once);
    }

    [Fact]
    public async Task LinkWorkspace_DoesNotAddWorkspaceMembersAsProjectMembers()
    {
        SetupWorkspaceMembers(_workspaceId, _workspaceUserIds);
        await _sut.LinkWorkspaceAsync(_projectId, _workspaceId, default);
        _memberRepoMock.Verify(r => r.AddRangeAsync(It.IsAny<IEnumerable<ProjectMember>>(), default), Times.Never);
    }

    [Fact]
    public async Task AddMember_ActiveTenantEmployee_SucceedsWithoutWorkspaceMembership()
    {
        SetupActiveEmployee(_userId, _employeeId, _tenantId);
        var result = await _sut.AddMemberAsync(_projectId, _userId, "member", default);
        result.IsSuccess.Should().BeTrue();
    }

    [Fact]
    public async Task RemoveLastAdmin_ReturnsFailure()
    {
        SetupOnlyAdmin(_projectId, _adminId);
        var result = await _sut.RemoveMemberAsync(_projectId, _adminId, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("at least one active admin");
    }
}
```

## Integration Tests

```csharp
public class ProjectEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task CreateProject_AdminAutomaticallyAdded()
    {
        var project = await CreateProjectAsync("Payroll App");
        var members = await GetMembersAsync(project.Id);
        members.Should().Contain(m => m.UserId == _callerId && m.Role == "admin");
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
| Duplicate project identifier in tenant | Unit | IDENTIFIER_TAKEN |
| Creator auto-added as admin | Unit/Integration | Admin member present |
| Link workspace | Unit | `project_workspaces` row added |
| Link workspace does not auto-add members | Unit | No bulk `project_members` insert |
| Add active tenant employee without workspace membership | Unit | Success |
| Remove last project admin | Unit | Failure |
| Tenant isolation | Integration | 404 for foreign project |

## Related

- [[modules/work-management/projects/overview|Projects Overview]]
- [[modules/work-management/projects/end-to-end-logic|Projects Logic]]
