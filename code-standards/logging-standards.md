# Logging Standards: ONEVO

## Stack

- **Library:** Serilog 3.x
- **Sinks:** Console (dev), Seq (dev), OpenTelemetry (staging/prod)
- **Enrichers:** Correlation ID, Tenant ID, User ID, Machine Name

## Log Levels

| Level | When to Use | Example |
|:------|:-----------|:--------|
| `Debug` | Development-only details | `"Querying employees for tenant {TenantId} with filter {Filter}"` |
| `Information` | Business events worth recording | `"Employee {EmployeeId} created in department {DepartmentId}"` |
| `Warning` | Recoverable issues, degraded service | `"Retry attempt {Attempt} for payroll provider {ProviderId}"` |
| `Error` | Failures that need attention | `"Failed to process payroll run {RunId}: {ErrorMessage}"` |
| `Fatal` | Application cannot continue | `"Database connection lost. Shutting down."` |

## Structured Logging Format

```csharp
// GOOD: Structured properties (searchable, filterable)
_logger.LogInformation("Employee {EmployeeId} hired in department {DepartmentId} for tenant {TenantId}",
    employee.Id, employee.DepartmentId, employee.TenantId);

// BAD: String interpolation (not searchable)
_logger.LogInformation($"Employee {employee.Id} hired in department {employee.DepartmentId}");

// BAD: Logging PII
_logger.LogInformation("User {Email} logged in from {IpAddress}", user.Email, ipAddress); // PII!
```

## PII Scrubbing

Serilog destructuring policies automatically scrub sensitive data:

```csharp
// Configuration in Program.cs
.Destructure.ByTransforming<Employee>(e => new 
{ 
    e.Id, e.TenantId, e.DepartmentId, e.EmploymentStatus,
    Name = "***REDACTED***" // Never log names
})
.Enrich.With(new RegexScrubber(new[]
{
    (@"[\w.-]+@[\w.-]+\.\w+", "***@***.***"),              // Email
    (@"eyJ[\w-]+\.eyJ[\w-]+\.[\w-]+", "***JWT***"),         // JWT tokens
    (@"\b\d{9,18}\b", "***ACCOUNT***"),                      // Bank account numbers
    (@"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "***PHONE***"),      // Phone numbers
    (@"\b\d{2}[- ]?\d{7}[- ]?\d\b", "***NI***"),            // NI numbers
}))
```

## Correlation ID

Every request gets a correlation ID that propagates through the entire stack:

```csharp
// Middleware sets it from header or generates new one
app.Use(async (context, next) =>
{
    var correlationId = context.Request.Headers["X-Correlation-Id"].FirstOrDefault() 
        ?? Guid.NewGuid().ToString();
    
    context.Items["CorrelationId"] = correlationId;
    context.Response.Headers["X-Correlation-Id"] = correlationId;
    
    using (LogContext.PushProperty("CorrelationId", correlationId))
    using (LogContext.PushProperty("TenantId", tenantContext.TenantId))
    using (LogContext.PushProperty("UserId", currentUser.UserId))
    {
        await next();
    }
});
```

## What to Log

| Event | Level | Properties |
|:------|:------|:-----------|
| API request received | Debug | Method, Path, CorrelationId |
| Business operation completed | Information | EntityId, TenantId, Operation |
| External API call | Information | Provider, Endpoint, StatusCode, Duration |
| Validation failure | Warning | EntityType, Errors (no PII) |
| Retry attempt | Warning | Provider, Attempt, MaxRetries |
| Unhandled exception | Error | ExceptionType, Message, StackTrace |
| Database query slow (>1s) | Warning | Query, Duration, TenantId |

## What NOT to Log

- Email addresses, phone numbers, names
- Bank account details, SSO credentials
- JWT tokens, API keys, passwords
- Full request/response bodies containing PII
- Stack traces in production (unless Error/Fatal level)

## Related

- [[infrastructure/observability|Observability]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[AI_CONTEXT/rules|Rules]]
