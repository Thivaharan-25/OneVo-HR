# Technology Stack: ONEVO

## 1. Programming Languages

| Language | Version | Key Usage Areas |
|:---------|:--------|:----------------|
| C# | 13 (.NET 9) | Backend API, business logic, background jobs, desktop agent service + tray app |
| SQL | PostgreSQL 16 | Database queries, RLS policies, migrations |
| TypeScript | ES2024 / 5.x | Frontend (Next.js 14) |
| XAML | .NET MAUI | Desktop agent tray app UI |

---

## 2. Backend

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Runtime | .NET | 9.0 | LTS, single deployable monolith |
| Web Framework | ASP.NET Core | 9.0 | Minimal APIs + Controllers |
| ORM | Entity Framework Core | 9.0 | Code-first migrations, `xmin` optimistic concurrency |
| Authentication | JWT (RS256) | - | Access tokens (15min) + Refresh tokens (7 days) |
| Authorization | Custom RBAC | - | `RequirePermission` attribute, 90+ permissions |
| Background Jobs | Hangfire | 1.8.x | 5-queue priority system (Critical/High/Default/Low/Batch) |
| Real-time | SignalR | 9.0 | WebSocket connections, presence tracking, live dashboards |
| API Documentation | Swagger/OpenAPI | 3.0 | Auto-generated, Kiota SDK generation |
| Validation | FluentValidation | 11.x | Request validation |
| Mapping | Mapster or AutoMapper | Latest | DTO ↔ Entity mapping |
| Logging | Serilog | 3.x | Structured logging with PII scrubbing |
| HTTP Client | HttpClientFactory | Built-in | For external API calls with Polly resilience |
| Resilience | Polly | 8.x | Circuit breakers, retries, timeouts |
| Testing | xUnit + Moq + FluentAssertions | Latest | Unit + integration tests |
| Architecture Tests | ArchUnitNET | Latest | Module boundary enforcement |

---

## 3. Frontend

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Framework | Next.js | 14+ | App Router, Server Components, Vercel deployment |
| Language | TypeScript | 5.x | Strict mode enabled |
| Runtime | Node.js | 20 LTS | |
| Package Manager | pnpm | 8.x | Workspace support |
| CSS Framework | Tailwind CSS | 3.x | Utility-first, CSS custom property tokens |
| Component Library | shadcn/ui | Latest | Copy-paste Radix primitives, enterprise-grade |
| Icons | Lucide React | Latest | Consistent icon set |
| Charts | Recharts | Latest | Standard charts (line, bar, pie, area) |
| Dashboard Blocks | Tremor | Latest | Pre-built KPI cards, sparklines |
| Animation | Framer Motion | Latest | Page transitions, micro-interactions |
| Theming | CSS Custom Properties | - | Light/dark mode, tenant branding |
| Server State | TanStack Query | v5 | API data fetching, caching, mutations, optimistic updates |
| Client State | Zustand | 4.x | Sidebar, filters, UI preferences, monitoring config cache |
| URL State | nuqs | Latest | Filters, pagination, search params in URL |
| Forms | React Hook Form + Zod | Latest | Form state + validation (mirrors backend FluentValidation) |
| Real-time | @microsoft/signalr | Latest | WebSocket connection to ONEVO backend |
| SignalR channels | `workforce-live`, `exception-alerts`, `notifications-{userId}`, `agent-status` | - | Auto-reconnect with exponential backoff |
| Testing | Vitest + RTL + Playwright + MSW | Latest | Unit, component, E2E, API mocking |
| Linting | ESLint + Prettier | - | |
| Bundle Analysis | @next/bundle-analyzer | - | |

### Key Frontend Dependencies

```json
{
  "@microsoft/signalr": "latest",
  "@tanstack/react-query": "^5",
  "@radix-ui/react-*": "latest",
  "zustand": "^4",
  "nuqs": "latest",
  "react-hook-form": "latest",
  "zod": "latest",
  "recharts": "latest",
  "@tremor/react": "latest",
  "lucide-react": "latest",
  "framer-motion": "latest",
  "date-fns": "latest",
  "class-variance-authority": "latest",
  "clsx": "latest",
  "tailwind-merge": "latest"
}
```

---

