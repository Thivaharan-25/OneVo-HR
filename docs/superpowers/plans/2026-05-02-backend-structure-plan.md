# Backend Folder Structure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold `C:\ONEVO-Backend\ONEVO.sln` as a real buildable .NET 9 solution with 9 projects, correct project references, and all 38 feature folder sets across Domain, Application, and Infrastructure layers.

**Architecture:** Clean Architecture — Domain → Application → Infrastructure → API hosts. No separate module `.csproj` files; modules are feature folders inside each layer project. All 38 features live flat under `Features/` with no WorkManagement parent wrapper.

**Tech Stack:** .NET 9 SDK, `dotnet` CLI, bash

---

## File Map

| Path | What it is |
|:-----|:-----------|
| `C:\ONEVO-Backend\ONEVO.sln` | Solution file wiring all 9 projects |
| `src/ONEVO.Domain/` | Layer 1 — entities, events, value objects |
| `src/ONEVO.Application/` | Layer 2 — CQRS handlers, interfaces, DTOs |
| `src/ONEVO.Infrastructure/` | Layer 3 — EF Core, services, SignalR |
| `src/ONEVO.Api/` | Host — customer-facing `/api/v1/*` |
| `src/ONEVO.Admin.Api/` | Host — developer console `/admin/v1/*` |
| `tests/ONEVO.Tests.Unit/` | xUnit — Application layer tests |
| `tests/ONEVO.Tests.Integration/` | xUnit — Infrastructure/DB tests |
| `tests/ONEVO.Tests.Architecture/` | xUnit — ArchUnitNET layer dependency tests |
| `tools/ONEVO.DbMigrator/` | Console — runs EF migrations |

---

## Task 1: Create solution root and all 9 projects

**Files:**
- Create: `C:\ONEVO-Backend\ONEVO.sln`
- Create: `src/ONEVO.Domain/ONEVO.Domain.csproj`
- Create: `src/ONEVO.Application/ONEVO.Application.csproj`
- Create: `src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj`
- Create: `src/ONEVO.Api/ONEVO.Api.csproj`
- Create: `src/ONEVO.Admin.Api/ONEVO.Admin.Api.csproj`
- Create: `tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj`
- Create: `tests/ONEVO.Tests.Integration/ONEVO.Tests.Integration.csproj`
- Create: `tests/ONEVO.Tests.Architecture/ONEVO.Tests.Architecture.csproj`
- Create: `tools/ONEVO.DbMigrator/ONEVO.DbMigrator.csproj`

- [ ] **Step 1: Create the solution root**

```bash
mkdir -p C:/ONEVO-Backend
cd C:/ONEVO-Backend
dotnet new sln -n ONEVO
```

Expected: `ONEVO.sln` created.

- [ ] **Step 2: Create the four src layer projects**

```bash
dotnet new classlib -n ONEVO.Domain -o src/ONEVO.Domain -f net9.0
dotnet new classlib -n ONEVO.Application -o src/ONEVO.Application -f net9.0
dotnet new classlib -n ONEVO.Infrastructure -o src/ONEVO.Infrastructure -f net9.0
dotnet new webapi -n ONEVO.Api -o src/ONEVO.Api -f net9.0
dotnet new webapi -n ONEVO.Admin.Api -o src/ONEVO.Admin.Api -f net9.0
```

- [ ] **Step 3: Create test and tools projects**

```bash
dotnet new xunit -n ONEVO.Tests.Unit -o tests/ONEVO.Tests.Unit -f net9.0
dotnet new xunit -n ONEVO.Tests.Integration -o tests/ONEVO.Tests.Integration -f net9.0
dotnet new xunit -n ONEVO.Tests.Architecture -o tests/ONEVO.Tests.Architecture -f net9.0
dotnet new console -n ONEVO.DbMigrator -o tools/ONEVO.DbMigrator -f net9.0
```

- [ ] **Step 4: Add all projects to the solution**

