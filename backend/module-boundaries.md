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

| Pattern               | Use When                                                  | Mechanism                             |
| :-------------------- | :-------------------------------------------------------- | :------------------------------------ |
| Sync (interface call) | Module A needs data from Module B to continue processing  | Call Module B's public service via DI |
| Async — integration event (cross-module) | Module A did something that OTHER modules should react to | Publish via `IEventBus.PublishAsync()` → RabbitMQ via MassTransit |
| Async — domain event (intra-module)      | Module A did something that THIS module should react to internally | Publish `INotification` via MediatR |

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

// ASYNC (cross-module integration event): Leave module publishes via IEventBus → RabbitMQ
public class ApproveLeaveRequestHandler : IRequestHandler<ApproveLeaveRequestCommand, Result<Unit>>
{
    private readonly IEventBus _eventBus; // Wraps MassTransit outbox publish

    public async Task<Result<Unit>> Handle(ApproveLeaveRequestCommand cmd, CancellationToken ct)
    {
        // ... approve the leave request
        await _eventBus.PublishAsync(new LeaveApproved(leaveRequest.Id, leaveRequest.EmployeeId), ct);
        // Written to leave_outbox_events; forwarded to RabbitMQ by OutboxProcessor
        return Result<Unit>.Success(Unit.Value);
    }
}

// WorkforcePresence module consumes via MassTransit IConsumer<T>
public class MarkLeaveInPresenceConsumer : IConsumer<LeaveApproved>
{
    public async Task Consume(ConsumeContext<LeaveApproved> context)
    {
        // Mark leave days in workforce presence records
        // Idempotency guaranteed by MassTransit inbox-state (processed_integration_events)
    }
}
```

### Rule 5: Shared Kernel is Minimal

`ONEVO.SharedKernel` contains ONLY (see [[backend/shared-kernel|Shared Kernel]] for full details):

- `BaseEntity` (Id, TenantId, CreatedAt, UpdatedAt, CreatedById)
- `BaseRepository<T>` (tenant-filtered CRUD)
- `ITenantContext` (current tenant from JWT)
- `Result<T>` (success/failure pattern)
- `IEncryptionService` (AES-256 for PII — see [[security/data-classification|Data Classification]])
- Common enums (`EmploymentType`, `EmploymentStatus`, etc.)
- Common utilities (`DateTimeProvider`, `IdGenerator`)
- Domain event base class (`DomainEvent`) — see [[backend/messaging/event-catalog|Event Catalog]]
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

## Module Independence Framework

Every optional module follows this three-level contract:

1. **STANDALONE** — Works with only Mandatory Core (Infrastructure + Auth + CoreHR identity). No optional module should hard-depend on another optional module.
2. **INTEGRATION** — Registers event handlers for other modules' events when both are active for the tenant.
3. **GRACEFUL DEGRADATION** — If a paired module is disabled, this module still works. The integration handler simply doesn't register.

**Example — Leave module:**

```
Standalone:  Leave requests work without Payroll, without WMS, without WorkforcePresence
+ Payroll:   LeaveApproved → PayrollAdjustment handler activates
+ WMS:       LeaveApproved → WMS capacity warning handler activates
+ WorkforcePresence: LeaveApproved → shift marked absent
Missing any: Leave still processes correctly, that integration just skips
```

### Integration Activation Rule

A handler is registered **only if** both modules are enabled for the tenant:

```csharp
// In Leave module registration — MassTransit consumers registered conditionally
if (moduleRegistry.IsEnabled(tenantId, ModuleNames.Payroll))
{
    cfg.ReceiveEndpoint("payroll-leave-events", e =>
    {
        e.Consumer<PayrollAdjustmentOnLeaveApprovedConsumer>(context);
    });
}

if (moduleRegistry.IsEnabled(tenantId, ModuleNames.WorkforcePresence))
{
    cfg.ReceiveEndpoint("workforce-presence-leave-events", e =>
    {
        e.Consumer<MarkShiftAbsentOnLeaveApprovedConsumer>(context);
    });
}
```

`ModuleRegistry.IsEnabled(tenantId, module)` is checked at startup per tenant and cached in Redis. Changing a tenant's module configuration clears the cache and re-evaluates on next request.

## Integration Registry

Auto-enabled integrations when both modules are active for a tenant. Each row is: Module A publishes domain event → Integration handler in Module B reacts → Module B updates state.

| Module A | + Module B | Auto-enabled integration |
|----------|------------|--------------------------|
| Leave | WorkforcePresence | Approved leave marks shift as absent |
| Leave | WMS (via bridge) | Leave approved → WMS capacity warning webhook |
| Leave | Payroll | Approved unpaid leave → payroll deduction entry |
| WorkforcePresence | ActivityMonitoring | Presence session correlates agent snapshots |
| WorkforcePresence | WMS (time logs) | Overtime engine: presence + WMS task logs → `overtime_entry` |
| ActivityMonitoring | ExceptionEngine | Agent snapshots → anomaly rule evaluation |
| WMS (time logs) | Payroll | Overtime entries from WMS data → payroll line item |
| WMS (productivity) | Performance | Monthly WMS scores → appraisal composite input |
| WMS (productivity) | Payroll | Approved `bonus_grant` → payroll bonus line item |
| CoreHR | WMS (via bridge) | EmployeeCreated/Terminated → WMS access provision/revoke webhook |
| Skills | WMS (resource) | ONEVO validated skills → WMS resource matching (Skills bridge) |

> **WMS integrations** are implemented as bridge webhooks, not in-process MediatR handlers. When ONEVO fires a domain event (e.g. `LeaveApprovedEvent`) and WMS is enabled for the tenant, a bridge handler calls the WMS webhook endpoint with the relevant payload.
