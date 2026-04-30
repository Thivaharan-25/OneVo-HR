# WorkSync Foundation — Testing

**Module:** WorkSync
**Feature:** Foundation
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Foundation/`

---

## Unit Tests

```csharp
public class WorkspaceServiceTests
{
    [Fact]
    public async Task CreateWorkspace_SeedsThreeSystemRoles()
    {
        var result = await _sut.CreateAsync(_validCommand, default);
        result.IsSuccess.Should().BeTrue();
        _roleRepoMock.Verify(r => r.AddRangeAsync(
            It.Is<IEnumerable<WorkspaceRole>>(roles =>
                roles.Count() == 3 &&
                roles.Any(r => r.Name == "Admin" && r.IsSystem) &&
                roles.Any(r => r.Name == "Member" && r.IsSystem) &&
                roles.Any(r => r.Name == "Viewer" && r.IsSystem)),
            default), Times.Once);
    }

    [Fact]
    public async Task CreateWorkspace_WorkSyncNotEnabled_ReturnsFailure()
    {
        SetupTenantWithoutWorkSync();
        var result = await _sut.CreateAsync(_validCommand, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("WorkSync not enabled");
    }

    [Fact]
    public async Task InviteMember_AlreadyMember_ReturnsFailure()
    {
        SetupExistingMember(_userId);
        var result = await _sut.InviteMemberAsync(_wsId, _userId, "Member", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("ALREADY_MEMBER");
    }

    [Fact]
    public async Task RemoveMember_LastAdmin_ReturnsFailure()
    {
        SetupSingleAdminMember(_userId);
        var result = await _sut.RemoveMemberAsync(_wsId, _userId, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("at least one Admin");
    }

    [Fact]
    public async Task CreateWorkspace_WithTeamsCreate_MissingLinkedMembers_ReturnsFailure()
    {
        SetupTeamsIntegrationEnabled();
        SetupWorkspaceMembersWithMissingTeamsLinks();
        var command = _validCommand with { TeamsSync = new TeamsSyncOptions { CreateTeam = true } };
        var result = await _sut.CreateAsync(command, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("TEAMS_MEMBERS_NOT_LINKED");
    }

    [Fact]
    public async Task LinkExistingTeam_AlreadyLinkedWorkspace_ReturnsConflict()
    {
        SetupExistingWorkspaceTeamsLink(_wsId);
        var result = await _sut.LinkExistingTeamAsync(_wsId, _teamsTeamId, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("WORKSPACE_ALREADY_LINKED_TO_TEAMS");
    }
}
```

## Integration Tests

```csharp
public class WorkspaceEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task CreateWorkspace_ThenAddMember_MemberCanListWorkspace()
    {
        var ws = await CreateWorkspaceAsync("Dev Team");
        await InviteMemberAsync(ws.Id, _otherUserId, "Member");
        var workspaces = await GetWorkspacesAsUserAsync(_otherUserId);
        workspaces.Should().Contain(w => w.Id == ws.Id);
    }

    [Fact]
    public async Task NonMember_CannotAccessWorkspaceResources()
    {
        var ws = await CreateWorkspaceAsync("Private");
        var response = await _nonMemberClient.GetAsync($"/api/v1/workspaces/{ws.Id}/projects");
        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }

    [Fact]
    public async Task CreateWorkspace_WithTeamsCheckbox_CreatesWorkspaceAndTeamsLink()
    {
        SetupAllMembersLinkedToTeams();
        SetupGraphTeamCreateSuccess();
        var ws = await CreateWorkspaceAsync("Dev Team", teamsCreate: true);
        await AssertWorkspaceTeamsLinkExists(ws.Id);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create workspace seeds 3 roles | Unit | 3 system roles created atomically |
| WorkSync not enabled for tenant | Unit | Failure |
| Invite already-member | Unit | ALREADY_MEMBER error |
| Remove last Admin | Unit | Failure |
| Member added can access workspace | Integration | 200 on workspace resources |
| Non-member blocked | Integration | 403 |
| Teams checkbox selected with missing linked members | Unit | TEAMS_MEMBERS_NOT_LINKED |
| Link existing Team when workspace already linked | Unit | Conflict |
| Create workspace with Teams checkbox | Integration | Workspace + Teams link created |
| Existing Teams group candidate matching | Unit | Match score and member diff returned |

## Related

- [[modules/work-management/foundation/overview|Foundation Overview]]
- [[modules/work-management/foundation/end-to-end-logic|Foundation Logic]]
- [[modules/integrations/microsoft-teams/testing|Microsoft Teams Integration Testing]]