```bash
dotnet sln add src/ONEVO.Domain/ONEVO.Domain.csproj
dotnet sln add src/ONEVO.Application/ONEVO.Application.csproj
dotnet sln add src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj
dotnet sln add src/ONEVO.Api/ONEVO.Api.csproj
dotnet sln add src/ONEVO.Admin.Api/ONEVO.Admin.Api.csproj
dotnet sln add tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj
dotnet sln add tests/ONEVO.Tests.Integration/ONEVO.Tests.Integration.csproj
dotnet sln add tests/ONEVO.Tests.Architecture/ONEVO.Tests.Architecture.csproj
dotnet sln add tools/ONEVO.DbMigrator/ONEVO.DbMigrator.csproj
```

- [ ] **Step 5: Wire all project references**

```bash
# Application → Domain
dotnet add src/ONEVO.Application/ONEVO.Application.csproj reference src/ONEVO.Domain/ONEVO.Domain.csproj

# Infrastructure → Application
dotnet add src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj reference src/ONEVO.Application/ONEVO.Application.csproj

# API hosts → Infrastructure + Application
dotnet add src/ONEVO.Api/ONEVO.Api.csproj reference src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj
dotnet add src/ONEVO.Api/ONEVO.Api.csproj reference src/ONEVO.Application/ONEVO.Application.csproj
dotnet add src/ONEVO.Admin.Api/ONEVO.Admin.Api.csproj reference src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj
dotnet add src/ONEVO.Admin.Api/ONEVO.Admin.Api.csproj reference src/ONEVO.Application/ONEVO.Application.csproj

# Test projects
dotnet add tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj reference src/ONEVO.Application/ONEVO.Application.csproj
dotnet add tests/ONEVO.Tests.Integration/ONEVO.Tests.Integration.csproj reference src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj
dotnet add tests/ONEVO.Tests.Architecture/ONEVO.Tests.Architecture.csproj reference src/ONEVO.Domain/ONEVO.Domain.csproj
dotnet add tests/ONEVO.Tests.Architecture/ONEVO.Tests.Architecture.csproj reference src/ONEVO.Application/ONEVO.Application.csproj
dotnet add tests/ONEVO.Tests.Architecture/ONEVO.Tests.Architecture.csproj reference src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj

# DbMigrator → Infrastructure
dotnet add tools/ONEVO.DbMigrator/ONEVO.DbMigrator.csproj reference src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj
```

- [ ] **Step 6: Remove auto-generated placeholder files**

```bash
rm -f src/ONEVO.Domain/Class1.cs
rm -f src/ONEVO.Application/Class1.cs
rm -f src/ONEVO.Infrastructure/Class1.cs
```

- [ ] **Step 7: Verify solution builds clean**

```bash
dotnet build
```

Expected output ends with: `Build succeeded.`

- [ ] **Step 8: Add .gitignore and commit**

```bash
dotnet new gitignore
git init
git add .
git commit -m "chore: scaffold ONEVO.sln — 9 projects wired with correct references"
```

---

## Task 2: Domain layer — Common + 38 feature folders

**Files:**
- Create: `src/ONEVO.Domain/Common/` (BaseEntity, IDomainEvent, ValueObject)
- Create: `src/ONEVO.Domain/Enums/`
- Create: `src/ONEVO.Domain/Errors/`
- Create: `src/ONEVO.Domain/ValueObjects/`
- Create: `src/ONEVO.Domain/Features/{Feature}/Entities/` × 38 + MicrosoftTeams
- Create: `src/ONEVO.Domain/Features/{Feature}/Events/` × 38 + MicrosoftTeams

- [ ] **Step 1: Create Domain Common directories**

```bash
cd C:/ONEVO-Backend
mkdir -p src/ONEVO.Domain/Common
mkdir -p src/ONEVO.Domain/Enums
mkdir -p src/ONEVO.Domain/Errors
mkdir -p src/ONEVO.Domain/ValueObjects
```

- [ ] **Step 2: Create all 38 feature folders in Domain**

