# AI Agent Rules and Guidelines for ONEVO

## 1. General Operating Principles

- **Source of Truth:** Always prioritize information found within this repository. If there's a conflict, the most recently updated file in `AI_CONTEXT/` takes precedence.
- **Contextual Awareness:** Before performing any task, read these files in order:
    1. [[AI_CONTEXT/project-context|Project Context]] — What ONEVO is
    2. [[AI_CONTEXT/tech-stack|Tech Stack]] — .NET 9, PostgreSQL, Redis, Vite + React, etc.
    3. [[current-focus/README|Current Focus]] — Current sprint/week priorities
    4. [[AI_CONTEXT/known-issues|Known Issues]] — Gotchas and deprecated patterns
    5. The specific module doc in `modules/` for the module you're working on
- **Hallucination Prevention:** If a request cannot be fulfilled with the provided context, explicitly state that the information is unavailable. **DO NOT invent or speculate.**
- **Token Efficiency:** Be concise. Leverage existing code patterns rather than rewriting. Read ONLY the module doc you need, not all 22.
- **Security & Privacy:** Never expose connection strings, API keys, encryption keys, or PII. Flag sensitive operations for human review.

---

## 2. .NET 9 / C# Code Generation Rules

### Architecture

- **Clean Architecture + CQRS:** The backend is organized into Domain, Application, Infrastructure, and API host projects.
- **Feature structure:** Features live under layer folders such as `ONEVO.Application/Features/{FeatureName}` and `ONEVO.Domain/Features/{FeatureName}`.
- **Shared contracts:** Keep cross-cutting primitives in the appropriate layer; do not create separate module projects.
- **Respect layer dependencies:** Domain has no external dependencies; Application depends on Domain; Infrastructure implements Application interfaces; API calls Application via MediatR.
- **Use MediatR** for command/query dispatch and in-process domain events.
- **Use domain events** for cross-feature side effects.

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

// ALWAYS: FluentValidation for request validation
public class CreateEmployeeCommandValidator : AbstractValidator<CreateEmployeeCommand>
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
5. **JWT claims** carry `tenant_id` — extracted by middleware into `ITenantContext`

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

```
// HR Management
employees:read, employees:write, employees:delete, employees:read-own, employees:read-team
leave:read, leave:create, leave:approve, leave:manage, leave:read-own
attendance:read, attendance:write, attendance:approve, attendance:read-own, attendance:read-team
payroll:read, payroll:write, payroll:run, payroll:approve
performance:read, performance:write, performance:manage, performance:read-team
skills:read, skills:write, skills:validate, skills:manage
documents:read, documents:write, documents:manage
grievance:read, grievance:write, grievance:manage
expense:read, expense:create, expense:approve, expense:manage
reports:read, reports:create, reports:manage

// Workforce Intelligence
workforce:view, workforce:manage
exceptions:view, exceptions:manage, exceptions:acknowledge
monitoring:configure, monitoring:view-settings
agent:register, agent:manage, agent:view-health
analytics:view, analytics:export
verification:view, verification:configure

// System
notifications:read, notifications:manage
settings:read, settings:admin
billing:read, billing:manage
roles:read, roles:manage
users:read, users:manage
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

- **xUnit** for all tests
- **FluentAssertions** for readable assertions
- **Moq** for mocking dependencies
- **Testcontainers** for integration tests with real PostgreSQL
- **ArchUnitNET** for architecture rule enforcement (including new modules)
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

## 10. Frontend / Vite + React Rules

### File & Component Conventions

**Naming:**

| Element | Convention | Example |
|:--------|:-----------|:--------|
| Files (components) | `kebab-case.tsx` | `employee-list.tsx`, `live-dashboard.tsx` |
| Files (utilities) | `kebab-case.ts` | `use-employees.ts`, `format-date.ts` |
| Components | `PascalCase` | `EmployeeList`, `LiveDashboard` |
| Hooks | `useCamelCase` | `useEmployees`, `useSignalR` |
| Stores (Zustand) | `useCamelCaseStore` | `useSidebarStore`, `useFilterStore` |
| Types/Interfaces | `PascalCase` | `Employee`, `LeaveRequest`, `ActivitySnapshot` |
| API query keys | `['resource', params]` | `['employees', { page: 1 }]` |
| Route segments | `kebab-case` | `/workforce/live`, `/hr/employees` |

**Directory Structure:**

```
src/
├── main.tsx                # Entry point; mounts App into #root
├── App.tsx                 # Provider stack + RouterProvider
├── router.tsx              # React Router v7 route config
├── pages/                  # Route page components
├── components/
│   ├── ui/                 # shadcn/ui primitives
│   ├── shared/             # Shared composed components
│   ├── hr/                 # Pillar 1 components
│   ├── workforce/          # Pillar 2 components
│   └── layout/             # NavRail, Topbar, Breadcrumbs
├── hooks/                  # Custom React hooks
├── lib/                    # Utilities, API client, constants
│   ├── api/                # API client + endpoint definitions
│   ├── signalr/            # SignalR connection manager
│   └── utils/              # Formatting, validation helpers
├── stores/                 # Zustand stores
├── types/                  # TypeScript types mirroring backend DTOs
└── styles/                 # Global CSS, Tailwind config
```

### Component Patterns

**SPA Components:**
- **Default to interactive React components** - the app is CSR-only.
- **Use React.lazy + Suspense** for heavy routes and widgets.
- **Do not use Next.js-only APIs** such as `next/dynamic`, `next/image`, middleware, or `app/` file routing.

**Permission Gating:**

```tsx
// Always gate features by permission
<PermissionGate permission="workforce:view">
  <WorkforceDashboard />
