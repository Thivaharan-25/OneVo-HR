# Technology Stack: ONEVO

## 1. Programming Languages

| Language | Version | Key Usage Areas |
|:---------|:--------|:----------------|
| C# | 14 (.NET 10) | Backend API, business logic, background jobs |
| SQL | PostgreSQL 16.13 baseline; PostgreSQL 18 target after environment approval | Database queries, RLS policies, migrations |
| TypeScript | ES2024 / 5.x | Frontend (Angular 21) |
| XAML | .NET MAUI | Desktop agent tray app UI |

---

## 2. Backend

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Runtime | .NET | 10 | Clean Architecture + CQRS backend |
| Web Framework | ASP.NET Core | 10.x | Controllers with admin endpoints under `/admin/v1/*` in `ONEVO.Api` |
| ORM | Entity Framework Core | 10.x | Code-first migrations, `xmin` optimistic concurrency |
| Authentication | BFF cookie sessions + backend-held JWT | - | Browser uses HttpOnly session cookies; backend owns JWT/refresh state |
| Authorization | Custom RBAC | - | `RequirePermission` attribute, 90+ permissions |
| Background Jobs | Hangfire | 1.8.23 | 5-queue priority system (Critical/High/Default/Low/Batch) |
| CQRS / Mediator | MediatR | 12.4.1 current | In-process command/query dispatch; optional domain events by exception |
| Real-time | SignalR | ASP.NET Core 10.x | WebSocket connections, presence tracking, live dashboards |
| API Documentation | Swagger/OpenAPI | 3.0 | Auto-generated, Kiota SDK generation |
| Validation | FluentValidation | 11.11.0 current | Request validation |
| Mapping | Mapster or AutoMapper | Latest | DTO ↔ Entity mapping |
| Logging | Serilog | 4.3.1 | Structured logging with PII scrubbing |
| HTTP Client | HttpClientFactory | Built-in | For external API calls with Polly resilience |
| Resilience | Polly | 8.6.6 | Circuit breakers, retries, timeouts |
| Testing | xUnit v3 + Moq + FluentAssertions | xUnit v3 / Moq 4.20.72 / FluentAssertions 8.x | Unit + integration tests |
| Architecture Tests | ArchUnitNET | 0.13.x | Module boundary enforcement |

---

## 3. Frontend

### Monorepo Structure

Three Angular apps share a single Angular workspace monorepo:

| App | Boundary | Persona |
|:----|:---------|:--------|
| `setup-control-app` | Tenant/company setup, legal entities, departments, positions, roles/permissions, policies, imports, add-on requests | Tenant owner, system admin, HR setup users |
| `operations-lifecycle-app` | Daily employee/manager/HR/workforce operations after setup is configured | Employees, managers, HR, workforce reviewers |
| `dev-console` | Internal ONEVO Developer Platform using `/admin/v1/*` | ONEVO platform operators only |
| `shared` (library) | Auth, API services, design system, models | Imported by all three apps |

Customer apps use the same BFF cookie session, same backend `/api/v1/*`, and same SignalR hubs. The Developer Platform uses internal platform-admin auth and `/admin/v1/*`. Final customer hostname mapping is a deployment decision; the app boundary names above are canonical.

### Core Stack

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Framework | Angular | 21.x | Standalone components, signals-based reactivity |
| Language | TypeScript | 5.x | Strict mode enabled |
| Runtime | Node.js | 22 LTS | |
| Package Manager | npm | Latest | |
| Build | Angular CLI (esbuild) | 21.x | `ng build`, `ng serve` |
| CSS Framework | Tailwind CSS | 4.x | Utility-first; CSS custom property tokens for tenant branding |
| Component Library | Angular Material | 21.x | Official Angular UI primitives; enterprise-grade |
| Icons | Material Symbols | Latest | Google icon font, variable weight |
| Charts | ng2-charts (Chart.js) | Latest | Line, bar, pie, doughnut, area |
| Animation | Angular Animations | Built-in | `@angular/animations` — page transitions, micro-interactions |
| Theming | CSS Custom Properties + Angular Material theming | — | Light/dark mode, per-tenant brand tokens |
| Reactive State | Angular Signals | Built-in (21.x) | `signal()`, `computed()`, `effect()` — no NgRx |
| URL State | Angular Router `ActivatedRoute` + `queryParams` | Built-in | Filters, pagination, search params |
| HTTP | Angular `HttpClient` | Built-in | `resource()` + `toSignal()` for signal integration |
| Forms | Angular Reactive Forms | Built-in | `FormBuilder`, `FormGroup`, `Validators` |
| Form Validation | Zod | Latest | Schema validation mirrors backend FluentValidation |
| Real-time | @microsoft/signalr | Latest | Wrapped in Angular services; auto-reconnect with exponential backoff |
| SignalR channels | `workforce-live`, `exception-alerts`, `notifications-{userId}`, `agent-status` | — | Same hub as always |
| Testing | Jest + Angular Testing Library + Playwright + MSW | Latest | Unit, component, E2E, API mocking |
| Linting | ESLint + Prettier | — | Angular ESLint config |
| i18n | Angular i18n | Built-in | `$localize` + locale files |

