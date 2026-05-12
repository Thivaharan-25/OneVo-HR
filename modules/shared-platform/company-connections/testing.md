# Company Connections - Testing

**Module:** Shared Platform  
**Feature:** Company Connections

---

## Unit Tests

| Scenario | Expected |
|:---|:---|
| Verified owner emails match | Connection is eligible but no data access is granted |
| Owner emails differ | Connection requires both-owner approval or operator approval |
| Duplicate active connection | Request is rejected with conflict |
| Revoked connection | New grants and workflow routing are blocked |
| Scope excludes target tenant | Cross-company read/action is denied |
| Scope excludes data category | Sensitive fields are omitted or denied |

## Integration Tests

| Scenario | Expected |
|:---|:---|
| Developer Platform creates connection | Audit includes actor, source tenant, target tenant, owner email snapshot |
| Tenant owner requests connection | Pending request notifies target owner/operator |
| Connection approved | Status becomes active and both tenants can list it within permissions |
| Access grant created | User can access only the selected connected tenant and resource type |
| Grant revoked | User loses cross-company view/action immediately |
| Connection revoked | Active grants are disabled and workflows cannot create new cross-company steps |

## Workflow Tests

| Scenario | Expected |
|:---|:---|
| Cross-company transfer without connection | Workflow is not started |
| Transfer with active connection and permission | Transfer case is created |
| Target company approval missing | Transfer remains pending |
| Transfer approved | Source keeps history; target creates its own employee record |
| Revocation during pending case | Case stops accepting new target actions unless policy explicitly allows completion |

## Security Tests

| Scenario | Expected |
|:---|:---|
| Tenant-local super admin uses `*` | No cross-company access unless scoped grant exists |
| Platform admin token calls tenant endpoint | Rejected by tenant API auth boundary |
| Tenant token calls admin endpoint | Rejected by admin API auth boundary |
| Raw repository query attempts cross-tenant read | Blocked by tenant isolation/RLS |
| Export cross-company report | Audit records requester tenant and every source tenant |

## Regression Search

Before completing KB or implementation work, search for:

- `legal entity`
- `legal entities`
- `primary legal entity`
- `current legal entity`
- `assigned legal entity`
- `cross-entity`
- `connected company`
- `company connection`
- `owner email`
- `cross-company`

Every result must either follow the company-connections model or be explicitly marked as legacy/deprecated.
