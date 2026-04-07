# WEEK1: Infrastructure & Foundation Setup

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 1
**Sprint:** Week 1 (Apr 7-11)
**Module:** Infrastructure + SharedKernel

## Description

Set up the foundational .NET 9 solution structure, shared kernel, tenant provisioning, user management, and file storage service.

## Acceptance Criteria

- [ ] Solution structure created with all **22 module projects** per [[module-catalog]]
- [ ] SharedKernel implemented: BaseEntity, BaseRepository, ITenantContext, Result<T>, IEncryptionService
- [ ] PostgreSQL with EF Core configured (snake_case convention, RLS policies)
- [ ] Redis connection configured
- [ ] Tenant CRUD + provisioning flow (signup → seed → activate) **with `industry_profile` selection**
- [ ] Industry profile sets default monitoring toggles in `monitoring_feature_toggles` — see [[configuration]]
- [ ] User CRUD with password hashing (Argon2id)
- [ ] File upload service (local disk for dev, configurable for production)
- [ ] Country reference data seeded (LK, GB, etc.)
- [ ] Docker Compose for local development (PostgreSQL + Redis)
- [ ] Swagger/OpenAPI documentation working
- [ ] Health check endpoints

## Related

- [[tech-stack]] — full tech stack
- [[shared-kernel]] — SharedKernel structure
- [[multi-tenancy]] — tenant isolation
- [[migration-patterns]] — EF Core migrations
- [[environment-parity]] — Docker Compose setup
- [[backend-standards]] — naming conventions
- [[module-catalog]] — 22-module solution structure
- [[configuration]] — industry profile seeding for monitoring toggles
- [[WEEK1-auth-security]] — builds on top of shared kernel (same week)
- [[WEEK1-org-structure]] — depends on shared kernel (same week)
- [[WEEK1-shared-platform]] — depends on shared kernel (same week)

## AI Instructions

When generating code for this task:
1. Create the solution structure per [[module-catalog]]
2. Follow naming conventions in [[backend-standards]]
3. Ensure all entities inherit from BaseEntity
4. Include tenant_id on all tenant-scoped entities
5. Use UUID v7 for primary keys
