# Company Connections

**Module:** Shared Platform  
**Feature:** Company Connections

---

## Purpose

Company Connections links separate ONEVO companies so approved cross-company flows can run without weakening tenant isolation.

In ONEVO, a company is a tenant. Each company has its own users, employees, subscription, modules, settings, branding, audit logs, and data boundary. A company connection is an explicit tenant-to-tenant relationship that allows selected cross-company views, transfers, workflow routing, automations, and collaboration.

The connection does not merge tenants. It only creates an approved relationship that other modules may use after checking permissions and scope.

## Core Rules

1. Every company is provisioned as a separate tenant.
2. A connected company is another tenant linked through an active company connection.
3. Owner email matching makes a connection eligible; it does not silently grant access.
4. Cross-company access requires an active connection, a permission, a scope, and audit logging.
5. Raw tenant data remains tenant-local unless a module exposes a controlled projection or workflow evidence package.
6. Revoking a connection blocks new cross-company access and invalidates active grants tied to the connection.

## Connection Types

| Type | Meaning |
|:---|:---|
| `same_owner` | Companies controlled by the same verified owner email |
| `group_company` | Companies in the same group, holding, or parent structure |
| `partner` | Operational partner relationship |
| `vendor` | Vendor/supplier relationship |
| `client` | Client/customer relationship |
| `custom` | Operator-defined relationship with a required note |

## Connection Statuses

| Status | Meaning |
|:---|:---|
| `pending` | Requested but not active |
| `active` | Approved and usable by scoped cross-company features |
| `rejected` | Request denied |
| `revoked` | Previously active connection was removed |

## Owner Email Matching

The Developer Platform may mark two tenants as eligible for connection when both tenants have a verified owner user with the same normalized email address.

Matching owner email is not enough to expose data. The connection must still be explicitly confirmed by an authorized ONEVO operator or by the required tenant owner approval flow. If owner emails do not match, both tenant owners or an authorized ONEVO operator must approve the connection.

## Permission Model

A user can act across connected companies only when all checks pass:

- the source and target tenants have an active company connection,
- the user has the required cross-company permission,
- the grant scope includes the target connected tenant,
- the grant scope includes the resource type and action,
- any sensitive data category is explicitly allowed,
- the relevant module is entitled for the tenant that owns the action.

Suggested permission keys:

| Permission | Purpose |
|:---|:---|
| `company-connections:read` | View connected companies and connection state |
| `company-connections:manage` | Request, approve, revoke, or manage connection grants |
| `cross-company:employees:read` | View approved employee projections from connected companies |
| `cross-company:employees:transfer` | Start or approve cross-company employee transfer |
| `cross-company:reports:view` | View approved cross-company reports and dashboards |
| `cross-company:workflows:manage` | Create or manage automations that reference connected companies |

Grant scopes should record selected connected tenant IDs, resource types, actions, allowed data fields or categories, expiry where applicable, and the user or role receiving the grant.

## Cross-Company Workflows

The Workflow Engine may use company connections for:

- cross-company employee transfer,
- shared approval chains,
- group-level reporting review,
- vendor/client task escalation,
- cross-company exception routing,
- target-company onboarding tasks after transfer approval.

Workflow instances that cross companies must store requester tenant, source tenant, target tenant, subject tenant, actor tenant, connection ID, and data-sharing scope.

## Cross-Company Data Views

Cross-company views are controlled projections. They are not direct access to another tenant's tables.

The system should distinguish:

- tenant-local source-of-truth records,
- read-only shared projections,
- copied or imported records,
- workflow evidence attached to a specific case.

Sensitive data such as payroll, identity verification evidence, activity screenshots, disciplinary documents, and private files requires separate data-category grants.

## Audit And Revocation

Every connection request, approval, rejection, revocation, grant creation, grant revocation, workflow action, data view, and export must be audit logged with both tenant IDs and the actor identity.

Revocation should:

- block new cross-company reads and actions,
- disable grants tied to the connection,
- prevent new workflow routing through that connection,
- preserve historical audit records and completed workflow evidence.

## Related

- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[developer-platform/userflow/tenant-management|Developer Platform Tenant Management]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Auth-Access/permissions-reference|Permissions Reference]]
