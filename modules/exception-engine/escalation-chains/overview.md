# Escalation Chains

**Module:** Exception Engine  
**Feature:** Escalation Chains

---

## Purpose

Time-based alert escalation for unresolved exception alerts and review cases. Escalation chains must use dynamic resolvers, not fixed role names.

Exception Engine may keep alert-specific severity and delay rules, but the person or group receiving an escalation is resolved through the same resolver model used by Automation Center.

## Resolver-Based Routing

Supported escalation targets:

- Employee's reporting manager
- Employee's team lead
- Employee's department owner
- Users with selected permission, such as `exceptions:manage`
- Users in selected department
- Users in selected team
- Users in selected position or position branch
- Users in selected job level, only when job levels are configured and linked
- Specific employee
- Configured escalation resolver
- Previous workflow approver
- Case conversation participants

Do not use fixed escalation labels like HR or CEO. If a customer wants an HR-like escalation, they should select a permission, department, team, position branch, specific employee, HR coverage resolver, or configured escalation resolver.

## Database Tables

### `escalation_chains`

Key columns describe severity, step order, resolver type, resolver configuration, delay, and action. The canonical schema uses `resolver_type` and `resolver_config`; do not add fixed recipient columns such as `notify_role` or `notify_user_id`.

Example for `critical`:

```text
1. employee's reporting manager immediately
2. users with permission exceptions:manage after 30 minutes
3. configured escalation resolver after 60 minutes
```

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AlertEscalated` | Unacknowledged alert escalated | [[modules/notifications/overview\|Notifications]], Workflow Engine |
| `CaseConversationCreated` | Alert automation opens a private case | Chat, Inbox, Audit |

## Key Business Rules

1. Escalation recipients are resolver outputs, not hard-coded role names.
2. Escalation can create or update a case conversation.
3. Escalation is time-based via delayed jobs.
4. If WorkSync Chat is enabled, escalation action cards appear in the case conversation; otherwise they appear in Inbox.
5. Microsoft Teams can mirror discussion only. Official actions remain in ONEVO.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/exceptions/escalation-chains` | `exceptions:manage` | List chains |
| POST | `/api/v1/exceptions/escalation-chains` | `exceptions:manage` | Create/update chain |

## Related

- [[modules/exception-engine/overview|Exception Engine Module]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine and Automation Center]]
- [[Userflow/Automation/automation-center|Automation Center]]
- [[security/auth-architecture|Auth Architecture]]
