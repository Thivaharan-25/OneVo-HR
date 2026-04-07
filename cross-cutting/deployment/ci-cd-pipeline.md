# CI/CD Pipeline: ONEVO

## Pipeline Overview

```
Push to PR → Build → Unit Tests → Architecture Tests → Integration Tests → Code Coverage Check
                                                                                    ↓
                                                              Merge to main → Build Docker Image → Deploy to Staging
                                                                                    ↓
                                                              Manual approval → Deploy to Production (Blue/Green)
```

## GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: onevo_test
          POSTGRES_USER: onevo
          POSTGRES_PASSWORD: test_password
        ports: ['5432:5432']
      redis:
        image: redis:7
        ports: ['6379:6379']
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'
      
      - name: Restore
        run: dotnet restore
      
      - name: Build
        run: dotnet build --no-restore --configuration Release
      
      - name: Unit Tests
        run: dotnet test tests/ONEVO.Tests.Unit --no-build -c Release
      
      - name: Architecture Tests
        run: dotnet test tests/ONEVO.Tests.Architecture --no-build -c Release
      
      - name: Integration Tests
        run: dotnet test tests/ONEVO.Tests.Integration --no-build -c Release
        env:
          ConnectionStrings__DefaultConnection: "Host=localhost;Database=onevo_test;Username=onevo;Password=test_password"
          ConnectionStrings__Redis: "localhost:6379"
      
      - name: Code Coverage
        run: dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage
      
      - name: Check Coverage Threshold
        run: |
          # Fail if coverage < 80%
          coverage=$(cat coverage/*/coverage.cobertura.xml | grep -oP 'line-rate="\K[^"]+')
          if (( $(echo "$coverage < 0.80" | bc -l) )); then
            echo "Coverage $coverage is below 80% threshold"
            exit 1
          fi

  deploy-staging:
    needs: build-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway (Staging)
        run: railway up --environment staging

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval
    steps:
      - name: Deploy to Railway (Production)
        run: railway up --environment production
```

## Deployment Strategy

### Blue/Green with Canary

```
1. Deploy new version to "green" environment (5% traffic)
2. Monitor error rates, latency for 15 minutes
3. If healthy: ramp to 25% → 50% → 100%
4. If unhealthy: route 100% back to "blue" (instant rollback)
```

### Rollback Procedure

| Level | Scenario | Action | Time |
|:------|:---------|:-------|:-----|
| Level 1 | App bug, no schema changes | Revert to previous Railway deployment | < 2 min |
| Level 2 | App bug + additive schema change | Revert app (new columns are ignored) | < 2 min |
| Level 3 | Destructive schema change failed | Point-in-time recovery from backup | < 15 min |

## Zero-Downtime Migrations

All schema changes follow expand-contract pattern (see [[migration-patterns]]):

```
Deploy 1: Add new columns/tables (expand) → app ignores them
Deploy 2: App starts using new schema + backfills data
Deploy 3: Remove old columns/tables (contract)
```

## Related

- [[environment-parity]]
- [[git-workflow]]
