# Integration & API (GitHub, CI/CD, Automation) - Phase 2

**Module:** WorkSync
**Feature:** Integration & API
**Phase:** Phase 2 - deferred
**Phase 1 Status:** Not active in current Phase 1 Work implementation. Keep as future integration and repository automation design reference.
**Namespace:** `WorkSync.Integrations`
**Owner:** DEV8
**Tables:** 7

---

## Purpose

Phase 2 GitHub repository integration (webhook events, commit tracking, PR tracking), CI/CD pipeline run tracking, and automation rules that trigger actions when webhook events arrive. GitHub webhook events and IDE extension events both write to the unified `code_activity_events` stream.

---

## Database Tables

### `repositories`
Key columns: `workspace_id`, `tenant_id`, `name`, `clone_url`, `provider` (`github`, `gitlab`, `bitbucket`), `webhook_secret` (used for HMAC validation), `github_repo_id`, `is_active`, `connected_by_id`.

### `task_repository_links`
Explicit user-created task-to-repo links. Key columns: `task_id`, `repository_id`, `created_by_id`, `created_at`.

Distinct from commit-level auto-detection in `commit_records.task_ids`.

### `code_activity_events`
Unified stream of all code events. Key columns: `repository_id`, `workspace_id`, `tenant_id`, `event_type` (`push`, `pr_opened`, `pr_merged`, `pr_closed`, `ci_started`, `ci_completed`), `source` (`github_webhook`; Phase 2 may add `ide_extension`), `actor_user_id`, `payload_json`, `received_at`.

Phase 2 GitHub webhooks and VS Code IDE extension events write here, differentiated by `source`.

### `commit_records`
Parsed commit data. Key columns: `code_activity_event_id`, `repository_id`, `commit_sha`, `message`, `author_name`, `author_email`, `committed_at`, `task_ids uuid[]` (auto-detected from `[TASK-123]` or `#123` patterns in commit message).

`task_ids` is populated by parsing the commit message at webhook receive time.

### `pull_request_records`
PR data. Key columns: `code_activity_event_id`, `repository_id`, `pr_number`, `title`, `description`, `state` (`open`, `merged`, `closed`), `source_branch`, `target_branch`, `author_user_id`, `merged_at`, `task_ids uuid[]`.

PR merge -> `code_activity_events` with `event_type = pr_merged` -> can trigger automation rules.

### `ci_pipeline_runs`
CI/CD run data. Key columns: `code_activity_event_id`, `repository_id`, `pipeline_name`, `branch`, `commit_sha`, `status` (`running`, `success`, `failure`, `cancelled`), `started_at`, `finished_at`, `duration_seconds`, `pipeline_url`.

### `task_automation_rules`
Phase 2 webhook-triggered automation rules. Key columns: `workspace_id`, `tenant_id`, `name`, `trigger_type` (`pr_merged`, `ci_success`, `ci_failure`, `push`), `condition_json` (`branch_pattern`, `repo_id`), `action_type` (`update_task_status`, `post_chat_message`, `assign_task`), `action_params_json`, `is_active`, `created_by_id`.

---

## Key Business Rules

1. **Webhook HMAC validation:** Every GitHub webhook request must be validated against `repositories.webhook_secret` using HMAC-SHA256 before processing. Reject with 401 if invalid.
2. **Task auto-detection:** Parse commit message for `[TASK-123]` or `#123` patterns -> populate `commit_records.task_ids`. This is best-effort - no FK constraint on `task_ids` array elements.
3. **Automation rule evaluation is Phase 2:** Hangfire evaluates rules after each `code_activity_events` insert. Query: `WHERE workspace_id = ? AND is_active = true AND trigger_type = ?` (indexed). Evaluate `condition_json` against event payload.
4. **Rule idempotency:** Same event processed twice must not duplicate actions. Use `code_activity_event_id` as idempotency key.
5. **All rule evaluations logged** in `audit_logs` with `rule_id` and action taken.
6. `task_repository_links` is the explicit user-created link (different from auto-detected commit references in `commit_records.task_ids`).

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `WebhookReceivedEvent` | Validated webhook arrives | Creates code_activity_events row, rule evaluation is Phase 2 |
| `CIPipelineFailedEvent` | ci_pipeline_runs.status -> failure | Phase 2 notifications/channel and automation rules |
| `PullRequestMergedEvent` | pr_records.state -> merged | Phase 2 automation rules and task status update |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workspaces/{wsId}/repositories` | `integrations:read` | List connected repos |
| POST | `/api/v1/workspaces/{wsId}/repositories` | `integrations:manage` | Connect repository |
| DELETE | `/api/v1/repositories/{id}` | `integrations:manage` | Disconnect repository |
| POST | `/api/v1/webhooks/github/{repoId}` | public (HMAC) | GitHub webhook receiver |
| GET | `/api/v1/tasks/{id}/repository-links` | `tasks:read` | Task repo links |
| POST | `/api/v1/tasks/{id}/repository-links` | `tasks:write` | Link task to repo |
| GET | `/api/v1/workspaces/{wsId}/automation-rules` | `integrations:read` | Phase 2: list automation rules |
| POST | `/api/v1/workspaces/{wsId}/automation-rules` | `integrations:manage` | Phase 2: create rule |
| PATCH | `/api/v1/automation-rules/{id}` | `integrations:manage` | Phase 2: update/toggle rule |

---

## Related

- [[Userflow/Work-Management/integration-automation-flow|WorkSync Integration Automation]] - repository connection and rule user flow

- [[modules/work-management/tasks/overview|Task Management]] - task_ids auto-detection, task_repository_links
- [[modules/ide-extension/overview|IDE Extension]] - IDE events also write to code_activity_events
- [[database/schemas/wms-integrations|WMS Integrations Schema]]
- [[current-focus/DEV8-documents-github-ide|DEV8 Tasks 2, 3]]
