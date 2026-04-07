# Migration Patterns: ONEVO

## EF Core Migrations

### Creating Migrations

```bash
# From solution root
dotnet ef migrations add <MigrationName> \
  --project src/ONEVO.Api \
  --startup-project src/ONEVO.Api \
  --output-dir Migrations

# Examples:
dotnet ef migrations add AddEmployeeDependents
dotnet ef migrations add AddLeaveModule
dotnet ef migrations add AlterAttendanceAddCorrections
```

### Applying Migrations

```bash
# Development
dotnet ef database update

# Production: generate SQL script and review before applying
dotnet ef migrations script --idempotent --output migration.sql
```

### Naming Convention

`{Action}{Entity/Module}{Detail}`

- `AddEmployeeTable`
- `AddLeaveModule`
- `AlterEmployeesAddManagerId`
- `CreateIndexOnAttendanceDate`
- `SeedDefaultRolesAndPermissions`

## Zero-Downtime Migration Strategy

Use the **expand-contract** pattern for all schema changes:

### Safe Migrations (can run during deployment)

| Operation | Safe? | Notes |
|:----------|:------|:------|
| Add new table | Yes | No impact on existing queries |
| Add nullable column | Yes | Existing code ignores it |
| Add index (CONCURRENTLY) | Yes | Use `CREATE INDEX CONCURRENTLY` |
| Add new enum value | Yes | Existing code ignores it |

### Dangerous Migrations (require expand-contract)

| Operation | Strategy |
|:----------|:---------|
| Rename column | Deploy 1: Add new column → Deploy 2: Migrate data + use new column → Deploy 3: Drop old column |
| Drop column | Deploy 1: Stop reading column → Deploy 2: Drop column |
| Change column type | Deploy 1: Add new column → Deploy 2: Migrate data → Deploy 3: Drop old |
| Add NOT NULL constraint | Deploy 1: Add column nullable → Deploy 2: Backfill data → Deploy 3: Add constraint |
| Drop table | Deploy 1: Stop all references → Deploy 2: Drop table |

### Example: Expand-Contract

```csharp
// Deploy 1: EXPAND — add new column (nullable)
migrationBuilder.AddColumn<string>(
    name: "work_email",
    table: "employees",
    type: "varchar(255)",
    nullable: true);

// Deploy 2: MIGRATE — backfill data + update code to use new column
// (done via Hangfire background job for large tables)

// Deploy 3: CONTRACT — drop old column (after all code uses new one)
migrationBuilder.DropColumn(
    name: "email",
    table: "employees");
```

## Seed Data

Seed data for reference tables and default configurations:

```csharp
// In migrations or dedicated seed service
public class SeedDefaultData : IDataSeeder
{
    public async Task SeedAsync(AppDbContext context)
    {
        // Countries (reference data — no tenant_id)
        if (!await context.Countries.AnyAsync())
        {
            context.Countries.AddRange(
                new Country { Code = "LK", Name = "Sri Lanka", CurrencyCode = "LKR", Timezone = "Asia/Colombo" },
                new Country { Code = "GB", Name = "United Kingdom", CurrencyCode = "GBP", Timezone = "Europe/London" }
            );
        }
        
        // Permissions (reference data — no tenant_id)
        if (!await context.Permissions.AnyAsync())
        {
            var permissions = PermissionSeedData.GetAllPermissions(); // 80+ permissions
            context.Permissions.AddRange(permissions);
        }
        
        await context.SaveChangesAsync();
    }
}
```

## RLS Policy Migrations

RLS policies are applied via raw SQL in migrations:

```csharp
migrationBuilder.Sql(@"
    ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
    ALTER TABLE employees FORCE ROW LEVEL SECURITY;
    
    DROP POLICY IF EXISTS tenant_isolation ON employees;
    CREATE POLICY tenant_isolation ON employees
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
");
```

## Rollback Strategy

| Level | Method | When to Use |
|:------|:-------|:------------|
| Level 1 | Roll back application code only | Additive schema changes (new columns, tables) |
| Level 2 | Roll back application + run reverse migration | Safe schema changes |
| Level 3 | Point-in-time recovery from backup | Destructive schema changes that failed |

**RPO:** 1 minute (continuous WAL archiving)
**RTO:** 15 minutes (automated failover)

## Related

- [[shared-kernel]]
- [[multi-tenancy]]
- [[auth]]
- [[core-hr]]
- [[leave]]
- [[payroll]]
- [[performance-module]]
- [[attendance]]
- [[expense]]
- [[grievance]]
- [[documents]]
- [[notifications]]
- [[org-structure]]
- [[workforce-presence]]
- [[activity-monitoring]]
- [[identity-verification]]
- [[exception-engine]]
- [[agent-gateway]]
- [[configuration]]
- [[productivity-analytics]]
- [[calendar]]
- [[skills]]
- [[reporting-engine]]
