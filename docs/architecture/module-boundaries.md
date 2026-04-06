# Module Boundary Rules: ONEVO

These rules keep the ONEVO monolith maintainable. **Non-negotiable** — violating them turns the modular monolith into a big ball of mud.

AI agents: **these rules override convenience**. Never generate code that violates these boundaries, even if it would be simpler.

## Core Rules

### Rule 1: Modules Only Access Each Other Through Public Interfaces

```csharp
// ALLOWED:
// From ONEVO.Modules.Leave:
using ONEVO.Modules.CoreHR.Public; // public interface
var employee = await _employeeService.GetByIdAsync(employeeId, ct);

// FORBIDDEN:
// From ONEVO.Modules.Leave:
using ONEVO.Modules.CoreHR.Internal.Repositories; // internal!
var employee = await _employeeRepository.GetByIdAsync(employeeId, ct);
```

Every module exposes a `Public/` folder containing interfaces and DTOs. Everything else is internal to the module.

### Rule 2: No Circular Dependencies

```
ALLOWED:
  Leave --> CoreHR     (Leave depends on CoreHR for employee data)
  Payroll --> Leave    (Payroll depends on Leave for leave adjustments)

FORBIDDEN:
  CoreHR --> Leave --> CoreHR  (circular!)
```

If two modules need bidirectional communication, use **domain events** for at least one direction.

### Rule 3: Each Module Owns Its Data

```csharp
// ALLOWED:
// Leave module reads/writes to leave_types, leave_requests, etc.
// CoreHR module reads/writes to employees, salary_history, etc.

// FORBIDDEN:
// Leave module directly queries the employees table
// CoreHR module directly queries the leave_requests table
```

If Module A needs data from Module B, it calls Module B's public interface or listens for Module B's domain events. Modules never share database tables.

### Rule 4: Sync for Queries, Domain Events for Side Effects

| Pattern | Use When | Mechanism |
|:--------|:---------|:----------|
| Sync (interface call) | Module A needs data from Module B to continue processing | Call Module B's public service via DI |
| Async (domain event) | Module A did something that other modules should react to | Publish `INotification` via MediatR |

```csharp
// SYNC: Leave module needs employee data to validate a leave request
public class CreateLeaveRequestHandler : IRequestHandler<CreateLeaveRequestCommand, Result<LeaveRequestDto>>
{
    private readonly IEmployeeService _employeeService; // From CoreHR.Public
    
    public async Task<Result<LeaveRequestDto>> Handle(CreateLeaveRequestCommand cmd, CancellationToken ct)
    {
        var employee = await _employeeService.GetByIdAsync(cmd.EmployeeId, ct);
        if (employee is null) return Result<LeaveRequestDto>.Failure("Employee not found");
        // ... validate and create leave request
    }
}

// ASYNC: Leave module publishes event when leave is approved
public class ApproveLeaveRequestHandler : IRequestHandler<ApproveLeaveRequestCommand, Result<Unit>>
{
    private readonly IPublisher _publisher; // MediatR IPublisher
    
    public async Task<Result<Unit>> Handle(ApproveLeaveRequestCommand cmd, CancellationToken ct)
    {
        // ... approve the leave request
        await _publisher.Publish(new LeaveApprovedEvent(leaveRequest.Id, leaveRequest.EmployeeId), ct);
        return Result<Unit>.Success(Unit.Value);
    }
}

// Attendance module reacts to LeaveApproved event
public class MarkLeaveInAttendanceHandler : INotificationHandler<LeaveApprovedEvent>
{
    public async Task Handle(LeaveApprovedEvent notification, CancellationToken ct)
    {
        // Mark leave days in attendance records
    }
}
```

### Rule 5: Shared Kernel is Minimal

`ONEVO.SharedKernel` contains ONLY (see [[shared-kernel]] for full details):

- `BaseEntity` (Id, TenantId, CreatedAt, UpdatedAt, CreatedById)
- `BaseRepository<T>` (tenant-filtered CRUD)
- `ITenantContext` (current tenant from JWT)
- `Result<T>` (success/failure pattern)
- `IEncryptionService` (AES-256 for PII — see [[data-classification]])
- Common enums (`EmploymentType`, `EmploymentStatus`, etc.)
- Common utilities (`DateTimeProvider`, `IdGenerator`)
- Domain event base class (`DomainEvent`) — see [[event-catalog]]
- Pagination types (`PagedRequest`, `PagedResult<T>`)

It does **NOT** contain business logic. If something is specific to 1-2 modules, it belongs in those modules.

## Directory Structure Per Module

```
ONEVO.Modules.{Name}/
├── Public/                           # PUBLIC — other modules import from here
│   ├── I{Name}Service.cs            # Public service interface
│   ├── Dtos/                         # Public DTOs for cross-module communication
│   └── Events/                       # Domain events this module publishes
├── Internal/                         # PRIVATE — only this module
│   ├── Entities/                     # EF Core entities
│   ├── Repositories/                 # Data access
│   ├── Services/                     # Business logic (implements public interfaces)
│   ├── Commands/                     # MediatR commands + handlers
│   ├── Queries/                      # MediatR queries + handlers
│   ├── Validators/                   # FluentValidation validators
│   ├── EventHandlers/                # Handlers for events from OTHER modules
│   ├── Mappings/                     # Entity ↔ DTO mappings
│   └── Configuration/                # EF Core entity configurations
├── Endpoints/                        # API endpoints (Minimal APIs or Controllers)
└── {Name}Module.cs                   # Module registration (IServiceCollection extension)
```

## Enforcement

### ArchUnitNET Tests

```csharp
[Fact]
public void Modules_Should_Not_Access_Other_Modules_Internals()
{
    var rule = Types()
        .That().ResideInNamespace("ONEVO.Modules.*.Internal", true)
        .Should().NotBeAccessibleFromOutsideOfTheirModule();
    
    rule.Check(Architecture);
}

[Fact]
public void No_Module_Should_Have_Circular_Dependencies()
{
    Slices()
        .Matching("ONEVO.Modules.(*)")
        .Should().BeFreeOfCycles()
        .Check(Architecture);
}

[Fact]
public void All_Repositories_Should_Extend_BaseRepository()
{
    var rule = Classes()
        .That().HaveNameEndingWith("Repository")
        .Should().BeAssignableTo(typeof(BaseRepository<>));
    
    rule.Check(Architecture);
}
```

### In Code Reviews

- Reject any PR that uses `using ONEVO.Modules.{Other}.Internal`
- Reject any PR that adds a direct `DbContext.Set<T>()` call for another module's entity
- Reject any PR that introduces a circular dependency
- Reject any PR that adds business logic to SharedKernel
