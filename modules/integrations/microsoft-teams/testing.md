# Microsoft Teams Integration - Testing

**Module:** Integrations
**Feature:** Microsoft Teams Integration
**Location:** `tests/ONEVO.Tests.Unit/Features/Integrations/MicrosoftTeams/`

---

## Unit Tests

```csharp
public class TeamsAccountLinkingTests
{
    [Fact]
    public async Task Callback_ValidCode_StoresEncryptedRefreshToken()
    {
        SetupGraphMe("aad-user-1", "anna@example.com");
        var result = await _sut.HandleCallbackAsync(_code, _state, default);
        result.IsSuccess.Should().BeTrue();
        _tokenStore.Verify(s => s.SaveEncryptedAsync(It.IsAny<GraphToken>(), default), Times.Once);
    }

    [Fact]
    public async Task WorkspaceEligibility_MissingMemberLinks_ReturnsMissingMembers()
    {
        SetupWorkspaceMembers(3);
        SetupLinkedTeamsAccounts(2);
        var result = await _sut.GetEligibilityAsync(_workspaceId, default);
        result.Value!.AllMembersLinked.Should().BeFalse();
        result.Value.MissingMembers.Should().HaveCount(1);
    }

    [Fact]
    public async Task ExistingTeamCandidate_ComputesMemberMatchScore()
    {
        SetupWorkspaceMembers("a@example.com", "b@example.com");
        SetupTeamsMembers("a@example.com", "b@example.com", "external@example.com");
        var result = await _sut.FindCandidatesAsync(_workspaceId, default);
        result.Value.Single().ExtraMembers.Should().Contain("external@example.com");
    }
}
```

## Integration Tests

```csharp
public class TeamsIntegrationEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task Connect_StartsOAuth_WithPkceState()
    {
        var response = await _client.GetAsync("/api/v1/integrations/teams/connect");
        response.StatusCode.Should().Be(HttpStatusCode.Redirect);
        response.Headers.Location!.Query.Should().Contain("code_challenge");
    }

    [Fact]
    public async Task CreateTeamForWorkspace_AllMembersLinked_CreatesWorkspaceLink()
    {
        SetupGraphTeamCreateSuccess();
        var response = await CreateTeamsWorkspaceLinkAsync(_workspaceId);
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        await AssertWorkspaceTeamsLinkExists(_workspaceId);
    }

    [Fact]
    public async Task GraphWebhook_DuplicateDelivery_DoesNotCreateDuplicateMessage()
    {
        await PostWebhookAsync(_teamsMessageId);
        await PostWebhookAsync(_teamsMessageId);
        await AssertOneVoMessageCountForExternalId(_teamsMessageId, expected: 1);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Microsoft OAuth success | Integration | Account link created and token encrypted |
| Microsoft OAuth denied | Integration | User sees connection denied; no token saved |
| Refresh token expired | Unit + Integration | Connection marked `reauth_required` |
| Fetch contacts maps to ONEVO users | Unit | Matched users include `onevo_user_id` |
| Workspace members all linked | Unit | Team creation allowed |
| Workspace members partially linked | Unit | Missing member list returned |
| Create Team during workspace creation | Integration | Workspace link and default channel link created |
| Existing Team candidate matching | Unit | Match score + extra/missing members returned |
| Link existing Team | Integration | `workspace_teams_links` row created |
| Graph webhook validation challenge | Integration | Challenge echoed according to Graph contract |
| Duplicate webhook delivery | Integration | No duplicate ONEVO message |
| Graph throttling | Unit | Retry job scheduled using Retry-After |
| Tenant disables Teams sync | Integration | Endpoints return disabled/403 state |

## Security Tests

| Scenario | Expected |
|:---------|:---------|
| User without `workspaces:manage` links Team | 403 |
| User without `chat:write` sends outbound Teams message | 403 |
| Webhook with invalid signature | 401 |
| Graph token logged by exception | Logs scrubbed; token never appears |
| User attempts to link Team from another tenant | 403 |

---

## Related

- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
- [[modules/integrations/microsoft-teams/end-to-end-logic|Microsoft Teams Integration Logic]]
