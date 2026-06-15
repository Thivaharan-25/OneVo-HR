# Escalation Chains — End-to-End Logic

**Module:** Exception Engine
**Feature:** Escalation Chains

---

## Configure Escalation Chain

### Flow

```
POST /api/v1/exceptions/escalation-chains
  -> EscalationController.Create(CreateChainCommand)
    -> [RequirePermission("exceptions:manage")]
    -> EscalationService.CreateChainAsync(command, ct)
      -> 1. Validate severity: info, warning, critical
      -> 2. For each step:
         -> Validate resolver_type and resolver_config
         -> Resolver may target reporting chain first eligible, reporting manager,
            team lead, department owner, selected permission, selected legal entity,
            selected department/team/position/position branch, optional job level
            when configured, specific employee, previous approver, case participants,
            HR coverage resolver, or configured escalation resolver
         -> Validate delay_minutes >= 0
      -> 3. INSERT into escalation_chains (one row per step)
         -> step_order = 1, 2, 3...
      -> Return Result.Success()
```

## Auto-Escalation

### Flow

```
EscalationJob (Hangfire, every 5 min)
  -> EscalationService.ProcessEscalationsAsync(ct)
    -> 1. Find alerts WHERE status = 'new'
       AND triggered_at + current_step.delay_minutes < now
    -> 2. For each unacknowledged alert:
       -> Find current step in escalation_chains for alert.severity
       -> If next step exists:
          -> Resolve notify target through resolver service
          -> UPDATE alert status = 'escalated'
          -> Create or update case conversation when configured
          -> Publish AlertEscalated event -> delivery router sends action card through Chat or Inbox
       -> If no next step:
          -> Alert remains at highest escalation level
```

### Key Rules

- **Escalation chains are per-severity, not per-rule.** All critical alerts follow the same chain.
- **Escalation is time-based** — delay_minutes from trigger or last escalation.

- **Routing is resolver-based.** No fixed role names are used to decide recipients.
- **Teams is discussion-only.** Teams replies can sync into the ONEVO case conversation, but official actions stay in ONEVO.

## Related

- [[frontend/architecture/overview|Escalation Chains Overview]]
- [[frontend/architecture/overview|Alert Generation]]
- [[frontend/architecture/overview|Evaluation Engine]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV2-exception-engine|DEV2: Exception Engine]]
