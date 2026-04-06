# Database Performance: ONEVO

## Indexing Strategy

### Mandatory Indexes

Every tenant-scoped table must have:

```sql
-- Composite index on tenant_id + primary lookup column
CREATE INDEX idx_{table}_tenant ON {table} (tenant_id);

-- For tables with frequent filtered queries
CREATE INDEX idx_{table}_tenant_{filter} ON {table} (tenant_id, {filter_column});
```

### Key Indexes

```sql
-- Employees (most queried table)
CREATE INDEX idx_employees_tenant_dept ON employees (tenant_id, department_id);
CREATE INDEX idx_employees_tenant_manager ON employees (tenant_id, manager_id);
CREATE INDEX idx_employees_tenant_status ON employees (tenant_id, employment_status);
CREATE UNIQUE INDEX uq_employees_tenant_empno ON employees (tenant_id, employee_no);

-- Attendance (high-volume, date-based queries)
CREATE INDEX idx_attendance_tenant_emp_date ON attendance_records (tenant_id, employee_id, date);
CREATE INDEX idx_attendance_tenant_date ON attendance_records (tenant_id, date);

-- Leave requests (frequent status queries)
CREATE INDEX idx_leave_requests_emp_status ON leave_requests (employee_id, status);
CREATE INDEX idx_leave_requests_dates ON leave_requests (start_date, end_date);

-- Audit logs (time-series, partitioned)
CREATE INDEX idx_audit_logs_tenant_time ON audit_logs (tenant_id, created_at);
CREATE INDEX idx_audit_logs_resource ON audit_logs (tenant_id, resource_type, resource_id);

-- Workflow instances (active workflow lookups)
CREATE INDEX idx_workflow_instances_resource ON workflow_instances (resource_type, resource_id);
CREATE INDEX idx_workflow_instances_status ON workflow_instances (tenant_id, status);
```

## N+1 Prevention

### EF Core Eager Loading

```csharp
// BAD: N+1 — loads department for each employee separately
var employees = await _context.Employees.ToListAsync();
foreach (var emp in employees)
    Console.WriteLine(emp.Department.Name); // N additional queries!

// GOOD: Eager load with Include
var employees = await _context.Employees
    .Include(e => e.Department)
    .Include(e => e.JobFamily)
    .ThenInclude(jf => jf.Levels)
    .Where(e => e.TenantId == tenantId)
    .ToListAsync(ct);

// BETTER: Project to DTO (only loads needed columns)
var employees = await _context.Employees
    .Where(e => e.TenantId == tenantId)
    .Select(e => new EmployeeListDto
    {
        Id = e.Id,
        FullName = e.FirstName + " " + e.LastName,
        DepartmentName = e.Department.Name,
        JobTitle = e.JobTitle.Name
    })
    .ToListAsync(ct);
```

### Split Queries for Complex Joins

```csharp
// For entities with multiple collection navigations
var employee = await _context.Employees
    .Include(e => e.Dependents)
    .Include(e => e.Addresses)
    .Include(e => e.Qualifications)
    .AsSplitQuery() // Prevents cartesian explosion
    .FirstOrDefaultAsync(e => e.Id == id, ct);
```

## Caching Strategy (Redis)

### 3-Layer Cache

| Layer | Storage | TTL | Use Case |
|:------|:--------|:----|:---------|
| L1 | In-memory (`IMemoryCache`) | 1-5 min | Hot data (current user permissions, tenant settings) |
| L2 | Redis | 5-60 min | Warm data (department tree, job families, feature flags) |
| L3 | PostgreSQL | Permanent | Source of truth |

### Cache Key Convention

```
onevo:{tenantId}:{entity}:{id}        → Single entity
onevo:{tenantId}:{entity}:list:{hash}  → List queries
onevo:global:{entity}:{id}             → Non-tenant data (countries, permissions)
```

### Cache Invalidation

- **Write-through:** Update cache on entity save
- **Event-driven:** Domain events trigger cache invalidation in relevant modules
- **TTL-based:** Fallback expiry for stale data protection

```csharp
public class CacheInvalidatingHandler : INotificationHandler<EmployeeUpdatedEvent>
{
    public async Task Handle(EmployeeUpdatedEvent notification, CancellationToken ct)
    {
        await _cache.RemoveAsync($"onevo:{notification.TenantId}:employee:{notification.EmployeeId}");
        await _cache.RemoveAsync($"onevo:{notification.TenantId}:employee:list:*"); // Pattern delete
    }
}
```

