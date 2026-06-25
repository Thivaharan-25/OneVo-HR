# Desktop Agent Version Manager

> Phase 2 only. This module is not part of Phase 1 navigation or `/admin/v1/*` API scope. Phase 1 does not support agent version publishing, ring assignment, force-update, or rollback from the Developer Platform.

## Purpose

Agent Version Manager controls the full lifecycle of the OneVo desktop agent binary across all tenant endpoints - from publishing new releases and managing deployment rings to pushing force-update commands directly to agents in the field.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `agent_version_releases` | Read + write - version catalog, channel, OS compatibility, download URL |
| `agent_deployment_rings` | Read - ring definitions (Internal=0, Beta=1, GA=2) |
| `agent_deployment_ring_assignments` | Read + write - tenant-to-ring assignments |
| `agent_commands` (AgentGateway) | Write - push update/rollback/diagnostic commands to field agents |
| Audit log | Write every version publish, ring change, and force-update |

## Capabilities

### Version Catalog
- Publish a new agent version with semver format (`major.minor.patch`), release channel, minimum OS version, release notes (Markdown), and download URL
- Set channel for any version: `stable`, `beta`, or `recalled`
- Recalled versions are permanently excluded from deployment eligibility - devices on recalled versions are targeted for force-update

### Deployment Rings

| Ring | Number | Audience |
|---|---|---|
| Internal | 0 | ONEVO internal test tenants - first to receive any new version |
| Beta | 1 | Opted-in beta partner tenants |
| GA | 2 | All remaining production tenants |

**Ring promotion gate:** Before a version can be promoted to GA (Ring 2), Ring 0 must run the version for >= 24 hours with no crash reports or forced rollbacks, and Ring 1 must confirm compatibility across >= 10 tenants. Operator confirms the gate manually.

### Ring Management
- Assign or move any tenant to a different deployment ring
- Each tenant can be in exactly one ring at a time
- View all tenants currently in each ring with their installed agent version

### Force-Update
- Push `UPDATE_AGENT` command via AgentGateway to all devices on a specific version within a ring
- Agents receive the command on next check-in and begin updating
- Used for recalled versions, urgent security patches, or ring-promotion pushes
- Requires `platform.agent_versions.force_update` permission

### Rollback
- Force-pin specific tenant agents to a previous stable version
- Pin prevents auto-updates past the pinned version until removed

## Navigation

| Route | Permission |
|---|---|
| `/operations/agent-versions` | Phase 2 permission contract |
| Publish / channel change | Phase 2 permission contract |
| Force-update | Phase 2 permission contract |

## Key Rules

- Recalled versions cannot be un-recalled - publish a new version to supersede them
- Force-update and rollback commands are dispatched through AgentGateway and are always audit-logged
- Semver format (`major.minor.patch`) is enforced - non-semver version strings are rejected
- One ring per tenant at a time - assigning a new ring removes the previous assignment

## Related

- [[developer-platform/modules/agent-version-manager/end-to-end-logic|Agent Version Manager End-to-End Logic]]
- [[developer-platform/modules/device-management/overview|Device Management]] - per-device visibility and commands
- [[modules/agent-gateway/overview|Agent Gateway]] - agent command infrastructure
