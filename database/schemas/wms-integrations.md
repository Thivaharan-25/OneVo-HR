# Schema: WMS — Integration & API

**Module:** `WorkSync.Integrations`
**Phase:** 1
**Owner:** DEV8

---

## `repositories` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `tenant_id` | uuid | FK → tenants |
| `provider` | varchar(20) | github / gitlab / bitbucket |
| `full_name` | varchar(255) | e.g. `org/repo` |
| `url` | varchar(500) | Clone URL |
| `default_branch` | varchar(100) | default 'main' |
| `auth_provider_id` | uuid | FK → auth_providers, nullable — OAuth connection |
| `webhook_secret` | varchar(255) | nullable — HMAC secret for webhook validation |
| `is_active` | boolean | default true |
| `created_at` | timestamptz | |

**Index:** `(workspace_id)`, `(tenant_id, provider)`

---

## `task_repository_links` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK → tasks |
| `repository_id` | uuid | FK → repositories |
| `linked_by` | uuid | FK → users |
| `linked_at` | timestamptz | |

**Unique:** `(task_id, repository_id)`

---

## `code_activity_events` — Phase 1

Unified event stream from GitHub/GitLab webhooks and IDE extension.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK → users, nullable — resolved from commit email / PR author |
| `tenant_id` | uuid | FK → tenants |
| `repository_id` | uuid | FK → repositories, nullable |
| `event_type` | varchar(30) | commit / push / pr_opened / pr_merged / pr_closed / branch_created / review_submitted / ci_started / ci_completed |
| `branch_name` | varchar(255) | nullable |
| `task_id` | uuid | FK → tasks, nullable — auto-resolved from commit message or PR |
| `event_metadata` | jsonb | Raw event payload (sanitized) |
| `occurred_at` | timestamptz | |
| `source` | varchar(30) | ide_extension / github_webhook / gitlab_webhook |

**Index:** `(repository_id, occurred_at DESC)`, `(task_id)` where not null, `(tenant_id, occurred_at DESC)`

---

## `commit_records` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `repository_id` | uuid | FK → repositories |
| `sha` | varchar(40) | Git SHA — UNIQUE |
| `author_user_id` | uuid | FK → users, nullable — resolved from commit email |
| `message` | text | |
| `task_ids` | uuid[] | Extracted task references from message |
| `committed_at` | timestamptz | |
| `pushed_at` | timestamptz | nullable |

**Unique:** `(repository_id, sha)`

---

## `pull_request_records` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `repository_id` | uuid | FK → repositories |
| `external_pr_id` | varchar(50) | Provider PR ID |
| `title` | varchar(500) | |
| `url` | varchar(500) | |
| `status` | varchar(20) | open / merged / closed |
| `author_user_id` | uuid | FK → users, nullable |
| `task_ids` | uuid[] | Extracted task references from title/body |
| `opened_at` | timestamptz | |
| `merged_at` | timestamptz | nullable |
| `closed_at` | timestamptz | nullable |

**Unique:** `(repository_id, external_pr_id)`

---

## `ci_pipeline_runs` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `repository_id` | uuid | FK → repositories |
| `external_run_id` | varchar(100) | Provider pipeline/action run ID |
| `branch_name` | varchar(255) | |
| `status` | varchar(20) | pending / running / success / failed / cancelled |
| `task_ids` | uuid[] | Tasks linked to this branch |
| `started_at` | timestamptz | |
| `finished_at` | timestamptz | nullable |

**Index:** `(repository_id, branch_name)`, `(status)` where status in (pending, running)

---

## `task_automation_rules` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `rule_name` | varchar(100) | |
| `trigger_type` | varchar(50) | commit_pushed / pr_opened / pr_merged / pr_closed / branch_created / ci_success / ci_failed |
| `condition_json` | jsonb | e.g. `{ "branch_pattern": "feat/*", "repo_id": "..." }` |
| `action_type` | varchar(50) | update_task_status / assign_task / add_label / log_time / post_chat_message |
| `action_params` | jsonb | Parameters for the action e.g. `{ "status": "in_progress" }` |
| `is_active` | boolean | default true |
| `created_by` | uuid | FK → users |
| `created_at` | timestamptz | |

**Index:** `(workspace_id, is_active, trigger_type)` — used by automation rule engine query

**Automation engine (Hangfire):** After each webhook event, query active rules for workspace where trigger_type matches. Evaluate condition_json against event. If match, execute action_type with action_params. Log result in `audit_logs`.