### Key npm Dependencies

```json
{
  "@angular/core": "^21",
  "@angular/material": "^21",
  "@angular/router": "^21",
  "@angular/forms": "^21",
  "@angular/animations": "^21",
  "@microsoft/signalr": "latest",
  "ng2-charts": "latest",
  "chart.js": "latest",
  "tailwindcss": "^4",
  "zod": "latest",
  "date-fns": "latest"
}
```

### Angular Conventions (v21 Standalone)

- **No NgModules** — every component, pipe, and directive is standalone (`standalone: true`)
- **Dependency injection** — use `inject()` function, not constructor injection
- **Reactive state** — `signal()` / `computed()` / `effect()` replace component state; no RxJS `BehaviorSubject` for UI state
- **New control flow** — use `@if`, `@for`, `@switch` (not `*ngIf`, `*ngFor`)
- **Typed routes** — Angular Router typed route params
- **HTTP with signals** — `toSignal(this.http.get(...))` or `resource()` for async data
- **Guards** — functional guards (`CanActivateFn`), not class-based
- **Interceptors** — functional interceptors (`HttpInterceptorFn`)

---

## 4. WorkPulse Agent

The WorkPulse Agent is the ONEVO activity monitoring package distributed as an **MSIX bundle** to employee devices. It covers every employee type — not just developers.

**Phase 1: Windows only. Phase 2: macOS.** See [[modules/agent-gateway/agent-overview|Agent Overview]] for the macOS Phase 2 architecture.

### Phase 1 — Windows

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Background Service | .NET Windows Service | 10 | `Microsoft.Extensions.Hosting.WindowsServices` — always-on data collector |
| Tray App UI | .NET MAUI | 10 | System tray icon, photo capture, employee login, break toggle |
| Language | C# | 14 | Same language family as backend |
| Local Storage | SQLite | via `Microsoft.Data.Sqlite` | Offline buffer for activity data |
| Activity Capture | Win32 APIs (user32.dll) | - | `SetWindowsHookEx` for keyboard/mouse event COUNTS (not keystrokes) |
| App Detection | Win32 APIs | - | `GetForegroundWindow`, `GetWindowText`, process enumeration |
| Idle Detection | Win32 APIs | - | `GetLastInputInfo` |
| Document Tracking | Process name matching | - | `WINWORD.EXE`, `EXCEL.EXE`, `POWERPNT.EXE`, Figma, Photoshop |
| Communication Tracking | Process name + UIAutomation | - | Outlook, Slack, Teams active time + send event counts (count only) |
| IPC | Named Pipes | `System.IO.Pipes` | Service ↔ MAUI tray app communication |
| Installer | MSIX bundle | Windows SDK | Silent MDM install (Intune/GPO), built-in auto-update, signed |
| HTTP Client | HttpClient + Polly | Built-in | Retry + circuit breaker for Agent Gateway |

### Phase 2 — macOS (Do NOT Build in Phase 1)

| Category | Technology | Notes |
|:---------|:-----------|:------|
| Background Service | `launchd` daemon | `~/Library/LaunchAgents/com.onevo.workpulse.plist` |
| Tray App UI | AppKit `NSStatusBar` | macOS menu bar icon |
| App Detection | `NSWorkspace.shared.frontmostApplication` | Requires Accessibility permission |
| Activity Capture | `CGEventTap` | Requires Accessibility permission (user must grant manually) |
| Idle Detection | `CGEventSource.secondsSinceLastEventType` | |
| Secure Storage | macOS Keychain (`SecKeychainItem`) | Replaces DPAPI |
| Installer | `.pkg` (Apple Developer ID signed) | Replaces MSIX |

