# Error Handling Architecture

## Error Boundary Hierarchy

Errors are caught at the narrowest possible scope to avoid blowing up the entire page when one section fails.

```
Root Layout
├── Global error boundary (app/global-error.tsx)
│   └── Catches: framework crashes, provider failures
│       Action: Full-page error with "Reload app" button
│
├── Dashboard Layout error (app/(dashboard)/error.tsx)
│   └── Catches: layout-level failures (auth provider, sidebar data)
│       Action: Error within dashboard chrome, sidebar still works
│
├── Section error (app/(dashboard)/people/error.tsx)
│   └── Catches: section-wide failures (People API down)
│       Action: Error card within content area, nav still works
│
├── Page error (app/(dashboard)/people/employees/error.tsx)
│   └── Catches: page-specific failures (employee list fetch failed)
│       Action: Error state with retry button, breadcrumbs visible
│
└── Component error (<ErrorBoundary> in feature components)
    └── Catches: individual widget failures (chart crash, malformed data)
        Action: Inline error card, rest of page unaffected
```

## Error Types

| Type | Source | Handling |
|:-----|:-------|:---------|
| `AuthError` | 401 from API, expired token | Redirect to `/login?redirect={current}`, clear auth store |
| `ForbiddenError` | 403 from API | Show inline "no permission" state, log to analytics |
| `NotFoundError` | 404 from API | Trigger `notFound()` → shows `not-found.tsx` |
| `ValidationError` | 400 from API (RFC 7807) | Map to form field errors via `errors` map |
| `ApiError` | 500, 502, 503 from API | Toast notification + retry button |
| `NetworkError` | Fetch failed, timeout | "Connection lost" banner + auto-retry with backoff |
| `RenderError` | React component crash | Error boundary catches, shows fallback UI |
| `ChunkLoadError` | Dynamic import failed | Auto-retry import, then show "update available" prompt |

## API Error Flow

```
API Response (non-2xx)
    │
    ▼
ApiClient.fetch() interceptor
    │
    ├── 401 → AuthError → refresh token attempt
    │   ├── Refresh succeeds → retry original request
    │   └── Refresh fails → redirect to /login
    │
    ├── 403 → ForbiddenError → throw (component handles)
    │
    ├── 404 → NotFoundError → throw (page calls notFound())
    │
    ├── 400 → ValidationError → throw (form maps to field errors)
    │
    ├── 429 → RateLimitError → auto-retry after Retry-After header
    │
    └── 5xx → ApiError → throw (error boundary catches)
              │
              ▼
         TanStack Query retry logic
              │
              ├── retry 1 → wait 1s
              ├── retry 2 → wait 2s
              ├── retry 3 → wait 4s
              └── give up → error state in component
```

## Network Resilience

### Offline Detection

```tsx
// components/shared/network-status-banner.tsx
export function NetworkStatusBanner() {
  const isOnline = useOnlineStatus();
  const wasOffline = useRef(false);

  if (!isOnline) {
    wasOffline.current = true;
    return (
      <Banner variant="warning" sticky>
        You're offline. Changes will sync when connection is restored.
      </Banner>
    );
  }

  if (wasOffline.current) {
    wasOffline.current = false;
    // Refetch all active queries
    queryClient.invalidateQueries();
    return (
      <Banner variant="success" autoHide={3000}>
        Back online. Syncing data...
      </Banner>
    );
  }

  return null;
}
```

### Stale Data Indicator

When TanStack Query is serving stale data while refetching:

```tsx
function EmployeeList() {
  const { data, isLoading, isFetching, isStale } = useEmployees(filters);

  return (
    <>
      {isStale && isFetching && (
        <div className="text-xs text-muted-foreground animate-pulse">
          Refreshing...
        </div>
      )}
      <DataTable data={data?.items} />
    </>
  );
}
```

## Error UI Components

### Page-Level Error State

```tsx
// Used in error.tsx files
export function PageError({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    // Report to error monitoring (Sentry)
    captureException(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center py-20">
      <AlertCircle className="h-12 w-12 text-destructive mb-4" />
      <h2 className="text-lg font-semibold">Something went wrong</h2>
      <p className="text-sm text-muted-foreground mt-1 max-w-md text-center">
        {error instanceof ApiError ? error.problem.detail : 'An unexpected error occurred.'}
      </p>
      <Button onClick={reset} className="mt-6">Try again</Button>
    </div>
  );
}
```

### Inline Error State

```tsx
// Used within components
export function InlineError({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <Card className="border-destructive/50 bg-destructive/5 p-4">
      <div className="flex items-center gap-2">
        <AlertCircle className="h-4 w-4 text-destructive" />
        <span className="text-sm">{message}</span>
        {onRetry && (
          <Button variant="ghost" size="sm" onClick={onRetry}>Retry</Button>
        )}
      </div>
    </Card>
  );
}
```

### Toast Notifications

```tsx
// Severity-based toast routing
function showErrorToast(error: ApiError) {
  const severity = error.problem.status >= 500 ? 'destructive' : 'warning';

  toast({
    variant: severity,
    title: error.problem.title,
    description: error.problem.detail,
    action: error.retryable ? (
      <ToastAction altText="Retry" onClick={error.retry}>Retry</ToastAction>
    ) : undefined,
    duration: severity === 'destructive' ? Infinity : 5000, // Critical errors persist
  });
}
```

## Chunk Load Error Recovery

When a dynamic import fails (deploy during user session):

```tsx
// lib/utils/dynamic-import.ts
export function safeImport<T>(importFn: () => Promise<T>): () => Promise<T> {
  return async () => {
    try {
      return await importFn();
    } catch (error) {
      if (error instanceof Error && error.name === 'ChunkLoadError') {
        // New deployment likely happened — prompt refresh
        toast({
          title: 'Update available',
          description: 'A new version is available. Please refresh.',
          action: <ToastAction altText="Refresh" onClick={() => window.location.reload()}>Refresh</ToastAction>,
          duration: Infinity,
        });
      }
      throw error;
    }
  };
}

// Usage
const ActivityHeatmap = dynamic(safeImport(() => import('@/components/workforce/activity-heatmap')));
```

## Related

- [[frontend/architecture/routing|Routing]] — error routes in route tree
- [[frontend/cross-cutting/error-monitoring|Error Monitoring]] — Sentry integration
- [[frontend/cross-cutting/authentication|Authentication]] — auth error flows
- [[frontend/data-layer/api-integration|Api Integration]] — API error types
