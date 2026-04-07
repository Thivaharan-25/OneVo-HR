# Observability: ONEVO

## Distributed Tracing (OpenTelemetry)

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddEntityFrameworkCoreInstrumentation()
        .AddSource("ONEVO.*")
        .AddOtlpExporter());
```

Every request generates a trace with spans for:
- HTTP request handling
- EF Core database queries
- External HTTP calls (Stripe, Resend, etc.)
- MediatR command/query handling
- Background job execution

## Correlation ID

Propagated from frontend through entire backend:

```
Frontend → X-Correlation-Id header → TenantMiddleware → Serilog LogContext → EF Core → External calls
```

All logs, traces, and error responses include the correlation ID for end-to-end debugging.

## Structured Logging (Serilog)

Log output format:
```json
{
  "Timestamp": "2026-04-05T10:00:00.000Z",
  "Level": "Information",
  "MessageTemplate": "Employee {EmployeeId} created in department {DepartmentId}",
  "Properties": {
    "EmployeeId": "uuid",
    "DepartmentId": "uuid",
    "TenantId": "uuid",
    "CorrelationId": "abc-123",
    "UserId": "uuid",
    "SourceContext": "ONEVO.Modules.CoreHR.Internal.Services.EmployeeService"
  }
}
```

See [[logging-standards]] for full logging rules and PII scrubbing.

## Related

- [[monitoring]]
- [[logging-standards]]
- [[ci-cd-pipeline]]
