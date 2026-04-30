# User Flow: IDE Agent Install

**Module:** IDE Extension + Agent Gateway
**Pillar:** Cross-Pillar
**Phase:** Phase 1
**Owner:** Dev 8 (IDE context + agent entitlement)

---

## Overview

This flow covers installing the existing OneVo desktop monitoring agent from the VS Code extension. The IDE extension is only a bootstrapper client. Agent ownership, registration, health, policy distribution, and telemetry remain in Agent Gateway.

The extension must never install the agent silently. Every install request is entitlement-checked server-side and requires explicit user consent.

---

## Flow

```
Extension starts
        |
        v
GET /api/v1/ide/entitlements
        |
        +-- has_monitoring_entitlement = false
        |       |
        |       v
        |   No agent prompt is shown
        |
        +-- has_monitoring_entitlement = true
                |
                v
        Non-intrusive prompt:
        "Set up OneVo monitoring agent?"
                |
                +-- Not Now / Never Ask Again --> Stop
                |
                +-- Set Up
                        |
                        v
        POST /api/v1/ide/agent-install/request
        Server validates:
          - authenticated user
          - tenant entitlement
          - active install/session
          - allowed platform
                        |
                        v
        agent_install_jobs row created
        response includes signed binary URL + sha256 + job id
                        |
                        v
        Extension downloads binary to temp location
                        |
                        v
        Extension verifies SHA256 hash
                        |
                        +-- Hash mismatch --> fail job, show error, do not run
                        |
                        v
        User confirms OS installer prompt
                        |
                        v
        Desktop agent installer runs
                        |
                        v
        Agent registers through Agent Gateway
                        |
                        v
        PUT /api/v1/ide/agent-install/{id}/installed
                        |
                        v
        Extension polls status until installed/failed
```

---

## Backend Responsibilities

| Endpoint | Owner | Responsibility |
|:--|:--|:--|
| `GET /api/v1/ide/entitlements` | IDE Extension | Return `has_monitoring_entitlement` from Agent Gateway entitlement state |
| `POST /api/v1/ide/agent-install/request` | IDE Extension + Agent Gateway | Validate entitlement and create `agent_install_jobs` |
| `GET /api/v1/ide/agent-install/status/{id}` | IDE Extension + Agent Gateway | Return job state |
| `PUT /api/v1/ide/agent-install/{id}/installed` | IDE Extension + Agent Gateway | Mark install complete after agent registration |

---

## Key Invariants

| Rule | Enforcement |
|:--|:--|
| IDE extension does not own the monitoring agent lifecycle | Agent Gateway remains system of record |
| Agent install is explicit opt-in | VS Code prompt + OS installer prompt |
| Entitlement is checked on every install request | Backend |
| Binary integrity is verified before execution | Extension verifies SHA256 from signed backend response |
| No duplicate agent database | Uses `agent_install_entitlements`, `agent_install_jobs`, and `registered_agents` |
| Failed installs are auditable | `agent_install_jobs.status = failed` with error summary |

---

## Tables Involved

- `ide_extension_installs`
- `ide_sessions`
- `agent_install_entitlements`
- `agent_install_jobs`
- `registered_agents`

---

## Related

- [[modules/ide-extension/overview|IDE Extension Module Overview]]
- [[modules/agent-gateway/overview|Agent Gateway]]
- [[database/schemas/ide-extension|IDE Extension Schema]]
- [[database/schemas/agent-gateway|Agent Gateway Schema]]
- [[docs/superpowers/specs/2026-04-30-ide-extension-design|IDE Extension Design Spec]]
