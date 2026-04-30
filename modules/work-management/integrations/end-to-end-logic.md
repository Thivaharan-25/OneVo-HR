# Integration & API — End-to-End Logic

**Module:** WorkSync
**Feature:** Integration & API

---

## GitHub Webhook Processing

```
POST /api/v1/webhooks/github/{repoId}
  (public endpoint — no JWT, validated via HMAC)
  → 1. Load repositories row by repoId
  → 2. HMAC-SHA256 validation:
         expected = HMAC(webhook_secret, raw_request_body)
         actual = X-Hub-Signature-256 header
         If mismatch: return 401 INVALID_SIGNATURE — do not process
  → 3. Parse event type from X-GitHub-Event header
  → 4. INSERT code_activity_events:
         repository_id, workspace_id, tenant_id
         event_type = mapped event (push/pr_opened/pr_merged/ci_*)
         source = "github_webhook"
         actor_user_id = lookup by github user email (nullable)
         payload_json = full webhook body
         received_at = now()
  → 5. Based on event_type:
         "push" → parse commits → INSERT commit_records per commit
                   For each commit: parse [TASK-123] / #123 from message
                   → populate commit_records.task_ids uuid[]
         "pull_request" → UPSERT pull_request_records
         "workflow_run" → UPSERT ci_pipeline_runs
  → 6. Publish WebhookReceivedEvent (triggers rule evaluation)
  → Return 200 (always — GitHub retries on non-200)
```

## Automation Rule Evaluation (Hangfire)

```
WebhookReceivedEvent → EvaluateAutomationRulesHandler
  → 1. Load rules: SELECT * FROM task_automation_rules
           WHERE workspace_id = ? AND is_active = true
           AND trigger_type = event.event_type
  → 2. For each rule:
         a. Evaluate condition_json against event payload:
              "branch_pattern" → glob match on branch name
              "repo_id" → exact match on repository_id
         b. If condition matches:
              Execute action_type:
                "update_task_status" → find tasks matching task_ids in event
                                       UPDATE tasks.status = action_params.new_status
                "post_chat_message" → INSERT message in action_params.channel_id
                "assign_task"       → INSERT task_assignments
         c. Log to audit_logs:
              entity_type = "AutomationRule"
              entity_id = rule.id
              action = "executed" / "condition_not_met"
              details_json = { event_id, action_taken }
  → 3. Idempotency: check audit_logs for (rule_id, code_activity_event_id)
         before executing — skip if already processed
```

## Connect Repository

```
POST /api/v1/workspaces/{wsId}/repositories
  body: { github_repo_id, name, clone_url, provider }
  → ConnectRepositoryHandler
    → 1. Verify workspace exists, user has integrations:manage
    → 2. Generate webhook_secret (secure random 32 bytes, hex-encoded)
    → 3. INSERT repositories row
    → 4. Call GitHub API: POST /repos/{owner}/{repo}/hooks
            with secret = webhook_secret
            events = ["push", "pull_request", "workflow_run"]
    → 5. Return { repository_id, webhook_url, webhook_secret }
         (webhook_secret shown once to user for GitHub setup)
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| HMAC mismatch | 401 | Invalid webhook signature |
| Unknown repo_id in webhook URL | 404 | Repository not found |
| Rule action: task not found | — | Logged in audit_logs, rule continues |
| GitHub API error on hook creation | 502 | Could not register webhook on GitHub |
| Duplicate event (retry) | — | Idempotency check skips re-execution |

### Edge Cases

- `task_ids` array: populated by regex parse — best effort, no FK constraint. Some task IDs in array may not exist (manual branch naming inconsistency).
- Multiple rules matching same event: all evaluated independently, all executed.
- Webhook delivery order not guaranteed by GitHub: events may arrive out of order. `received_at` is insertion time, not commit time.

## Related

- [[modules/work-management/integrations/overview|Integrations Overview]]
- [[modules/work-management/integrations/testing|Integrations Testing]]
