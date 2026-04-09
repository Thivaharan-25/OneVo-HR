# Shared Kernel: ONEVO

The shared kernel (`ONEVO.SharedKernel`) contains code genuinely shared across 3+ modules. It is the **only** place where cross-module code lives.

## Directory Structure

```
ONEVO.SharedKernel/
├── Entities/
│   ├── BaseEntity.cs              # Id, TenantId, CreatedAt, UpdatedAt, CreatedById, IsDeleted
│   ├── IAuditableEntity.cs        # CreatedAt, UpdatedAt, CreatedById, UpdatedById
│   └── ISoftDeletable.cs          # IsDeleted, DeletedAt, DeletedById
├── Repositories/
│   ├── IRepository.cs             # Generic repository interface
│   ├── BaseRepository.cs          # Tenant-filtered CRUD (auto-applies TenantId)
│   └── IUnitOfWork.cs             # SaveChangesAsync wrapper
├── Results/
│   ├── Result.cs                  # Result<T> for success/failure without exceptions
│   ├── Error.cs                   # Error type with Code + Message
│   └── ValidationError.cs         # Validation-specific error with field details
├── MultiTenancy/
│   ├── ITenantContext.cs           # Current tenant from JWT (TenantId, UserId)
│   ├── TenantContext.cs            # HttpContext-based implementation
│   └── TenantMiddleware.cs        # Extracts tenant from JWT, sets ITenantContext
├── Security/
│   ├── IEncryptionService.cs      # AES-256 encrypt/decrypt
│   ├── ICurrentUser.cs            # Current user context (UserId, TenantId, EffectivePermissions, GrantedModules, HierarchyScope)
│   ├── RequirePermissionAttribute.cs # [RequirePermission("resource:action")] — checks effective permissions
│   ├── IHierarchyScope.cs         # Resolves subordinate IDs for hierarchy-scoped data access
│   └── HierarchyScopeFilter.cs    # Auto-applies hierarchy WHERE clause to queries
├── Events/
│   ├── DomainEvent.cs             # Base domain event (Id, OccurredAt, TenantId)
│   ├── IDomainEventHandler.cs     # MediatR INotificationHandler wrapper
│   └── IntegrationEvent.cs        # For future RabbitMQ events
├── Pagination/
│   ├── PagedRequest.cs            # PageNumber, PageSize, SortBy, SortDirection
│   ├── PagedResult.cs             # Items, TotalCount, PageNumber, PageSize, TotalPages
│   └── CursorPagedResult.cs       # Items, NextCursor, HasMore (for cursor-based pagination)
├── Enums/
│   ├── EmploymentType.cs          # FullTime, PartTime, Contract, Intern, Probation
│   ├── EmploymentStatus.cs        # Active, OnLeave, Suspended, Terminated, Resigned
│   ├── ApprovalStatus.cs          # Pending, Approved, Rejected, Cancelled
│   ├── WorkMode.cs                # Office, Remote, Hybrid
│   └── Severity.cs                # Critical, High, Medium, Low
├── Utilities/
│   ├── IDateTimeProvider.cs       # Abstraction for DateTimeOffset.UtcNow (testable)
│   ├── IdGenerator.cs             # UUID v7 generation (time-sortable)
│   ├── SlugGenerator.cs           # URL-safe slug generation
│   └── StringExtensions.cs        # ToSnakeCase(), Truncate(), etc.
├── Exceptions/
│   ├── ONEVOException.cs          # Base exception (for truly exceptional cases)
│   ├── TenantMismatchException.cs # Critical: cross-tenant access attempt
│   └── ConcurrencyException.cs    # EF Core concurrency conflict
├── Configuration/
│   ├── DatabaseSettings.cs        # PostgreSQL connection config
│   ├── RedisSettings.cs           # Redis connection config
│   ├── JwtSettings.cs             # JWT configuration (Issuer, Audience, Keys)
│   └── EncryptionSettings.cs      # AES-256 key config
└── Extensions/
    ├── ServiceCollectionExtensions.cs  # DI registration helpers
    ├── QueryableExtensions.cs          # ApplyPaging(), ApplySorting(), ApplyHierarchyScope()
    └── ClaimsPrincipalExtensions.cs    # GetTenantId(), GetUserId(), HasPermission(), GetGrantedModules()
```

## Key Implementations

