# HR Coverage Routing

**Area:** Leave / Workflow Routing  
**Trigger:** Tenant wants HR or people-operations users to approve or review requests for defined employee groups  
**Required Permission(s):** `workflows:manage` to configure routing; runtime approval still requires the action permission such as `leave:approve`

---

## Purpose

HR coverage routing defines which HR/people-operations user or group is responsible for a set of employees. It is needed when multiple HR users split responsibility inside the same department or legal entity.

Example:

```text
Engineering has 40 employees.
HR A handles Backend group.
HR B handles Frontend group.
```

ONEVO cannot infer that split from the department alone. The split must be represented by a configured coverage rule based on team, position branch, legal entity, department, or selected employees.

HR coverage is approval routing. It must not change the employee's reporting manager or position hierarchy.

---

## Coverage Sources

| Source | Use when |
|:-------|:---------|
| Legal entity | One HR owner handles a whole company/entity. |
| Department | One HR owner handles a whole department. |
| Team | HR responsibility follows an explicit stored team. |
| Position branch | HR responsibility follows a manager/position subtree. |
| Selected employees | Temporary or exceptional split; avoid for long-term large groups. |

Coverage rules should be effective-dated and auditable.

---

## Runtime Resolution

When a workflow step uses `hr_coverage_owner`:

1. Load the request employee.
2. Evaluate active HR coverage rules in specificity order:
   - selected employee
   - position branch
   - team
   - department
   - legal entity
3. Return the configured HR owner candidates.
4. Validate each candidate is active, has an active user account, and has the required runtime permission such as `leave:approve`.
5. If no valid candidate exists, fall back to the workflow's next resolver or block and notify the automation owner.

Specific employee coverage should not be the default for large teams because it is harder to maintain than position-branch or team coverage.

---

## User Journey

### Configure Coverage

1. Authorized user opens Automation Center or Leave Settings -> HR Coverage.
2. User selects coverage source: legal entity, department, team, position branch, or selected employees.
3. User selects HR owner resolver:
   - specific employee
   - users with selected permission
   - selected team
4. User sets effective date and optional end date.
5. System validates that the coverage owner can approve the target request type.
6. System saves the rule and writes audit history.

### Use Coverage In Leave Workflow

1. User creates or edits a Leave Approval workflow.
2. User sets resolver to `hr_coverage_owner`.
3. Employee submits leave.
4. Workflow resolves the employee's HR coverage owner.
5. Resolved owner receives the approval action card.

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No coverage rule matches | Workflow falls back or blocks | "No HR coverage owner found" |
| Coverage owner lacks approval permission | Candidate skipped | "Coverage owner cannot approve this request" in admin diagnostics |
| Overlapping rules at same specificity | Validation warning or block | "Two active HR coverage rules overlap" |
| Employee transfers position/legal entity | Coverage re-resolves on next request | No stale HR owner is stored on employee |

---

## Related

- [[Userflow/Leave/leave-approval|Leave Approval]]
- [[Userflow/Automation/automation-center|Automation Center]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/org-structure/positions/overview|Positions]]
