# AI Agent Rules and Guidelines for ONEVO

## 1. General Operating Principles

- **Source of Truth:** Always prioritize information found within this repository. If there's a conflict, the most recently updated file in `AI_CONTEXT/` takes precedence.
- **Contextual Awareness:** Before performing any task, read these files in order:
    1. [[project-context]] — What ONEVO is
    2. [[tech-stack]] — .NET 9, PostgreSQL, Redis, etc.
    3. [[current-focus]] — Current sprint/week priorities
    4. [[known-issues]] — Gotchas and deprecated patterns
    5. The specific module doc in `docs/architecture/modules/` for the module you're working on
- **Hallucination Prevention:** If a request cannot be fulfilled with the provided context, explicitly state that the information is unavailable. **DO NOT invent or speculate.**
- **Token Efficiency:** Be concise. Leverage existing code patterns rather than rewriting. Read ONLY the module doc you need, not all 22.
- **Security & Privacy:** Never expose connection strings, API keys, encryption keys, or PII. Flag sensitive operations for human review.

## 2. .NET 9 / C# Code Generation Rules

### Architecture

- **Monolithic + Service-Oriented:** All modules live in one .NET solution but maintain strict namespace boundaries
- **Module structure:** `ONEVO.Modules.{ModuleName}` — each module has its own namespace
- **[[shared-kernel|Shared kernel]]:** `ONEVO.SharedKernel` — only cross-cutting concerns used by 3+ modules
- **Never** reference one module's internal classes from another module (see [[module-boundaries]])
- **Use MediatR** for command/query dispatch within modules (see [[event-catalog]])
- **Use domain events** for cross-module side effects (not direct service calls)

### Naming Conventions

| Element | Convention | Example |
|:--------|:-----------|:--------|
| Namespaces | `PascalCase` | `ONEVO.Modules.CoreHR`, `ONEVO.Modules.ActivityMonitoring` |
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

// NEVER: Access another module's internals
using ONEVO.Modules.ActivityMonitoring.Internal.Repositories; // BAD

// NEVER: Skip tenant_id filtering
var employees = _dbContext.Employees.ToListAsync(); // BAD

// NEVER: Hardcode secrets
var conn = "Host=localhost;Database=onevo"; // BAD

// NEVER: String concatenation for SQL
var sql = $"SELECT * FROM employees WHERE id = '{id}'"; // BAD
```

### [[multi-tenancy|Multi-Tenancy]] Rules

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

## 3. Workforce Intelligence Rules (NEW)

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

// Workforce Intelligence (NEW)
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

## 4. Database Rules

- **EF Core Code-First** [[migration-patterns|migrations]] only — never raw DDL in production
- **snake_case** for all table/column names
- **UUID** primary keys (not auto-increment)
- **Soft delete** where appropriate (`IsDeleted` + `DeletedAt`)
- **Audit columns** on all entities: `created_at`, `updated_at`, `created_by_id`
- **Indexes** on: `tenant_id` (all tables), foreign keys, frequently queried columns
- **No cascade deletes** — handle deletion in services
- **Time-series tables** (activity_snapshots, activity_raw_buffer) use `pg_partman` partitioning — see [[performance]]

## 5. Testing Rules

- **xUnit** for all tests
- **FluentAssertions** for readable assertions
- **Moq** for mocking dependencies
- **Testcontainers** for integration tests with real PostgreSQL
- **ArchUnitNET** for architecture rule enforcement (including new modules)
- Minimum **80% code coverage** for services
- Every public API endpoint must have at least one integration test

## 6. Git Workflow

- **Commit Messages:** `type(scope): subject` (e.g., `feat(activity-monitoring): add snapshot ingestion`) — see [[git-workflow]]
- **Types:** feat, fix, refactor, test, docs, chore, perf
- **Branches:** `feature/`, `bugfix/`, `hotfix/` prefixes
- **PRs:** Small, focused. Require at least one reviewer.

## 7. Logging Rules (Serilog) — see [[logging-standards]]

- Structured logging: `_logger.LogInformation("Snapshot received for {EmployeeId} in tenant {TenantId}", id, tenantId)`
- **Never** log PII or activity content (emails, names, bank details, window titles, screenshot data)
- **Always** include correlation ID in log context
- Log levels: `Debug` for dev, `Information` for business events, `Warning` for recoverable issues, `Error` for failures
