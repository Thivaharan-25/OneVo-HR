# Remote Commands

**Module:** Agent Gateway
**Feature:** Remote Commands (Server → Agent)

## Purpose

Bidirectional SignalR command channel that enables the server to push commands to desktop agents in real-time. Primary use cases: on-demand screenshot/photo capture triggered by managers, and monitoring lifecycle control triggered by workforce-presence events.

## Architecture

```
Manager UI → API → AgentCommandService → SignalR Hub → Desktop Agent
                                              ↓ (fallback)
                                    agent_commands table → Agent polls via heartbeat
```

**Primary path (real-time):** Command dispatched via SignalR `ExecuteCommand` method. Agent acknowledges, executes, reports result.

**Fallback path (offline/disconnected):** Command stored in `agent_commands` table. Agent discovers pending commands via heartbeat response `has_pending_commands: true`, polls `GET /api/v1/agent/commands`.

## SignalR Hub

```csharp
// ONEVO.Api/Hubs/AgentCommandHub.cs
[Authorize(AuthenticationSchemes = "DeviceJwt")]
public class AgentCommandHub : Hub
{
    // Agent connects with device JWT after employee login
    public override async Task OnConnectedAsync()
    {
        var agentId = Context.User!.FindFirst("agent_id")!.Value;
        await Groups.AddToGroupAsync(Context.ConnectionId, $"agent-{agentId}");
        await _agentService.SetSignalRConnectedAsync(Guid.Parse(agentId), true);
    }
    
    // Agent reports command acknowledgement
    public async Task CommandAcknowledged(Guid commandId)
    {
        await _commandService.MarkDeliveredAsync(commandId);
    }
    
    // Agent reports command completion
    public async Task CommandCompleted(Guid commandId, JsonDocument resultJson)
    {
        await _commandService.MarkCompletedAsync(commandId, resultJson);
        // Fires AgentCommandCompleted domain event
    }
    
    // Agent reports command failure
    public async Task CommandFailed(Guid commandId, string error)
    {
        await _commandService.MarkFailedAsync(commandId, error);
    }
}
```

## Command Types

| Type | Trigger | Employee Notification | Result |
|:-----|:--------|:---------------------|:-------|
| `capture_screenshot` | Manager clicks "Request Screenshot" on alert | "Your manager has requested a screen capture" (3s delay) | Screenshot uploaded to storage, URL in result_json |
| `capture_photo` | Manager clicks "Request Photo" on alert | "Your manager has requested identity verification" (opens camera window) | Photo uploaded, URL in result_json |
| `start_monitoring` | `PresenceSessionStarted` event (clock-in) | None (expected system behavior) | Collectors begin |
| `stop_monitoring` | `PresenceSessionEnded` event (clock-out) | None | Collectors stop, buffer flushed |
| `pause_monitoring` | `BreakStarted` event | "Monitoring paused for break" | Collectors pause, NO data captured |
| `resume_monitoring` | `BreakEnded` event | "Monitoring resumed" | Collectors resume |
| `refresh_policy` | Admin changes policy or app allowlist | None | Agent re-fetches policy via GET /api/v1/agent/policy |

## Security

- **Manager-facing endpoints** require User JWT with `agent:command` permission
- **Agent-facing hub** uses Device JWT authentication
- **Command audit:** Every command is logged in `agent_commands` table with `requested_by` (who initiated)
- **Expiry:** Commands expire after 5 minutes if not delivered. Manager must re-request.
- **Rate limit:** Max 10 capture commands per agent per hour (prevent harassment)

## Domain Event Handlers

```csharp
// Listen to workforce-presence events and translate to agent commands
public class PresenceToAgentCommandHandler :
    INotificationHandler<PresenceSessionStarted>,
    INotificationHandler<PresenceSessionEnded>,
    INotificationHandler<BreakStarted>,
    INotificationHandler<BreakEnded>
{
    public async Task Handle(PresenceSessionStarted notification, CancellationToken ct)
    {
        var agentId = await _agentService.GetAgentByEmployeeIdAsync(notification.EmployeeId, ct);
        if (agentId == null) return; // No agent registered for this employee
        await _commandService.SendCommandAsync(agentId.Value, new AgentCommand
        {
            Type = "start_monitoring",
            Payload = new { sessionId = notification.SessionId }
        }, ct);
    }
    // ... similar for other events
}

// Listen to exception-engine capture requests
public class RemoteCaptureCommandHandler : INotificationHandler<RemoteCaptureRequested>
{
    public async Task Handle(RemoteCaptureRequested notification, CancellationToken ct)
    {
        var agentId = await _agentService.GetAgentByEmployeeIdAsync(notification.EmployeeId, ct);
        if (agentId == null) return Result.Failure("No agent registered");
        await _commandService.SendCommandAsync(agentId.Value, new AgentCommand
        {
            Type = notification.CaptureType, // "capture_screenshot" or "capture_photo"
            RequestedBy = notification.RequestedByUserId,
            Payload = new { reason = notification.Reason, alertId = notification.AlertId }
        }, ct);
    }
}
```

## Related

- [[modules/agent-gateway/overview|Agent Gateway Overview]]
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — Full protocol including command endpoints
- [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]] — Presence event → agent command flow
- [[modules/identity-verification/overview|Identity Verification]] — Consumes photo/screenshot results
- [[modules/exception-engine/overview|Exception Engine]] — Triggers remote capture requests
- [[modules/agent-gateway/tamper-resistance|Tamper Resistance]] — Agent integrity when receiving commands
