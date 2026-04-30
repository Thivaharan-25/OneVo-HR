# Schema: WMS — Chat + Chat AI

**Module:** `WorkSync.Chat` + `WorkSync.ChatAI`
**Phase:** 1 + Phase 2 Teams sync additions
**Owner:** DEV7

---

## `channels` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `tenant_id` | uuid | FK → tenants |
| `name` | varchar(100) | nullable for DMs |
| `description` | text | nullable |
| `channel_type` | varchar(20) | public / private / direct |
| `created_by` | uuid | FK → users |
| `is_archived` | boolean | default false |
| `created_at` | timestamptz | |

**Index:** `(workspace_id, channel_type)`

---

## `channel_members` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `channel_id` | uuid | FK → channels |
| `user_id` | uuid | FK → users |
| `role` | varchar(20) | admin / member |
| `last_read_at` | timestamptz | nullable — for unread count calculation |
| `joined_at` | timestamptz | |

**Unique:** `(channel_id, user_id)`
**DM constraint:** channel_type = direct → exactly 2 members enforced at application layer

---

## `messages` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `channel_id` | uuid | FK → channels |
| `user_id` | uuid | FK → users |
| `content` | text | Rich text / markdown |
| `parent_message_id` | uuid | FK → messages, nullable — thread reply |
| `is_edited` | boolean | default false |
| `edited_at` | timestamptz | nullable |
| `is_deleted` | boolean | default false — soft delete |
| `deleted_at` | timestamptz | nullable |
| `created_at` | timestamptz | |

**Index:** `(channel_id, created_at DESC)`, `(parent_message_id)` where not null
**Teams sync columns:** `external_source`, `external_message_id`, `sync_direction`, and `sync_status` are required for Microsoft Teams two-way sync.
**Teams sync unique key:** `(tenant_id, external_source, external_message_id)` where `external_message_id IS NOT NULL`.

---

## `message_reactions` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `message_id` | uuid | FK → messages |
| `user_id` | uuid | FK → users |
| `emoji` | varchar(10) | Unicode emoji or shortcode |

**Unique:** `(message_id, user_id, emoji)`

---

## `message_attachments` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `message_id` | uuid | FK → messages |
| `file_asset_id` | uuid | FK → file_assets |

---

## `message_pins` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `channel_id` | uuid | FK → channels |
| `message_id` | uuid | FK → messages |
| `pinned_by` | uuid | FK → users |
| `pinned_at` | timestamptz | |

**Unique:** `(channel_id, message_id)`

---

## `premium_ai_detections` — Phase 1

One row per message that the AI processes. Only created when tenant has `premium_ai` feature flag.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `message_id` | uuid | FK → messages |
| `channel_id` | uuid | FK → channels |
| `detected_intent` | varchar(20) | task / report / issue / reminder / other |
| `confidence_score` | numeric(5,4) | 0.0000–1.0000 |
| `auto_created` | boolean | Whether an entity was auto-created |
| `created_entity_type` | varchar(30) | nullable — task / reminder |
| `created_entity_id` | uuid | nullable |
| `detected_at` | timestamptz | |

---

## `ai_action_jobs` — Phase 1

Universal undo state machine for all AI-triggered and IDE-tag-triggered reversible creates.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `detection_id` | uuid | FK → premium_ai_detections, nullable |
| `tag_execution_id` | uuid | FK → ide_tag_executions, nullable |
| `user_id` | uuid | FK → users |
| `tenant_id` | uuid | FK → tenants |
| `action_type` | varchar(50) | auto_create_task / auto_create_reminder / auto_update_status |
| `action_params` | jsonb | Params used to create the entity |
| `status` | varchar(20) | pending / finalized / undone / failed |
| `created_entity_type` | varchar(50) | nullable — task / reminder / etc |
| `created_entity_id` | uuid | nullable |
| `undo_expires_at` | timestamptz | nullable — 10s for chat AI, 30s for IDE tags |
| `undone_at` | timestamptz | nullable |
| `finalized_at` | timestamptz | nullable |
| `created_at` | timestamptz | |

**Index:** `(user_id, status, undo_expires_at)` — for Hangfire finalization job

**Hangfire job:** Scans `status = pending AND undo_expires_at < now()` every 5 seconds. Finalizes by creating the entity from `action_params` and setting `status = finalized`.

---

## `chat_reminder_items` — Phase 1

Two-way sync between chat and task status.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `channel_id` | uuid | FK → channels |
| `task_id` | uuid | FK → tasks, nullable |
| `user_id` | uuid | FK → users |
| `title` | varchar(255) | |
| `status` | varchar(20) | pending / done / snoozed |
| `reminder_at` | timestamptz | nullable |
| `created_at` | timestamptz | |

**Sync rule:** When `task.status` changes to `done`, linked `chat_reminder_items.status` is set to `done` via domain event. When `chat_reminder_items.status` is set to `done`, the linked task status updates via command.

---

## `channel_teams_links` - Phase 2

Maps ONEVO chat channels to Microsoft Teams channels or chats. Owned by WorkSync Chat; Graph credentials remain in Shared Platform integration tables.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK -> tenants |
| `workspace_id` | uuid | FK -> workspaces |
| `channel_id` | uuid | FK -> channels |
| `workspace_teams_link_id` | uuid | FK -> workspace_teams_links |
| `teams_team_id` | varchar(255) | Nullable for private/group chat links |
| `teams_channel_id` | varchar(255) | Nullable for direct/group Teams chat |
| `teams_chat_id` | varchar(255) | Nullable for Team channel links |
| `link_type` | varchar(20) | `team_channel`, `group_chat`, `one_to_one_chat` |
| `sync_direction` | varchar(20) | `two_way`, `onevo_to_teams`, `teams_to_onevo`, `paused` |
| `status` | varchar(20) | `active`, `paused`, `failed`, `disconnected` |
| `created_by_id` | uuid | FK -> users |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Unique:** `(tenant_id, channel_id)` where `status = 'active'`
**Index:** `(tenant_id, teams_team_id, teams_channel_id)`, `(tenant_id, teams_chat_id)`

---

## `teams_message_sync_state` - Phase 2

Idempotency and retry state for Microsoft Teams message sync.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK -> tenants |
| `channel_id` | uuid | FK -> channels |
| `message_id` | uuid | FK -> messages |
| `external_source` | varchar(30) | `microsoft_teams` |
| `external_message_id` | varchar(255) | Graph message ID |
| `external_conversation_id` | varchar(255) | Teams channel/chat ID |
| `sync_direction` | varchar(20) | `inbound`, `outbound` |
| `sync_status` | varchar(20) | `pending`, `synced`, `failed`, `skipped` |
| `last_synced_at` | timestamptz | nullable |
| `last_error` | text | nullable |
| `retry_count` | integer | default 0 |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Unique:** `(tenant_id, external_source, external_message_id)`
**Index:** `(tenant_id, sync_status, updated_at)`
