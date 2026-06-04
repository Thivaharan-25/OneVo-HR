# AI Agent Rules and Guidelines for ONEVO

## 1. General Operating Principles

- **Source of Truth:** Always prioritize information found within this repository. If there's a conflict, the most recently updated file in `AI_CONTEXT/` takes precedence.
- **Contextual Awareness:** Before performing any task, read these files in order:
    1. [[AI_CONTEXT/project-context|Project Context]] — What ONEVO is
    2. [[AI_CONTEXT/tech-stack|Tech Stack]] — .NET 10 / C# 14, PostgreSQL, Redis, Angular 21 three-app monorepo, etc.
    3. [[current-focus/README|Current Focus]] — Current sprint/week priorities
    4. [[AI_CONTEXT/known-issues|Known Issues]] — Gotchas and deprecated patterns
    5. The specific module doc in `modules/` for the module you're working on
- **Hallucination Prevention:** If a request cannot be fulfilled with the provided context, explicitly state that the information is unavailable. **DO NOT invent or speculate.**
- **Token Efficiency:** Be concise. Leverage existing code patterns rather than rewriting. Read ONLY the module doc you need, not all 22.
- **Security & Privacy:** Never expose connection strings, API keys, encryption keys, or PII. Flag sensitive operations for human review.

---

## 2. .NET 10 / C# 14 Code Generation Rules

### Architecture

- **Clean Architecture + CQRS:** The backend is organized into Domain, Application, Infrastructure, and API host projects.
- **Feature structure:** Features are organized as `{Feature}/{SubFeature}` under each layer.
  - Application: `ONEVO.Application/Features/{Feature}/{SubFeature}/` — contains Commands, Queries, DTOs, RepositoryInterfaces, ServiceInterfaces
  - Domain: `ONEVO.Domain/Features/{Feature}/{SubFeature}/` — contains Entities, ValueObjects, Events (optional)
  - Infrastructure repos: `ONEVO.Infrastructure/Persistence/Repositories/{Feature}/{SubFeature}/`
  - Infrastructure service implementations: `ONEVO.Infrastructure/Services/{Feature}/{SubFeature}/`
- **Shared contracts:** Keep cross-cutting primitives in the appropriate layer; do not create separate module projects.
- **Respect layer dependencies:** Domain has no external dependencies; Application depends on Domain; Infrastructure implements Application interfaces; API calls Application via MediatR.
- **Use MediatR** for command/query dispatch.
- **Use domain events only by exception** for justified post-save side effects. Clean Architecture and CQRS do not require events.
- **Use repositories for persistence:** Command/query handlers, optional event handlers, application services, domain services, permission resolvers, tenant provisioning services, and module services must not inject EF Core, `ApplicationDbContext`, or `DbSet<T>`. Application must not expose an `IApplicationDbContext` abstraction. Database access belongs behind Application-owned repository/reader interfaces implemented in Infrastructure under `Persistence/Repositories/`. See [[backend/repository-persistence-boundary|Repository Persistence Boundary]].
- **Repository interfaces:** `Application/Common/RepositoryInterfaces/` (common) or `Application/Features/{Feature}/{SubFeature}/RepositoryInterfaces/` (feature-specific). Do not use `Interfaces/`, `Repositories/`, or `Services/` as folder names for interfaces.
- **Service interfaces:** `Application/Common/ServiceInterfaces/` (common) or `Application/Features/{Feature}/{SubFeature}/ServiceInterfaces/` (feature-specific). Do not use `Interfaces/`, `Repositories/`, or `Services/` as folder names for interfaces.
- **DevPlatform naming:** `DevPlatform` is the Feature for all tenant management, subscription, provisioning, billing, and role template operations. Do not use `Tenancy` as a top-level Feature name. Tenancy is a SubFeature of DevPlatform.
- **Infrastructure services:** Non-EF service implementations go in `Infrastructure/Services/{Feature}/{SubFeature}/`, not in a flat `Tenancy/` or generic folder.

### Naming Conventions

