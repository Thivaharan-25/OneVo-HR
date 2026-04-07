# Monitoring: ONEVO

## Grafana Dashboards

### Application Dashboard
- Request rate by endpoint
- Error rate (4xx, 5xx)
- Response time percentiles (p50, p95, p99)
- Active users (from presence_sessions)
- Background job queue depths

### Database Dashboard
- Active connections / pool utilization
- Query execution time (slow queries > 1s)
- Rows read/written per second
- Table sizes and index usage
- Replication lag

### Business Dashboard
- Payroll runs status (by tenant)
- Leave requests pending (SLA tracking)
- Active tenants / subscription plan distribution
- Employee count growth

## Alerting Rules

| Alert | Condition | Severity | Action |
|:------|:---------|:---------|:-------|
| High Error Rate | 5xx > 5% for 5 min | Critical | Page on-call |
| Slow API | p99 > 5s for 10 min | Warning | Investigate |
| DB Connection Exhaustion | Pool > 80% for 5 min | Critical | Scale PgBouncer |
| Payroll Run Failed | payroll_run.status = 'failed' | Critical | Notify finance team |
| Certificate Expiry | TLS cert < 14 days | Warning | Renew cert |
| Disk Usage | > 80% | Warning | Clean up / scale |

## Health Checks

```csharp
// Registered in Program.cs
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "postgresql")
    .AddRedis(redisConnectionString, name: "redis")
    .AddCheck<HangfireHealthCheck>("hangfire");

// Endpoints
app.MapHealthChecks("/health");         // Kubernetes liveness
app.MapHealthChecks("/health/ready");   // Kubernetes readiness
```

## Related

- [[observability]]
- [[logging-standards]]
- [[exception-engine]]
- [[alert-generation]]
