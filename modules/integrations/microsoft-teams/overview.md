# Microsoft Teams Integration

**Module:** Integrations
**Feature:** Microsoft Teams Integration
**Phase:** Phase 2 - deferred. Not part of Phase 1 Work scope unless explicitly reactivated.
**Owner:** Shared Platform + WorkSync

---

## Purpose

Connects ONEVO users and Work workspaces to Microsoft Teams through Microsoft Graph in Phase 2. Workspace/team mapping, member sync, ONEVO Chat channel/message sync, private chat sync, and advanced edit/delete/reaction parity are not active Phase 1 Work scope unless explicitly reactivated.


---

## Scope

### Included

- Tenant-level Microsoft Graph app configuration.
- Phase 2: link a Work workspace to a Microsoft Team.
- Sync workspace members to the linked Microsoft Team membership view.
- Maintain webhook/delta sync state and idempotency.

### Not Included

- Meeting transcript ingestion or AI meeting summaries.
- Discrepancy detection for unscheduled meetings.
- ONEVO Chat channel/message sync.
- Private 1:1 or group chat sync.

---

## Microsoft Graph Permissions

Graph scopes must be minimized and tenant-admin approved before sync is enabled.

| Capability | Delegated/Application Scope |
|:-----------|:----------------------------|
| Link current user | `User.Read`, `offline_access` |
| Read tenant users for matching | `User.ReadBasic.All` or admin-approved directory read |
| Read team/channel metadata | Minimal approved Team/channel read scope |
| Read team members | Minimal approved Team member read scope |
| Subscriptions/delta | Graph change notifications + delta APIs |

Private 1:1, group chat sync, and channel message sync require stronger Graph permissions and are Phase 2.

---

## Public Interface

```csharp
public interface IMicrosoftTeamsIntegrationService
{
    Task<Result<TeamsAccountStatusDto>> GetAccountStatusAsync(Guid userId, CancellationToken ct);
    Task<Result<IReadOnlyList<TeamsContactDto>>> SearchContactsAsync(Guid userId, string query, CancellationToken ct);
    Task<Result<WorkspaceTeamsEligibilityDto>> GetWorkspaceEligibilityAsync(Guid workspaceId, CancellationToken ct);
    Task<Result<TeamsWorkspaceLinkDto>> CreateTeamForWorkspaceAsync(Guid workspaceId, TeamsCreateOptions options, CancellationToken ct);
    Task<Result<IReadOnlyList<TeamsGroupCandidateDto>>> FindMatchingTeamsAsync(Guid workspaceId, CancellationToken ct);
    Task<Result<TeamsWorkspaceLinkDto>> LinkExistingTeamAsync(Guid workspaceId, string teamsTeamId, CancellationToken ct);
    Task<Result<TeamsMemberSyncResultDto>> SyncWorkspaceMembersAsync(Guid workspaceId, CancellationToken ct);
}
```

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|

---

## Database Tables

Owned schema is documented in [[database/schemas/shared-platform|Shared Platform Schema]] for account/token/subscription data and [[database/schemas/wms-project-management|WMS Project Management Schema]] for WorkSync mappings.

Required tables:

- `external_account_connections`
- `microsoft_graph_tokens`
- `teams_webhook_subscriptions`
- `teams_delta_sync_state`
- `workspace_teams_links`
- `teams_member_sync_status`

---

## Key Business Rules

1. Workspace/member sync is idempotent by `(tenant_id, workspace_teams_link_id, user_id)`.
2. Sync failures are recorded and retried; users see a sync warning rather than duplicate membership rows.

---

## Related

- [[modules/work-management/foundation/overview|Work Foundation]]
- [[database/schemas/shared-platform|Shared Platform Schema]]
- [[backend/external-integrations|External Integrations]]
- [[security/compliance|Compliance]]
