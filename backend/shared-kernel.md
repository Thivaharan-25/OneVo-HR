# Shared Kernel: ONEVO

**Last Updated:** 2026-05-08

`ONEVO.SharedKernel` is not a separate project. Shared primitives live in:

- `ONEVO.Domain/Common/` for entities, value objects, errors, and optional domain-event marker types.
- `ONEVO.Application/Common/` for interfaces, models, and pipeline behaviors.

## Domain Common

### BaseEntity

```csharp
public abstract class BaseEntity
{
    public Guid Id { get; set; }
    public Guid TenantId { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset? UpdatedAt { get; set; }
    public Guid CreatedById { get; set; }
    public bool IsDeleted { get; set; }

    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    protected void AddDomainEvent(IDomainEvent domainEvent)
        => _domainEvents.Add(domainEvent);

    public void ClearDomainEvents()
        => _domainEvents.Clear();
}
```

Domain-event support exists for optional post-save side effects. It does not mean every entity should raise events.

### IDomainEvent

```csharp
public interface IDomainEvent : INotification
{
}
```

`IDomainEvent` is optional. It is not an `IEventBus`, not an integration event, and not a RabbitMQ contract.

### ValueObject

```csharp
public abstract class ValueObject
{
    protected abstract IEnumerable<object?> GetEqualityComponents();
}
```

Use value objects for immutable concepts such as `Email`, `Money`, `PhoneNumber`, and `Address`.

## Application Common

### Result<T>

```csharp
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }

    public static Result<T> Success(T value) => new(true, value, null);
    public static Result<T> Failure(string error) => new(false, default, error);
}
```

Handlers return `Result<T>` for expected business outcomes. Exceptions are for infrastructure failures and unexpected states.

### Interfaces

Application defines interfaces. Infrastructure implements them.

Common examples:

- `IUnitOfWork`
- `ICurrentUser`
- `ICacheService`
- `IEncryptionService`
- `IEmailService`
- `IStorageService`
- `IDateTimeProvider`
- `IBackgroundJobService`
- `INotificationDispatcher`
- `ITokenService`
- `IPasswordHasher`

Feature-specific repositories and readers live under:

```text
ONEVO.Application/Features/{Feature}/Interfaces/
```

## Validation Location

Command validators live beside the command:

```text
ONEVO.Application/Features/{Feature}/Commands/{UseCase}/{UseCase}Validator.cs
```

Do not use a feature-level `Validators/` folder.

## Optional Event Location

Only create event folders when a use case has a justified post-save side effect:

```text
ONEVO.Domain/Features/{Feature}/Events/
ONEVO.Application/Features/{Feature}/EventHandlers/
```

See [[backend/domain-events|Domain Events]] for the decision rule.
