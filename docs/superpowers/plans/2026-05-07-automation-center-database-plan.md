# Automation Center Database Plan

**Date:** 2026-05-07  
**Status:** Approved for documentation alignment - additive migration direction  
**Scope:** Database design plan and canonical schema documentation. EF migrations still require a separate implementation task.

---

## Why A Database Change Is Needed

The current database schema does not fully support the Automation Center direction.

Current gaps:

- `workflow_steps` still models fixed approver fields such as `approver_type` and `approver_role_id`.
- `workflow_step_instances` has one `assigned_to_id`, which cannot represent multiple approvers, all-required approval, or sequential approval cleanly.
- `escalation_rules` and `escalation_chains` still contain role-targeting fields such as `escalate_to_role_id` and `notify_role`.
- There is no first-class automation definition/template model for the builder.
- There is no explicit case conversation metadata linking a private conversation to a workflow item, approval, alert, request, or escalation.
- Delivery routing is not modeled as Chat-first, Inbox fallback, Teams discussion mirror.

## Proposed Schema Direction

### 1. Add Automation Definition Tables

Add:

- `automation_definitions`
- `automation_definition_versions`
- `automation_templates`
- `automation_runs`

Purpose:

- Store builder-created automations using versioned trigger, condition, resolver, action, wait, and escalation configuration.
- Keep templates editable after application.
- Track each automation execution without mutating historical definitions.

### 2. Replace Fixed Approver Fields With Resolver Config

Change workflow step modeling from:

- `approver_type`
- `approver_role_id`

To:

- `resolver_type`
- `resolver_config jsonb`
- `approval_mode`
- `execution_order`

Supported `approval_mode` values:

- `only_one_required`
- `all_required`
- `sequential`

### 3. Add Workflow Step Assignment Table

Add:

- `workflow_step_assignments`

Purpose:

- Represent zero, one, or many resolved approvers.
- Track per-approver status for all-required and sequential approval.
- Keep audit and completion rules clear.

Suggested columns:

- `id`
- `workflow_step_instance_id`
- `assignee_employee_id`
- `assignee_user_id`
- `sequence_order`
- `status`
- `assigned_at`
- `acted_at`
- `resolved_from`

### 4. Make Escalation Resolver-Based

Replace:

- `escalation_rules.escalate_to_role_id`
- `escalation_chains.notify_role`
- `escalation_chains.notify_user_id`

With:

- `resolver_type`
- `resolver_config jsonb`
- `delay_minutes` or working-time delay fields
- `action_config jsonb`

### 5. Add Case Conversation Metadata

Add either a dedicated table or extend `channels` with case fields.

Preferred dedicated table:

- `case_conversations`

Suggested columns:

- `id`
- `tenant_id`
- `channel_id`
- `case_type`
- `resource_type`
- `resource_id`
- `workflow_instance_id`
- `automation_run_id`
- `status`
- `created_by_automation_id`
- `created_at`
- `resolved_at`

This keeps normal DMs separate from workflow cases while reusing WorkSync Chat messages and members.

### 6. Add Delivery Routing Records

Add:

- `workflow_delivery_attempts`

Purpose:

- Record whether an action card was sent to Chat, Inbox, Teams mirror, email, or push.
- Preserve source-of-truth behavior: Teams discussion can sync back, but official actions stay in ONEVO.

### 7. Update Cross-Module References

After validation, update:

- `database/schemas/shared-platform.md`
- `database/schemas/exception-engine.md`
- `database/schemas/wms-chat.md`
- `database/schema-catalog.md`
- `database/cross-module-relationships.md`
- `modules/shared-platform/overview.md`
- `modules/shared-platform/workflow-engine/overview.md`
- `modules/exception-engine/overview.md`
- `modules/work-management/chat/overview.md`

## Migration Notes

- Keep legacy workflow rows readable during migration.
- Backfill existing `workflow_steps.approver_type` values into resolver configs where possible.
- Backfill single `workflow_step_instances.assigned_to_id` into one `workflow_step_assignments` row.
- Avoid destructive column drops in the first migration; deprecate first, remove later.
- Add indexes on tenant, workflow instance, resolver type, case resource, and unresolved status.

## Resolved Decisions

1. Automation Center definitions live in Shared Platform.
2. Case conversation metadata uses a dedicated `case_conversations` table linked to WorkSync Chat `channels`.
3. Escalation delays start with simple minute/SLA fields plus JSON action config; working-calendar-specific behavior can be added later without replacing the table.
4. Inbox is a delivery surface for the same workflow action card. Chat messages remain in WorkSync Chat; workflow decisions remain in Shared Platform workflow/case APIs.

## Deferred Questions

1. Exact Inbox storage table is still not defined in the provided schema docs.
2. Final enum names must be mirrored in code constants when EF migrations are implemented.
3. Legacy fields are deprecated after the additive migration, but not dropped until a later contract migration.

## Recommendation

Use Shared Platform for automation/workflow state, add `case_conversations` as metadata over WorkSync Chat channels, and keep Inbox as a delivery surface that can show the same workflow action card and comments when Chat is disabled.