| Element | Convention | Example |
|:--------|:-----------|:--------|
| Namespaces | `PascalCase` | `ONEVO.Application.Features.CoreHR`, `ONEVO.Domain.Features.ActivityMonitoring` |
| Classes | `PascalCase` | `EmployeeService`, `ActivitySnapshotHandler` |
| Interfaces | `IPascalCase` | `IEmployeeRepository`, `IActivityMonitoringService` |
| Methods | `PascalCase` | `GetEmployeeByIdAsync()`, `IngestSnapshotAsync()` |
| Properties | `PascalCase` | `FirstName`, `TenantId`, `IntensityScore` |
| Private fields | `_camelCase` | `_employeeRepository`, `_exceptionEngine` |
| Constants | `PascalCase` | `MaxRetryAttempts`, `SnapshotIntervalMinutes` |
| Enums | `PascalCase` (singular) | `MonitoringFeature`, `AlertSeverity` |
| DB columns | `snake_case` | `tenant_id`, `intensity_score`, `captured_at` |
| API routes | `kebab-case` | `/api/v1/employees`, `/api/v1/workforce/live` |
| Files | `PascalCase` | `ActivityMonitoringService.cs`, `ExceptionRuleDto.cs` |

### Patterns to Follow

```csharp
// ALWAYS: Async + CancellationToken
public async Task<Result<EmployeeDto>> GetEmployeeByIdAsync(Guid id, CancellationToken ct)

// ALWAYS: Return Result<T> for business logic
public Result<LeaveRequest> ApproveLeaveRequest(Guid requestId) =>
    leaveRequest.Status != LeaveStatus.Pending
        ? Result<LeaveRequest>.Failure("Only pending requests can be approved")
        : Result<LeaveRequest>.Success(leaveRequest.Approve());

// ALWAYS: FluentValidation for command validation; validator colocated with the command
public class CreateEmployeeValidator : AbstractValidator<CreateEmployeeCommand>
{
    public CreateEmployeeCommandValidator()
    {
        RuleFor(x => x.FirstName).NotEmpty().MaximumLength(100);
        RuleFor(x => x.Email).NotEmpty().EmailAddress();
    }
}

// ALWAYS: Inject ITenantContext for multi-tenant queries
public class EmployeeRepository : BaseRepository<Employee>, IEmployeeRepository
{
    public EmployeeRepository(AppDbContext context, ITenantContext tenantContext)
        : base(context, tenantContext) { }
}
```

### Patterns to AVOID

```csharp
// NEVER: Synchronous I/O
var employee = _repository.GetById(id); // BAD

// NEVER: Throw exceptions for business logic
if (employee == null) throw new NotFoundException("Employee not found"); // BAD

// NEVER: Reference Infrastructure from Domain/Application
using ONEVO.Infrastructure.Persistence.Repositories; // BAD inside Domain/Application

// NEVER: Skip tenant_id filtering
var employees = _dbContext.Employees.ToListAsync(); // BAD

// NEVER: Query DbContext from an Application handler
private readonly IApplicationDbContext _db; // BAD in handlers; use repositories/readers

// NEVER: Create Events/EventHandlers folders as a default template
// Add events only when a post-save side effect is genuinely justified

// NEVER: Hardcode secrets
var conn = "Host=localhost;Database=onevo"; // BAD

// NEVER: String concatenation for SQL
var sql = $"SELECT * FROM employees WHERE id = '{id}'"; // BAD
```

### [[infrastructure/multi-tenancy|Multi-Tenancy]] Rules

1. **Every entity** (except `countries`, `permissions`, `subscription_plans`, `payroll_providers`) must include `TenantId`
2. **BaseRepository** automatically filters by `TenantId` — never bypass
3. **PostgreSQL RLS** is the second layer — safety net
4. **ArchUnitNET tests** verify no repository bypasses tenant filtering
5. **Backend-held auth/session state** carries `tenant_id` — extracted by middleware into `ITenantContext`

### API Design Rules

