# Task: Auth & Security Module

**Assignee:** Dev 2
**Module:** Auth
**Priority:** Critical
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] (shared kernel, solution structure)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] JWT authentication (RS256) with 15-min access tokens
- [ ] Refresh token rotation (7-day, HttpOnly cookie, chain tracking)
- [ ] RBAC middleware: `[RequirePermission("resource:action")]`
- [ ] **90+ permissions** seeded (resource:action pairs for all 22 modules incl. Workforce Intelligence: workforce:*, exceptions:*, monitoring:*, agent:*, analytics:*, verification:*) — see [[modules/auth/authorization/overview|authorization]]
- [ ] Default roles created: Employee, Manager, HR_Admin, Org_Owner
- [ ] **Device JWT** support for Agent Gateway (`type: "agent"` claim, device_id + tenant_id, no user permissions) — see [[modules/agent-gateway/overview|agent-gateway]]
- [ ] GDPR consent type `monitoring` for employee monitoring opt-in
- [ ] Session management (`sessions` table with device tracking)
- [ ] MFA setup support (TOTP, Email OTP)
- [ ] Audit log interceptor (JSON diffs of old/new values)
- [ ] GDPR consent records (type, version, timestamp)
- [ ] Password hashing with Argon2id
- [ ] Rate limiting on login endpoint (5 attempts/min per IP)
- [ ] Account lockout after 10 failed attempts

### Backend References

- [[modules/auth/authentication/overview|Authentication]] — login, JWT token issuance
- [[modules/auth/authorization/overview|Authorization]] — RBAC, permissions
- [[modules/auth/session-management/overview|Session Management]] — session tracking
- [[modules/auth/mfa/overview|MFA]] — TOTP verification
- [[modules/auth/audit-logging/overview|Audit Logging]] — audit trail
- [[modules/auth/gdpr-consent/overview|GDPR Consent]] — consent records
- [[security/data-classification|Data Classification]] — PII handling
- [[infrastructure/multi-tenancy|Multi Tenancy]] — JWT tenant isolation
- [[backend/shared-kernel|Shared Kernel]] — RequirePermissionAttribute, ICurrentUser

---

## Step 2: Frontend

### Pages to Build

```
app/(auth)/
├── layout.tsx                    # Centered card layout, brand logo
├── login/page.tsx                # Login page
├── forgot-password/page.tsx      # Password reset request
├── reset-password/page.tsx       # Token-based reset
└── mfa/page.tsx                  # MFA verification challenge

app/(dashboard)/admin/
├── users/page.tsx                # User management (invite, disable, sessions)
├── roles/page.tsx                # Role & permission management
├── components/                   # Colocated admin components
│   ├── UserTable.tsx             # User management DataTable
│   └── RolePermissionMatrix.tsx  # Permission grid editor (checkboxes grouped by module)
└── _types.ts                     # Local TypeScript definitions
```

### What to Build

- [ ] Login page: email/password form, "Remember me", SSO button (if configured), tenant branding (logo/colors)
- [ ] MFA challenge page: 6-digit TOTP input, backup code option, countdown timer
- [ ] Password reset flow: request page (email input) + reset page (new password + token)
- [ ] Auth provider (React context): store access token, auto-refresh, redirect on 401
- [ ] Role management page: list roles, create/edit with RolePermissionMatrix (checkboxes grouped by module)
- [ ] User management page: UserTable with invite, view sessions, revoke sessions, disable/enable
- [ ] GDPR consent dialog: shown after login if pending consents, must accept before proceeding
- [ ] User menu dropdown: profile link, security settings, active sessions, logout
- [ ] Colocated components: UserTable, RolePermissionMatrix
- [ ] PermissionGate component implementation (wraps children, checks permissions from JWT)

### Userflows

- [[Userflow/Auth-Access/login-flow|Login Flow]] — full login flow with MFA and SSO variations
- [[Userflow/Auth-Access/password-reset|Password Reset]] — forgot password + reset flow
- [[Userflow/Auth-Access/mfa-setup|Mfa Setup]] — enable/disable MFA
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]] — consent collection after login
- [[Userflow/Auth-Access/role-creation|Role Creation]] — create and configure roles
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] — assign permissions to roles
- [[Userflow/Auth-Access/user-invitation|User Invitation]] — invite new users

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/tenants/resolve?domain={hostname}` | Resolve tenant branding |
| POST | `/api/v1/auth/login` | Login with credentials |
| POST | `/api/v1/auth/mfa/verify` | Verify MFA code |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout (revoke session) |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password with token |
| GET | `/api/v1/auth/sessions` | List user sessions |
| DELETE | `/api/v1/auth/sessions/{id}` | Revoke session |
| GET | `/api/v1/roles` | List roles |
| POST | `/api/v1/roles` | Create role |
| PUT | `/api/v1/roles/{id}` | Update role + permissions |
| GET | `/api/v1/permissions` | List all permissions (grouped) |
| POST | `/api/v1/users/invite` | Invite new user |
| GET | `/api/v1/consent/pending` | Check pending consents |
| POST | `/api/v1/consent` | Submit consent response |

### Frontend References

- [[frontend/architecture/app-structure|Frontend Structure]] — auth route group layout
- [[frontend/design-system/components/component-catalog|Component Catalog]] — Input, Button, Dialog, Switch
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — brand colors for tenant theming
- [[frontend/data-layer/api-integration|API Integration]] — auth token management
- [[frontend/data-layer/state-management|State Management]] — auth state in Zustand

---

## Related Tasks

- [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] — solution setup and shared kernel this depends on
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — device JWT used by Agent Gateway
- [[current-focus/DEV2-core-hr-lifecycle|DEV2 Core Hr Lifecycle]] — onboarding creates user accounts
- All other tasks — all modules use RBAC middleware from this task
