# Microsoft Teams Integration

**Module:** Integrations
**Feature:** Microsoft Teams Integration
**Phase:** Phase 2
**Owner:** Shared Platform + WorkSync

---

## Purpose

Connects ONEVO users and WorkSync workspaces to Microsoft Teams through Microsoft Graph. Supports user account linking, Teams contact/member discovery, workspace-to-Team mapping, optional Team creation during workspace creation, existing Team sync, and two-way message sync between ONEVO Chat and Teams.

This integration is not the same as Activity Monitoring meeting detection. Activity Monitoring detects that Teams was used on the device; this module reads and writes Teams data through Graph only after tenant/user consent.

---

## Scope

### Included

- Tenant-level Microsoft Graph app configuration.
- User-level Teams account linking.
- Fetch Teams contacts/users and map them to ONEVO users/employees.
- Detect whether all workspace members have linked Teams accounts.
- Create a new Microsoft Team/group when a workspace is created, when requested by checkbox.
- Search and link an existing Microsoft Team with matching members.
- Send ONEVO chat messages to linked Teams conversations.
- Pull Teams messages into ONEVO chat.
- Sync message edits, deletes, reactions, and attachments where Graph permissions allow.
- Maintain webhook/delta sync state and idempotency.

### Not Included

- Meeting transcript ingestion or AI meeting summaries.
- Activity Monitoring Teams process detection.
- Discrepancy detection for unscheduled meetings.
- Bypassing ONEVO RBAC. ONEVO permissions remain enforced before any outbound Teams action.

---

## Microsoft Graph Permissions

Graph scopes must be minimized and tenant-admin approved before sync is enabled.

| Capability | Delegated/Application Scope |
|:-----------|:----------------------------|
| Link current user | `User.Read`, `offline_access` |
| Read tenant users for matching | `User.ReadBasic.All` or admin-approved directory read |
| Read joined Teams/channels | `Team.ReadBasic.All`, `Channel.ReadBasic.All` |
| Create Team/group | `Group.ReadWrite.All`, `Team.Create` where available |
| Read channel messages | `ChannelMessage.Read.All` |
| Send channel messages | `ChannelMessage.Send` or application send equivalent when approved |
| Read chat messages | `Chat.Read` / `Chat.ReadWrite` depending on supported scope |
| Send chat messages | `ChatMessage.Send` or approved Graph send permission |
| Subscriptions/delta | Graph change notifications + delta APIs |

Private 1:1 and group chat sync requires stronger Graph permissions than channel sync. Tenants may enable channel sync only.

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
    Task<Result> SendOneVoMessageToTeamsAsync(Guid messageId, CancellationToken ct);
    Task<Result> ImportTeamsMessageAsync(TeamsMessageWebhookDto webhook, CancellationToken ct);
}
```

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/integrations/teams/status` | Authenticated | Current user's Teams link status |
| GET | `/api/v1/integrations/teams/connect` | Authenticated | Start Microsoft OAuth consent |
| GET | `/api/v1/integrations/teams/callback` | Public callback | OAuth callback; stores encrypted refresh token |
| DELETE | `/api/v1/integrations/teams/disconnect` | Authenticated | Disconnect current user's Teams account |
| GET | `/api/v1/integrations/teams/contacts` | `chat:write` | Search Teams contacts visible to current user |
| GET | `/api/v1/workspaces/{id}/teams/eligibility` | `workspaces:manage` | Check member linking and Teams sync readiness |
| GET | `/api/v1/workspaces/{id}/teams/candidates` | `workspaces:manage` | Find existing Teams groups with matching members |
| POST | `/api/v1/workspaces/{id}/teams/create` | `workspaces:manage` | Create a Microsoft Team for this workspace |
| POST | `/api/v1/workspaces/{id}/teams/link` | `workspaces:manage` | Link an existing Microsoft Team |
| POST | `/api/v1/integrations/teams/webhooks/messages` | Graph webhook | Receive Teams message change notifications |

---

## Database Tables

Owned schema is documented in [[database/schemas/shared-platform|Shared Platform Schema]] for account/token/subscription data and [[database/schemas/wms-chat|WMS Chat Schema]] / [[database/schemas/wms-project-management|WMS Project Management Schema]] for WorkSync mappings.

Required tables:

- `external_account_connections`
- `microsoft_graph_tokens`
- `teams_webhook_subscriptions`
- `teams_delta_sync_state`
- `workspace_teams_links`
- `channel_teams_links`
- `teams_member_sync_status`
- `teams_message_sync_state`

---

## Key Business Rules

1. Teams sync is disabled until a tenant admin configures Microsoft Graph and required scopes are approved.
2. A ONEVO user can send to Teams only if their Teams account is linked and their ONEVO permissions allow the chat action.
3. Workspace Team creation is optional and must be explicitly chosen during workspace creation.
4. Existing Team sync must show member match quality before linking.
5. ONEVO never silently invites unmanaged external Teams users into ONEVO workspaces.
6. Inbound Teams messages are mapped by Azure AD user id or verified email. Unmatched senders are imported as external participants only if tenant policy allows it.
7. Message sync is idempotent by `(tenant_id, external_source, external_message_id)`.
8. Deleting a message in ONEVO soft-deletes it locally and attempts a Teams delete only when the caller has Teams permission and tenant policy allows outbound deletes.
9. Sync failures are recorded and retried; users see a sync warning rather than a duplicate message.
10. Teams message content is confidential communication data and follows chat retention/legal-hold rules.

---

## Related

- [[modules/work-management/foundation/overview|WorkSync Foundation]]
- [[modules/work-management/chat/overview|Chat & Messaging]]
- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync Logic]]
- [[modules/work-management/chat/teams-sync/testing|Teams Chat Sync Testing]]
- [[database/schemas/shared-platform|Shared Platform Schema]]
- [[database/schemas/wms-chat|WMS Chat Schema]]
- [[backend/external-integrations|External Integrations]]
- [[security/compliance|Compliance]]
