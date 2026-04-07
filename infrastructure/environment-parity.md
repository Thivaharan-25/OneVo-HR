# Environment Parity: ONEVO

## Docker Compose (Local Development)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: onevo_dev
      POSTGRES_USER: onevo
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-rls.sql:/docker-entrypoint-initdb.d/01-rls.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@onevo.dev
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"

volumes:
  postgres_data:
```

## Environment Comparison

| Setting | Local | Staging | Production |
|:--------|:------|:--------|:-----------|
| PostgreSQL | Docker (localhost:5432) | Railway managed | Railway managed + PgBouncer |
| Redis | Docker (localhost:6379) | Railway managed | Railway managed |
| JWT signing | Development RSA keys | Staging keys | Production keys (rotated) |
| Email | Console logger (no actual send) | Resend (sandbox) | Resend (production) |
| Stripe | Test mode | Test mode | Live mode |
| File storage | Local disk (./uploads) | Railway volume | S3-compatible |
| RLS | Enabled | Enabled | Enabled |
| Rate limiting | Disabled | Relaxed | Full enforcement |
| Observability | Console + Seq | OpenTelemetry → Grafana | OpenTelemetry → Grafana |
| HTTPS | HTTP (localhost) | HTTPS (Railway) | HTTPS (Cloudflare → Railway) |

## Local Setup

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Apply migrations
dotnet ef database update --project src/ONEVO.Api

# 3. Seed data
dotnet run --project tools/ONEVO.DbMigrator -- --seed

# 4. Run API
dotnet run --project src/ONEVO.Api

# API available at https://localhost:5001
# Swagger at https://localhost:5001/swagger
```

## Related

- [[ci-cd-pipeline]] — build and deploy pipeline
- [[multi-tenancy]] — RLS setup in Docker
- [[migration-patterns]] — running migrations locally
- [[tech-stack]] — all infrastructure components

## Seed Data (Development)

Using Bogus library for realistic fake data:

```csharp
// Seeds a demo tenant with:
// - 1 tenant (Acme Corp)
// - 5 users (admin, hr_admin, manager, employee x2)
// - 3 departments (Engineering, HR, Marketing)
// - 10 employees with full profiles
// - Sample leave types, policies, entitlements
// - Sample shifts and schedules
```

## Related

- [[ci-cd-pipeline]]
- [[multi-tenancy]]