- Minimal APIs for simple CRUD, Controllers for complex flows
- API versioning: `/api/v1/`, `/api/v2/`
- RFC 7807 Problem Details for all errors
- `[Authorize]` + `[RequirePermission("resource:action")]` on every endpoint
- Cursor-based pagination, `PageSize` max 100
- `X-Correlation-Id` header in all responses

---

## 3. Workforce Intelligence Rules

### Activity Data Rules

1. **Activity data is append-only** — never UPDATE rows in `activity_snapshots`, `application_usage`, or `activity_raw_buffer`. These are time-series logs. Only `activity_daily_summary` is computed (INSERT or UPDATE on conflict for the day).

2. **Agent Gateway is high-throughput** — the `/api/v1/agent/ingest` endpoint receives data every 2-3 minutes from every active agent:
   - Minimal validation (schema check only, detailed validation async)
   - Batch INSERT via `COPY` or `unnest()` for raw buffer
   - Return 202 Accepted immediately, process asynchronously
   - Rate limit per device (not per user)

3. **Exception rules use JSONB thresholds:**
   ```json
   {"idle_percent_max": 40, "window_minutes": 60, "consecutive_snapshots": 3}
   ```
   Always validate against a known schema before evaluating.

4. **Monitoring data retention** (shorter than HR data):
   - Raw buffer: 48 hours
   - Snapshots: 90 days
   - Daily summaries: 2 years
   - Screenshots: per tenant retention policy (default 30 days)
   - Always check `retention_policies` before querying old data

5. **Never log activity content** — log activity COUNTS (keyboard_events_count, mouse_events_count) but NEVER log window titles, application names, or screenshot contents. These may contain sensitive business data.

6. **Desktop agent policy pattern:**
   ```csharp
   // Always merge tenant + employee override — override wins
   var tenantPolicy = await _configService.GetMonitoringTogglesAsync(tenantId, ct);
   var employeeOverride = await _configService.GetEmployeeOverrideAsync(employeeId, ct);
   var effectivePolicy = tenantPolicy.MergeWith(employeeOverride);
   ```

7. **Covert mode requires disclosure — GDPR/privacy law obligation:**
   "Covert" privacy mode hides monitoring data from employee self-service views. It does **NOT** exempt the tenant from informing employees that monitoring exists. Tenant onboarding **MUST** include a mandatory data processing disclosure step regardless of privacy mode. Never implement the privacy transparency mode feature without gating the `covert` option behind this disclosure confirmation. See [[security/compliance|Compliance]].

### RBAC Permissions — Full List

Data scope for employee-record permissions (`employees:read`, `leave:read`, `attendance:read`, etc.) is controlled by `user_roles.scope_type` / `user_roles.scope_id` or by `user_permission_overrides.scope_type` / `user_permission_overrides.scope_id` for scoped overrides. Scope is not stored on `role_permissions`, and separate `:read-team` codes must not be created. See [[Userflow/Auth-Access/access-policy|Access Policy Reference]].

```
// HR Management
employees:read, employees:write, employees:delete, employees:read-own
leave:read, leave:create, leave:approve, leave:manage, leave:read-own
attendance:read, attendance:write, attendance:approve, attendance:read-own
payroll:read, payroll:write, payroll:run, payroll:approve
performance:read, performance:write, performance:manage
skills:read, skills:write, skills:validate, skills:manage
documents:read, documents:write, documents:manage
grievance:read, grievance:write, grievance:manage
expense:read, expense:create, expense:approve, expense:manage
reports:read, reports:create, reports:export

// Workforce Intelligence
workforce:view, workforce:manage
monitoring:alerts:read, monitoring:alerts:resolve, exceptions:manage
monitoring:configure, monitoring:view-settings
agent:register, agent:manage, agent:view-health, agent:command
analytics:view, analytics:export, analytics:read, analytics:write
verification:view, verification:review, verification:configure

// System
notifications:read, notifications:manage
settings:read, settings:admin, settings:alerts, settings:notifications, settings:system
settings:billing, settings:branding, settings:integrations, settings:device, settings:device:configure
billing:read, billing:manage
roles:read, roles:create, roles:update, roles:delete, roles:assign, permissions:manage
users:read, users:manage
audit:read, audit:export
org:read, org:manage
workflows:read, workflows:manage
```