## Table Partitioning

For high-volume time-series tables, use `pg_partman`:

```sql
-- Partition audit_logs by month
SELECT create_parent(
    p_parent_table := 'public.audit_logs',
    p_control := 'created_at',
    p_type := 'range',
    p_interval := '1 month'
);

-- Partition biometric_events by month
SELECT create_parent(
    p_parent_table := 'public.biometric_events',
    p_control := 'event_time',
    p_type := 'range',
    p_interval := '1 month'
);

-- Workforce Intelligence: activity_raw_buffer — partitioned DAILY, purged after 48h
SELECT create_parent(
    p_parent_table := 'public.activity_raw_buffer',
    p_control := 'received_at',
    p_type := 'range',
    p_interval := '1 day'
);

-- Workforce Intelligence: activity_snapshots — partitioned MONTHLY, 90-day retention
SELECT create_parent(
    p_parent_table := 'public.activity_snapshots',
    p_control := 'captured_at',
    p_type := 'range',
    p_interval := '1 month'
);
```

### Workforce Intelligence Indexes

```sql
-- Activity snapshots (high-volume, always query with tenant_id + date range)
CREATE INDEX idx_activity_snapshots_tenant_emp_time ON activity_snapshots (tenant_id, employee_id, captured_at);
CREATE INDEX idx_activity_snapshots_tenant_time ON activity_snapshots (tenant_id, captured_at);

-- Activity daily summary (primary reporting table)
CREATE UNIQUE INDEX uq_activity_daily_tenant_emp_date ON activity_daily_summary (tenant_id, employee_id, date);

-- Application usage
CREATE INDEX idx_app_usage_tenant_emp_date ON application_usage (tenant_id, employee_id, date);

-- Presence sessions (one row/employee/day)
CREATE UNIQUE INDEX uq_presence_tenant_emp_date ON presence_sessions (tenant_id, employee_id, date);
CREATE INDEX idx_presence_tenant_date ON presence_sessions (tenant_id, date);

-- Device sessions
CREATE INDEX idx_device_sessions_tenant_emp ON device_sessions (tenant_id, employee_id, session_start);

-- Exception alerts (active alert queries)
CREATE INDEX idx_exception_alerts_tenant_status ON exception_alerts (tenant_id, status);
CREATE INDEX idx_exception_alerts_tenant_emp ON exception_alerts (tenant_id, employee_id, triggered_at);

-- Registered agents
CREATE UNIQUE INDEX uq_agents_tenant_device ON registered_agents (tenant_id, device_id);
CREATE INDEX idx_agents_tenant_status ON registered_agents (tenant_id, status);

-- Productivity reports
CREATE UNIQUE INDEX uq_daily_report_tenant_emp_date ON daily_employee_report (tenant_id, employee_id, date);
CREATE UNIQUE INDEX uq_workforce_snapshot_tenant_date ON workforce_snapshot (tenant_id, date);
```

## Connection Pooling (PgBouncer)

```ini
[pgbouncer]
pool_mode = transaction        ; Release connection after each transaction
max_client_conn = 200          ; Max client connections
default_pool_size = 25         ; Connections per database/user pair
reserve_pool_size = 5          ; Extra connections for burst
server_idle_timeout = 300      ; Close idle server connections after 5 min
```

## Query Performance Rules

1. **Always** use `.AsNoTracking()` for read-only queries
2. **Always** project to DTOs (`.Select()`) instead of loading full entities for list endpoints
3. **Never** load more than 100 records in a single query (use pagination)
4. **Use** `EXPLAIN ANALYZE` to verify query plans for new queries
5. **Avoid** `LIKE '%search%'` — use PostgreSQL FTS with GIN indexes
6. **Monitor** slow queries via `pg_stat_statements` extension — see [[monitoring]]

## Related

- [[multi-tenancy]] — tenant_id indexing requirements
- [[search-architecture]] — GIN indexes for full-text search
- [[migration-patterns]] — creating indexes safely (CONCURRENTLY)
- [[coding-standards]] — EF Core query patterns
- [[observability]] — query performance tracing
