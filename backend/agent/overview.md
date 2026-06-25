# ONEVO Agent - Overview

**Last Updated:** 2026-04-27

The ONEVO Agent is a **separate solution** (`ONEVO.Agent.sln`) that runs on employee computers. It captures activity data and sends it to `ONEVO.Api` via the `AgentGateway` feature endpoints.

## Why a separate solution

- **Independent release cycle** - server deploys daily; agent uses ring-based rollout to thousands of machines via `agent_deployment_rings` and `agent_version_releases` tables in DevPlatform
- **Security boundary** - agent binary on employee machines must not contain server internals
- **Phase 2 expansion** - `ONEVO.Agent.Mac/` added without touching the server solution

## Solution structure

```
ONEVO.Agent.sln
+-- src/
|   +-- ONEVO.Agent.Core/               Pure logic - no OS or framework dependencies
|   |   +-- Capture/
|   |   |   +-- IScreenshotCapture.cs
|   |   |   +-- IAppUsageCapture.cs
|   |   |   +-- IBrowserActivityCapture.cs
|   |   +-- Sync/
|   |   |   +-- IAgentApiClient.cs      POSTs data to ONEVO.Api AgentGateway endpoints
|   |   |   +-- IOfflineQueue.cs        Buffers data when network is unavailable
|   |   +-- Policy/
|   |   |   +-- AgentPolicy.cs          Capture rules fetched from server
|   |   +-- Models/
|   |       +-- ActivitySnapshot.cs
|   |       +-- AppUsageRecord.cs
|   |       +-- HeartbeatPayload.cs
|   |
|   +-- ONEVO.Agent.Windows/            Windows tray app + capture implementations (Phase 1)
|   |   +-- Capture/
|   |   |   +-- WindowsScreenshotCapture.cs
|   |   |   +-- WindowsAppUsageCapture.cs
|   |   |   +-- WindowsBrowserCapture.cs
|   |   +-- Tray/
|   |   |   +-- SystemTrayIcon.cs
|   |   |   +-- TrayContextMenu.cs
|   |   +-- Storage/
|   |   |   +-- SQLiteOfflineQueue.cs
|   |   +-- AutoUpdate/
|   |   |   +-- AgentUpdater.cs
|   |   +-- Program.cs                  .NET Worker Service host
|   |
|   +-- ONEVO.Agent.Infrastructure/     HTTP client layer
|       +-- AgentApiClient.cs           IAgentApiClient implementation
|       +-- AgentAuthService.cs         Machine token management
|       +-- PolicySyncService.cs        Fetches capture policy from AgentGateway
|
+-- tests/
    +-- ONEVO.Agent.Tests.Unit/
```

## Authentication

1. IT admin provisions a machine token via `AgentGateway` admin endpoint
2. Token stored in **Windows Credential Manager** (not registry, not plain file)
3. Agent uses token for all API calls - issuer: `onevo-agent`
4. Token is tenant-scoped - identifies which tenant and employee this machine belongs to

## Server-side integration

The `AgentGateway` feature in `ONEVO.Application/Features/AgentGateway/` handles:
- Agent registration
- Heartbeat ingestion
- Snapshot ingestion
- Policy delivery
- Version check (reads from `DevPlatform` feature)

## Phase roadmap

| Phase | Platform |
|-------|---------|
| Phase 1 | Windows only - `ONEVO.Agent.Windows` |
| Phase 2 | macOS - add `ONEVO.Agent.Mac` to same solution |
