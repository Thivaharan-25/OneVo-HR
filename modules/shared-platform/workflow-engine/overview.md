# Workflow Engine

**Module:** Shared Platform  
**Feature:** Workflow Engine (Generic)

---

## Purpose

Resource-type agnostic approval engine. Same engine handles leave, overtime, document, expense approvals via `resource_type` + `resource_id` polymorphic references.

## How It Works

1. Module creates a workflow instance: `resource_type = "LeaveRequest"`, `resource_id = {id}`
2. Engine resolves approvers based on step definition
3. Approver takes action → engine advances to next step or completes
4. Module receives `WorkflowCompleted` event with outcome

## Database Tables

### `workflow_definitions`
Templates: `name`, `code`, `resource_type`, `version`.

### `workflow_steps`
Steps within definition: `step_order`, `step_type` (`approval`, `notification`, `condition`), `approver_type` (`reporting_manager`, `department_head`, `role`, `specific_user`), `sla_hours`, `on_timeout_action`.

### `workflow_instances`
Active instances: `workflow_definition_id`, `resource_type`, `resource_id`, `current_step_order`, `status`.

### `workflow_step_instances`
Current step state: `assigned_to_id`, `status`, `sla_deadline_at`.

### `approval_actions`
Action records: `actor_id`, `action` (`approve`, `reject`, `delegate`, `request_info`), `comment`, `delegated_to_id`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workflows/{resourceType}/{resourceId}` | Authenticated | Status |
| POST | `/api/v1/workflows/{instanceId}/approve` | Authenticated | Approve |
| POST | `/api/v1/workflows/{instanceId}/reject` | Authenticated | Reject |

## Related

- [[shared-platform|Shared Platform Module]]
- [[notification-infrastructure]]
- [[compliance-governance]]
- [[feature-flags]]
- [[event-catalog]]
- [[multi-tenancy]]
- [[authorization]]
- [[error-handling]]
- [[WEEK1-shared-platform]]