---

## 4. Database Rules

- **EF Core Code-First** [[database/migration-patterns|migrations]] only — never raw DDL in production
- **snake_case** for all table/column names
- **UUID** primary keys (not auto-increment)
- **Soft delete** where appropriate (`IsDeleted` + `DeletedAt`)
- **Audit columns** on all entities: `created_at`, `updated_at`, `created_by_id`
- **Indexes** on: `tenant_id` (all tables), foreign keys, frequently queried columns
- **No cascade deletes** — handle deletion in services
- **Time-series tables** (activity_snapshots, activity_raw_buffer) use `pg_partman` partitioning — see [[database/performance|Performance]]

---

## 5. Testing Rules

- **xUnit v3** for all new tests
- **FluentAssertions 8.x** for readable assertions
- **Moq 4.20.72** for mocking dependencies
- **Testcontainers** for integration tests with real PostgreSQL
- **ArchUnitNET 0.13.x** for architecture rule enforcement (including new modules)
- Minimum **80% code coverage** for services
- Every public API endpoint must have at least one integration test

---

## 6. Git Workflow

- **Commit Messages:** `type(scope): subject` (e.g., `feat(activity-monitoring): add snapshot ingestion`) — see [[code-standards/git-workflow|Git Workflow]]
- **Types:** feat, fix, refactor, test, docs, chore, perf
- **Branches:** `feature/`, `bugfix/`, `hotfix/` prefixes
- **PRs:** Small, focused. Require at least one reviewer.

---

## 7. Logging Rules (Serilog) — see [[code-standards/logging-standards|Logging Standards]]

- Structured logging: `_logger.LogInformation("Snapshot received for {EmployeeId} in tenant {TenantId}", id, tenantId)`
- **Never** log PII or activity content (emails, names, bank details, window titles, screenshot data)
- **Always** include correlation ID in log context
- Log levels: `Debug` for dev, `Information` for business events, `Warning` for recoverable issues, `Error` for failures

---

## 8. Phase Guard Rules

### Phase 2 Modules — DO NOT BUILD

The following modules are **Phase 2 deferred**. Workers MUST NOT build routes, pages, components, API integrations, or sidebar/navigation items for these modules during Phase 1:

| Module | Routes | Status |
|:-------|:-------|:-------|
| Payroll | `/hr/payroll/*` | Phase 2 — Deferred |
| Performance | `/hr/performance/*` | Phase 2 — Deferred |
| Skills | `/hr/skills/*` | Phase 2 — Deferred |
| Documents | `/hr/documents/*` | Phase 2 — Deferred |
| Grievance | `/hr/grievance/*` | Phase 2 — Deferred |
| Expense | `/hr/expense/*` | Phase 2 — Deferred |
| Reporting Engine | `/reports/*` | Phase 2 — Deferred |

### How to Enforce

1. **Sidebar/Navigation:** Only render nav items for Phase 1 modules. Phase 2 items in `navigation-patterns.md` are marked with `// Phase 2` comments — skip them.
2. **Routes:** Phase 2 routes in `app-structure.md` are marked with `— Phase 2` comments — do not create these page files.
3. **Components:** Only build components with Phase 1 in the component catalog. Do not build feature-specific components for Phase 2 modules.
4. **If a task file references a Phase 2 module:** SKIP the task or the specific acceptance criterion. Report it as blocked.

---

## 9. Task Completion Rules

