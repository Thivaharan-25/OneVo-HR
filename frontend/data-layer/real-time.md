# Real-Time Architecture (SignalR)

## Overview

ONEVO uses **SignalR** (WebSocket with fallbacks) for real-time push from the .NET backend. The frontend treats pushes as **cache invalidation signals** — when a push arrives, the relevant `resource()` is reloaded. The API remains the single source of truth.

## SignalR Service (`shared/src/lib/realtime/signalr.service.ts`)

Package: `@microsoft/signalr`

An Angular singleton service that builds and manages the `HubConnection`. Both apps inject this service from `@onevo/shared`. The connection starts on successful authentication and stops on logout.

## Connection Lifecycle

```
AuthService.setSession() called
    │
    ├── SignalRService.connect() — builds HubConnection with cookie credentials
    ├── connection.start()
    │
    ├── On connected → join tenant hub groups (server-side via hub method)
    │   ├── tenant:{tenantId}              (tenant-wide broadcasts)
    │   ├── user:{userId}                  (personal notifications)
    │   └── workforce:{tenantId}           (live workforce — management-app only)
    │
    ├── On message → dispatch to registered handlers
    │   ├── resource.reload()              (cache invalidation)
    │   ├── MatSnackBar notification       (user-visible toast)
    │   └── AuthService signal update      (permission changes)
    │
    ├── On disconnected → auto-reconnect with exponential backoff
    │   ├── Attempt 1: immediate
    │   ├── Attempt 2: 2 s
    │   ├── Attempt 3: 5 s
    │   ├── Attempt 4: 10 s
    │   ├── Attempt 5+: 30 s
    │   └── Show reconnecting banner after 5 s disconnected
    │
    └── On auth expired → stop connection, navigate to /login
```

## SignalR Service Implementation

```typescript
// shared/src/lib/realtime/signalr.service.ts
@Injectable({ providedIn: 'root' })
export class SignalRService implements OnDestroy {
  private connection: HubConnection | null = null;
  private auth = inject(AuthService);

  connectionStatus = signal<'connected' | 'reconnecting' | 'disconnected'>('disconnected');

  connect(hubUrl: string) {
    this.connection = new HubConnectionBuilder()
      .withUrl(hubUrl, { withCredentials: true })
      .withAutomaticReconnect({
        nextRetryDelayInMilliseconds: (ctx) => {
          const delays = [0, 2000, 5000, 10000, 30000];
          return delays[Math.min(ctx.previousRetryCount, delays.length - 1)];
        },
      })
      .configureLogging(LogLevel.Warning)
      .build();

    this.connection.onreconnecting(() => this.connectionStatus.set('reconnecting'));
    this.connection.onreconnected(() => this.connectionStatus.set('connected'));
    this.connection.onclose(() => this.connectionStatus.set('disconnected'));

    this.connection.start().catch(console.error);
  }

  on<T>(method: string, handler: (data: T) => void): void {
    this.connection?.on(method, handler);
  }

  off(method: string): void {
    this.connection?.off(method);
  }

  disconnect() {
    this.connection?.stop();
    this.connection = null;
    this.connectionStatus.set('disconnected');
  }

  ngOnDestroy() { this.disconnect(); }
}
```

## Hub Channels & Events

### Tenant Hub (`tenant:{tenantId}`)

| Event | Payload | Action |
|:------|:--------|:-------|
| `EmployeeCreated` | `{ employeeId }` | Reload employee list resource |
| `EmployeeUpdated` | `{ employeeId }` | Reload employee detail resource |
| `LeaveRequestSubmitted` | `{ requestId, employeeName }` | Reload leave resources + toast to managers |
| `LeaveRequestDecided` | `{ requestId, status }` | Reload leave resources + toast to requester |
| `PayrollRunCompleted` | `{ runId }` | Reload payroll resource + toast |
| `ExceptionAlertCreated` | `{ alertId, severity }` | Reload exceptions resource, bump notification count |
| `ExceptionAlertResolved` | `{ alertId }` | Reload exceptions resource |
| `ConfigurationChanged` | `{ settingKey }` | Reload tenant config + feature flags |

### User Hub (`user:{userId}`)

| Event | Payload | Action |
|:------|:--------|:-------|
| `NotificationReceived` | `{ notification }` | Add to notification signal, bump count, toast |
| `SessionExpired` | — | `AuthService.clear()`, navigate to `/login` |
| `PermissionsChanged` | `{ permissions[] }` | Update `AuthService` permissions signal |

### Workforce Hub (`workforce:{tenantId}`) — management-app only

| Event | Payload | Action |
|:------|:--------|:-------|
| `WorkforceStatusUpdate` | `{ snapshot }` | `resource.set(snapshot)` directly (high frequency) |
| `EmployeeStatusChanged` | `{ employeeId, status }` | Update individual card signal |
| `ActivityIntensityUpdate` | `{ departmentId, intensity }` | Update heatmap signal |

## Handler Registration Pattern

Register handlers in the component that owns the resource. Unregister in `ngOnDestroy`.

```typescript
// management-app: exception-list.component.ts
export class ExceptionListComponent implements OnInit, OnDestroy {
  private signalR = inject(SignalRService);

  alertsResource = resource({
    loader: () => firstValueFrom(this.exceptionService.getAlerts()),
  });

  ngOnInit() {
    this.signalR.on('ExceptionAlertCreated', () => this.alertsResource.reload());
    this.signalR.on('ExceptionAlertResolved', () => this.alertsResource.reload());
  }

  ngOnDestroy() {
    this.signalR.off('ExceptionAlertCreated');
    this.signalR.off('ExceptionAlertResolved');
  }
}
```

For high-frequency events, set the resource value directly to avoid refetch storms:

```typescript
// management-app: workforce-live.component.ts
ngOnInit() {
  // High-frequency: set directly
  this.signalR.on<WorkforceSnapshot>('WorkforceStatusUpdate', (snapshot) => {
    this.presenceResource.set(snapshot);
  });

  // Low-frequency: invalidate and reload
  this.signalR.on('EmployeeStatusChanged', () => this.presenceResource.reload());
}
```

## Connection Status Banner

```typescript
// shared/src/lib/ui/shell/connection-banner.component.ts
@Component({
  selector: 'app-connection-banner',
  standalone: true,
  imports: [MatButtonModule, NgClass],
  template: `
    @if (status() !== 'connected') {
      <div class="connection-banner" [ngClass]="status()">
        @if (status() === 'reconnecting') {
          Connection lost. Reconnecting...
        } @else {
          Unable to connect. Some data may be stale.
          <button mat-button (click)="retry()">Retry</button>
        }
      </div>
    }
  `,
})
export class ConnectionBannerComponent {
  private signalR = inject(SignalRService);
  status = this.signalR.connectionStatus;

  retry() { this.signalR.connect(inject(SIGNALR_HUB_URL)); }
}
```

## Performance Considerations

- **Workforce hub** is only connected when the live dashboard component is active — not app-wide
- High-frequency events (`WorkforceStatusUpdate`) use `resource.set()` to avoid HTTP refetch
- Low-frequency events (`EmployeeCreated`) use `resource.reload()` to get authoritative server data
- On reconnection: call `resource.reload()` on all active resources to catch missed events

## Related

- [[frontend/data-layer/state-management|State Management]] — Angular Signals + resource() patterns
- [[frontend/data-layer/api-integration|API Integration]] — HttpClient services
- [[frontend/data-layer/caching-strategy|Caching Strategy]] — cache invalidation rules
- [[frontend/architecture/overview|Overview]] — real-time as overlay principle
