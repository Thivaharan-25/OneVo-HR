# Shared Kernel: ONEVO

**Last Updated:** 2026-05-08

`ONEVO.SharedKernel` is not a separate project. Shared primitives live in:

- `ONEVO.Domain/Common/` for entities, value objects, errors, and optional domain-event marker types.
- `ONEVO.Application/Common/RepositoryInterfaces/` for common persistence contracts.
- `ONEVO.Application/Common/ServiceInterfaces/` for common service contracts.
- `ONEVO.Application/Common/Models/` and `ONEVO.Application/Common/Behaviors/` for shared models and pipeline behaviors.

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

### Repository And Service Interfaces

Application defines repository and service interfaces. Infrastructure implements them.

Common repository examples:

- `IUnitOfWork`

Common service examples:

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
ONEVO.Application/Features/{Feature}/{SubFeature}/RepositoryInterfaces/
ONEVO.Application/Features/{Feature}/{SubFeature}/ServiceInterfaces/
```

## Validation Location

Command validators live beside the command:

```text
ONEVO.Application/Features/{Feature}/{SubFeature}/Commands/{UseCase}/{UseCase}Validator.cs
```

Do not use a feature-level `Validators/` folder.

## Optional Event Location

Only create event folders when a use case has a justified post-save side effect:

```text
ONEVO.Domain/Features/{Feature}/{SubFeature}/Events/
ONEVO.Application/Features/{Feature}/{SubFeature}/EventHandlers/
```

See [[backend/domain-events|Domain Events]] for the decision rule.