- **Checkbox tracking:** When a feature or acceptance criterion is implemented, mark its checkbox `- [ ]` → `- [x]` in the relevant task file under `current-focus/`
- **Status updates:** Update the task file's **Status** field as work progresses: `Planned` → `In Progress` → `Complete`
- **Changelog logging:** After completing significant work, create a new entry in `AI_CONTEXT/changelog/` with format `YYYY-MM-DD-<description>.md`
- **One source of truth:** Checkboxes live ONLY in individual task files (`current-focus/DEV*.md`), NOT in `current-focus/README.md`. The README tracks high-level status only.
- **Cross-reference:** When checking a box, verify the related module feature docs are up-to-date with any implementation changes.

---

## 10. Frontend / Angular 21 Rules

ONEVO has three Angular apps in one workspace monorepo: `setup-control-app`, `operations-lifecycle-app`, and internal `dev-console`, sharing a `shared` Angular library. See [[AI_CONTEXT/tech-stack|Tech Stack]] Section 3 for the full stack.

### Angular 21 Mandatory Patterns

- **Standalone components only** — every `@Component`, `@Directive`, `@Pipe` must have `standalone: true`. No NgModules.
- **`inject()` for DI** — never constructor injection.
- **New control flow** — `@if`, `@for`, `@switch` only. Never `*ngIf`, `*ngFor`, `*ngSwitch`.
- **Signals for state** — `signal()`, `computed()`, `effect()`. Never `BehaviorSubject` or `Subject` for UI state.
- **Functional guards** — `CanActivateFn`. Never class-based guards.
- **Functional interceptors** — `HttpInterceptorFn`. Never class-based interceptors.
- **Lazy loading** — `loadComponent` / `loadChildren` for all heavy feature routes.

### File & Component Conventions

**Naming:**

| Element | Convention | Example |
|:--------|:-----------|:--------|
| Component files | `kebab-case.component.ts` | `employee-list.component.ts` |
| Service files | `kebab-case.service.ts` | `employee.service.ts` |
| Guard files | `kebab-case.guard.ts` | `auth.guard.ts` |
| Pipe files | `kebab-case.pipe.ts` | `format-date.pipe.ts` |
| Signal store files | `kebab-case.store.ts` | `sidebar.store.ts` |
| Component classes | `PascalCaseComponent` | `EmployeeListComponent` |
| Services | `PascalCaseService` | `EmployeeService` |
| Types/Interfaces | `PascalCase` | `Employee`, `LeaveRequest` |
| Route segments | `kebab-case` | `/workforce/live`, `/hr/employees` |

**Directory Structure (per app):**

```
projects/{app-name}/src/app/
├── app.routes.ts           # Typed route definitions
├── app.config.ts           # provideRouter, provideHttpClient, provideAnimations, etc.
├── shell/
│   ├── shell.component.ts  # Root shell (nav rail, topbar, router-outlet)
│   ├── nav-rail/
│   └── header/
└── features/
    ├── hr/                 # Pillar 1 feature components
    ├── workforce/          # Pillar 2 feature components
    └── worksync/           # Pillar 3 feature components (operations-lifecycle-app only)

projects/shared/src/lib/
├── auth/                   # AuthService, auth.guard.ts, auth.interceptor.ts
├── api/                    # Typed HttpClient services per domain
├── realtime/               # SignalRService (shared hub management)
├── ui/                     # Shared Angular Material + custom components
├── models/                 # TypeScript interfaces/DTOs matching backend
└── utils/                  # Date, formatting, validation helpers
```

### Component Patterns

**Standalone Component:**

```typescript
@Component({
  selector: 'app-employee-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, HasPermissionDirective],
  templateUrl: './employee-list.component.html',
})
export class EmployeeListComponent {
  private employeeService = inject(EmployeeService);

  employees = toSignal(this.employeeService.getAll(), { initialValue: [] });
}
```

**Permission Gating (template):**

```html
<!-- Structural directive from shared lib -->
<div *hasPermission="'workforce:view'">
  <app-workforce-dashboard />
</div>

<!-- New control flow + permission signal -->
@if (authService.hasPermission('exceptions:manage')) {
  <app-exception-panel />
}
```

**HTTP + Signals Data Fetching:**

