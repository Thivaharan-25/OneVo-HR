# Company Connections - End-to-End Logic

**Module:** Shared Platform  
**Feature:** Company Connections

---

## Create Eligible Connection From Developer Platform

```text
GET /admin/v1/company-connections/eligible?ownerEmail=owner@example.com
  -> Normalize email
  -> Find active/provisioning/pending_confirmation/pending_payment tenants with verified owner email
  -> Return eligible tenant pairs and existing connection state

POST /admin/v1/tenants/{tenantId}/company-connections
  -> Validate platform-admin permission
  -> Validate target tenant exists
  -> Check no active duplicate connection exists
  -> If verified owner emails match:
       create pending or active connection according to operator confirmation rule
     Else:
       create pending connection requiring both-owner approval or operator approval
  -> Audit request with source tenant, target tenant, actor, owner email snapshot, and reason
```

## Tenant Owner Request

```text
POST /api/v1/company-connections/request
  -> Validate caller is tenant owner or has company-connections:manage
  -> Validate target company identifier
  -> Create pending connection request
  -> Notify target tenant owner or platform operator
  -> Audit request
```

Tenant-facing requests may be disabled in Phase 1 if all connection creation remains Developer Platform-only.

## Approval

```text
PATCH /admin/v1/company-connections/{connectionId}/approve
  -> Validate platform-admin or required owner approval
  -> Load pending connection
  -> Verify both tenants are eligible for connection
  -> Set status = active
  -> Record approved_at and approved_by
  -> Audit approval
  -> Notify both tenant owners
```

Owner email matching can shorten eligibility review, but it must not expose data before approval.

## Reject Or Revoke

```text
PATCH /admin/v1/company-connections/{connectionId}/reject
  -> Validate actor
  -> Set status = rejected
  -> Audit rejection reason

PATCH /admin/v1/company-connections/{connectionId}/revoke
  -> Validate actor
  -> Set status = revoked
  -> Disable active access grants tied to connection
  -> Block new workflow routing through connection
  -> Preserve historical audit and completed case evidence
```

## Grant Scoped Cross-Company Access

```text
POST /api/v1/company-connections/{id}/access-grants
  -> Validate caller has company-connections:manage in source tenant
  -> Verify connection is active
  -> Validate target tenant is part of connection
  -> Validate permission key and module entitlement
  -> Persist grant scope:
       connected_tenant_ids
       resource_types
       actions
       allowed_data_categories
       assignee user/role
       expiry
  -> Audit grant
```

## Cross-Company Employee Transfer

```text
POST /api/v1/employees/{id}/cross-company-transfer
  -> Validate employee belongs to source tenant
  -> Validate target tenant is actively connected
  -> Validate caller has cross-company:employees:transfer
  -> Start Workflow Engine transfer case
  -> Route source approval and target acceptance
  -> Share only approved transfer evidence with target tenant
  -> On approval:
       source tenant keeps historical employment record
       target tenant creates or activates its own employee record
       documents/payroll/activity data remain source-local unless explicitly shared
  -> Audit all actions with both tenant IDs
```

## Cross-Company Data View

```text
GET /api/v1/cross-company/views/{viewKey}
  -> Validate user session in current tenant
  -> Resolve active grants for viewKey
  -> Verify connected tenants and allowed data categories
  -> Query controlled projections only
  -> Return normalized read-only view
  -> Audit view or export event according to sensitivity
```

## Failure Rules

| Scenario | Result |
|:---|:---|
| No active connection | 403 cross-company connection required |
| Owner email matches but no approval | 403 connection not active |
| Revoked connection | 403 connection revoked |
| Missing scope for target tenant | 403 target company not in grant |
| Sensitive data not granted | Field omitted or 403 for that view |
| Target module not entitled | 422 module not available for target tenant |

## Related

- [[modules/shared-platform/company-connections/overview|Company Connections]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]

