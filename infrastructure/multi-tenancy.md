# Multi-Tenancy Architecture: ONEVO

## Overview

ONEVO uses a **shared database, shared schema** multi-tenancy model with **4 layers of data isolation**:

```
Layer 1: JWT Claims         → tenant_id in access token
Layer 2: BaseRepository     → automatic WHERE tenant_id = @current filter
Layer 3: PostgreSQL RLS     → database-level row filtering (safety net)
Layer 4: ArchUnitNET Tests  → compile-time verification of boundary rules
```

## Layer 1: JWT Claims

Every authenticated request carries a JWT with `tenant_id`:

```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "email": "user@company.com",
  "roles": ["HR_Admin"],
  "permissions": ["employees:read", "employees:write", "leave:approve"],
  "iat": 1679616000,
  "exp": 1679616900
}
```

The `TenantMiddleware` extracts `tenant_id` and populates `ITenantContext`:

```csharp
public class TenantMiddleware
{
    public async Task InvokeAsync(HttpContext context, ITenantContext tenantContext)
    {
        var tenantId = context.User.FindFirst("tenant_id")?.Value;
        if (tenantId is null) { context.Response.StatusCode = 401; return; }
        
        tenantContext.SetTenant(Guid.Parse(tenantId));
        await _next(context);
    }
}
```

## Layer 2: BaseRepository Auto-Filtering

`BaseRepository<T>` automatically applies tenant filtering to ALL queries:

```csharp
// Every query goes through this filtered IQueryable
protected IQueryable<T> Query => _context.Set<T>()
    .Where(e => e.TenantId == _tenantContext.TenantId)
    .Where(e => !e.IsDeleted);
```

**Non-tenant-scoped tables** (no `tenant_id`): `countries`, `permissions`, `subscription_plans`, `payroll_providers`. These use a separate `ReferenceRepository<T>` without tenant filtering.

## Layer 3: PostgreSQL Row-Level Security

Even if application code bypasses `BaseRepository`, RLS at the database level prevents cross-tenant access:

```sql
-- Enable RLS on every tenant-scoped table
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

-- Policy: users can only see rows matching their tenant
CREATE POLICY tenant_isolation ON employees
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Set tenant context per connection (done by EF Core interceptor)
SET LOCAL app.current_tenant_id = 'tenant-uuid';
```

### EF Core RLS Interceptor

```csharp
public class TenantRlsInterceptor : DbConnectionInterceptor
{
    private readonly ITenantContext _tenantContext;
    
    public override async Task ConnectionOpenedAsync(DbConnection connection, ...)
    {
        await using var cmd = connection.CreateCommand();
        cmd.CommandText = $"SET LOCAL app.current_tenant_id = '{_tenantContext.TenantId}'";
        await cmd.ExecuteNonQueryAsync();
    }
}
```

> **Safety note — string interpolation in RLS interceptor:**
> The interpolation above is safe **only** because `TenantId` is a `Guid`. A `Guid` can only contain hex digits and hyphens — it is structurally incapable of containing SQL injection characters (quotes, semicolons, etc.). PostgreSQL will reject any malformed UUID before it reaches the `SET LOCAL` command.
>
> **Do NOT copy this pattern for any non-`Guid` value.** If you ever need to set a `SET LOCAL` variable from a string (e.g., a tenant name, a user-supplied label), use a parameterized command:
> ```csharp
> cmd.CommandText = "SELECT set_config('app.current_tenant_id', $1, true)";
> cmd.Parameters.Add(new NpgsqlParameter { Value = tenantId.ToString() });
> ```
> The RLS policy itself is a defence-in-depth safety net — the application-level `BaseRepository<T>` filter is the primary enforcement layer.

## Layer 4: ArchUnitNET Compile-Time Tests

```csharp
[Fact]
public void All_Entities_Except_Reference_Should_Have_TenantId()
{
    var referenceEntities = new[] { "Country", "Permission", "SubscriptionPlan", "PayrollProvider" };
    
    var rule = Classes()
        .That().AreAssignableTo(typeof(BaseEntity))
        .And().DoNotHaveNameMatching(string.Join("|", referenceEntities))
        .Should().HavePropertyWithName("TenantId");
    
    rule.Check(Architecture);
}

[Fact]
public void No_Repository_Should_Bypass_BaseRepository()
{
    var rule = Classes()
        .That().HaveNameEndingWith("Repository")
        .Should().BeAssignableTo(typeof(BaseRepository<>));
    
    rule.Check(Architecture);
}
```

## Tenant Provisioning Flow

```
1. Signup      → Create tenant record (status: provisioning)
2. Seed        → Create default roles, permissions, settings, department
3. Activate    → Set status to active, send welcome email
4. Configure   → Admin sets up org structure, imports employees
```

```csharp
public async Task<Result<TenantDto>> ProvisionTenantAsync(CreateTenantCommand cmd, CancellationToken ct)
{
    // 1. Create tenant
    var tenant = new Tenant { Name = cmd.Name, Slug = cmd.Slug, Status = "provisioning" };
    await _tenantRepository.AddAsync(tenant, ct);
    
    // 2. Seed defaults (runs in tenant context)
    await _seedService.SeedDefaultRolesAsync(tenant.Id, ct);
    await _seedService.SeedDefaultSettingsAsync(tenant.Id, ct);
    await _seedService.SeedDefaultDepartmentAsync(tenant.Id, ct);
    
    // 3. Create admin user
    var adminUser = await _userService.CreateAdminUserAsync(tenant.Id, cmd.AdminEmail, ct);
    
    // 4. Activate
    tenant.Status = "active";
    await _unitOfWork.SaveChangesAsync(ct);
    
    return Result<TenantDto>.Success(tenant.ToDto());
}
```

## Tenant Offboarding (GDPR)

```
1. Initiate    → Admin requests account deletion
2. Grace       → 30-day grace period (data preserved but tenant deactivated)
3. Export      → Generate GDPR compliance export (all tenant data)
4. Purge       → Permanent deletion of all tenant data
5. Confirm     → Send confirmation email, audit log entry
```

## Connection String Strategy

| Environment | Strategy | Notes |
|:------------|:---------|:------|
| Local dev | Single PostgreSQL instance | Docker Compose, RLS enabled |
| Staging | Shared database | Same as production architecture |
| Production | Shared database + PgBouncer | Connection pooling, read replicas |

## Performance Considerations

- **Index on `tenant_id`** on every tenant-scoped table (composite indexes with other frequently queried columns) — see [[database/performance|Performance]]
- **Partition large tables** by tenant_id (for very large tenants) or by time (for audit_logs, biometric_events)
- **Redis caching** keyed by `tenant:{tenantId}:{entity}:{id}` — never cache cross-tenant data (see [[database/performance|Performance]])
- **Rate limiting** per tenant via Redis token bucket

## Related

- [[backend/shared-kernel|Shared Kernel]] — BaseRepository, ITenantContext implementation
- [[security/auth-architecture|Auth Architecture]] — JWT claims carrying tenant_id
- [[backend/module-boundaries|Module Boundaries]] — ArchUnitNET tests for tenant isolation enforcement
- [[security/compliance|Compliance]] — GDPR tenant offboarding and data export
