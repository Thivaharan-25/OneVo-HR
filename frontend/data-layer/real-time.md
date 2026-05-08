# Real-Time Architecture (SignalR)

## Overview

ONEVO uses **SignalR** (WebSocket with fallbacks) for real-time push from the .NET backend. The frontend treats pushes as **cache invalidation signals** â€” when a push arrives, TanStack Query refetches the relevant data. The API remains the single source of truth.

## SignalR Client (`src/lib/signalr/client.ts`)

Package: `@microsoft/signalr`

Builds and exports a shared `HubConnection` instance using `HubConnectionBuilder`. `SignalRProvider` (in `App.tsx`) manages connection lifecycle (start on auth, stop on logout).

## Connection Lifecycle

```
App Mount â†’ SignalRProvider initializes
    â”‚
    â”œâ”€â”€ Build connection with cookie-backed session
    â”œâ”€â”€ Start connection
    â”‚
    â”œâ”€â”€ On connected â†’ subscribe to tenant hub groups
    â”‚   â”œâ”€â”€ tenant:{tenantId}              (tenant-wide broadcasts)
    â”‚   â”œâ”€â”€ user:{userId}                  (personal notifications)
    â”‚   â””â”€â”€ workforce:{tenantId}           (live workforce data â€” if feature enabled)
    â”‚
    â”œâ”€â”€ On message â†’ dispatch to registered handlers
    â”‚   â”œâ”€â”€ TanStack Query invalidation
    â”‚   â”œâ”€â”€ Toast notification
    â”‚   â””â”€â”€ Zustand store update (notification count)
    â”‚
    â”œâ”€â”€ On disconnected â†’ auto-reconnect with exponential backoff
    â”‚   â”œâ”€â”€ Attempt 1: immediate
    â”‚   â”œâ”€â”€ Attempt 2: 2s
    â”‚   â”œâ”€â”€ Attempt 3: 5s
    â”‚   â”œâ”€â”€ Attempt 4: 10s
    â”‚   â”œâ”€â”€ Attempt 5+: 30s
    â”‚   â””â”€â”€ Show "Reconnecting..." banner after 5s disconnected
    â”‚
    â””â”€â”€ On auth expired â†’ stop connection, redirect to login
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
      .withUrl(`${import.meta.env.VITE_API_URL}/hubs/main`, {`r`n        withCredentials: true,`r`n      })
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
| `SessionExpired` | â€” | Redirect to login |
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
  // Pattern: event â†’ invalidate relevant query keys
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

- [[frontend/data-layer/state-management|State Management]] â€” TanStack Query cache patterns
- [[frontend/data-layer/api-integration|Api Integration]] â€” API client
- [[frontend/data-layer/caching-strategy|Caching Strategy]] â€” cache invalidation rules
- [[frontend/architecture/overview|Overview]] â€” real-time as overlay principle

