# WEEK1: Auth & Security Module

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 2
**Sprint:** Week 1 (Apr 7-11)
**Module:** Auth

## Description

Implement JWT authentication, RBAC authorization with 80+ permissions, session management, MFA support, audit logging, and GDPR consent tracking.

## Acceptance Criteria

- [ ] JWT authentication (RS256) with 15-min access tokens
- [ ] Refresh token rotation (7-day, HttpOnly cookie, chain tracking)
- [ ] RBAC middleware: `[RequirePermission("resource:action")]`
- [ ] **90+ permissions** seeded (resource:action pairs for all 22 modules incl. Workforce Intelligence: workforce:*, exceptions:*, monitoring:*, agent:*, analytics:*, verification:*) — see [[auth]]
- [ ] Default roles created: Employee, Manager, HR_Admin, Org_Owner
- [ ] **Device JWT** support for Agent Gateway (`type: "agent"` claim, device_id + tenant_id, no user permissions) — see [[agent-gateway]]
- [ ] GDPR consent type `monitoring` for employee monitoring opt-in
- [ ] Session management (user_sessions with device tracking)
- [ ] MFA setup support (TOTP, Email OTP)
- [ ] Audit log interceptor (JSON diffs of old/new values)
- [ ] GDPR consent records (type, version, timestamp)
- [ ] Password hashing with Argon2id
- [ ] Rate limiting on login endpoint (5 attempts/min per IP)
- [ ] Account lockout after 10 failed attempts

## Related

- [[auth-architecture]] — full auth design
- [[data-classification]] — PII handling
- [[module-catalog]] — Auth module details
- [[compliance]] — GDPR consent requirements
- [[multi-tenancy]] — JWT tenant isolation
- [[shared-kernel]] — RequirePermissionAttribute, ICurrentUser
- [[WEEK1-infrastructure-setup]] — solution setup and shared kernel this depends on
- [[WEEK1-shared-platform]] — device JWT used by Agent Gateway (built same week)
