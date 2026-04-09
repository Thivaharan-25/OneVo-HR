# Recognitions

**Module:** Performance  
**Feature:** Recognitions

---

## Purpose

Peer-to-peer recognition with reward points.

## Database Tables

### `recognitions`
Fields: `from_employee_id`, `to_employee_id`, `category` (`teamwork`, `innovation`, `leadership`, `other`), `message`, `points`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/performance/recognitions` | `performance:write` | Give recognition |

## Related

- [[database/performance|Performance Module]]
- [[modules/performance/reviews/overview|Reviews]]
- [[modules/performance/review-cycles/overview|Review Cycles]]
- [[modules/performance/feedback/overview|Feedback]]
- [[modules/performance/goals-okr/overview|Goals Okr]]
- [[modules/performance/improvement-plans/overview|Improvement Plans]]
- [[Userflow/Performance/succession-planning|Succession Planning]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[modules/notifications/overview|Notifications]]
- [[backend/messaging/error-handling|Error Handling]]
- Performance task file (deferred to Phase 2)
