# CQRS Patterns: ONEVO

**Last Updated:** 2026-05-08

ONEVO uses **MediatR** for in-process CQRS. Every write is a `Command`, every read is a `Query`. Commands and queries use the same pipeline behaviors, but they follow different conventions.

CQRS does not require domain events. The default use-case shape is command/query, validator, handler, repository/domain, unit of work, response. Events are optional and should be added only for justified post-save side effects.

## Application Feature Structure

```text
ONEVO.Application/Features/{Feature}/{SubFeature}/
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
|-- RepositoryInterfaces/
|   `-- I{SubFeature}Repository.cs
|-- ServiceInterfaces/
|   `-- I{SubFeature}Service.cs
|-- Mappings/                   # optional — manual entity→DTO mapping; only when non-trivial
|   `-- {SubFeature}Mappings.cs
|-- Helpers/                    # optional — SubFeature-scoped utility logic with no DI deps
|   `-- {SubFeature}Helper.cs
`-- EventHandlers/              # optional — only when a justified domain event exists
```

No feature-level `Validators/` folder. A validator belongs beside the command it validates.

## Command

A Command changes state. It returns `Result<TResponse>`.

```csharp
// ONEVO.Application/Features/Leave/Request/Commands/ApproveLeaveRequest/
public record ApproveLeaveRequestCommand(
    Guid LeaveRequestId,
    Guid ApproverId
) : IRequest<Result<LeaveRequestDto>>;

public class ApproveLeaveRequestHandler
    : IRequestHandler<ApproveLeaveRequestCommand, Result<LeaveRequestDto>>
{
    private readonly ILeaveRequestRepository _leaveRequests;
    private readonly IUnitOfWork _uow;

    public ApproveLeaveRequestHandler(ILeaveRequestRepository leaveRequests, IUnitOfWork uow)
    {
        _leaveRequests = leaveRequests;
        _uow = uow;
    }

    public async Task<Result<LeaveRequestDto>> Handle(
        ApproveLeaveRequestCommand command,
        CancellationToken ct)
    {
        var request = await _leaveRequests.GetByIdAsync(command.LeaveRequestId, ct);

        if (request is null)
            return Result<LeaveRequestDto>.Failure("Leave request not found");

        request.Approve(command.ApproverId);

        await _uow.SaveChangesAsync(ct);

        return Result<LeaveRequestDto>.Success(request.ToDto());
    }
}
```

The command handler owns the use case. It may call domain methods, repositories, readers, services, and `IUnitOfWork`. It does not use EF Core or `ApplicationDbContext` directly.

## Command Validator

Every command that modifies state has a FluentValidation validator colocated with the command.

```csharp
// ONEVO.Application/Features/Leave/Request/Commands/ApproveLeaveRequest/
public class ApproveLeaveRequestValidator
    : AbstractValidator<ApproveLeaveRequestCommand>
{
    public ApproveLeaveRequestValidator()
    {
        RuleFor(x => x.LeaveRequestId).NotEmpty();
        RuleFor(x => x.ApproverId).NotEmpty();
    }
}
```

`ValidationBehavior` runs before every handler. If validation fails, the handler never executes.

## Query

A Query reads state. It never modifies data.

```csharp
// ONEVO.Application/Features/Leave/Request/Queries/GetLeaveBalance/
public record GetLeaveBalanceQuery(
    Guid EmployeeId,
    int Year
) : IRequest<Result<LeaveBalanceDto>>;

public class GetLeaveBalanceHandler
    : IRequestHandler<GetLeaveBalanceQuery, Result<LeaveBalanceDto>>
{
    private readonly ILeaveBalanceReader _leaveBalances;

    public GetLeaveBalanceHandler(ILeaveBalanceReader leaveBalances)
        => _leaveBalances = leaveBalances;

    public async Task<Result<LeaveBalanceDto>> Handle(
        GetLeaveBalanceQuery query,
        CancellationToken ct)
    {
        var balance = await _leaveBalances.GetBalanceAsync(query.EmployeeId, query.Year, ct);

        if (balance is null)
            return Result<LeaveBalanceDto>.Failure("No entitlement found");

        return Result<LeaveBalanceDto>.Success(balance);
    }
}
```

Queries use repository or reader interfaces that return DTOs/read models. Queries do not mutate entities and do not call `SaveChangesAsync`.

## DTOs

```text
Application/Features/Leave/Request/DTOs/
|-- Requests/
|   `-- CreateLeaveRequestDto.cs
`-- Responses/
    |-- LeaveRequestDto.cs
    `-- LeaveBalanceDto.cs
```

Handlers never return Domain entities. They return response DTOs or read models wrapped in `Result<T>`.

## Optional Domain Events

Use domain events only when a saved business action needs decoupled side effects that should not be hardcoded into the originating command handler.

Good uses:

- Employee termination should trigger access cleanup, notifications, and workspace revocation.
- A verified identity result should trigger downstream onboarding steps.
- A monitoring anomaly should trigger notification enrichment after the anomaly is persisted.

Poor uses:

- Creating an event for every CRUD operation.
- Moving simple command logic into event handlers.
- Using events because "CQRS needs them". It does not.

If an event is justified, place it in `ONEVO.Domain/Features/{Feature}/{SubFeature}/Events/` and place handlers in `ONEVO.Application/Features/{Feature}/{SubFeature}/EventHandlers/`.

## Pipeline Behaviors

```text
[1] ValidationBehavior
[2] LoggingBehavior
[3] PerformanceBehavior
[4] UnhandledExceptionBehavior
```

## Result<T>

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

Controllers map `Result<T>` to HTTP responses:

- `IsSuccess = true` -> 200 / 201
- `IsSuccess = false` with not-found failure -> 404
- `IsSuccess = false` with validation or business failure -> 422

## Controller

Controllers stay thin. They map HTTP input to commands/queries and map `Result<T>` back to HTTP.

```csharp
[ApiController]
[Route("api/v1/leave")]
public class LeaveController : ControllerBase
{
    private readonly ISender _mediator;

    public LeaveController(ISender mediator) => _mediator = mediator;

    [HttpPost("{id}/approve")]
    [RequirePermission("leave:approve")]
    public async Task<IActionResult> Approve(
        Guid id,
        ApproveLeaveRequestDto dto,
        CancellationToken ct)
    {
        var result = await _mediator.Send(
            new ApproveLeaveRequestCommand(id, dto.ApproverId),
            ct);

        return result.IsSuccess
            ? Ok(result.Value)
            : UnprocessableEntity(result.Error);
    }
}
```
