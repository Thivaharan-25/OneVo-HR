# Performance Improvement Plans — End-to-End Logic

**Module:** Performance
**Feature:** Performance Improvement Plans (PIP)

---

## Create PIP

### Flow

```
POST /api/v1/performance/pips
  -> PipController.Create(CreatePipCommand)
    -> [RequirePermission("performance:manage")]
    -> PipService.CreateAsync(command, ct)
      -> 1. Validate employee exists
      -> 2. Check no active PIP for same employee
      -> 3. INSERT into performance_improvement_plans
         -> status = 'active'
         -> objectives_json: measurable goals with deadlines
      -> 4. Notify employee and HR
      -> Return Result.Success(pipDto)
```

## Complete PIP

### Flow

```
PUT /api/v1/performance/pips/{id}/complete
  -> PipController.Complete(id, CompletePipCommand)
    -> [RequirePermission("performance:manage")]
    -> PipService.CompleteAsync(id, command, ct)
      -> 1. UPDATE status = 'completed'
      -> 2. Set outcome: improved, no_improvement, termination
      -> 3. If outcome = 'termination':
         -> Trigger offboarding workflow
      -> Return Result.Success()
```

## Related

- [[improvement-plans|Improvement Plans Overview]]
- [[reviews]]
- [[review-cycles]]
- [[event-catalog]]
- [[error-handling]]
