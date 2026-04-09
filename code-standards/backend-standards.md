# Coding Standards: ONEVO (.NET 9 / C#)

## 1. General Principles

- **Readability over cleverness** — code is read far more than written
- **Consistency** — follow existing patterns in the codebase (see [[backend/module-boundaries|Module Boundaries]])
- **Explicit over implicit** — prefer `Result<T>` (see [[backend/shared-kernel|Shared Kernel]]) over exceptions, `async/await` over callbacks
- **Fail fast** — validate inputs at the boundary, use `FluentValidation`

## 2. Naming Conventions

| Element | Convention | Example |
|:--------|:-----------|:--------|
| Namespaces | `PascalCase` | `ONEVO.Modules.CoreHR.Internal.Services` |
| Classes/Records | `PascalCase` | `EmployeeService`, `CreateEmployeeCommand` |
| Interfaces | `IPascalCase` | `IEmployeeRepository` |
| Methods | `PascalCase` + Async suffix | `GetEmployeeByIdAsync()` |
| Properties | `PascalCase` | `FirstName`, `TenantId` |
| Private fields | `_camelCase` | `_employeeRepository` |
| Local variables | `camelCase` | `employeeId`, `leaveRequest` |
| Constants | `PascalCase` | `MaxPageSize`, `DefaultCurrency` |
| Enums | `PascalCase` (singular) | `EmploymentType.FullTime` |
| DTOs | `{Entity}{Action}Dto` | `EmployeeListDto`, `CreateEmployeeDto` |
| Commands | `{Action}{Entity}Command` | `CreateEmployeeCommand`, `ApproveLeaveRequestCommand` |
| Queries | `Get{Entity}Query` | `GetEmployeeByIdQuery`, `GetEmployeesQuery` |
| Validators | `{Command}Validator` | `CreateEmployeeCommandValidator` |
| Handlers | `{Command/Query}Handler` | `CreateEmployeeCommandHandler` |
| Events | `{Entity}{Action}Event` | `EmployeeHiredEvent`, `LeaveApprovedEvent` |

## 3. File Organization Per Module

```
ONEVO.Modules.{Name}/
├── Public/                     # Exported interfaces + DTOs
│   ├── I{Name}Service.cs
│   ├── Dtos/
│   │   ├── {Entity}Dto.cs
│   │   ├── {Entity}ListDto.cs
│   │   ├── Create{Entity}Dto.cs
│   │   └── Update{Entity}Dto.cs
│   └── Events/
│       └── {Entity}{Action}Event.cs
├── Internal/
│   ├── Entities/
│   │   └── {Entity}.cs          # EF Core entity
│   ├── Configuration/
│   │   └── {Entity}Configuration.cs  # EF Core Fluent API config
│   ├── Repositories/
│   │   ├── I{Entity}Repository.cs
│   │   └── {Entity}Repository.cs
│   ├── Services/
│   │   └── {Name}Service.cs     # Implements I{Name}Service
│   ├── Commands/
│   │   ├── Create{Entity}/
│   │   │   ├── Create{Entity}Command.cs
│   │   │   ├── Create{Entity}CommandHandler.cs
│   │   │   └── Create{Entity}CommandValidator.cs
│   │   └── Update{Entity}/
│   │       └── ...
│   ├── Queries/
│   │   ├── Get{Entity}ById/
│   │   │   ├── Get{Entity}ByIdQuery.cs
│   │   │   └── Get{Entity}ByIdQueryHandler.cs
│   │   └── Get{Entities}/
│   │       └── ...
│   ├── EventHandlers/           # Handles events from OTHER modules
│   │   └── Handle{Event}.cs
│   └── Mappings/
│       └── {Entity}Mappings.cs  # Entity ↔ DTO mapping
├── Endpoints/
│   └── {Entity}Endpoints.cs     # Minimal API endpoint definitions
└── {Name}Module.cs              # DI registration
```

## 4. Code Patterns

### Entity Definition

```csharp
public class Employee : BaseEntity
{
    public Guid UserId { get; set; }
    public Guid DepartmentId { get; set; }
    public Guid? ManagerId { get; set; }
    public string EmployeeNo { get; set; } = string.Empty;
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public EmploymentType EmploymentType { get; set; }
    public EmploymentStatus EmploymentStatus { get; set; }
    public DateOnly HireDate { get; set; }
    
    // Navigation properties
    public Department Department { get; set; } = null!;
    public Employee? Manager { get; set; }
    public ICollection<Employee> DirectReports { get; set; } = new List<Employee>();
}
```

### Command + Handler (MediatR)

