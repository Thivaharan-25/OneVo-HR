# Succession Planning — End-to-End Logic

**Module:** Performance
**Feature:** Succession Planning

---

## Create Succession Plan

### Flow

```
POST /api/v1/performance/succession-plans
  -> SuccessionController.Create(CreateSuccessionPlanCommand)
    -> [RequirePermission("performance:manage")]
    -> SuccessionService.CreateAsync(command, ct)
      -> 1. Validate position (job_title) exists
      -> 2. Validate current holder and successor are active employees
      -> 3. Assess readiness: ready_now, 1_year, 2_years, not_ready
      -> 4. INSERT into succession_plans
         -> development_plan_json for successor development areas
      -> Return Result.Success(planDto)
```

## Related

- [[database/performance|Performance Module]]
- [[frontend/architecture/overview|Succession Planning Overview]]
- [[modules/performance/reviews/end-to-end-logic|Reviews — End-to-End Logic]]
- [[modules/performance/goals-okr/end-to-end-logic|Goals & OKR — End-to-End Logic]]
- [[modules/performance/improvement-plans/end-to-end-logic|Improvement Plans — End-to-End Logic]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/notification-system|Notification System]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- Performance task file (deferred to Phase 2)
