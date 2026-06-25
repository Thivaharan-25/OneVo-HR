# Error Monitoring

> **Provider not yet confirmed.** No product decision has been made on which error tracking service to use. The requirements below are provider-agnostic. Once a provider is chosen, add SDK setup, CLI commands, and source-map upload instructions here.

## Required Capabilities

Whichever provider is chosen must support:

- **PII scrubbing** — strip email, IP, username from error reports before transmission
- **Sensitive field redaction** — redact `password`, `salary`, `ssn`, `token` from request payloads
- **User context tagging** — attach `user.id` (no PII), `tenant_id`, `user_role`, `plan` to error events
- **Error boundary integration** — capture Angular component-level render errors with section tags
- **API error capture** — capture HTTP errors with `status_code`, `endpoint`, `correlation_id`, `problem_detail`
- **Noisy error filtering** — ignore `ResizeObserver loop`, `AbortError`, `Network request failed`, `Load failed`, `ChunkLoadError`
- **Source map upload** — CI pipeline uploads source maps to the provider so error reports show original TypeScript source; source maps are NOT served to the client (security)

## Sampling Targets

| Signal | Target Rate |
|:-------|:------------|
| Error traces | 10% of transactions |
| Session replay (normal) | 0% |
| Session replay (on error) | 100% |

## Alert Rules

| Condition | Severity | Action |
|:----------|:---------|:-------|
| Error rate > 5% of requests in 5 min | Critical | PagerDuty alert |
| New error type (first occurrence) | Warning | Notification |
| Error count > 100 in 1 hour | High | Notification |
| Unhandled promise rejection | Medium | Issue created in error tracker |
| API 5xx error spike | Critical | PagerDuty alert |

## Related

- [[backend/messaging/error-handling|Error Handling]] - error boundary architecture
- [[frontend/cross-cutting/analytics|Analytics]] - product analytics
- [[frontend/cross-cutting/security|Security]] - PII scrubbing