</PermissionGate>

// For conditional rendering within a component
const { hasPermission } = useAuth();
if (!hasPermission('exceptions:manage')) return null;
```

**Data Fetching (TanStack Query):**

```tsx
// Standard pattern for data fetching
export function useEmployees(filters: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => api.employees.list(filters),
    staleTime: 30_000, // 30 seconds
  });
}

// Mutation with optimistic update
export function useApproveLeave() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.leave.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave-requests'] });
    },
  });
}
```

**Form Pattern:**

```tsx
const schema = z.object({
  firstName: z.string().min(1).max(100),
  email: z.string().email(),
});

type FormData = z.infer<typeof schema>;

export function CreateEmployeeForm() {
  const form = useForm<FormData>({ resolver: zodResolver(schema) });
  const mutation = useCreateEmployee();
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(data => mutation.mutate(data))}>
        {/* fields */}
      </form>
    </Form>
  );
}
```

### Frontend API Integration Rules

- **All API calls go through the typed API client** — never raw `fetch()`
- **Use TanStack Query for ALL data fetching** — no `useEffect` + `useState` for API calls
- **Handle loading, error, empty states** for every data-fetching component
- **Pagination via React Router `useSearchParams`** — page/cursor in URL params
- **Error display:** RFC 7807 Problem Details → user-friendly error toast

### Frontend Real-time Rules

- **SignalR for:** workforce-live, exception-alerts, notifications, agent-status
- **Polling fallback:** 30s polling if SignalR connection fails
- **Reconnection:** Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s)
- **Stale data indicator:** Show "Last updated X seconds ago" on live dashboards

### Frontend Styling Rules

- **Tailwind utilities first** — avoid custom CSS unless absolutely necessary
- **shadcn/ui for all base components** — don't build custom buttons, dialogs, etc.
- **CSS Custom Properties for theming** — light/dark mode, tenant brand colors
- **Responsive:** Desktop-first, but all pages must be usable on tablet (≥768px)
- **No inline styles** — use Tailwind classes or CSS modules

### Frontend Testing Rules

- **Vitest for hooks and utilities** — pure logic tests
- **React Testing Library for components** — test behavior, not implementation
- **Playwright for critical E2E flows** — login, leave request, exception management
- **MSW for API mocking** — realistic API responses in tests
- **No snapshot tests** — they break on every UI change

### Frontend Security Rules

- **Never store JWT in localStorage** — access token in memory, refresh in HttpOnly cookie
- **Sanitize all user-generated content** before rendering (XSS prevention)
- **RBAC check on every route** — redirect to 403 if unauthorized
- **No sensitive data in URL params** — employee IDs are OK, PII is not
- **CSP headers** configured at the hosting/API edge; there is no Next.js middleware in this app.

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
