# Repository Persistence Boundary

ONEVO uses a single EF Core `ApplicationDbContext`, but application code must treat the database as reachable only through repository-style persistence abstractions.

## Rule

Only Infrastructure persistence classes may inject `ApplicationDbContext`, EF Core `DbSet<T>`, or run EF Core queries.

Command handlers, query handlers, event handlers, application services, domain services, permission resolvers, tenant provisioning services, and module services must not query the database directly. They call Application-owned repository/reader interfaces instead.

## Where Interfaces Live

Repository interfaces live in Application:

```text
ONEVO.Application/Features/{Feature}/{SubFeature}/RepositoryInterfaces/I{SubFeature}Repository.cs
ONEVO.Application/Common/RepositoryInterfaces/I{SharedConcern}Repository.cs
```

Infrastructure implements those interfaces:

```text
ONEVO.Infrastructure/Persistence/Repositories/{Feature}/{SubFeature}/{SubFeature}Repository.cs
```

## Allowed Direct DbContext Usage

Direct `ApplicationDbContext` access is allowed only in:

- `ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs`
- EF Core configurations, migrations, factories, and interceptors
- Repository implementations under `ONEVO.Infrastructure/Persistence/Repositories/`
- Reviewed low-level persistence utilities whose name and namespace make the persistence role explicit

All other code must depend on repositories/readers/services that hide EF Core. Application must not expose an `IApplicationDbContext`/`DbSet<T>` abstraction; repository interfaces are the persistence boundary.

## Handler Pattern

```csharp
public class ExecutePayrollCommandHandler : IRequestHandler<ExecutePayrollCommand, Result<PayrollRunDto>>
{
    private readonly IPayrollRepository _payroll;
    private readonly IUnitOfWork _uow;

    public ExecutePayrollCommandHandler(IPayrollRepository payroll, IUnitOfWork uow)
    {
        _payroll = payroll;
        _uow = uow;
    }

    public async Task<Result<PayrollRunDto>> Handle(ExecutePayrollCommand request, CancellationToken ct)
    {
        var run = await _payroll.GetCurrentRunForUpdateAsync(request.TenantId, request.PeriodStart, request.PeriodEnd, ct);
        // domain behavior here
        await _uow.SaveChangesAsync(ct);
        return Result<PayrollRunDto>.Success(/* projection */);
    }
}
```

## Payroll Placement

Payroll persistence belongs here:

```text
ONEVO.Application/Features/Payroll/{SubFeature}/RepositoryInterfaces/IPayrollRepository.cs
ONEVO.Infrastructure/Persistence/Repositories/Payroll/{SubFeature}/PayrollRepository.cs
```

Use a feature-specific repository for payroll because payroll has batch persistence, joins, projections, and locking requirements such as `SELECT FOR UPDATE`. Do not create a thin CRUD wrapper unless it centralizes tenant filtering, locking, projection, or transactional behavior.

## Tenant Safety

Repositories own tenant filtering and any intentional cross-tenant access. Any method using `IgnoreQueryFilters()` or raw SQL must include an explicit tenant predicate unless it is a platform-level lookup such as tenant slug or subscription plan catalog access.

PostgreSQL RLS is a safety net, not a replacement for repository-level tenant scoping.
