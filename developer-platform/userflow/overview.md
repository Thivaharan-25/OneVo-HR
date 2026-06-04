# User Flow Overview

## Purpose

This section documents the step-by-step flows a Developer Platform operator follows inside the OneVo Dev Console (`console.onevo.io`). Each flow is detailed in a sibling file, while module behavior is specified under `developer-platform/modules/*`.

## Login Flow

1. Navigate to `console.onevo.io/login`.
2. Click Sign in with Google.
3. Google returns an ID token; backend validates it against `dev_platform_accounts`.
4. Backend checks `is_active = true` and resolves effective platform permissions.
5. Backend issues a platform-admin JWT (`iss: onevo-platform-admin`, 30-minute expiry).
6. Redirect to `/`, the Dashboard.

Accounts not in `dev_platform_accounts`, accounts without a valid invite, or accounts with `is_active = false` are rejected. There is no self-registration. Accounts are invited through Platform Access by an operator with `platform.accounts.manage`.

## Navigation Map

The Developer Platform uses a sidebar icon rail plus a side panel for sections that have child modules. Dashboard has no side panel.

| Rail Area | Has Panel | Child Routes |
|---|---:|---|
| Dashboard | No | `/` |
| Platform Management | Yes | `/platform/tenants`, `/platform/subscriptions`, `/platform/platform-users`, `/platform/platform-roles`, `/platform/global-policies`, `/platform/module-catalog`, `/platform/templates`, `/platform/feature-flags` |
| System Operations | Yes | `/operations/platform-health`, `/operations/services`; device, infrastructure, background-job, and agent-version flows are Phase 2 |
| Security & Compliance | Yes | `/security/security-center`, `/security/audit-logs`, `/security/compliance`, `/security/data-retention` |
| Analytics & Reports | Yes | `/analytics/platform`, `/analytics/reports` |
| Settings | Yes | `/settings/system`, `/settings/app-catalog`, `/settings/api-keys` *(Phase 2)* |

## Access Model

Developer Platform access is permission-based. Built-in roles such as Platform Super Admin, Tenant Operations Manager, Billing Manager, Security Auditor, Module Catalog Manager, and Operations Engineer are presets composed from `dev_platform_permissions`.

The platform-admin JWT includes account identity and effective platform permissions or a permission version reference. All `/admin/v1/*` endpoints enforce permission checks server-side. Frontend route gates are a convenience only.

| Action | Required Permission |
|---|---|
| Create tenant draft | `platform.tenants.create` |
| Suspend / unsuspend tenant | `platform.tenants.suspend` |
| Activate provisioning tenant | `platform.tenants.activate` |
| Impersonate tenant user | `platform.tenants.impersonate` |
| Manage platform accounts | `platform.accounts.manage` |
| Manage platform roles | `platform.roles.manage` |
| Manage subscription plans/gateways | `platform.subscriptions.manage` / `platform.payment_gateways.manage` |
| Manage product module catalog | `platform.module_catalog.manage` |
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
| `role-template-management.md` | Global role templates and tenant role materialization |
| `global-policies.md` | Global policy edit, impact preview, and publish |
| `feature-flags.md` | Global flag list, toggle global default, per-tenant override |
| `agent-versions.md` | *(Phase 2)* Version catalog, publish, force-update ring, ring assignment, rollback |
| `platform-health.md` | Platform health overview |
| `services-monitor.md` | Service detail and safe service actions |
| `device-management.md` | *(Phase 2)* Device/agent search and approved commands |
| `infrastructure-operations.md` | *(Phase 2)* Infrastructure capacity and dependencies |
| `background-jobs.md` | *(Phase 2)* Background job observability and retry |
| `security-center.md` | Security overview and session review |
| `audit-console.md` | Cross-tenant audit query and export |
| `compliance-center.md` | Compliance exports and legal holds |
| `data-retention.md` | Retention policy setup and sweep behavior |
| `platform-analytics.md` | Cross-tenant analytics |
| `reports.md` | Platform report exports |
| `system-config.md` | System defaults and tenant overrides |
| `app-catalog.md` | Global app catalog and uncatalogued app approval |
| `api-keys.md` | *(Phase 2)* Platform API keys |