```csharp
public record CreateEmployeeCommand(
    string FirstName,
    string LastName,
    string Email,
    Guid DepartmentId,
    Guid JobFamilyId,
    EmploymentType EmploymentType,
    DateOnly HireDate
) : IRequest<Result<EmployeeDto>>;

public class CreateEmployeeCommandHandler : IRequestHandler<CreateEmployeeCommand, Result<EmployeeDto>>
{
    private readonly IEmployeeRepository _repository;
    private readonly ITenantContext _tenantContext;
    private readonly IUnitOfWork _unitOfWork;

    public async Task<Result<EmployeeDto>> Handle(CreateEmployeeCommand cmd, CancellationToken ct)
    {
        var employee = new Employee
        {
            TenantId = _tenantContext.TenantId,
            FirstName = cmd.FirstName,
            LastName = cmd.LastName,
            DepartmentId = cmd.DepartmentId,
            EmploymentType = cmd.EmploymentType,
            HireDate = cmd.HireDate,
            EmploymentStatus = EmploymentStatus.Active
        };
        
        employee.AddDomainEvent(new EmployeeHiredEvent(employee.Id, employee.TenantId, employee.DepartmentId));
        
        await _repository.AddAsync(employee, ct);
        await _unitOfWork.SaveChangesAsync(ct);
        
        return Result<EmployeeDto>.Success(employee.ToDto());
    }
}
```

### Minimal API Endpoints

```csharp
public static class EmployeeEndpoints
{
    public static void MapEmployeeEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v1/employees").RequireAuthorization();
        
        group.MapGet("/", GetEmployees).RequirePermission("employees:read");
        group.MapGet("/{id:guid}", GetEmployeeById).RequirePermission("employees:read");
        group.MapPost("/", CreateEmployee).RequirePermission("employees:write");
        group.MapPut("/{id:guid}", UpdateEmployee).RequirePermission("employees:write");
        group.MapDelete("/{id:guid}", DeleteEmployee).RequirePermission("employees:delete");
    }
    
    private static async Task<IResult> GetEmployees(
        [AsParameters] PagedRequest request,
        ISender sender,
        CancellationToken ct)
    {
        var result = await sender.Send(new GetEmployeesQuery(request), ct);
        return result.IsSuccess ? Results.Ok(result.Value) : Results.Problem(result.Error!.ToProblemDetails());
    }
}
```

## 5. Error Handling

```csharp
// Use Result<T> for business logic — never throw exceptions for expected cases
public async Task<Result<LeaveRequestDto>> ApproveLeaveRequest(Guid requestId, CancellationToken ct)
{
    var request = await _repository.GetByIdAsync(requestId, ct);
    if (request is null)
        return Result<LeaveRequestDto>.Failure("Leave request not found");
    
    if (request.Status != ApprovalStatus.Pending)
        return Result<LeaveRequestDto>.Failure("Only pending requests can be approved");
    
    request.Status = ApprovalStatus.Approved;
    request.AddDomainEvent(new LeaveApprovedEvent(request.Id, request.EmployeeId));
    
    await _unitOfWork.SaveChangesAsync(ct);
    return Result<LeaveRequestDto>.Success(request.ToDto());
}

// Exceptions are for truly exceptional cases (infrastructure failures)
// Global exception handler converts them to RFC 7807 Problem Details
```

## 6. Code Formatting

- **Indentation:** 4 spaces (C# standard)
- **Braces:** Allman style (new line) — follows .NET convention
- **Line length:** 120 characters max
- **Usings:** Implicit usings enabled, file-scoped namespaces
- **Nullable:** Nullable reference types enabled project-wide
- **EditorConfig:** Enforce via `.editorconfig` in solution root

## Related

- [[AI_CONTEXT/rules|Rules]] — AI agent code generation rules
- [[backend/module-boundaries|Module Boundaries]] — module structure and boundary enforcement
- [[backend/shared-kernel|Shared Kernel]] — base classes and utilities
- [[code-standards/git-workflow|Git Workflow]] — commit message format and branching
- [[code-standards/logging-standards|Logging Standards]] — Serilog patterns

## 7. Git Commit Messages

```
type(scope): subject

Types: feat, fix, refactor, test, docs, chore, perf
Scope: module name (core-hr, leave, attendance, auth, etc.)

Examples:
feat(core-hr): add employee CRUD endpoints
fix(leave): correct entitlement calculation for part-time employees
refactor(auth): extract permission checking to middleware
test(attendance): add integration tests for biometric webhook
docs(architecture): update module dependency map
chore(ci): add code coverage threshold check
perf(payroll): optimize payroll run query with batch processing
```

## Related

- [[AI_CONTEXT/rules|Rules]]
- [[backend/shared-kernel|Shared Kernel]]
- [[backend/module-boundaries|Module Boundaries]]
