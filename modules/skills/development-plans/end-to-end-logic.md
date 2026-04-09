# Development Plans — End-to-End Logic

**Module:** Skills
**Feature:** Individual Development Plans

---

## Create Development Plan

### Flow

```
POST /api/v1/development-plans
  -> DevelopmentPlanController.Create(CreatePlanCommand)
    -> [RequirePermission("skills:write")]
    -> DevelopmentPlanService.CreateAsync(command, ct)
      -> 1. Validate employee exists
      -> 2. INSERT into development_plans (status = 'draft')
      -> 3. For each milestone:
         -> INSERT into development_plan_items
         -> Link to skill_id and/or course_id if applicable
      -> Return Result.Success(planDto)
```

## Track Progress

### Flow

```
PUT /api/v1/development-plans/{planId}/items/{itemId}
  -> DevelopmentPlanController.UpdateItem(planId, itemId, UpdateCommand)
    -> [Authenticated]
    -> DevelopmentPlanService.UpdateItemAsync(itemId, command, ct)
      -> 1. UPDATE development_plan_items status
      -> 2. If all items completed:
         -> UPDATE development_plans status = 'completed'
      -> Return Result.Success()
```

## Related

- [[modules/skills/development-plans/overview|Development Plans]] — feature overview
- [[modules/skills/courses-learning/overview|Courses Learning]] — courses linked to milestones
- [[modules/skills/employee-skills/overview|Employee Skills]] — skill targets resolved from plan items
- [[backend/messaging/event-catalog|Event Catalog]] — DevelopmentPlanMilestoneCompleted events
- [[backend/messaging/error-handling|Error Handling]] — orphaned milestone and link validation errors
