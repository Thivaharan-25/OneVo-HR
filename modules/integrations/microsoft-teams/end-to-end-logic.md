# Microsoft Teams Integration - End-to-End Logic

**Module:** Integrations
**Feature:** Microsoft Teams Integration
**Phase:** Phase 2 - deferred. Workspace/member sync and chat/message sync are not active Phase 1 Work scope unless explicitly reactivated.

---


```
  -> [Authenticated]
  -> TeamsOAuthStartHandler
    -> 1. Verify tenant has Microsoft Teams integration enabled
    -> 2. Build Microsoft authorization URL with tenant-approved scopes
    -> 3. Store anti-forgery state + PKCE verifier
    -> 4. Redirect user to Microsoft consent

  -> TeamsOAuthCallbackHandler
    -> 1. Validate state and PKCE verifier
    -> 2. Exchange code for access + refresh token
    -> 3. Call Graph /me to get azure_ad_user_id, mail, displayName
    -> 4. Match to ONEVO users.email / employees work email
    -> 5. UPSERT external_account_connections
    -> 6. Store refresh token encrypted in microsoft_graph_tokens
    -> 7. Publish TeamsAccountLinkedEvent
```


```
  -> [RequirePermission("workspaces:manage")]
  -> TeamsContactSearchHandler
    -> 2. Query Graph people/users with query text
    -> 3. Match results to ONEVO users by azure_ad_user_id or email
    -> 4. Return contacts with:
         - teams_user_id
         - display_name
         - email
         - onevo_user_id if matched
         - is_onevo_member
         - can_sync_to_workspace
```


```
  -> [RequirePermission("workspaces:manage")]
  -> WorkspaceTeamsEligibilityHandler
    -> 1. Load workspace_members
    -> 2. For each member, check external_account_connections(provider = "microsoft_teams")
    -> 3. Return:
         all_members_linked
         linked_count
         missing_members[]
         can_create_team
         can_link_existing_team
```


```
POST /api/v1/workspaces
  body: {
    name,
    slug,
    members[],
    teams_sync: {
      create_team: true,
      sync_existing_team_id: null,
      create_default_channel: true
    }
  }
  -> CreateWorkspaceHandler
    -> 1. Create workspace, roles, and members transactionally
    -> 2. If teams_sync.create_team = true:
         d. INSERT workspace_teams_links
         a. Keep workspace
         b. Mark workspace_teams_links.status = failed
         c. Show retry action to workspace admin
```


```
  -> WorkspaceTeamsCandidateHandler
    -> 1. Load workspace member emails / azure_ad_user_ids
    -> 4. Return candidates with match_score, missing_in_teams, extra_in_teams

  body: { teams_team_id, sync_members: true }
  -> LinkExistingTeamHandler
    -> 2. Show/validate member diff
    -> 3. INSERT workspace_teams_links
    -> 4. UPSERT teams_member_sync_status for linked members
    -> 5. Subscribe to required Graph workspace/member notifications if approved
```

## Outbound Message Sync - Phase 2

```
POST /api/v1/channels/{id}/messages
  -> SendMessageHandler
    -> 1. Save ONEVO message
    -> 2. Publish MessageSentEvent
    -> 3. TeamsOutboundMessageSyncHandler
       a. Check channel_teams_links
       d. UPSERT teams_message_sync_state with external_message_id
       e. Set messages.sync_status = synced
```

## Inbound Message Sync - Phase 2

```
  -> TeamsMessageWebhookHandler
    -> 1. Validate Graph webhook signature/challenge
    -> 2. Resolve teams_team_id/channel_id/chat_id to ONEVO channel
    -> 3. Use delta token to fetch changed messages
         a. Check teams_message_sync_state for duplicate
         b. Map sender to ONEVO user
         c. INSERT messages with external_source = "microsoft_teams"
         d. INSERT teams_message_sync_state
         e. Push SignalR update to ONEVO channel
```

## Graph Webhook Renewal


```
Hangfire recurring job: TeamsWebhookRenewalJob
  Cadence: daily at 02:00 UTC

  1. Load all teams_webhook_subscriptions where status = active
  2. For each subscription where expiry_date < NOW() + 3 days:
       a. Call Graph PATCH /subscriptions/{id}
            body: { expirationDateTime: NOW() + max_lifetime }
       b. On success -> update expiry_date + last_renewed_at
       c. On 404 (subscription gone) -> set status = expired; trigger re-subscribe
       d. On throttle (429) -> honour Retry-After header; defer to next job run
       e. On other error -> set status = failed; fall back to delta poll for that resource

  3. For any subscription with status = expired or failed:
       a. Query teams_delta_sync_state for the same resource
       b. Use stored delta_token to poll Graph /messages/delta directly
       c. Process delta results same as webhook inbound path
       d. Attempt to re-create subscription; on success set status = active
```

Re-subscription flow:
```
POST /subscriptions
  changeType: created,updated,deleted
  expirationDateTime: NOW() + max_lifetime
  clientState: HMAC-SHA256(tenant_id + subscription_id, webhook_secret)
  -> On success: INSERT or UPDATE teams_webhook_subscriptions
```

Subscription lifetime constants:
| Resource type | Max lifetime |
|:---|:---|
| Channel messages | 60 days |
| Chat messages | 60 minutes (must be renewed frequently; prefer delta poll for chats) |
| Users/groups | 29 days |

For chat message subscriptions (1-hour max), ONEVO defaults to delta poll rather than webhook subscription unless the tenant has approved Application-level permissions. Chat webhooks are opt-in per tenant.

---

## Error Scenarios

| Scenario | Handling |
|:---------|:---------|
| Graph token expired | Refresh token; retry once; mark reauth_required if refresh fails |
| Graph throttling | Respect retry-after and queue retry job |

---

## Related

- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
- [[modules/integrations/microsoft-teams/testing|Microsoft Teams Integration Testing]]
- [[modules/work-management/foundation/end-to-end-logic|Work Foundation Logic]]
