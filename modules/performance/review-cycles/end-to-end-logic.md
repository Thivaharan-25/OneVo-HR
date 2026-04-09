# Review Cycles — End-to-End Logic

**Module:** Performance
**Feature:** Review Cycles

---

## Create Review Cycle

### Flow

```
POST /api/v1/performance/cycles
  -> ReviewCycleController.Create(CreateCycleCommand)
    -> [RequirePermission("performance:manage")]
    -> ReviewCycleService.CreateAsync(command, ct)
      -> 1. Validate: name, cycle_type (quarterly/annual/probation), dates
      -> 2. INSERT into review_cycles (status = 'draft')
         -> include_productivity_data flag (optional, for Pillar 2 integration)
      -> Return Result.Success(cycleDto)
```

## Activate Review Cycle

### Flow

```
PUT /api/v1/performance/cycles/{id}/activate
  -> ReviewCycleController.Activate(id)
    -> [RequirePermission("performance:manage")]
    -> ReviewCycleService.ActivateAsync(id, ct)
      -> 1. UPDATE status = 'active'
      -> 2. Auto-create review records for all eligible employees
         -> INSERT into reviews for each employee (status = 'draft')
         -> Assign reviewer based on reporting hierarchy
      -> 3. If include_productivity_data:
         -> Pre-fetch productivity scores from IProductivityAnalyticsService
         -> Populate productivity_score on review records
      -> 4. Notify all participants via notifications
      -> Return Result.Success()
```

## Related

- [[modules/performance/review-cycles/overview|Review Cycles Overview]]
- [[modules/performance/reviews/overview|Reviews]]
- [[modules/performance/feedback/overview|Feedback]]
- [[modules/performance/goals-okr/overview|Goals Okr]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
