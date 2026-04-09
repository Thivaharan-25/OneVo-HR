# Error Monitoring

## Stack

| Tool | Purpose |
|:-----|:--------|
| **Sentry** | Error tracking, performance monitoring, session replay |

## Integration

### Sentry Init

```tsx
// lib/sentry.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENV, // 'development' | 'staging' | 'production'
  release: process.env.NEXT_PUBLIC_APP_VERSION,

  tracesSampleRate: 0.1,       // 10% of transactions
  replaysSessionSampleRate: 0, // No session replays by default
  replaysOnErrorSampleRate: 1, // 100% replay on error

  // Scrub PII from error reports
  beforeSend(event) {
    // Remove user PII
    if (event.user) {
      delete event.user.email;
      delete event.user.ip_address;
      delete event.user.username;
    }

    // Remove sensitive request data
    if (event.request?.data) {
      const sensitiveKeys = ['password', 'salary', 'ssn', 'token'];
      for (const key of sensitiveKeys) {
        if (key in event.request.data) {
          event.request.data[key] = '[REDACTED]';
        }
      }
    }

    return event;
  },

  // Ignore noisy errors
  ignoreErrors: [
    'ResizeObserver loop',
    'AbortError',
    'Network request failed',
    'Load failed',
    'ChunkLoadError', // Handled by our chunk recovery logic
  ],
});
```

### User Context

```tsx
// Set on login (ID only, no PII)
Sentry.setUser({
  id: user.id,
  // NO email, name, or other PII
});

Sentry.setTag('tenant_id', user.tenantId);
Sentry.setTag('user_role', user.role);
Sentry.setTag('plan', user.tenantPlan);
```

### Error Boundary Integration

```tsx
// app/(dashboard)/hr/error.tsx
'use client';
import * as Sentry from '@sentry/nextjs';

export default function HRError({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    Sentry.captureException(error, {
      tags: { section: 'hr' },
    });
  }, [error]);

  return <PageError error={error} reset={reset} />;
}
```

### API Error Capture

```tsx
// Capture API errors with context
function captureApiError(error: ApiError, context?: Record<string, any>) {
  Sentry.captureException(error, {
    tags: {
      error_type: 'api',
      status_code: error.problem.status,
      endpoint: error.endpoint,
    },
    extra: {
      problem_detail: error.problem.detail,
      correlation_id: error.correlationId,
      ...context,
    },
  });
}
```

## Alert Rules

| Condition | Severity | Action |
|:----------|:---------|:-------|
| Error rate > 5% of requests in 5 min | Critical | PagerDuty alert |
| New error type (first occurrence) | Warning | Slack notification |
| Error count > 100 in 1 hour | High | Slack notification |
| Unhandled promise rejection | Medium | Sentry issue created |
| API 5xx error spike | Critical | PagerDuty + Slack |

## Source Maps

- Upload source maps to Sentry during CI build
- Source maps are NOT served to the client (security)
- Allows Sentry to show original TypeScript source in error reports

```bash
# In CI pipeline
npx @sentry/cli sourcemaps upload --release=$APP_VERSION ./next/static
```

## Related

- [[backend/messaging/error-handling|Error Handling]] — error boundary architecture
- [[frontend/cross-cutting/analytics|Analytics]] — product analytics
- [[frontend/cross-cutting/security|Security]] — PII scrubbing
