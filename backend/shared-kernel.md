# ONEVO.Domain — Layer Guide

**Last Updated:** 2026-04-27

The innermost layer. Contains pure business entities and rules. **Zero external dependencies** — no EF Core, no MediatR attributes, no framework code.

> This file replaces the former SharedKernel documentation. The `ONEVO.SharedKernel` project no longer exists. Its contents have been redistributed into `ONEVO.Domain` (entities, value objects, enums, errors) and `ONEVO.Application/Common/` (interfaces, models).

---

## What lives in ONEVO.Domain

### Common/BaseEntity.cs

```csharp
public abstract class BaseEntity
{
    public Guid Id { get; set; }
    public Guid TenantId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? UpdatedAt { get; set; }
    public Guid CreatedById { get; set; }
    public bool IsDeleted { get; set; } = false;

    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyList<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    protected void AddDomainEvent(IDomainEvent domainEvent)
        => _domainEvents.Add(domainEvent);

    public void ClearDomainEvents()
        => _domainEvents.Clear();
}
```

### Common/IDomainEvent.cs

```csharp
public interface IDomainEvent : INotification { } // INotification from MediatR
```

This is the **only** MediatR reference in Domain — and only because MediatR's `INotification` is a marker interface with no implementation. Domain events replace `IEventBus` + RabbitMQ entirely.

### Common/ValueObject.cs

```csharp
public abstract class ValueObject
{
    protected abstract IEnumerable<object> GetEqualityComponents();

    public override bool Equals(object? obj) { ... }
    public override int GetHashCode() { ... }
}
```

### Enums/

All shared enums used across features:
- `EmploymentType` (FullTime, PartTime, Contract, Intern)
- `EmploymentStatus` (Active, OnLeave, Suspended, Terminated)
- `ApprovalStatus` (Pending, Approved, Rejected, Cancelled)
- `Severity` (Low, Medium, High, Critical)
- `WorkMode` (OnSite, Remote, Hybrid)

### Errors/

- `DomainException` — business rule violation, maps to HTTP 422
- `NotFoundException` — entity not found, maps to HTTP 404
- `ForbiddenException` — permission denied, maps to HTTP 403

### ValueObjects/

Immutable types validated on construction:
- `Email` — validates format, normalises to lowercase
- `Money` — amount + currency code
- `PhoneNumber` — E.164 format
- `Address` — street, city, country, postal code

### Features/

24 feature sub-folders. Each contains:

```
Features/{Feature}/
├── Entities/     Business entities — POCOs, no EF attributes
└── Events/       IDomainEvent implementations
```

---

## What does NOT live in ONEVO.Domain

| Item | Where it lives |
|------|---------------|
| Repository interfaces | `ONEVO.Application/Common/Interfaces/` |
| MediatR handlers | `ONEVO.Application/Features/` |
| EF Core configurations | `ONEVO.Infrastructure/Persistence/Configurations/` |
| DTOs | `ONEVO.Application/Features/{Feature}/DTOs/` |
| Validation | `ONEVO.Application/Features/{Feature}/Validators/` |

---

## Feature entity example

```csharp
// ONEVO.Domain/Features/Leave/Entities/LeaveRequest.cs
public class LeaveRequest : BaseEntity
{
    public Guid EmployeeId { get; private set; }
    public Guid LeaveTypeId { get; private set; }
    public DateTime StartDate { get; private set; }
    public DateTime EndDate { get; private set; }
    public ApprovalStatus Status { get; private set; }

    private LeaveRequest() { } // EF constructor

    public static LeaveRequest Create(Guid employeeId, Guid leaveTypeId,
        DateTime start, DateTime end, Guid tenantId)
    {
        var request = new LeaveRequest
        {
            Id = Guid.NewGuid(),
            EmployeeId = employeeId,
            LeaveTypeId = leaveTypeId,
            StartDate = start,
            EndDate = end,
            Status = ApprovalStatus.Pending,
            TenantId = tenantId
        };
        request.AddDomainEvent(new LeaveRequestSubmittedEvent(request.Id, employeeId));
        return request;
    }

    public void Approve()
    {
        if (Status != ApprovalStatus.Pending)
            throw new DomainException("Only pending requests can be approved.");
        Status = ApprovalStatus.Approved;
        AddDomainEvent(new LeaveApprovedEvent(Id, EmployeeId));
    }
}
```