## 4. Desktop Agent

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Background Service | .NET Windows Service | 9.0 | `Microsoft.Extensions.Hosting.WindowsServices` — always-on data collector |
| Tray App UI | .NET MAUI | 9.0 | System tray icon, photo capture, employee login |
| Language | C# | 13 | Same as backend |
| Local Storage | SQLite | via `Microsoft.Data.Sqlite` | Offline buffer for activity data |
| Activity Capture | Win32 APIs (user32.dll) | - | `SetWindowsHookEx` for keyboard/mouse event COUNTS (not keystrokes) |
| App Detection | Win32 APIs | - | `GetForegroundWindow`, `GetWindowText`, process enumeration |
| Idle Detection | Win32 APIs | - | `GetLastInputInfo` |
| IPC | Named Pipes | `System.IO.Pipes` | Service ↔ MAUI tray app communication |
| Installer | MSIX | Windows SDK | Silent install, auto-update |
| HTTP Client | HttpClient + Polly | Built-in | Retry + circuit breaker for Agent Gateway |

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
│   │   └── DeviceTracker.cs       # Device active/idle cycle tracking
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
| Primary DB | PostgreSQL | 16.x | All application data, RLS for multi-tenancy |
| Connection Pool | PgBouncer | Latest | Connection pooling for PostgreSQL |
| Cache | Redis | 7.x | L1/L2/L3 caching, rate limiting, feature flags |
| Partitioning | pg_partman | Latest | Time-series partitioning for activity data, audit_logs, biometric_events |
| Search (Phase 1) | PostgreSQL Full-Text Search | Built-in | Initial search implementation |
| Search (Phase 2) | Meilisearch | Latest | Upgraded search at scale |
| File Storage | Blob Storage (Railway/S3) | - | Documents, avatars, screenshots, verification photos |

---

## 6. Infrastructure & Deployment

| Category | Technology | Notes |
|:---------|:-----------|:------|
| Backend Hosting | Railway | .NET 9 deployment |
| Frontend Hosting | Vercel | Next.js 14 |
| CDN/Edge | Cloudflare | WAF, DDoS, geo-routing, rate limiting |
| Containerization | Docker | Development + deployment |
| CI/CD | GitHub Actions | Build, test, deploy pipeline |
| Observability | OpenTelemetry + Prometheus + Grafana | Distributed tracing, metrics, dashboards |
| Status Page | BetterStack | Public status page |
| In-app Support | Crisp | Chat widget with auto-context |

---

## 7. External Integrations

| Service | Purpose | Auth Method | Priority |
|:--------|:--------|:------------|:---------|
| Stripe | Billing & subscriptions | API Key + Webhooks | Phase 1 |
| Resend | Transactional email | API Key | Phase 1 |
| Biometric Terminals | Attendance capture | HMAC-SHA256 webhooks | Phase 1 |
| Google Calendar | Leave event sync | OAuth 2.0 | Phase 2 |
| Slack | Notifications | App integration | Phase 2 |
| Microsoft Teams Graph API | Rich meeting analytics | OAuth 2.0 | Phase 2 |
| ADP / Oracle | Payroll sync | OAuth + REST | Phase 4 |
| LMS Providers | Learning content | SSO + API | Phase 3 |

See [[backend/external-integrations|External Integrations]] for full integration details.

---

## 8. Architecture Patterns

| Pattern | Where Used |
|:--------|:-----------|
| CQRS | Write/read separation across modules |
| Event Sourcing | Audit trails (`audit_logs` with JSON diffs) — see [[backend/messaging/event-catalog\|Event Catalog]] |
| [[backend/messaging/exchange-topology\|Transactional Outbox]] | Reliable domain event delivery |
| Repository Pattern | Data access via `BaseRepository<T>` — see [[backend/shared-kernel\|Shared Kernel]] |
| Unit of Work | EF Core `DbContext` per request |
| Mediator (MediatR) | Command/Query handling within modules — see [[backend/module-boundaries\|Module Boundaries]] |
| Specification Pattern | Complex query composition |
| Result Pattern | `Result<T, Error>` for explicit error handling — see [[backend/shared-kernel\|Shared Kernel]] |
| Time-Series Buffer | Raw activity data → buffer table (partitioned, purged 48h) → aggregated summaries |
| Tiered Real-Time | Agent→server (2-3 min), exception engine (5 min), dashboard (30s polling / SignalR push) |

---

## 9. NOT Using in Phase 1

| Technology | Reason |
|:-----------|:-------|
| Python AI Service | AI chatbot (Nexis) deferred |
| ChromaDB | AI semantic cache deferred |
| Groq | LLM routing deferred |
| Flutter | Mobile app deferred |
| RabbitMQ | Using in-process domain events initially; RabbitMQ for scale later |
| Meilisearch | PostgreSQL FTS sufficient for Phase 1 |
| Teams Graph API (deep) | Basic meeting detection via process name sufficient for Phase 1 |

## Related

- [[AI_CONTEXT/project-context|Project Context]]
- [[AI_CONTEXT/rules|Rules]]
- [[current-focus/README|Current Focus]]
- [[AI_CONTEXT/known-issues|Known Issues]]
- [[backend/module-catalog|Module Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[modules/agent-gateway/overview|Agent Gateway]]
- [[backend/external-integrations|External Integrations]]
