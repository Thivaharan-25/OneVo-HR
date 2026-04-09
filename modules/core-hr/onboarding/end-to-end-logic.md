# Onboarding — End-to-End Logic

**Module:** Core HR
**Feature:** Onboarding

---

## Start Onboarding

### Flow

```
POST /api/v1/employees/{id}/onboarding
  -> EmployeeController.StartOnboarding(id)
    -> [RequirePermission("employees:write")]
    -> OnboardingService.StartAsync(employeeId, ct)
      -> 1. Load employee via IEmployeeService
      -> 2. Find matching onboarding_template:
         -> Match by department_id first, fallback to global template
      -> 3. Create onboarding_tasks from template:
         -> For each task in template.tasks_json:
            -> INSERT into onboarding_tasks
            -> Assign to appropriate person (HR, IT, manager)
            -> Set due_date based on hire_date + offset_days
      -> 4. Publish EmployeeOnboardingStarted event
         -> Consumers: notifications (notify assignees)
      -> Return Result.Success(onboardingDto)
```

## Complete Onboarding Task

### Flow

```
PUT /api/v1/onboarding/tasks/{taskId}/complete
  -> OnboardingController.CompleteTask(taskId)
    -> [Authenticated]
    -> OnboardingService.CompleteTaskAsync(taskId, ct)
      -> 1. Load task, verify caller is assigned_to
      -> 2. UPDATE status = 'completed', completed_at = now
      -> 3. Check if all tasks for employee are completed
         -> If yes -> Mark onboarding as complete
      -> Return Result.Success()
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| No template for department | Use global template |
| No global template | Return 400 "No onboarding template configured" |
| Task already completed | Return 400 |
| Not assigned to caller | Return 403 |

## Related

- [[modules/core-hr/onboarding/overview|Onboarding Overview]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