```bash
FEATURES=(
  Auth InfrastructureModule OrgStructure CoreHR Leave Payroll Performance Skills Documents
  WorkforcePresence ActivityMonitoring DiscrepancyEngine IdentityVerification ExceptionEngine ProductivityAnalytics
  WMFoundation Projects Tasks Planning OKR Time Resources Chat ChatAI Collaboration WorkSyncAnalytics WorkSyncIntegrations
  SharedPlatform Notifications Configuration Calendar ReportingEngine Grievance Expense AgentGateway DevPlatform IDEExtension
)

for f in "${FEATURES[@]}"; do
  mkdir -p "src/ONEVO.Domain/Features/$f/Entities"
  mkdir -p "src/ONEVO.Domain/Features/$f/Events"
done

# Integrations/MicrosoftTeams is nested
mkdir -p "src/ONEVO.Domain/Features/Integrations/MicrosoftTeams/Entities"
mkdir -p "src/ONEVO.Domain/Features/Integrations/MicrosoftTeams/Events"
```

- [ ] **Step 3: Verify build still passes**

```bash
dotnet build
```

Expected: `Build succeeded.`

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "chore: add Domain layer — Common + 38 feature folders"
```

---

## Task 3: Application layer — Common + 38 feature folders

**Files:**
- Create: `src/ONEVO.Application/Common/Behaviors/`
- Create: `src/ONEVO.Application/Common/Interfaces/`
- Create: `src/ONEVO.Application/Common/Models/`
- Create: `src/ONEVO.Application/Features/{Feature}/{Commands,Queries,DTOs/Requests,DTOs/Responses,Validators,EventHandlers}/` × 38 + MicrosoftTeams

- [ ] **Step 1: Create Application Common directories**

```bash
cd C:/ONEVO-Backend
mkdir -p src/ONEVO.Application/Common/Behaviors
mkdir -p src/ONEVO.Application/Common/Interfaces
mkdir -p src/ONEVO.Application/Common/Models
```

- [ ] **Step 2: Create all 38 feature folders in Application**

```bash
FEATURES=(
  Auth InfrastructureModule OrgStructure CoreHR Leave Payroll Performance Skills Documents
  WorkforcePresence ActivityMonitoring DiscrepancyEngine IdentityVerification ExceptionEngine ProductivityAnalytics
  WMFoundation Projects Tasks Planning OKR Time Resources Chat ChatAI Collaboration WorkSyncAnalytics WorkSyncIntegrations
  SharedPlatform Notifications Configuration Calendar ReportingEngine Grievance Expense AgentGateway DevPlatform IDEExtension
)

for f in "${FEATURES[@]}"; do
  mkdir -p "src/ONEVO.Application/Features/$f/Commands"
  mkdir -p "src/ONEVO.Application/Features/$f/Queries"
  mkdir -p "src/ONEVO.Application/Features/$f/DTOs/Requests"
  mkdir -p "src/ONEVO.Application/Features/$f/DTOs/Responses"
  mkdir -p "src/ONEVO.Application/Features/$f/Validators"
  mkdir -p "src/ONEVO.Application/Features/$f/EventHandlers"
done

mkdir -p "src/ONEVO.Application/Features/Integrations/MicrosoftTeams/Commands"
mkdir -p "src/ONEVO.Application/Features/Integrations/MicrosoftTeams/Queries"
mkdir -p "src/ONEVO.Application/Features/Integrations/MicrosoftTeams/DTOs/Requests"
mkdir -p "src/ONEVO.Application/Features/Integrations/MicrosoftTeams/DTOs/Responses"
mkdir -p "src/ONEVO.Application/Features/Integrations/MicrosoftTeams/Validators"
mkdir -p "src/ONEVO.Application/Features/Integrations/MicrosoftTeams/EventHandlers"
```

- [ ] **Step 3: Verify build still passes**

```bash
dotnet build
```

Expected: `Build succeeded.`

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "chore: add Application layer — Common + 38 feature folders"
```

---

## Task 4: Infrastructure layer — Persistence + Services

