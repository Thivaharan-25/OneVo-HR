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
    public async Task CreateProject_StoresSelectedWorkspaceId()
    {
        var result = await _sut.CreateAsync(_validCommandWithWorkspace(_workspaceId), default);
        result.IsSuccess.Should().BeTrue();
        result.Value.WorkspaceId.Should().Be(_workspaceId);
    }

    [Fact]
    public async Task InviteMember_ActiveTenantEmployee_CreatesPendingInvitation()
    {
        SetupActiveEmployee(_userId, _employeeId, _tenantId);
        var result = await _sut.InviteMemberAsync(_projectId, _userId, "member", default);
        result.IsSuccess.Should().BeTrue();
        result.Value.Status.Should().Be("pending");
    }

    [Fact]
    public async Task AcceptMemberInvitation_CreatesProjectMember()
    {
        SetupPendingMemberInvitation(_projectId, _userId, _employeeId);
        var result = await _sut.AcceptMemberInvitationAsync(_projectId, _inviteId, _userId, default);
        result.IsSuccess.Should().BeTrue();
        _memberRepoMock.Verify(r => r.AddAsync(
            It.Is<ProjectMember>(m => m.UserId == _userId && m.EmployeeId == _employeeId),
            default),
            Times.Once);
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
| Create project with selected workspace | Unit | `projects.workspace_id` stored |
| Invite active tenant employee | Unit | pending `project_member_invitations` row |
| Accept member invitation | Unit | `project_members` row added |
| Simple project-link invitation accepted | Unit | `project_links` row added |
| Remove last project admin | Unit | Failure |
| Tenant isolation | Integration | 404 for foreign project |

## Related

- [[modules/work-management/projects/overview|Projects Overview]]
- [[modules/work-management/projects/end-to-end-logic|Projects Logic]]
