# CQRS Patterns: ONEVO

**Last Updated:** 2026-04-27

ONEVO uses **MediatR** for in-process CQRS. Every write is a `Command`, every read is a `Query`. Both use the same pipeline but follow different conventions.

---

## Command

A Command changes state. It returns `Result<TResponse>`.

```csharp
// ONEVO.Application/Features/Leave/Commands/ApproveLeaveRequest/
// ApproveLeaveRequestCommand.cs
public record ApproveLeaveRequestCommand(
    Guid LeaveRequestId,
    Guid ApproverId
) : IRequest<Result<LeaveRequestDto>>;

// ApproveLeaveRequestCommandHandler.cs
public class ApproveLeaveRequestCommandHandler
    : IRequestHandler<ApproveLeaveRequestCommand, Result<LeaveRequestDto>>
{
    private readonly IApplicationDbContext _db;
    private readonly IUnitOfWork _uow;

    public ApproveLeaveRequestCommandHandler(IApplicationDbContext db, IUnitOfWork uow)
    {
        _db = db;
        _uow = uow;
    }

    public async Task<Result<LeaveRequestDto>> Handle(
        ApproveLeaveRequestCommand cmd, CancellationToken ct)
    {
        var request = await _db.LeaveRequests
            .FirstOrDefaultAsync(r => r.Id == cmd.LeaveRequestId, ct);

        if (request is null)
            return Result<LeaveRequestDto>.Failure("Leave request not found");

        request.Approve(); // raises LeaveApprovedEvent on the entity

        await _uow.SaveChangesAsync(ct); // interceptor dispatches domain events after save

        return Result<LeaveRequestDto>.Success(request.ToDto());
    }
}
```

---

## Query

A Query reads state. It never modifies data.

```csharp
// ONEVO.Application/Features/Leave/Queries/GetLeaveBalance/
// GetLeaveBalanceQuery.cs
public record GetLeaveBalanceQuery(
    Guid EmployeeId,
    int Year
) : IRequest<Result<LeaveBalanceDto>>;

// GetLeaveBalanceQueryHandler.cs
public class GetLeaveBalanceQueryHandler
    : IRequestHandler<GetLeaveBalanceQuery, Result<LeaveBalanceDto>>
{
    private readonly IApplicationDbContext _db;

    public GetLeaveBalanceQueryHandler(IApplicationDbContext db) => _db = db;

    public async Task<Result<LeaveBalanceDto>> Handle(
        GetLeaveBalanceQuery query, CancellationToken ct)
    {
        var balance = await _db.LeaveEntitlements
            .Where(e => e.EmployeeId == query.EmployeeId && e.Year == query.Year)
            .Select(e => new LeaveBalanceDto { ... })
            .FirstOrDefaultAsync(ct);

        if (balance is null)
            return Result<LeaveBalanceDto>.Failure("No entitlement found");

        return Result<LeaveBalanceDto>.Success(balance);
    }
}
```

---

## DTOs

```
Application/Features/Leave/DTOs/
├── Requests/
│   └── CreateLeaveRequestDto.cs    ← what the HTTP controller receives from the client
└── Responses/
    ├── LeaveRequestDto.cs           ← what handlers return to the controller
    └── LeaveBalanceDto.cs
```

Handlers **never return Domain entities** — always response DTOs.

---

## Validator

Every Command that modifies state has a FluentValidation validator:

```csharp
// ONEVO.Application/Features/Leave/Validators/
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

---

## Pipeline Behaviors (run in order)

```
[1] ValidationBehavior        — FluentValidation. Returns 422 before handler if invalid.
[2] LoggingBehavior           — logs command/query name, UserId, TenantId.
[3] PerformanceBehavior       — logs warning if elapsed > 500ms.
[4] UnhandledExceptionBehavior — catches any unhandled exception, re-throws for middleware.
```

---

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
- `IsSuccess = true` → 200 / 201
- `IsSuccess = false` with `NotFoundException` message → 404
- `IsSuccess = false` with business error → 422

---

## Controller (thin)

```csharp
[ApiController]
[Route("api/v1/leave")]
public class LeaveController : ControllerBase
{
    private readonly ISender _mediator;
    public LeaveController(ISender mediator) => _mediator = mediator;

    [HttpPost("{id}/approve")]
    [RequirePermission("leave:approve")]
    public async Task<IActionResult> Approve(Guid id, ApproveLeaveRequestDto dto, CancellationToken ct)
    {
        var result = await _mediator.Send(
            new ApproveLeaveRequestCommand(id, dto.ApproverId), ct);

        return result.IsSuccess
            ? Ok(result.Value)
            : UnprocessableEntity(result.Error);
    }
}
```
