# Feedback

**Module:** Performance  
**Feature:** Feedback Requests

---

## Purpose

Manages peer feedback requests, optionally linked to review cycles.

## Database Tables

### `feedback_requests`
Fields: `requester_id`, `respondent_id`, `subject_id` (who is being reviewed), `cycle_id` (nullable for ad hoc), `status` (`pending`, `completed`, `declined`), `feedback_text`.

## Related

- [[database/performance|Performance Module]]
- [[modules/performance/review-cycles/overview|Review Cycles]]
- [[modules/performance/reviews/overview|Reviews]]
- [[modules/performance/goals-okr/overview|Goals Okr]]
- [[modules/performance/recognitions/overview|Recognitions]]
- [[modules/performance/improvement-plans/overview|Improvement Plans]]
- [[Userflow/Performance/succession-planning|Succession Planning]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[modules/notifications/overview|Notifications]]
- [[backend/messaging/error-handling|Error Handling]]
- Performance task file (deferred to Phase 2)
