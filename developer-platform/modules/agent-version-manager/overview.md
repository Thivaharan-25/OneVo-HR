# Desktop Agent Version Manager

## Purpose

The Agent Version Manager controls the lifecycle and rollout of the OneVo desktop agent binary across all tenant endpoints. It manages version catalog, deployment rings, tenant ring assignments, and can push update or rollback commands directly to agents via the AgentGateway.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `agent_version_releases` | Read + write — version catalog, release metadata |
| `agent_deployment_rings` | Read + write — ring definitions |
| `agent_deployment_ring_assignments` | Read + write — which tenants are in which ring |
| `agent_commands` (AgentGateway) | Write — push commands to agents in the field |

The first three tables are new tables introduced for the Developer Platform. `agent_commands` is an existing AgentGateway table.

## Capabilities

### Version Catalog
- List all desktop agent releases with:
  - Version number
  - Release notes
  - Minimum OS version requirement
  - Current status label

### Version Status Labels
Mark any version as one of:

| Status | Meaning |
|---|---|
| `stable` | Recommended release; GA ring default |
| `beta` | Available to opted-in beta tenants |
| `deprecated` | Older release; agents are prompted to update |
| `recalled` | Critical defect; agents are force-updated away from this version |

### Deployment Rings
Rings control which tenants receive a version first. The three fixed rings are:

| Ring | Audience |
|---|---|
| Ring 0 | Internal OneVo test tenants |
| Ring 1 | Opted-in beta tenants |
| Ring 2 | All tenants (General Availability) |

### Ring Management
- View all tenants assigned to each ring
- Assign or move a tenant to a different ring

### Force-Update Command
- Push an `UPDATE_AGENT` command via AgentGateway to all agents in a selected ring
- Agents receive the command on next check-in and begin updating to the designated version
- Used when a version is recalled or an urgent security patch must be applied immediately

### Rollback
- Force-pin a specific tenant's agents to a previous stable version
- Agents in that tenant will not auto-update past the pinned version until the pin is removed

## Notes

- Force-update and rollback commands are dispatched through AgentGateway and are audit-logged.
- Ring promotion to Ring 2 follows a validation gate: Ring 0 must run the version for at least 24 hours with no crash reports or forced rollbacks, and Ring 1 must confirm agent compatibility across at least 10 tenants. The operator confirms the gate manually before promoting to Ring 2 (GA).
- Recalled versions trigger automatic escalation — consider pushing a force-update to Ring 2 immediately.
