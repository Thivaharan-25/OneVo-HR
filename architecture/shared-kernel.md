# Shared Kernel: ONEVO

The shared kernel (`ONEVO.SharedKernel`) contains code genuinely shared across 3+ modules. It is the **only** place where cross-module code lives.

## Directory Structure

```
ONEVO.SharedKernel/
├── Entities/
��   ├── BaseEntity.cs              # Id, TenantId, CreatedAt, UpdatedAt, CreatedById, IsDeleted
│   ├── IAuditableEntity.cs        # CreatedAt, UpdatedAt, CreatedById, UpdatedById
│   └── ISoftDeletable.cs          # IsDeleted, DeletedAt, DeletedById
├── Repositories/
│   ├── IRepository.cs             # Generic repository interface
│   ├── BaseRepository.cs          # Tenant-filtered CRUD (auto-applies TenantId)
│   └── IUnitOfWork.cs             # SaveChangesAsync wrapper
├── Results/
��   ├── Result.cs                  # Result<T> for success/failure without exceptions
│   ├── Error.cs                   # Error type with Code + Message
│   └── ValidationError.cs         # Validation-specific error with field details
├── MultiTenancy/
│   ├── ITenantContext.cs           # Current tenant from JWT (TenantId, UserId)
│   ├─�� TenantContext.cs            # HttpContext-based implementation
│   └─��� TenantMiddleware.cs        # Extracts tenant from JWT, sets ITenantContext
├── Security/
│   ├── IEncryptionService.cs      # AES-256 encrypt/decrypt
���   ├── ICurrentUser.cs            # Current user context (UserId, TenantId, Roles, Permissions)
│   └── RequirePermissionAttribute.cs # [RequirePermission("resource:action")]
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
│   ├── ONEVOException.cs       # Base exception (for truly exceptional cases)
│   ├── TenantMismatchException.cs # Critical: cross-tenant access attempt
│   └── ConcurrencyException.cs    # EF Core concurrency conflict
├── Configuration/
���   ├── DatabaseSettings.cs        # PostgreSQL connection config
│   ├── RedisSettings.cs           # Redis connection config
│   ├── JwtSettings.cs             # JWT configuration (Issuer, Audience, Keys)
│   └── EncryptionSettings.cs      # AES-256 key config
└── Extensions/
    ├── ServiceCollectionExtensions.cs  # DI registration helpers
    ├── QueryableExtensions.cs          # ApplyPaging(), ApplySorting()
    └── ClaimsPrincipalExtensions.cs    # GetTenantId(), GetUserId(), HasPermission()
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

- [[module-boundaries]] — rules for using SharedKernel vs module code
- [[multi-tenancy]] — how `ITenantContext` and `BaseRepository` enforce tenant isolation
- [[module-catalog]] — all modules that depend on SharedKernel
- [[coding-standards]] — naming conventions and code patterns

## Rules

1. **Three-module rule:** Don't add to SharedKernel until 3+ modules need it
2. **No business logic:** If it contains domain rules, it belongs in a module
3. **Backward compatible:** Changes affect all modules — treat like API changes
4. **Review required:** SharedKernel PRs need review from 2+ developers
