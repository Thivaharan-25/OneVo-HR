# Schema: Microsoft Teams Integration

**Module:** Integrations — Microsoft Teams
**Phase:** Phase 2
**Tables:** 8

---

## `external_account_connections`

User-level link between an ONEVO user and their Microsoft Teams (Azure AD) account.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `provider` | `varchar(30)` | `microsoft_teams` |
| `azure_ad_user_id` | `varchar(255)` | Azure AD object ID — used for Graph calls |
| `display_name` | `varchar(255)` | Display name from Graph `/me` |
| `external_email` | `varchar(255)` | Microsoft account email from Graph `/me` |
| `status` | `varchar(20)` | `active`, `reauth_required`, `revoked` |
| `linked_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, user_id, provider)`
**Index:** `(tenant_id, azure_ad_user_id)` — used for inbound message sender resolution

**Foreign Keys:** `tenant_id` → tenants, `user_id` → users

---

## `microsoft_graph_tokens`

Encrypted OAuth tokens for Microsoft Graph API calls per user connection.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `external_account_connection_id` | `uuid` | FK → external_account_connections |
| `access_token_encrypted` | `bytea` | Short-lived; nullable when expired |
| `refresh_token_encrypted` | `bytea` | Long-lived; encrypted via IEncryptionService |
| `scopes` | `jsonb` | Array of granted Graph scopes |
| `expires_at` | `timestamptz` | Access token expiry |
| `status` | `varchar(20)` | `active`, `reauth_required`, `revoked` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, user_id)`

Raw tokens are never returned to the frontend or logged.

**Foreign Keys:** `tenant_id` → tenants, `user_id` → users, `external_account_connection_id` → external_account_connections

---

## `teams_webhook_subscriptions`

Tracks active Microsoft Graph change notification subscriptions for Teams channels and chats.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `graph_subscription_id` | `varchar(100)` | ID returned by Graph POST /subscriptions |
| `resource` | `varchar(500)` | Graph resource path e.g. `/teams/{id}/channels/{id}/messages` |
| `resource_type` | `varchar(30)` | `channel_messages`, `chat_messages`, `users` |
| `change_types` | `varchar(100)` | Comma-separated: `created,updated,deleted` |
| `notification_url` | `varchar(500)` | ONEVO webhook endpoint for Graph callbacks |
| `client_state` | `varchar(255)` | HMAC-SHA256 value for webhook validation |
| `expiry_date` | `timestamptz` | When Graph subscription expires |
| `status` | `varchar(20)` | `active`, `expired`, `failed` |
| `last_renewed_at` | `timestamptz` | Nullable; set by TeamsWebhookRenewalJob |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, graph_subscription_id)`
**Index:** `(tenant_id, status, expiry_date)` — used by renewal job query

**Foreign Keys:** `tenant_id` → tenants

---

## `teams_delta_sync_state`

Stores the delta token per resource so incremental Graph delta queries resume correctly after a webhook gap or subscription expiry.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `resource_type` | `varchar(30)` | `channel_messages`, `chat_messages` |
| `teams_team_id` | `varchar(255)` | Nullable; Teams team ID for channel resources |
| `teams_channel_id` | `varchar(255)` | Nullable; Teams channel ID |
| `teams_chat_id` | `varchar(255)` | Nullable; Teams chat ID for chat resources |
| `delta_token` | `text` | Opaque token from Graph delta response `@odata.deltaLink` |
| `last_synced_at` | `timestamptz` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, resource_type, teams_team_id, teams_channel_id)` for channel resources; `(tenant_id, resource_type, teams_chat_id)` for chat resources

**Foreign Keys:** `tenant_id` → tenants

---

## `workspace_teams_links`

Maps an ONEVO WorkSync workspace to a Microsoft Teams team/group.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `workspace_id` | `uuid` | FK → workspaces |
| `teams_team_id` | `varchar(255)` | Microsoft Teams team/group ID |
| `teams_team_name` | `varchar(255)` | Display name at link time |
| `teams_team_url` | `varchar(500)` | Nullable; deep link to the Team |
| `sync_enabled` | `boolean` | Admin can pause sync without deleting the link |
| `status` | `varchar(20)` | `active`, `paused`, `failed` |
| `linked_by_id` | `uuid` | FK → users — workspace admin who created the link |
| `linked_at` | `timestamptz` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, workspace_id)` — one workspace maps to at most one Team
**Unique:** `(tenant_id, teams_team_id)` — one Team maps to at most one workspace