```typescript
// Preferred: resource() for async data with signals
employeesResource = resource({
  request: () => this.filters(),
  loader: ({ request }) => firstValueFrom(this.employeeService.list(request)),
});

// Alternative: toSignal for simple observables
employees = toSignal(this.employeeService.getAll(), { initialValue: [] });
```

**Reactive Form Pattern:**

```typescript
export class CreateEmployeeComponent {
  private fb = inject(FormBuilder);
  private employeeService = inject(EmployeeService);

  form = this.fb.group({
    firstName: ['', [Validators.required, Validators.maxLength(100)]],
    email: ['', [Validators.required, Validators.email]],
  });

  // Zod schema for additional cross-field validation
  private schema = z.object({
    firstName: z.string().min(1).max(100),
    email: z.string().email(),
  });

  submit() {
    const result = this.schema.safeParse(this.form.value);
    if (result.success) {
      this.employeeService.create(result.data).subscribe();
    }
  }
}
```

### Frontend API Integration Rules

- **All API calls go through typed Angular services in `shared/api/`** — never raw `HttpClient` in components
- **Use `resource()` or `toSignal()` for data fetching** — no manual subscribe/unsubscribe in components
- **Handle loading, error, empty states** for every data-fetching component
- **Pagination via `ActivatedRoute.queryParams`** — page/cursor in URL params
- **Error display:** RFC 7807 Problem Details → Angular Material snackbar/toast

### Frontend Real-time Rules

- **SignalR for:** `workforce-live`, `exception-alerts`, `notifications-{userId}`, `agent-status`
- **`SignalRService` in shared lib** — one connection shared across customer apps via service injection
- **Polling fallback:** 30 s polling if SignalR connection fails
- **Reconnection:** Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s)
- **Stale data indicator:** Show "Last updated X seconds ago" on live dashboards

### Frontend Styling Rules

- **Tailwind utilities first** — avoid custom CSS unless absolutely necessary
- **Angular Material for all base components** — buttons, dialogs, tables, forms, snackbars
- **CSS Custom Properties for theming** — light/dark mode, tenant brand color tokens
- **Responsive:** Desktop-first, but all pages must be usable on tablet (≥768px)
- **No inline styles** — use Tailwind classes or component SCSS

### Frontend Testing Rules

- **Jest + Angular Testing Library for components** — test behavior, not implementation
- **Playwright for critical E2E flows** — login, leave request, exception management
- **MSW for API mocking** — realistic API responses in tests
- **No snapshot tests** — they break on every UI change

### Frontend Security Rules

- **Never expose tenant JWTs to customer web JavaScript** — browser auth uses HttpOnly cookie sessions; no localStorage, sessionStorage, or in-memory token access for customer web
- **Sanitize all user-generated content** — Angular's `DomSanitizer` for dynamic HTML
- **RBAC check on every route guard** — redirect to 403 if unauthorized
- **No sensitive data in URL params** — employee IDs are OK, PII is not
- **CSP headers** configured at the hosting/API edge

---

## 11. WorkPulse Agent Rules

### Privacy & Security — NON-NEGOTIABLE

**What We Collect:**
- Keyboard **event counts** (how many key presses) — NOT keystrokes/content
- Mouse **event counts** — NOT coordinates or click targets
- Foreground application **name** — e.g., "Google Chrome", "Microsoft Excel"
- Window title — **hashed (SHA-256) before storage or transmission**
- Idle time (seconds since last input)
- Meeting app process detection (Teams.exe, zoom.exe, Google Meet via browser extension)
- Camera/mic **active status** (boolean) — NOT audio/video content
- Device active/idle cycles
- Document tool active time (Word, Excel, PowerPoint, Figma — process name only)
- Communication tool active time + **send event counts** (Outlook, Slack — count only, zero content)
- Browser **domain name only** (when browser extension enabled) — e.g., `github.com` — NEVER full URL or page content

