# WebApi Layer Guide

One active host project. `ONEVO.Api` is the composition root for both customer APIs and Developer Console admin APIs; no business logic lives in host code.

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

### Controller folder structure

```
Controllers/
|-- Admin/                          # Developer Console admin controllers
`-- {Feature}/
    `-- {SubFeature}/               # Customer-facing controllers
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
builder.Services.AddInfrastructure(config);  // EF, JWT, BCrypt, IMemoryCache; Redis only if future distributed cache is enabled
builder.Services.AddSignalR();
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(opts => { /* see security.md */ });
```

## ONEVO.Api (developer console)

**Base URL:** `/admin/v1/`
**JWT issuer expected:** `onevo-platform-admin`
**Controller location:** `ONEVO.Api/Controllers/Admin/`
**Same DI pattern** — uses the same `AddApplication()` + `AddInfrastructure(config)` registrations as `/api/v1/*`

DevPlatform entities have no `TenantId`. Admin controllers are protected with `[Authorize(Policy = "PlatformAdmin")]`, backed by the `AdminBearer` platform-admin JWT scheme.
