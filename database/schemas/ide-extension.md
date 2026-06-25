# Schema: IDE Extension

**Module:** `ONEVO.Modules.IDEExtension`
**Phase:** 2
**Owner:** DEV7 (core + tag engine) + DEV8 (context engine + entitlement)

---

## `ide_extension_installs` - Phase 2

One row per device-user-editor combination. Tracks all active IDE extension installs.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK -> users |
| `tenant_id` | uuid | FK -> tenants |
| `workspace_id` | uuid | FK -> workspaces, nullable - active workspace at install time |
| `editor_type` | varchar(20) | vscode / jetbrains |
| `editor_version` | varchar(50) | e.g. 1.90.0 |
| `extension_version` | varchar(20) | e.g. 1.2.3 |
| `device_fingerprint` | varchar(255) | OS + hardware hash - not PII, used for dedup |
| `installed_at` | timestamptz | |
| `last_active_at` | timestamptz | Updated on each session start |
| `is_active` | boolean | Set to false on explicit uninstall |

**Index:** `(user_id, is_active)`, `(tenant_id)`

---

## `ide_sessions` - Phase 2

One row per editor session (extension activated -> deactivated). Used for tag execution audit and context tracking.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `install_id` | uuid | FK -> ide_extension_installs |
| `user_id` | uuid | FK -> users |
| `tenant_id` | uuid | FK -> tenants |
| `workspace_id` | uuid | FK -> workspaces, nullable |
| `active_project_id` | uuid | FK -> projects, nullable - updated on branch switch |
| `started_at` | timestamptz | |
| `ended_at` | timestamptz | nullable - null means session still open |

**Index:** `(user_id, started_at DESC)`, `(install_id)`

---

## `ide_tag_executions` - Phase 2

Full audit trail of every `@entity:action` command typed in the IDE extension.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK -> users |
| `tenant_id` | uuid | FK -> tenants |
| `session_id` | uuid | FK -> ide_sessions, nullable |
| `raw_tag_input` | text | The exact string the user typed (e.g. `@task:new "Fix bug" #sprint:current`) |
| `parsed_entity` | varchar(50) | task / sprint / time / chat / time_off / doc / board / okr / review / notify |
| `parsed_action` | varchar(50) | new / status / assign / log / send / request / view / move / link / approve |
| `resolved_params` | jsonb | Parameters after autocomplete resolution |
| `permission_check_result` | varchar(20) | allowed / denied |
| `execution_status` | varchar(20) | pending / success / failed / undone |
| `created_entity_type` | varchar(50) | nullable - task / time_log / message / time_off_request |
| `created_entity_id` | uuid | nullable |
| `undo_expires_at` | timestamptz | nullable - set for reversible actions |
| `undone_at` | timestamptz | nullable - set when user clicks undo |
| `executed_at` | timestamptz | |

**Index:** `(user_id, executed_at DESC)`, `(session_id)`, `(execution_status, undo_expires_at)` where status = pending

**Note:** `id` is referenced by `ai_action_jobs.tag_execution_id` - AI auto-creates that originate from a tag share the same undo state machine.

---

## `ide_context_links` - Phase 2

User-created or auto-detected links between code context (branch/file) and Work Management entities.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK -> users |
| `tenant_id` | uuid | FK -> tenants |
| `repository_url` | varchar(500) | Full clone URL of the repo |
| `branch_name` | varchar(255) | Git branch name |
| `file_path` | varchar(1000) | nullable - for file-level links |
| `entity_type` | varchar(30) | task / project / sprint / document |
| `entity_id` | uuid | ID of the linked entity |
| `link_type` | varchar(30) | branch / commit / file / pr |
| `created_at` | timestamptz | |
| `created_by` | uuid | FK -> users |

**Index:** `(repository_url, branch_name)` - primary lookup for branch context detection
**Index:** `(tenant_id, entity_type, entity_id)`

---

## `ide_chat_threads` - Phase 2

Tracks chat threads that were started with code context (e.g. user opened a task-linked chat from within the IDE).

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `channel_id` | uuid | FK -> channels |
| `user_id` | uuid | FK -> users |
| `ide_session_id` | uuid | FK -> ide_sessions, nullable |
| `context_task_id` | uuid | FK -> tasks, nullable - task that was in context when thread started |
| `context_file_path` | varchar(1000) | nullable - file that was open |
| `last_message_at` | timestamptz | |

---

## Related Tables (owned by other modules, used by IDE Extension)

| Table | Owner Module | How IDE Extension Uses It |
|:------|:-------------|:--------------------------|
| `agent_install_entitlements` | AgentGateway | Checked server-side on every install request |
| `agent_install_jobs` | AgentGateway | Created when user approves monitoring agent install |
| `registered_agents` | AgentGateway | Checked to determine if agent already installed |
| `channels` | Work Management.Chat | Chat sidebar panel - list and subscribe to channels |
| `messages` | Work Management.Chat | Chat sidebar panel - send and receive messages |
| `tasks` | Work Management.Tasks | Tasks panel - list assigned tasks |
| `time_logs` | Work Management.Time | Time tracking - start/stop timer |
| `repositories` | Work Management.Integrations | Context engine - resolve branch to repo |
| `task_repository_links` | Work Management.Integrations | Context engine - resolve branch to task |