**Files:**
- Create: `src/ONEVO.Infrastructure/Persistence/Configurations/{Feature}/` × 38 + MicrosoftTeams
- Create: `src/ONEVO.Infrastructure/Persistence/Interceptors/`
- Create: `src/ONEVO.Infrastructure/Persistence/Migrations/`
- Create: `src/ONEVO.Infrastructure/Email/`
- Create: `src/ONEVO.Infrastructure/Storage/`
- Create: `src/ONEVO.Infrastructure/Security/`
- Create: `src/ONEVO.Infrastructure/RealTime/`

- [ ] **Step 1: Create Persistence directories**

```bash
cd C:/ONEVO-Backend
mkdir -p src/ONEVO.Infrastructure/Persistence/Migrations
mkdir -p src/ONEVO.Infrastructure/Persistence/Interceptors
```

- [ ] **Step 2: Create EF Configuration folders for all 38 features**

```bash
FEATURES=(
  Auth InfrastructureModule OrgStructure CoreHR Leave Payroll Performance Skills Documents
  WorkforcePresence ActivityMonitoring DiscrepancyEngine IdentityVerification ExceptionEngine ProductivityAnalytics
  WMFoundation Projects Tasks Planning OKR Time Resources Chat ChatAI Collaboration WorkSyncAnalytics WorkSyncIntegrations
  SharedPlatform Notifications Configuration Calendar ReportingEngine Grievance Expense AgentGateway DevPlatform IDEExtension
)

for f in "${FEATURES[@]}"; do
  mkdir -p "src/ONEVO.Infrastructure/Persistence/Configurations/$f"
done

mkdir -p "src/ONEVO.Infrastructure/Persistence/Configurations/Integrations/MicrosoftTeams"
```

- [ ] **Step 3: Create Services directories**

```bash
mkdir -p src/ONEVO.Infrastructure/Email
mkdir -p src/ONEVO.Infrastructure/Storage
mkdir -p src/ONEVO.Infrastructure/Security
mkdir -p src/ONEVO.Infrastructure/RealTime
```

- [ ] **Step 4: Verify build still passes**

```bash
dotnet build
```

Expected: `Build succeeded.`

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "chore: add Infrastructure layer — Persistence configs + Services structure"
```

---

## Task 5: API host structures

**Files:**
- Create: `src/ONEVO.Api/Controllers/`
- Create: `src/ONEVO.Api/Hubs/`
- Create: `src/ONEVO.Api/Middleware/`
- Create: `src/ONEVO.Admin.Api/Controllers/`
- Create: `src/ONEVO.Admin.Api/Middleware/`

- [ ] **Step 1: Create ONEVO.Api directories**

```bash
cd C:/ONEVO-Backend
mkdir -p src/ONEVO.Api/Controllers
mkdir -p src/ONEVO.Api/Hubs
mkdir -p src/ONEVO.Api/Middleware
```

- [ ] **Step 2: Create ONEVO.Admin.Api directories**

```bash
mkdir -p src/ONEVO.Admin.Api/Controllers
mkdir -p src/ONEVO.Admin.Api/Middleware
```

- [ ] **Step 3: Final full build verification**

```bash
dotnet build
```

Expected: `Build succeeded.  0 Warning(s)  0 Error(s)`

- [ ] **Step 4: Final commit**

```bash
git add .
git commit -m "chore: add API host folder structures — Controllers, Hubs, Middleware"
```

---

## Quick Reference — Feature List (38 + MicrosoftTeams)

| Pillar | Features |
|:-------|:---------|
| HR | Auth, InfrastructureModule, OrgStructure, CoreHR, Leave, Payroll, Performance, Skills, Documents |
| WFI | WorkforcePresence, ActivityMonitoring, DiscrepancyEngine, IdentityVerification, ExceptionEngine, ProductivityAnalytics |
| WorkSync | WMFoundation, Projects, Tasks, Planning, OKR, Time, Resources, Chat, ChatAI, Collaboration, WorkSyncAnalytics, WorkSyncIntegrations |
| Foundation | SharedPlatform, Notifications, Configuration, Calendar, ReportingEngine, Grievance, Expense, AgentGateway, DevPlatform, IDEExtension |
| Nested | Integrations/MicrosoftTeams |
