# Real-Time Architecture

## SignalR Setup

```typescript
// lib/signalr/connection.ts
import { HubConnectionBuilder, LogLevel } from '@microsoft/signalr';
import { getAccessToken } from '@/lib/auth';

export function createSignalRConnection() {
  return new HubConnectionBuilder()
    .withUrl(`${process.env.NEXT_PUBLIC_API_URL}/hubs/notifications`, {
      accessTokenFactory: () => getAccessToken() ?? '',
    })
    .withAutomaticReconnect([0, 1000, 2000, 5000, 10000, 30000]) // Backoff
    .configureLogging(LogLevel.Warning)
    .build();
}
```

## SignalR Provider

```tsx
// providers/signalr-provider.tsx
export function SignalRProvider({ children }: { children: React.ReactNode }) {
  const connection = useRef(createSignalRConnection());
  
  useEffect(() => {
    connection.current.start().catch(console.error);
    return () => { connection.current.stop(); };
  }, []);
  
  return (
    <SignalRContext.Provider value={connection.current}>
      {children}
    </SignalRContext.Provider>
  );
}
```

## Channels

| Channel | Data | Permission | UI Update |
|:--------|:-----|:-----------|:----------|
| `workforce-live` | Presence changes, active/idle transitions | `workforce:view` | Live dashboard cards |
| `exception-alerts` | New exception alerts | `exceptions:view` | Toast + badge count |
| `activity-feed` | Activity snapshots (admin drill-down) | `workforce:view` | Employee detail live |
| `agent-status` | Agent online/offline | `agent:view-health` | Agent health indicator |
| `notifications-{userId}` | Personal notifications | Authenticated | Bell icon badge |

## Hook Pattern

```typescript
// hooks/use-workforce-live.ts
export function useWorkforceLive() {
  const connection = useSignalR();
  const queryClient = useQueryClient();
  
  useEffect(() => {
    connection.on('workforce-live', (update: WorkforceUpdate) => {
      // Update TanStack Query cache directly
      queryClient.setQueryData(['workforce', 'live'], (old: WorkforceStatus) => ({
        ...old,
        ...update,
      }));
    });
    
    return () => connection.off('workforce-live');
  }, [connection, queryClient]);
}

// hooks/use-exception-alerts.ts
export function useExceptionAlerts() {
  const connection = useSignalR();
  const queryClient = useQueryClient();
  
  useEffect(() => {
    connection.on('exception-alerts', (alert: ExceptionAlert) => {
      // Add to cache
      queryClient.setQueryData(['exception-alerts', { status: 'new' }], 
        (old: ExceptionAlert[]) => [alert, ...(old ?? [])]);
      
      // Show toast
      toast.warning(`Exception: ${alert.summary}`, {
        description: alert.employeeName,
      });
    });
    
    return () => connection.off('exception-alerts');
  }, [connection, queryClient]);
}
```

## Fallback Polling

If SignalR connection fails, fall back to polling:

```typescript
export function useWorkforceStatus() {
  const isConnected = useSignalRStatus();
  
  return useQuery({
    queryKey: ['workforce', 'live'],
    queryFn: () => workforceApi.liveStatus(),
    refetchInterval: isConnected ? false : 30_000, // Poll only when SignalR is down
  });
}
```
