# Technology Stack: ONEVO

## 1. Programming Languages

| Language | Version | Key Usage Areas |
|:---------|:--------|:----------------|
| C# | 13 (.NET 9) | Backend API, business logic, background jobs, desktop agent |
| SQL | PostgreSQL 16 | Database queries, RLS policies, migrations |
| TypeScript | ES2024 | Frontend (Next.js 14 — built after backend foundation) |
| XAML | .NET MAUI | Desktop agent tray app UI |

## 2. Backend Technologies

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

## 3. Desktop Agent Technologies

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Background Service | .NET Windows Service | 9.0 | `Microsoft.Extensions.Hosting.WindowsServices` — always-on data collector |
| Tray App UI | .NET MAUI | 9.0 | System tray icon, photo capture, employee login |
| Local Storage | SQLite | via Microsoft.Data.Sqlite | Offline buffer for activity data |
| Activity Capture | Win32 APIs (user32.dll) | - | `SetWindowsHookEx` for keyboard/mouse event COUNTS (not keystrokes) |
| App Detection | Win32 APIs | - | `GetForegroundWindow`, `GetWindowText`, process enumeration |
| Idle Detection | Win32 APIs | - | `GetLastInputInfo` |
| IPC | Named Pipes | System.IO.Pipes | Service ↔ MAUI tray app communication |
| Installer | MSIX | Windows SDK | Silent install, auto-update |
| HTTP Client | HttpClient + Polly | Built-in | Retry + circuit breaker for Agent Gateway |

See [[agent-gateway]] for the API contract and `agent/` brain for full agent architecture.

## 4. Frontend Technologies

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Framework | Next.js | 14+ | App Router, Server Components |
| Language | TypeScript | 5.x | Strict mode |
| Styling | Tailwind CSS | 3.x | Utility-first, CSS custom property tokens |
| Components | shadcn/ui | Latest | Copy-paste, Radix primitives |
| Charts | Recharts + Tremor | Latest | Standard charts + dashboard blocks |
| Server State | TanStack Query | v5 | API data fetching, caching, mutations |
| Client State | Zustand | 4.x | Sidebar, filters, monitoring config cache |
| Forms | React Hook Form + Zod | Latest | Validation mirrors backend FluentValidation |
| URL State | nuqs | Latest | Search params, filters, pagination |
| Real-time | @microsoft/signalr | Latest | Live dashboards, exception alerts |
| Testing | Vitest + RTL + Playwright | Latest | Unit, component, E2E |

See `frontend/` brain for full frontend architecture.

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

See [[external-integrations]] for full integration details.

## 8. Architecture Patterns

| Pattern | Where Used |
|:--------|:-----------|
| CQRS | Write/read separation across modules |
| Event Sourcing | Audit trails (`audit_logs` with JSON diffs) — see [[event-catalog]] |
| [[exchange-topology\|Transactional Outbox]] | Reliable domain event delivery |
| Repository Pattern | Data access via `BaseRepository<T>` — see [[shared-kernel]] |
| Unit of Work | EF Core `DbContext` per request |
| Mediator (MediatR) | Command/Query handling within modules — see [[module-boundaries]] |
| Specification Pattern | Complex query composition |
| Result Pattern | `Result<T, Error>` for explicit error handling — see [[shared-kernel]] |
| Time-Series Buffer | Raw activity data → buffer table (partitioned, purged 48h) → aggregated summaries |
| Tiered Real-Time | Agent→server (2-3 min), exception engine (5 min), dashboard (30s polling / SignalR push) |

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