### Win32 APIs (P/Invoke)

| API | DLL | Purpose |
|:----|:----|:--------|
| `SetWindowsHookEx` | user32.dll | Keyboard/mouse event COUNTING (not keylogging) |
| `GetForegroundWindow` | user32.dll | Active window detection |
| `GetWindowText` | user32.dll | Window title capture (hashed before storage) |
| `GetLastInputInfo` | user32.dll | Idle detection (time since last input) |
| `EnumProcesses` / `Process.GetProcesses()` | kernel32.dll / .NET | Process enumeration for meeting detection |

### Agent NuGet Dependencies

| Package | Purpose |
|:--------|:--------|
| `Microsoft.Extensions.Hosting.WindowsServices` | Windows Service hosting |
| `Microsoft.Data.Sqlite` | SQLite local buffer |
| `Polly` | HTTP resilience (retry, circuit breaker, timeout) |
| `System.Text.Json` | JSON serialization |
| `Serilog` + `Serilog.Sinks.File` | Local logging (rolling file) |
| `CommunityToolkit.Maui` | MAUI helpers (tray icon, notifications) |

### Agent Project Structure

```
ONEVO.Agent/
├── ONEVO.Agent.Service/           # Windows Service (background collector)
│   ├── Collectors/
│   │   ├── ActivityCollector.cs    # Keyboard/mouse event counting
│   │   ├── AppTracker.cs          # Foreground app detection
│   │   ├── IdleDetector.cs        # Idle period detection
│   │   ├── MeetingDetector.cs     # Meeting app process detection
│   │   ├── DeviceTracker.cs       # Device active/idle cycle tracking
│   │   ├── DocumentTracker.cs     # Word/Excel/PPT/Figma/Photoshop time tracking
│   │   └── CommunicationTracker.cs # Outlook/Slack/Teams active time + send counts
│   ├── Buffer/
│   │   ├── SqliteBuffer.cs        # Local SQLite storage
│   │   └── BufferCleanup.cs       # Purge sent data
│   ├── Sync/
│   │   ├── DataSyncService.cs     # Batch & send to Agent Gateway
│   │   ├── HeartbeatService.cs    # 60-second heartbeat
│   │   └── PolicySyncService.cs   # Fetch monitoring policy
│   ├── Security/
│   │   ├── DeviceTokenStore.cs    # Secure Device JWT storage (DPAPI)
│   │   └── TamperDetector.cs      # Detect service manipulation
│   ├── IPC/
│   │   └── NamedPipeServer.cs     # Listen for MAUI app commands
│   └── Program.cs
│
├── ONEVO.Agent.TrayApp/           # MAUI tray app
│   ├── Views/
│   │   ├── LoginWindow.xaml
│   │   ├── StatusPopup.xaml
│   │   └── PhotoCaptureWindow.xaml
│   ├── Services/
│   │   ├── NamedPipeClient.cs
│   │   ├── CameraService.cs
│   │   └── TrayIconService.cs
│   └── App.xaml.cs
│
├── ONEVO.Agent.Shared/            # Shared types between Service and TrayApp
│   ├── Models/
│   │   ├── ActivitySnapshot.cs
│   │   ├── AppUsageRecord.cs
│   │   ├── DeviceSession.cs
│   │   └── AgentPolicy.cs
│   ├── IPC/
│   │   └── IpcMessages.cs
│   └── Constants.cs
│
└── ONEVO.Agent.Installer/         # MSIX packaging
    └── Package.appxmanifest
```

See [[modules/agent-gateway/overview|Agent Gateway]] for the server-side API contract.

---

## 5. Database & Storage

| Type | Technology | Version | Key Usage |
|:-----|:-----------|:--------|:----------|
| Primary DB | PostgreSQL | 16.13 baseline; 18.x target after hosting and migration validation | All application data, RLS for multi-tenancy |
| Connection Pool | PgBouncer | Latest | Connection pooling for PostgreSQL |
| Cache | `IMemoryCache` in Phase 1; Redis optional/future | Redis 8.x target only after distributed hosting support validation | Phase 1 process-local caching, rate limiting, feature flags; future distributed cache if multi-instance deployment requires it |
| Partitioning | pg_partman | Latest | Time-series partitioning for activity data, audit_logs, biometric_events |
| Search (Phase 1) | PostgreSQL Full-Text Search | Built-in | Initial search implementation |
| Search (Phase 2) | Meilisearch | Latest | Upgraded search at scale |
| File Storage | Cloudflare R2 object storage | - | Documents, logos, avatars, screenshots, verification photos, payslips, report exports |