**Foreign Keys:** `tenant_id` → tenants, `workspace_id` → workspaces, `linked_by_id` → users

---

## `channel_teams_links`

Maps an ONEVO chat channel to a Microsoft Teams channel within the linked Team.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `onevo_channel_id` | `uuid` | FK → channels (WMS chat) |
| `workspace_teams_link_id` | `uuid` | FK → workspace_teams_links |
| `teams_channel_id` | `varchar(255)` | Microsoft Teams channel ID |
| `teams_channel_name` | `varchar(255)` | Display name at link time |
| `sync_direction` | `varchar(20)` | `inbound`, `outbound`, `two_way` |
| `status` | `varchar(20)` | `active`, `paused`, `failed` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, onevo_channel_id)` — one ONEVO channel maps to at most one Teams channel
**Unique:** `(tenant_id, workspace_teams_link_id, teams_channel_id)`

**Foreign Keys:** `tenant_id` → tenants, `onevo_channel_id` → channels, `workspace_teams_link_id` → workspace_teams_links

---

## `teams_member_sync_status`

Tracks which workspace members have linked their Teams account — used for eligibility checks before Team creation or linking.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `workspace_teams_link_id` | `uuid` | FK → workspace_teams_links |
| `user_id` | `uuid` | FK → users |
| `external_account_connection_id` | `uuid` | FK → external_account_connections; nullable if not linked |
| `is_linked` | `boolean` | True if user has an active Teams account connection |
| `synced_at` | `timestamptz` | When this status was last evaluated |
| `created_at` | `timestamptz` | |

**Unique:** `(tenant_id, workspace_teams_link_id, user_id)`

**Foreign Keys:** `tenant_id` → tenants, `workspace_teams_link_id` → workspace_teams_links, `user_id` → users, `external_account_connection_id` → external_account_connections

---

## `teams_message_sync_state`

Idempotency and sync state for messages flowing between ONEVO chat and Teams. Prevents duplicate messages in either direction.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `onevo_message_id` | `uuid` | FK → messages (WMS chat); nullable for inbound-only before local message created |
| `channel_teams_link_id` | `uuid` | FK → channel_teams_links |
| `external_source` | `varchar(30)` | `microsoft_teams` |
| `external_message_id` | `varchar(255)` | Teams message ID from Graph |
| `external_conversation_id` | `varchar(255)` | Teams channel or chat ID |
| `external_reply_to_id` | `varchar(255)` | Nullable; parent message ID for thread replies |
| `sync_direction` | `varchar(20)` | `inbound`, `outbound` |
| `sync_status` | `varchar(20)` | `synced`, `pending`, `failed`, `skipped` |
| `last_synced_at` | `timestamptz` | Nullable |
| `last_error` | `text` | Nullable; last sync error message |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, external_source, external_message_id)` — primary idempotency key
**Index:** `(tenant_id, sync_status)` where sync_status in ('pending', 'failed') — used by retry job
**Index:** `(onevo_message_id)` where onevo_message_id is not null

**Foreign Keys:** `tenant_id` → tenants, `onevo_message_id` → messages, `channel_teams_link_id` → channel_teams_links

---

## Related

- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
- [[modules/integrations/microsoft-teams/end-to-end-logic|End-to-End Logic]]
- [[database/schemas/wms-chat|WMS Chat Schema]]
- [[database/schemas/wms-project-management|WMS Project Management Schema]]
- [[database/schemas/shared-platform|Shared Platform Schema]]
- [[database/schema-catalog|Schema Catalog]]