### BaseEntity

```csharp
public abstract class BaseEntity
{
    public Guid Id { get; set; } = IdGenerator.NewId(); // UUID v7
    public Guid TenantId { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset UpdatedAt { get; set; }
    public Guid? CreatedById { get; set; }
    public bool IsDeleted { get; set; }
    public DateTimeOffset? DeletedAt { get; set; }
    
    private readonly List<DomainEvent> _domainEvents = new();
    public IReadOnlyList<DomainEvent> DomainEvents => _domainEvents.AsReadOnly();
    public void AddDomainEvent(DomainEvent @event) => _domainEvents.Add(@event);
    public void ClearDomainEvents() => _domainEvents.Clear();
}
```

### BaseRepository (Tenant-Filtered)

```csharp
public class BaseRepository<T> : IRepository<T> where T : BaseEntity
{
    protected readonly AppDbContext _context;
    protected readonly ITenantContext _tenantContext;
    
    protected IQueryable<T> Query => _context.Set<T>()
        .Where(e => e.TenantId == _tenantContext.TenantId)
        .Where(e => !e.IsDeleted);
    
    public async Task<T?> GetByIdAsync(Guid id, CancellationToken ct)
        => await Query.FirstOrDefaultAsync(e => e.Id == id, ct);
    
    public async Task<PagedResult<T>> GetPagedAsync(PagedRequest request, CancellationToken ct)
        => await Query.ApplyPaging(request).ToPagedResultAsync(ct);
    
    public async Task AddAsync(T entity, CancellationToken ct)
    {
        entity.TenantId = _tenantContext.TenantId; // Enforce tenant
        entity.CreatedAt = DateTimeOffset.UtcNow;
        await _context.Set<T>().AddAsync(entity, ct);
    }
}
```

### ICurrentUser (Hybrid Permission Context)

```csharp
public interface ICurrentUser
{
    Guid UserId { get; }
    Guid TenantId { get; }
    IReadOnlyList<string> EffectivePermissions { get; }  // Resolved: role + overrides, filtered by feature grants
    IReadOnlyList<string> GrantedModules { get; }         // Modules this user has access to
    bool IsSuperAdmin { get; }                             // Has "*" permission — bypasses all checks
    
    bool HasPermission(string permission);
    bool HasAnyPermission(params string[] permissions);
    bool HasAllPermissions(params string[] permissions);
    bool IsModuleGranted(string module);
}
```

### IHierarchyScope (Data Access Scoping)

```csharp
public interface IHierarchyScope
{
    /// Returns IDs of all employees below this user in the reporting chain.
    /// Super Admin returns null (meaning no filter — access all).
    Task<HashSet<Guid>?> GetSubordinateIdsAsync(CancellationToken ct);
}

// Usage in any service that returns employee data:
public async Task<PagedResult<EmployeeDto>> GetEmployeesAsync(PagedRequest request, CancellationToken ct)
{
    var subordinateIds = await _hierarchyScope.GetSubordinateIdsAsync(ct);
    
    var query = _repository.Query;
    if (subordinateIds != null) // null = Super Admin, no filtering
        query = query.Where(e => subordinateIds.Contains(e.Id));
    
    return await query.ApplyPaging(request).ToPagedResultAsync(ct);
}
```

### Result<T>

```csharp
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public Error? Error { get; }
    
    public static Result<T> Success(T value) => new(true, value, null);
    public static Result<T> Failure(string message) => new(false, default, new Error(message));
    public static Result<T> Failure(Error error) => new(false, default, error);
}
```

## Related

- [[backend/module-boundaries|Module Boundaries]] — rules for using SharedKernel vs module code
- [[infrastructure/multi-tenancy|Multi Tenancy]] — how `ITenantContext` and `BaseRepository` enforce tenant isolation
- [[backend/module-catalog|Module Catalog]] — all modules that depend on SharedKernel
- [[code-standards/backend-standards|Backend Standards]] — naming conventions and code patterns
- [[frontend/architecture/overview|Overview]] — hybrid permission control model

## Rules

1. **Three-module rule:** Don't add to SharedKernel until 3+ modules need it
2. **No business logic:** If it contains domain rules, it belongs in a module
3. **Backward compatible:** Changes affect all modules — treat like API changes
4. **Review required:** SharedKernel PRs need review from 2+ developers
