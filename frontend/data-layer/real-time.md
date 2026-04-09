# Real-Time Architecture (SignalR)

## Overview

ONEVO uses **SignalR** (WebSocket with fallbacks) for real-time push from the .NET backend. The frontend treats pushes as **cache invalidation signals** — when a push arrives, TanStack Query refetches the relevant data. The API remains the single source of truth.

## Connection Lifecycle

```
App Mount → SignalRProvider initializes
    │
    ├── Build connection with auth token
    ├── Start connection
    │
    ├── On connected → subscribe to tenant hub groups
    │   ├── tenant:{tenantId}              (tenant-wide broadcasts)
    │   ├── user:{userId}                  (personal notifications)
    │   └── workforce:{tenantId}           (live workforce data — if feature enabled)
    │
    ├── On message → dispatch to registered handlers
    │   ├── TanStack Query invalidation
    │   ├── Toast notification
    │   └── Zustand store update (notification count)
    │
    ├── On disconnected → auto-reconnect with exponential backoff
    │   ├── Attempt 1: immediate
    │   ├── Attempt 2: 2s
    │   ├── Attempt 3: 5s
    │   ├── Attempt 4: 10s
    │   ├── Attempt 5+: 30s
    │   └── Show "Reconnecting..." banner after 5s disconnected
    │
    └── On auth expired → stop connection, redirect to login
```

## SignalR Provider

```tsx
// components/providers/signalr-provider.tsx
export function SignalRProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const connectionRef = useRef<HubConnection | null>(null);

  useEffect(() => {
    if (!user) return;

    const connection = new HubConnectionBuilder()
      .withUrl(`${process.env.NEXT_PUBLIC_API_URL}/hubs/main`, {
        accessTokenFactory: () => getAccessToken(),
      })
      .withAutomaticReconnect({
        nextRetryDelayInMilliseconds: (retryContext) => {
          const delays = [0, 2000, 5000, 10000, 30000];
          return delays[Math.min(retryContext.previousRetryCount, delays.length - 1)];
        },
      })
      .configureLogging(LogLevel.Warning)
      .build();

    // Register handlers
    registerHandlers(connection, queryClient);

    connection.start().catch(console.error);
    connectionRef.current = connection;

    return () => { connection.stop(); };
  }, [user?.id]);

  return (
    <SignalRContext.Provider value={connectionRef}>
      <ConnectionStatusBanner />
      {children}
    </SignalRContext.Provider>
  );
}
```

## Hub Channels & Events

### Tenant Hub (`tenant:{tenantId}`)

| Event | Payload | Action |
|:------|:--------|:-------|
| `EmployeeCreated` | `{ employeeId }` | Invalidate `['employees']` queries |
| `EmployeeUpdated` | `{ employeeId }` | Invalidate `['employee', id]` + `['employees']` |
| `LeaveRequestSubmitted` | `{ requestId, employeeName }` | Invalidate `['leave-requests']`, toast to managers |
| `LeaveRequestDecided` | `{ requestId, status }` | Invalidate `['leave-requests']`, toast to requester |
| `PayrollRunCompleted` | `{ runId }` | Invalidate `['payroll-runs']`, toast |
| `ExceptionAlertCreated` | `{ alertId, severity }` | Invalidate `['exception-alerts']`, bump notification count |
| `ExceptionAlertResolved` | `{ alertId }` | Invalidate `['exception-alerts']` |
| `ConfigurationChanged` | `{ settingKey }` | Invalidate `['tenant-config']`, may trigger feature flag refresh |

### User Hub (`user:{userId}`)

| Event | Payload | Action |
|:------|:--------|:-------|
| `NotificationReceived` | `{ notification }` | Add to notification store, bump count, toast |
| `SessionExpired` | — | Redirect to login |
| `PermissionsChanged` | `{ permissions[] }` | Update auth store, may trigger UI re-render |

### Workforce Hub (`workforce:{tenantId}`)

| Event | Payload | Action |
|:------|:--------|:-------|
| `WorkforceStatusUpdate` | `{ snapshot }` | Update `['workforce-live']` cache directly (no refetch) |
| `EmployeeStatusChanged` | `{ employeeId, status }` | Update individual employee in live dashboard |
| `ActivityIntensityUpdate` | `{ departmentId, intensity }` | Update heatmap cell |

## Handler Registration

```tsx
function registerHandlers(connection: HubConnection, queryClient: QueryClient) {
  // Pattern: event → invalidate relevant query keys
  connection.on('EmployeeCreated', () => {
    queryClient.invalidateQueries({ queryKey: ['employees'] });
  });

  connection.on('EmployeeUpdated', ({ employeeId }) => {
    queryClient.invalidateQueries({ queryKey: ['employees'] });
    queryClient.invalidateQueries({ queryKey: ['employee', employeeId] });
  });

  connection.on('LeaveRequestSubmitted', ({ employeeName }) => {
    queryClient.invalidateQueries({ queryKey: ['leave-requests'] });
    toast.info(`${employeeName} submitted a leave request`);
  });

  connection.on('ExceptionAlertCreated', ({ severity }) => {
    queryClient.invalidateQueries({ queryKey: ['exception-alerts'] });
    if (severity === 'critical') {
      toast.error('Critical exception alert raised');
    }
  });

  // Workforce: direct cache update (high frequency, avoid refetch)
  connection.on('WorkforceStatusUpdate', ({ snapshot }) => {
    queryClient.setQueryData(['workforce-live'], snapshot);
  });

  connection.on('NotificationReceived', ({ notification }) => {
    useNotificationStore.getState().addNotification(notification);
  });
}
```

## Connection Status Banner

```tsx
function ConnectionStatusBanner() {
  const connection = useSignalR();
  const [status, setStatus] = useState<'connected' | 'reconnecting' | 'disconnected'>('connected');

  useEffect(() => {
    if (!connection.current) return;
    connection.current.onreconnecting(() => setStatus('reconnecting'));
    connection.current.onreconnected(() => {
      setStatus('connected');
      // Refetch all active queries to catch up on missed events
      queryClient.invalidateQueries();
    });
    connection.current.onclose(() => setStatus('disconnected'));
  }, [connection]);

  if (status === 'connected') return null;

  return (
    <Banner variant={status === 'reconnecting' ? 'warning' : 'destructive'} sticky>
      {status === 'reconnecting'
        ? 'Connection lost. Reconnecting...'
        : 'Unable to connect. Some data may be stale.'}
      {status === 'disconnected' && (
        <Button size="sm" variant="outline" onClick={() => connection.current?.start()}>
          Retry
        </Button>
      )}
    </Banner>
  );
}
```

## Performance Considerations

- **Workforce hub** is separate and only joined when the live dashboard is mounted (not app-wide)
- High-frequency events (WorkforceStatusUpdate) use **direct cache updates** (`setQueryData`) instead of refetch
- Low-frequency events (EmployeeCreated) use **invalidation** (triggers background refetch)
- Batch invalidations with `queryClient.invalidateQueries({ predicate })` to avoid refetch storms

## Related

- [[frontend/data-layer/state-management|State Management]] — TanStack Query cache patterns
- [[frontend/data-layer/api-integration|Api Integration]] — API client
- [[frontend/data-layer/caching-strategy|Caching Strategy]] — cache invalidation rules
- [[frontend/architecture/overview|Overview]] — real-time as overlay principle