---

## 6. Infrastructure & Deployment

| Category | Technology | Notes |
|:---------|:-----------|:------|
| Backend Hosting | Azure | .NET 10 deployment through the selected Azure hosting service |
| Frontend Hosting | Azure | Angular build output served through the selected Azure hosting/static delivery path |
| DNS / Edge | Cloudflare DNS + optional Cloudflare proxy | `onevo.com`, wildcard `*.onevo.com`, DDoS/WAF/CDN if proxy mode is enabled |
| Tenant URLs | Cloudflare wildcard DNS -> Azure | Default tenant URL pattern: `{tenantSlug}.onevo.com` |
| Containerization | Docker | Development + deployment — all services in docker-compose.yml |
| Message Broker | None in Phase 1 | No RabbitMQ/MassTransit; optional in-process domain events only for justified post-save side effects |
| CI/CD | GitHub Actions | Build, test, deploy pipeline |
| Observability | OpenTelemetry + Prometheus + Grafana | Distributed tracing, metrics, dashboards |
| Status Page | BetterStack | Public status page |
| In-app Support | Crisp | Chat widget with auto-context |

---

## 7. External Integrations

| Service | Purpose | Auth Method | Priority |
|:--------|:--------|:------------|:---------|
| Stripe | International billing, subscriptions, cards | API Key + Webhooks | Phase 1 |
| PayHere | Sri Lanka/local billing, subscriptions, cards/bank methods | Merchant ID + Merchant Secret + Webhooks | Phase 1 |
| Resend | Transactional email | API Key | Phase 1 |
| Biometric Terminals | Attendance capture | HMAC-SHA256 webhooks | Phase 1 |
| Google Calendar | Leave event sync | OAuth 2.0 | Phase 2 |
| Slack | Notifications | App integration | Phase 2 |
| ADP / Oracle | Payroll sync | OAuth + REST | Phase 4 |
| LMS Providers | Learning content | SSO + API | Phase 3 |

See [[backend/external-integrations|External Integrations]] for full integration details.

---

## 8. Architecture Patterns

| Pattern | Where Used |
|:--------|:-----------|
| CQRS | Write/read separation through MediatR commands and queries |
| Audit Trail | `audit_logs` with JSON diffs |
| Domain Events | Optional in-process MediatR notifications for justified post-save side effects |
| Repository Pattern | Data access via `BaseRepository<T>` — see [[backend/shared-kernel\|Shared Kernel]] |
| Unit of Work | EF Core `DbContext` per request |
| Mediator (MediatR) | Command/query handling; optional event notification dispatch |
| Specification Pattern | Complex query composition |
| Result Pattern | `Result<T, Error>` for explicit error handling — see [[backend/shared-kernel\|Shared Kernel]] |
| Time-Series Buffer | Raw activity data → buffer table (partitioned, purged 48h) → aggregated summaries |
| Tiered Real-Time | Agent→server (2-3 min), exception engine (5 min), dashboard (30s polling / SignalR push) |

---

## 9. NOT Using in Phase 1

| Technology | Reason |
|:-----------|:-------|
| ChromaDB | AI semantic cache deferred |
| Groq | LLM routing deferred |
| Flutter | Mobile app deferred |
| Meilisearch | PostgreSQL FTS sufficient for Phase 1 |
| NgRx | Angular Signals cover all state management needs in Phase 1 |
| Teams chat/group sync | Requires tenant Graph consent, user account linking, webhook/delta sync, and communication-data compliance review. Phase 1 optional integration. |
| macOS Agent | WorkPulse Agent is Windows-only in Phase 1. macOS requires `CGEventTap` + `NSWorkspace` + `launchd` — a parallel implementation. Phase 2. |
| Browser Extension | Optional browser domain tracking via Chrome/Edge/Firefox extension. Phase 2. |

## Related

- [[AI_CONTEXT/project-context|Project Context]]
- [[AI_CONTEXT/rules|Rules]]
- [[current-focus/README|Current Focus]]
- [[AI_CONTEXT/known-issues|Known Issues]]
- [[backend/module-catalog|Module Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[modules/agent-gateway/overview|Agent Gateway]]
- [[backend/external-integrations|External Integrations]]

