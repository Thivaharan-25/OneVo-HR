# User Flow Overview

## Purpose

This section documents the step-by-step flows a Developer Platform operator follows inside the OneVo Dev Console (`console.onevo.io`). Each flow is detailed in a sibling file, while module behavior is specified under `developer-platform/modules/*`.

## Login Flow

1. Navigate to `console.onevo.io/login`.
2. Enter email/password.
3. Backend validates the account, password hash, active status, and lockout state.
4. Backend creates a pending MFA challenge; no full platform session exists yet.
5. User completes MFA.
6. Backend resolves effective platform permissions and issues a platform-admin JWT (`iss: onevo-platform-admin`, 30-minute expiry).
7. Redirect to `/`, the Dashboard.

Users not in `platform_users`, users without a valid invite, inactive users, or users who fail MFA are rejected. There is no self-registration. Users are invited through Platform Users by an operator with `platform.accounts.manage`. Optional Google OAuth setup for invited managers still requires MFA before a session is issued.

## Navigation Map

The Developer Platform uses a flat Super Admin sidebar.

| Sidebar Item | Route |
|---|---|
| Dashboard | `/` |
| **Platform Management** _(sidebar group)_ | |
| &nbsp;&nbsp;&nbsp;Tenants | `/platform/tenants` |
| &nbsp;&nbsp;&nbsp;Subscription Plans | `/platform/subscription-plans` |
| &nbsp;&nbsp;&nbsp;Module Catalog | `/platform/module-catalog` |
| &nbsp;&nbsp;&nbsp;Demo Profiles | `/platform/demo-profiles` |
| &nbsp;&nbsp;&nbsp;Templates | `/platform/templates` |
| Requests Center | `/platform/requests` |
| Customer Support | `/platform/support` |
| Platform Users | `/platform/platform-users` |
| Platform Roles | `/platform/platform-roles` |
| Security Center | `/security/security-center` |
| Audit Console | `/security/audit-console` |
| Compliance Center | `/security/compliance` |
| Reports / Analytics | `/reports-analytics` |
| System Config | `/settings/system` |
| Operations | `/operations` |
| App Catalog | `/settings/app-catalog` |

## Access Model

Developer Platform access is permission-based. Built-in roles such as Platform Super Admin, Tenant Operations Manager, Billing Manager, Security Auditor, Module Catalog Manager, and Operations Engineer are presets composed from platform permission codes.

The platform-admin JWT includes account identity and effective platform permissions or a permission version reference. All `/admin/v1/*` endpoints enforce permission checks server-side. Frontend route gates are a convenience only.

| Action | Required Permission |
|---|---|
| Create tenant draft | `platform.tenants.manage` |
| Suspend / reactivate tenant | `platform.tenants.manage` |
| Activate provisioning tenant | `platform.tenants.activate` |
| Impersonate tenant user | `platform.tenants.impersonate` |
| Manage platform accounts | `platform.accounts.manage` |
| Manage platform roles | `platform.roles.manage` |
| Manage subscription plans/gateways | `platform.subscriptions.manage` / `platform.payment_gateways.manage` |
| Manage product module catalog | `platform.module_catalog.manage` |
| Manage demo profiles | `platform.demo_profiles.manage` |
| Approve/reject requests | `platform.requests.manage` |
| Manage support tickets | `platform.support.manage` |
| Manage templates | `platform.templates.manage` |
| Manage tenant runtime overrides | `platform.tenants.feature_overrides.manage` |
| Force-update agent ring | *(Phase 2)* `platform.agent_versions.force_update` |

## Detailed Flows

| File | Covers |
|---|---|
| `dashboard.md` | Dashboard summary and click-through |
| `platform-access.md` | Platform manager invites, roles, permissions, and session revocation |
| `tenant-management.md` | Tenant list, tenant detail, suspend/unsuspend, impersonation, subscription override |
| `provisioning-flow.md` | Two-step tenant creation plus post-creation Manage/Configure flow |
| `subscription-management.md` | Reusable plans, gateway configuration, and tenant commercial assignment |
| `module-catalog.md` | ONEVO product module catalog management |
| `demo-profiles.md` | Demo/trial profile setup, module access, limits, and upgrade options |
| `requests-center.md` | Demo access requests and trial extension requests |
| `customer-support.md` | Support ticket queue, assignment, replies, notes, and closure |
| `configuration-template-management.md` | Template Management - unified library, type filter chips, type-picker-first creation |
| `role-template-management.md` | Template Management - role template creation and tenant role materialization |
| `global-policies.md` | System Config policy defaults: edit, impact preview, and publish |
| `feature-flags.md` | Tenant Detail runtime overrides and feature flag override rules |
| `agent-versions.md` | *(Phase 2)* Version catalog, publish, force-update ring, ring assignment, rollback |
| `platform-health.md` | Platform health overview, service detail, dependencies, safe service actions, and Phase 1 aggregate job/config/security checks |
| `device-management.md` | *(Phase 2)* Device/agent search and approved commands |
| `infrastructure-operations.md` | *(Phase 2)* Infrastructure capacity and dependencies |
| `background-jobs.md` | *(Phase 2)* Background job observability and retry |
| `security-center.md` | Security overview and session review |
| `audit-console.md` | Cross-tenant audit query and export |
| `compliance-center.md` | Compliance exports, legal holds, legal document versions, and acceptance tracking |
| `data-retention.md` | Retention policy setup and sweep behavior |
| `platform-analytics.md` | Cross-tenant analytics |
| `reports.md` | Platform report exports |
| `system-config.md` | System defaults and tenant overrides |
| `app-catalog.md` | Global app catalog and uncatalogued app approval |
| `api-keys.md` | *(Phase 2)* Platform API keys |

