# OKR & Goals (Phase 2) - End-to-End Logic

**Module:** WorkSync
**Feature:** OKR & Goals (Phase 2)

---

## Phase Guard

This is a deferred Phase 2 design reference. Do not build OKR/Goals routes, pages, APIs, tests, or navigation items in Phase 1.

---

## Create Objective with Key Results

```
POST /api/v1/workspaces/{wsId}/objectives
  body: { title, quarter, start_date, end_date, key_results: [...] }
  -> CreateObjectiveHandler
    -> 1. Verify user is workspace member
    -> 2. INSERT objectives (progress = 0, status = "on_track" default)
    -> 3. For each key_result in body:
         INSERT key_results (start_value, current_value = start_value,
                             target_value, result_type, unit, progress = 0)
    -> Return Result<ObjectiveDto> with key results
  -> 201 Created
```

## Add Check-In (Update Progress)

```
POST /api/v1/key-results/{id}/check-ins
  body: { new_value, note }
  -> AddCheckInHandler
    -> 1. Load key_result
    -> 2. BEGIN TRANSACTION
         a. INSERT okr_check_ins:
                previous_value = key_result.current_value
                new_value = body.new_value
         b. UPDATE key_results:
                current_value = new_value
                progress = (new_value - start_value) / (target_value - start_value) * 100
                           (clamped to 0-100)
         c. Recalculate objective.progress:
                = AVG(key_results.progress) WHERE objective_id = ?
                Update objectives.progress
                Update objectives.status based on progress:
                  >= 70% -> "on_track"
                  40-69% -> "at_risk"
                  < 40% -> "off_track"
                  = 100% -> "completed"
    -> 3. COMMIT
    -> 4. Publish OKRCheckInAddedEvent
    -> Return Result<KeyResultDto>
```

## Nested Objectives

```
POST /api/v1/workspaces/{wsId}/objectives
  body: { ..., parent_objective_id }
  -> Same as Create Objective
  -> parent_objective_id links child to parent
  -> Parent progress = AVG(all child objectives progress)
  -> No depth limit enforced at DB level (UI limits to 3 levels)
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Boolean KR: new_value not 0 or 1 | 422 | Boolean result must be 0 or 1 |
| target_value = start_value | 422 | Target must differ from start value |
| Check-in on completed objective | 422 | Objective is completed |

## Related

- [[modules/work-management/okr/overview|OKR Overview]]
- [[modules/work-management/okr/testing|OKR Testing]]
