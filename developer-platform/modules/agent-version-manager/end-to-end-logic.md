# Agent Version Manager End-to-End Logic

> Phase 2 only. Do not implement these routes or commands in Phase 1.

## Publish Agent Version

1. Operator opens System Operations -> Agent Versions.
2. Frontend calls `GET /admin/v1/agent-versions`.
3. Operator enters version, channel, release notes, OS requirements, and download URL.
4. Frontend calls `POST /admin/v1/agent-versions`.
5. Backend verifies `platform.agent_versions.manage`.
6. Backend stores `agent_version_releases` and audits the publish event.

## Promote Or Recall Version

1. Operator opens version detail.
2. Operator changes channel to stable, beta, deprecated, or recalled.
3. Frontend calls `PATCH /admin/v1/agent-versions/{id}/channel`.
4. Backend validates rollout gate and writes audit history.

## Force Update Ring

1. Operator selects version and deployment ring.
2. Frontend calls `POST /admin/v1/agent-versions/{id}/force-update`.
3. Backend verifies `platform.agent_versions.force_update`.
4. Backend writes Agent Gateway commands for eligible agents.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/agent-versions` | List versions | `platform.agent_versions.read` |
| POST | `/admin/v1/agent-versions` | Publish version | `platform.agent_versions.manage` |
| PATCH | `/admin/v1/agent-versions/{id}/channel` | Change channel | `platform.agent_versions.manage` |
| POST | `/admin/v1/agent-versions/{id}/force-update` | Force update ring | `platform.agent_versions.force_update` |
| GET | `/admin/v1/agent-rings` | Ring assignments | `platform.agent_versions.read` |
| PUT | `/admin/v1/tenants/{id}/agent-ring` | Assign tenant to ring | `platform.agent_versions.manage` |
