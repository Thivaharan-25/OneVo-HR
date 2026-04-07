# Goals / OKR — End-to-End Logic

**Module:** Performance
**Feature:** Goals & OKR

---

## Create Goal

### Flow

```
POST /api/v1/performance/goals
  -> GoalController.Create(CreateGoalCommand)
    -> [RequirePermission("performance:write")]
    -> GoalService.CreateGoalAsync(command, ct)
      -> 1. Validate: title, goal_type (individual/team/company)
      -> 2. If parent_goal_id provided:
         -> Validate parent exists (cascading OKR)
         -> Validate parent is company or team level (not individual)
      -> 3. INSERT into goals
         -> status = 'not_started', current_value = 0
      -> Return Result.Success(goalDto)
```

## Update Goal Progress

### Flow

```
PUT /api/v1/performance/goals/{id}
  -> GoalController.Update(id, UpdateGoalCommand)
    -> [RequirePermission("performance:write")]
    -> GoalService.UpdateProgressAsync(id, command, ct)
      -> 1. UPDATE current_value, status
      -> 2. If current_value >= target_value:
         -> Auto-set status = 'completed'
      -> Return Result.Success(goalDto)
```

### Key Rules

- **Goals are hierarchical** — `parent_goal_id` forms cascading OKRs (company -> team -> individual).
- **Weight** determines contribution to overall performance score.

## Related

- [[goals-okr|Goals & OKR Overview]]
- [[review-cycles]]
- [[reviews]]
- [[event-catalog]]
- [[error-handling]]
