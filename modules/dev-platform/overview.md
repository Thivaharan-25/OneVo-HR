# Dev Platform Feature

**Last Updated:** 2026-04-27

The `DevPlatform` feature provides the developer console backend. In Phase 1 it is served by `/admin/v1/*` inside the single `ONEVO.Api` backend deployment. `ONEVO.Admin.Api` is deprecated scaffold only and must not be deployed as a second backend unit.

## Key entities

| Entity | Tables | Notes |
|--------|--------|-------|
| `DevPlatformAccount` | 1 | Platform admin accounts — no TenantId |
| `DevPlatformSession` | 1 | Admin JWT session tracking — no TenantId |
| `AgentVersionRelease` | 1 | Agent binary releases |
| `AgentDeploymentRing` | 1 | Canary / Beta / Stable rings |
| `AgentDeploymentRingAssignment` | 1 | Tenant-to-ring assignment |

**Total: 5 tables (Phase 1)**

## Important

DevPlatform entities have **no TenantId**. They are platform-level, not tenant-level. The global tenant query filter in `ApplicationDbContext` is excluded for these entities.

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/DevPlatform/Entities/
  ONEVO.Domain/Features/DevPlatform/Events/

Application (CQRS):
  ONEVO.Application/Features/DevPlatform/Commands/
  ONEVO.Application/Features/DevPlatform/Queries/
  ONEVO.Application/Features/DevPlatform/DTOs/Requests/
  ONEVO.Application/Features/DevPlatform/DTOs/Responses/
  ONEVO.Application/Features/DevPlatform/Validators/
  ONEVO.Application/Features/DevPlatform/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/DevPlatform/

API endpoints:
  ONEVO.Api/Controllers/Admin/              ← Admin API namespace, not customer API

## Related

- [[developer-platform/overview|Developer Platform Overview]]
- [[developer-platform/auth|Authentication]]
- [[backend/folder-structure|Folder Structure]]
