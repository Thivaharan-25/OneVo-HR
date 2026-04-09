# Database Documentation: ONEVO

## Overview

- **RDBMS:** PostgreSQL 16
- **ORM:** Entity Framework Core 9
- **Total Tables:** ~153 across 22 modules (see [[database/schema-catalog|Schema Catalog]])
- **Multi-tenancy:** `tenant_id` on all tenant-scoped tables + PostgreSQL RLS
- **Connection Pooling:** PgBouncer
- **Partitioning:** `pg_partman` for time-series tables

## Schema Conventions

### Naming

| Element | Convention | Example |
|:--------|:-----------|:--------|
| Tables | `snake_case`, plural | `employees`, `leave_requests` |
| Columns | `snake_case` | `first_name`, `tenant_id`, `is_active` |
| Primary keys | `id` (uuid) | `id uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| Foreign keys | `{referenced_table_singular}_id` | `employee_id`, `department_id` |
| Indexes | `idx_{table}_{columns}` | `idx_employees_tenant_department` |
| Unique constraints | `uq_{table}_{columns}` | `uq_users_email_tenant` |

### Standard Columns

Every tenant-scoped table includes:

```sql
id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
tenant_id       uuid NOT NULL REFERENCES tenants(id),
created_at      timestamptz NOT NULL DEFAULT now(),
updated_at      timestamptz NOT NULL DEFAULT now(),
created_by_id   uuid REFERENCES users(id),
is_deleted      boolean NOT NULL DEFAULT false,
deleted_at      timestamptz
```

### EF Core Configuration

```csharp
// In AppDbContext.OnModelCreating:
modelBuilder.UseSnakeCaseNamingConvention(); // snake_case in DB, PascalCase in C#

// Entity configuration
modelBuilder.Entity<Employee>(e =>
{
    e.HasIndex(x => new { x.TenantId, x.DepartmentId });
    e.HasIndex(x => new { x.TenantId, x.EmployeeNo }).IsUnique();
    e.Property(x => x.Id).HasDefaultValueSql("gen_random_uuid()");
    e.HasQueryFilter(x => !x.IsDeleted); // Global soft-delete filter
});
```

### Key Relationships

- `employees` is the central hub — most HR tables link to it
- `tenants` is the root — every tenant-scoped table references it
- Self-referencing: `departments` (parent), `employees` (manager), `goals` (parent), `document_categories` (parent)
- Polymorphic: `workflow_instances` uses `resource_type` + `resource_id` to link to any entity

## Data Types

| C# Type | PostgreSQL Type | Usage |
|:--------|:---------------|:------|
| `Guid` | `uuid` | Primary keys, foreign keys |
| `string` | `varchar(n)` or `text` | Names, descriptions |
| `decimal` | `decimal(p,s)` | Monetary values, rates |
| `bool` | `boolean` | Flags |
| `DateTimeOffset` | `timestamptz` | Timestamps |
| `DateOnly` | `date` | Dates without time |
| `TimeOnly` | `time` | Times without date |
| `byte[]` | `bytea` | Encrypted fields |
| `JsonDocument` / typed class | `jsonb` | Flexible structured data |

## Encrypted Columns (bytea)

| Table | Column | Contains |
|:------|:-------|:---------|
| `employee_bank_details` | `account_number_encrypted` | Bank account numbers |
| `sso_providers` | `client_id_encrypted`, `client_secret_encrypted` | SSO credentials |
| `hardware_terminals` | `api_key_encrypted` | Terminal API keys |
| `integration_connections` | `credentials_encrypted` | Integration credentials |
| `notification_channels` | `credentials_encrypted` | Channel provider credentials |

All encrypted via `IEncryptionService` (AES-256) in [[backend/shared-kernel|Shared Kernel]]. See [[security/data-classification|Data Classification]] for full PII inventory.

## Key Documents

| Document | Purpose |
|:---------|:--------|
| [[database/schema-catalog|Schema Catalog]] | Master index of all ~153 tables, grouped by module with phase tags |
| [[database/cross-module-relationships|Cross-Module Relationships]] | FK dependencies across module boundaries + migration order |
| [[database/migration-patterns|Migration Patterns]] | EF Core migrations, zero-downtime strategies |
| [[database/performance|Performance]] | Indexing, query optimization, N+1 prevention |

### Per-Module Schemas

| Schema | Tables | Phase |
|:-------|:-------|:------|
| [[database/schemas/infrastructure|Infrastructure]] | 4 | 1 |
| [[database/schemas/auth|Auth & Security]] | 9 | 1 |
| [[database/schemas/org-structure|Org Structure]] | 8 | 1 |
| [[database/schemas/core-hr|Core HR]] | 13 | 1 |
| [[database/schemas/leave|Leave]] | 5 | 1 |
| [[database/schemas/calendar|Calendar]] | 1 | 1 |
| [[database/schemas/configuration|Configuration]] | 6 | 1 |
| [[database/schemas/agent-gateway|Agent Gateway]] | 4 | 1 |
| [[database/schemas/activity-monitoring|Activity Monitoring]] | 8 | 1 |
| [[database/schemas/workforce-presence|Workforce Presence]] | 3 | 1 |
| [[database/schemas/exception-engine|Exception Engine]] | 5 | 1 |
| [[database/schemas/identity-verification|Identity Verification]] | 6 | 1 |
| [[database/schemas/productivity-analytics|Productivity Analytics]] | 4 | 1 |
| [[database/schemas/shared-platform|Shared Platform]] | 30 | 1 |
| [[database/schemas/notifications|Notifications]] | 2 | 1 |
| [[database/schemas/payroll|Payroll]] | 11 | 2 |
| [[database/schemas/performance|Performance (module)]] | 7 | 2 |
| [[database/schemas/skills|Skills & Learning]] | 15 | 2 |
| [[database/schemas/documents|Documents]] | 6 | 2 |
| [[database/schemas/grievance|Grievance]] | 2 | 2 |
| [[database/schemas/expense|Expense]] | 3 | 2 |
| [[database/schemas/reporting-engine|Reporting Engine]] | 3 | 2 |

> **Build approach:** Use the per-module schema files in `database/schemas/` as the canonical reference when writing EF Core entity classes. The `end-to-end-logic.md` files describe behavior, not schema — they are for flow reference only.

## Related

- [[database/schema-catalog|Schema Catalog]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
