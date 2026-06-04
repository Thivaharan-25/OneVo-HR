# Background Jobs

> Phase 2 only as a standalone operations module. Phase 1 may show basic read-only job health summaries inside Platform Health, but it must not expose job retry, schedule editing, or a dedicated Background Jobs screen.

## Purpose

Background Jobs provides observability and approved controls for ONEVO's scheduled and queued background work - invoice generation, retention sweeps, dunning, health checks, alert creation, webhook retry, and more. Operators use it to monitor job health, investigate failures, and manually retry approved jobs after transient errors.

## Database Tables / Systems Controlled

| Source | Role |
|---|---|
| Hangfire / job store | Read job state, run history, error details; write retry triggers |
| Scheduled task registry | Read job schedule definitions; update schedules where operator control is permitted |
| Audit log | Write every retry and schedule change with actor and reason |

## Background Jobs in ONEVO

Key jobs operators monitor via this screen:

| Job | Schedule | What It Does |
|---|---|---|
| `InvoiceGenerationJob` | Daily (per billing dates) | Generates invoices and initiates gateway charges |
| `DunningCheckJob` | Daily at 02:00 UTC | Retries failed payments; auto-suspends after grace period |
| `PlatformHealthCheckJob` | Every 2 minutes | Creates or resolves service health alerts |
| `ResourceUtilizationCheckJob` | Every 5 minutes | Creates or resolves CPU/memory/storage alerts |
| `WebhookRetryJob` | Every minute | Retries failed webhook events; dead-letters after 5 failures |
| `AlertDismissalJob` | Daily | Auto-dismisses Info alerts older than 48 hours |
| `RetentionSweepJob` | Configurable | Deletes records beyond retention period (skips legal holds) |

## Capabilities

- View all registered jobs with last run status, next scheduled run, and run duration
- View failed job detail with sanitized error message (secrets and stack traces redacted)
- Retry approved failed jobs - only idempotent jobs can be retried
- Enable, disable, or adjust job schedule - requires `platform.health.manage` and an audit reason
- Filter by: job status, job type, date range

## Navigation

| Route | Permission |
|---|---|
| `/operations/background-jobs` | Phase 2 permission contract |
| Retry / schedule update | Phase 2 permission contract |

## Key Rules

- Non-retryable jobs (one-time migrations, non-idempotent operations) cannot be manually triggered via this screen
- Raw exception payloads are redacted in responses - sanitized error messages only
- Schedule changes require an audit reason
- Every retry is audit-logged with job name, actor, and reason

## Related

- [[developer-platform/modules/background-jobs/end-to-end-logic|Background Jobs End-to-End Logic]]
- [[developer-platform/modules/platform-health/overview|Platform Health]] - job queue health is surfaced here
- [[developer-platform/modules/subscription-manager/overview|Subscription Manager]] - dunning and invoice jobs