**What We NEVER Collect:**
- Keystroke content (what was typed)
- Mouse coordinates or click targets
- Window title plaintext (always hash)
- Screen content (screenshots only on explicit remote command — never scheduled)
- Audio or video content
- File names, file contents, or file system browsing
- Network traffic content
- Browser URL paths, page text, or search queries
- Clipboard content
- Email subject lines, recipients, or message content
- Message text from Slack, Teams, or any chat tool

**Security Rules:**
1. **Device JWT stored via DPAPI** (Windows Data Protection API) — never plaintext
2. **All HTTP communication over HTTPS** — certificate pinning in production
3. **Local SQLite is encrypted** (SQLCipher or similar) — data at rest protection
4. **Log files never contain activity content** — only counts, statuses, errors
5. **Photo captures stored temporarily** — sent to server immediately, deleted locally after confirmation
6. **Tamper detection** — if service is stopped unexpectedly, report on next startup

### Agent Performance Rules

- **CPU usage < 2%** sustained (< 5% during batch send)
- **Memory < 50MB** working set
- **Network < 10KB per sync** (compressed JSON batches)
- **SQLite buffer max 100MB** — older unsent data dropped if buffer is full
- **No UI thread blocking** in MAUI app — all I/O on background threads

### Agent Network Resilience

```csharp
// HTTP client with Polly resilience
services.AddHttpClient<IAgentGatewayClient>("AgentGateway")
    .AddPolicyHandler(Policy
        .Handle<HttpRequestException>()
        .OrResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode && r.StatusCode != HttpStatusCode.Unauthorized)
        .WaitAndRetryAsync(3, attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt))))
    .AddPolicyHandler(Policy
        .Handle<HttpRequestException>()
        .CircuitBreakerAsync(5, TimeSpan.FromMinutes(2)));
```

- **Offline mode:** If server unreachable, keep buffering to SQLite. Sync when back online.
- **401 Unauthorized:** Stop syncing, show "re-registration needed" in tray app. Do NOT retry.
- **429 Too Many Requests:** Honor `Retry-After` header.
- **Server errors (5xx):** Exponential backoff with jitter (2s, 4s, 8s, max 30s).

### Agent Coding Standards

Follow the same conventions as the backend:
- **Async everywhere** with CancellationToken
- **Structured logging** via Serilog (file sink, rolling daily, max 7 days)
- **Dependency injection** via `Microsoft.Extensions.DependencyInjection`
- **Configuration** via `appsettings.json` + environment variables
- **No hardcoded values** — all thresholds come from server policy or local config

### Agent Policy Enforcement

```csharp
// Before collecting any data type, check policy
if (!_policy.ActivityMonitoring)
{
    _logger.LogDebug("Activity monitoring disabled by policy, skipping collection");
    return;
}
```

- **Check policy before every collection cycle** — not just at startup
- **Policy refresh:** On employee login + every 60 minutes
- **If policy fetch fails:** Use last known policy from SQLite cache
- **If no policy exists:** Collect NOTHING. Default is off.

### Agent IPC Protocol (Named Pipes)

Message format between Service and MAUI app:

```json
// Service → MAUI: Request photo capture
{"type": "capture_photo", "reason": "scheduled_verification", "requestId": "uuid"}

// MAUI → Service: Photo captured
{"type": "photo_captured", "requestId": "uuid", "photoPath": "C:\\temp\\verify.jpg"}

// MAUI → Service: Employee logged in
{"type": "employee_login", "employeeId": "uuid", "email": "user@company.com"}

// Service → MAUI: Status update
{"type": "status_update", "connected": true, "lastSync": "2026-04-05T10:30:00Z", "bufferedCount": 42}
```

## Related

- [[AI_CONTEXT/project-context|Project Context]]
- [[AI_CONTEXT/tech-stack|Tech Stack]]
- [[AI_CONTEXT/known-issues|Known Issues]]
- [[current-focus/README|Current Focus]]
- [[backend/module-boundaries|Module Boundaries]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/shared-kernel|Shared Kernel]]
- [[modules/agent-gateway/overview|Agent Gateway]]
