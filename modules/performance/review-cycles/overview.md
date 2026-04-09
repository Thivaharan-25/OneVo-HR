# Review Cycles

**Module:** Performance  
**Feature:** Review Cycles

---

## Purpose

Manages performance review cycles (quarterly, annual, probation) with optional productivity data integration.

## Database Tables

### `review_cycles`
Key columns: `name`, `cycle_type` (`quarterly`, `annual`, `probation`), `start_date`, `end_date`, `status` (`draft`, `active`, `completed`), `include_productivity_data` (NEW — pull scores from Productivity Analytics).

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/performance/cycles` | `performance:read` | List cycles |
| POST | `/api/v1/performance/cycles` | `performance:manage` | Create cycle |

## Related

- [[database/performance|Performance Module]]
- [[modules/performance/reviews/overview|Reviews]]
- [[modules/performance/feedback/overview|Feedback]]
- [[modules/performance/goals-okr/overview|Goals Okr]]
- [[modules/performance/recognitions/overview|Recognitions]]
- [[modules/performance/improvement-plans/overview|Improvement Plans]]
- [[Userflow/Performance/succession-planning|Succession Planning]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[modules/notifications/overview|Notifications]]
- [[backend/messaging/error-handling|Error Handling]]
- Performance task file (deferred to Phase 2)
