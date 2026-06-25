# Real-Time Architecture

## SignalR Setup

```typescript
// shared/src/lib/realtime/signalr.service.ts
import { Injectable, OnDestroy } from '@angular/core';
import { inject } from '@angular/core';
import { HubConnectionBuilder, LogLevel } from '@microsoft/signalr';
import { signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class SignalRService implements OnDestroy {
  connectionStatus = signal<'connected' | 'reconnecting' | 'disconnected'>('disconnected');

  private connection = new HubConnectionBuilder()
    .withUrl(`${environment.apiBaseUrl}/hubs/notifications`, { withCredentials: true })
    .withAutomaticReconnect([0, 1000, 2000, 5000, 10000, 30000])
    .configureLogging(LogLevel.Warning)
    .build();

  connect() {
    this.connection.onreconnecting(() => this.connectionStatus.set('reconnecting'));
    this.connection.onreconnected(() => this.connectionStatus.set('connected'));
    this.connection.onclose(() => this.connectionStatus.set('disconnected'));
    this.connection.start().then(() => this.connectionStatus.set('connected')).catch(console.error);
  }

  on<T>(method: string, handler: (data: T) => void) { this.connection.on(method, handler); }
  off(method: string) { this.connection.off(method); }
  disconnect() { this.connection.stop(); }
  ngOnDestroy() { this.disconnect(); }
}
```

## Channels

| Channel | Data | Permission | UI Update |
|:--------|:-----|:-----------|:----------|
| `monitoring-live` | Presence changes, active/idle transitions | `monitoring:view` | Live dashboard cards |
| `notifications-{userId}` | Phase 1 monitoring/attendance alerts | `monitoring:alerts:read` | Toast + badge count |
| `activity-feed` | Activity snapshots (admin drill-down) | `monitoring:view` | Employee detail live |
| `agent-status` | Agent online/offline | `agent:view-health` | Agent health indicator |
| `notifications-{userId}` | Personal notifications | Authenticated | Bell icon badge |

## Angular Pattern

```typescript
// customer-app: monitoring-live.component.ts
export class MonitoringLiveComponent implements OnInit, OnDestroy {
  private signalR = inject(SignalRService);

  presenceResource = resource({
    loader: () => firstValueFrom(this.monitoringService.getLiveStatus()),
  });

  ngOnInit() {
    // High-frequency: set resource value directly (avoids HTTP refetch)
    this.signalR.on<MonitoringUpdate>('MonitoringStatusUpdate', (update) => {
      this.presenceResource.set({ ...this.presenceResource.value()!, ...update });
    });
  }

  ngOnDestroy() { this.signalR.off('MonitoringStatusUpdate'); }
}

// customer-app: monitoring-alert-list.component.ts
export class MonitoringAlertListComponent implements OnInit, OnDestroy {
  private signalR = inject(SignalRService);
  private snackBar = inject(MatSnackBar);

  alertsResource = resource({
    loader: () => firstValueFrom(this.monitoringAlertService.getAlerts({ status: 'new' })),
  });

  ngOnInit() {
    this.signalR.on('MonitoringAlertCreated', (alert: MonitoringAlert) => {
      this.alertsResource.reload();
      // Show toast
      toast.warning(`Alert: ${alert.summary}`, {
        description: alert.employeeName,
      });
    });
    
    return () => connection.off('MonitoringAlertCreated');
  }, [connection, queryClient]);
}
```

## Fallback Polling

If SignalR connection fails, fall back to polling:

```typescript
export function useMonitoringStatus() {
  const isConnected = useSignalRStatus();
  
  return useQuery({
    queryKey: ['monitoring', 'live'],
    queryFn: () => monitoringApi.liveStatus(),
    refetchInterval: isConnected ? false : 30_000, // Poll only when SignalR is down
  });
}
```

## Related

- [[modules/notifications/signalr-real-time/overview|Signalr Real Time]] - SignalR implementation
- [[modules/time-attendance/overview|Time & Attendance]] - live presence tracking
- [[modules/exception-engine/overview|Exception Engine]] - Phase 2 real-time alerts
- [[backend/notification-system|Notification System]] - notification delivery

