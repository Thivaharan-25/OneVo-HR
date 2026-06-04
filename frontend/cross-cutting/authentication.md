# Authentication (Frontend)

## Browser Session Model

The customer-facing ONEVO web apps use a BFF-style cookie session model.

Browser JavaScript never receives, stores, decodes, or sends the tenant user JWT. The backend owns token creation, refresh, validation, rotation, and revocation. The frontend only receives user/session state and permission metadata via the `AuthService` in `@onevo/shared`.

## Auth Flow

```
User                 Angular App                   Backend API
 |                       |                              |
 |-- credentials ------->|                              |
 |                       |-- POST /api/v1/auth/login -->|
 |                       |   withCredentials: true      |
 |                       |                              |-- verify password
 |                       |                              |-- require TOTP if MFA
 |                       |<-- 200/202 ------------------|
 |                       |   Set-Cookie: onevo_session  |
 |                       |   Body: user, permissions,   |
 |                       |         activeModules,       |
 |                       |         activeFeatures       |
 |<-- navigate() --------|                              |
```

If MFA is required, `/api/v1/auth/login` returns `mfa_required: true` without creating a full session. After TOTP verification via `/api/v1/auth/mfa/verify`, the backend sets the HttpOnly session cookie and returns safe session metadata.

## Cookie and Session Handling

| Item | Storage | Lifetime | Sent As |
|:-----|:--------|:---------|:--------|
| Web session | HttpOnly Secure SameSite cookie | Server-controlled | Automatic via `withCredentials: true` |
| CSRF token | Readable CSRF cookie + `X-CSRF-Token` header | Server-controlled | Header on mutations |
| User / permissions | `AuthService` signals | Current app lifecycle | Not an auth credential |

Do not add any token manager for customer web auth. Do not store anything from the session response in localStorage or sessionStorage.

## Initial Session Check

On app bootstrap, `AuthService.initializeSession()` calls `/api/v1/auth/session`:

```typescript
// shared/src/lib/auth/auth.service.ts
@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  private _user = signal<User | null>(null);
  private _permissions = signal<string[]>([]);
  private _activeModules = signal<string[]>([]);
  private _activeFeatures = signal<string[]>([]);
  private _initialized = signal(false);

  user = this._user.asReadonly();
  isAuthenticated = computed(() => this._user() !== null);
  isInitialized = this._initialized.asReadonly();

  initializeSession(): Observable<boolean> {
    return this.http.get<SessionDto>('/api/v1/auth/session').pipe(
      tap(session => this.setSession(session)),
      map(() => true),
      catchError(() => {
        this._initialized.set(true);
        return of(false);
      }),
      tap(() => this._initialized.set(true)),
    );
  }

  setSession(session: SessionDto) {
    this._user.set(session.user);
    this._permissions.set(session.permissions);
    this._activeModules.set(session.activeModules);
    this._activeFeatures.set(session.activeFeatures);
  }

  clear() {
    this._user.set(null);
    this._permissions.set([]);
    this._activeModules.set([]);
    this._activeFeatures.set([]);
  }
}
```

The browser never parses JWT claims. Permissions, active module entitlements, active feature keys, and user display data come from backend session endpoints only.

## App Bootstrap (APP_INITIALIZER)

Session is initialized before the Angular app renders:

```typescript
// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor, tenantInterceptor, correlationInterceptor, errorInterceptor])),
    provideAnimationsAsync(),
    {
      provide: APP_INITIALIZER,
      useFactory: () => {
        const auth = inject(AuthService);
        return () => firstValueFrom(auth.initializeSession());
      },
      multi: true,
    },
  ],
};
```

## Session Refresh

```typescript
// shared/src/lib/auth/auth.service.ts
refreshSession(): Observable<boolean> {
  return this.http.post<SessionDto>('/api/v1/auth/refresh', {}).pipe(
    tap(session => this.setSession(session)),
    map(() => true),
    catchError(() => of(false)),
  );
}
```

The backend may rotate internal JWTs or session records during this call — none are exposed to browser JavaScript.

## Logout

```typescript
// shared/src/lib/auth/auth.service.ts
logout(): Observable<void> {
  return this.http.post<void>('/api/v1/auth/logout', {}).pipe(
    finalize(() => {
      this.clear();
      inject(SignalRService).disconnect();
      inject(Router).navigate(['/login']);
    }),
  );
}
```

`/api/v1/auth/logout` revokes the server-side session and clears the HttpOnly cookie.

## Multi-Tab Session Sync

Use `BroadcastChannel` only to sync state changes such as logout or session refresh. Never broadcast JWTs or cookie values.

```typescript
// shared/src/lib/auth/auth-sync.service.ts
@Injectable({ providedIn: 'root' })
export class AuthSyncService implements OnDestroy {
  private channel = new BroadcastChannel('onevo-auth');
  private auth = inject(AuthService);
  private router = inject(Router);

  constructor() {
    this.channel.onmessage = (event) => {
      if (event.data.type === 'LOGOUT') {
        this.auth.clear();
        this.router.navigate(['/login']);
      }
      if (event.data.type === 'SESSION_REFRESHED') {
        firstValueFrom(this.auth.initializeSession());
      }
    };
  }

  broadcastLogout() { this.channel.postMessage({ type: 'LOGOUT' }); }
  broadcastRefresh() { this.channel.postMessage({ type: 'SESSION_REFRESHED' }); }

  ngOnDestroy() { this.channel.close(); }
}
```

## Context Switcher (Setup / Control ↔ Operations / Lifecycle)

Authorized users can switch between the customer apps. Both customer apps use the same BFF cookie session. The final customer hostname mapping is a deployment decision, so redirects must use configured app URLs rather than hardcoded subdomains:

```typescript
// shared/src/lib/ui/shell/context-switcher.component.ts
export class ContextSwitcherComponent {
  private auth = inject(AuthService);

  // Only show if user has permissions in the target app
  canSwitchToSetup = this.auth.hasAnyPermission('org:manage', 'roles:manage', 'settings:write');
  canSwitchToOperations = this.auth.hasAnyPermission('employees:read', 'leave:read', 'workforce:view');

  switchToSetup() {
    window.location.href = environment.appUrls.setupControl;
  }

  switchToOperations() {
    window.location.href = environment.appUrls.operationsLifecycle;
  }
}
```

## Non-Browser Clients

This page describes the customer web frontend only. IDE extensions, WorkPulse Agent, and platform-admin internals use Bearer tokens through their own documented storage and authentication rules.

## Related

- [[frontend/cross-cutting/authorization|Authorization]] — RBAC permission system
- [[frontend/cross-cutting/security|Security]] — XSS, CSRF protection
- [[frontend/data-layer/api-integration|API Integration]] — HttpClient interceptors
- [[frontend/architecture/routing|Routing]] — functional route guards
