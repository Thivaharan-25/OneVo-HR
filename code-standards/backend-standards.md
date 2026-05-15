# Coding Standards: ONEVO (.NET 9 / C# 13 current)

**Last Updated:** 2026-05-13

.NET 10 / C# 14 is a future migration target. These standards follow the current `net9.0` backend projects until the migration is completed.

## General Principles

- Readability over cleverness.
- Follow [[backend/folder-structure|Folder Structure]] and [[backend/module-boundaries|Module Boundaries]].
- Use `Result<T>` for expected business outcomes.
- Use `async/await` with `CancellationToken` on async paths.
- Validate command input with FluentValidation.

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Namespaces | `PascalCase` | `ONEVO.Application.Features.CoreHR` |
| Classes/Records | `PascalCase` | `CreateEmployeeCommand` |
| Interfaces | `IPascalCase` | `IEmployeeRepository` |
| Methods | `PascalCase` + `Async` suffix | `GetEmployeeByIdAsync()` |
| Properties | `PascalCase` | `FirstName` |
| Private fields | `_camelCase` | `_employeeRepository` |
| Local variables | `camelCase` | `employeeId` |
| DTOs | `{Entity}{Purpose}Dto` | `EmployeeListDto` |
| Commands | `{Action}{Entity}Command` | `CreateEmployeeCommand` |
| Queries | `Get{Entity}Query` or `List{Entities}Query` | `GetEmployeeByIdQuery` |
| Validators | `{UseCase}Validator` | `CreateEmployeeValidator` |
| Handlers | `{UseCase}Handler` | `CreateEmployeeHandler` |
| Optional events | `{Entity}{Action}Event` | `EmployeeTerminatedEvent` |

## Feature File Organization

```text
ONEVO.Application/Features/{Feature}/
|-- Commands/
|   `-- {UseCase}/
|       |-- {UseCase}Command.cs
|       |-- {UseCase}Handler.cs
|       `-- {UseCase}Validator.cs
|-- Queries/
|   `-- {UseCase}/
|       |-- {UseCase}Query.cs
|       `-- {UseCase}Handler.cs
|-- DTOs/
|   |-- Requests/
|   `-- Responses/
`-- Interfaces/
```

Command validators are colocated with the command. Do not create feature-level `Validators/` folders.

Optional only when justified:

```text
ONEVO.Domain/Features/{Feature}/Events/
ONEVO.Application/Features/{Feature}/EventHandlers/
```

## Command Pattern

```csharp
public record CreateEmployeeCommand(
    string FirstName,
    string LastName,
    string Email,
    Guid DepartmentId,
    EmploymentType EmploymentType,
    DateOnly HireDate
) : IRequest<Result<EmployeeDto>>;

public class CreateEmployeeHandler
    : IRequestHandler<CreateEmployeeCommand, Result<EmployeeDto>>
{
    private readonly IEmployeeRepository _employees;
    private readonly IUnitOfWork _unitOfWork;

    public async Task<Result<EmployeeDto>> Handle(CreateEmployeeCommand command, CancellationToken ct)
    {
        var employee = Employee.Create(
            command.FirstName,
            command.LastName,
            command.Email,
            command.DepartmentId,
            command.EmploymentType,
            command.HireDate);

        await _employees.AddAsync(employee, ct);
        await _unitOfWork.SaveChangesAsync(ct);

        return Result<EmployeeDto>.Success(employee.ToDto());
    }
}
```

Do not add a domain event unless the use case needs a decoupled post-save side effect.

## Error Handling

```csharp
public async Task<Result<LeaveRequestDto>> ApproveLeaveRequest(
    ApproveLeaveRequestCommand command,
    CancellationToken ct)
{
    var request = await _leaveRequests.GetByIdAsync(command.LeaveRequestId, ct);

    if (request is null)
        return Result<LeaveRequestDto>.Failure("Leave request not found");

    if (!request.CanBeApproved)
        return Result<LeaveRequestDto>.Failure("Only pending requests can be approved");

    request.Approve(command.ApproverId);

    await _unitOfWork.SaveChangesAsync(ct);

    return Result<LeaveRequestDto>.Success(request.ToDto());
}
```

## Database

- EF Core snake_case convention handles database naming.
- Use `Guid` for primary keys.
- Use `DateTimeOffset` for timestamps and `DateOnly` for dates.
- Encrypt sensitive fields through `IEncryptionService`.
- Do not bypass repositories/readers from handlers.

## Do Not

- Do not use synchronous I/O.
- Do not throw exceptions for expected business failures.
- Do not inject `ApplicationDbContext` into handlers.
- Do not introduce `IApplicationDbContext`.
- Do not create `Events/` or `EventHandlers/` as default folders.
- Do not log PII.
- Do not hardcode secrets.

## Related

- [[backend/folder-structure|Folder Structure]]
- [[backend/cqrs-patterns|CQRS Patterns]]
- [[backend/module-boundaries|Module Boundaries]]
- [[backend/domain-events|Domain Events]]
- [[code-standards/git-workflow|Git Workflow]]
- [[code-standards/logging-standards|Logging Standards]]
