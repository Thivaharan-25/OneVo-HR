# WebApi Layer Guide

Two host projects. Both are composition roots only — no business logic.

## ONEVO.Api (customer-facing)

**Base URL:** `/api/v1/`
**JWT issuer expected:** `onevo-customer`

### Controller pattern (all controllers are thin)

```csharp
[ApiController]
[Route("api/v1/[controller]")]
public class LeaveController : ControllerBase
{
    private readonly ISender _mediator;
    public LeaveController(ISender mediator) => _mediator = mediator;

    [HttpPost]
    [RequirePermission("leave:create")]
    public async Task<IActionResult> Create(
        [FromBody] CreateLeaveRequestDto dto, CancellationToken ct)
    {
        var result = await _mediator.Send(
            new CreateLeaveRequestCommand(dto.EmployeeId, dto.LeaveTypeId,
                dto.StartDate, dto.EndDate), ct);

        return result.IsSuccess
            ? CreatedAtAction(nameof(GetById), new { id = result.Value!.Id }, result.Value)
            : UnprocessableEntity(result.Error);
    }
}
```

### Middleware pipeline order (Program.cs)

```csharp
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseMiddleware<TenantResolutionMiddleware>();
app.UseMiddleware<PermissionMiddleware>();
app.UseAuthorization();
app.UseMiddleware<ExceptionHandlerMiddleware>(); // RFC 7807 — last
app.MapControllers();
app.MapHubs(); // SignalR
```

### Program.cs service registration

```csharp
builder.Services.AddApplication();           // MediatR + behaviors
builder.Services.AddInfrastructure(config);  // EF, JWT, BCrypt, Redis…
builder.Services.AddSignalR();
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(opts => { /* see security.md */ });
```

## ONEVO.Admin.Api (developer console)

**Base URL:** `/admin/v1/`
**JWT issuer expected:** `onevo-platform-admin`
**Same DI pattern** — calls `AddApplication()` + `AddInfrastructure(config)`

DevPlatform entities have no `TenantId` — `PlatformAdminAuthMiddleware` validates admin JWT before any endpoint runs.
