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

- [[performance|Performance Module]]
- [[review-cycles]]
- [[reviews]]
- [[goals-okr]]
- [[recognitions]]
- [[improvement-plans]]
- [[succession-planning]]
- [[multi-tenancy]]
- [[notifications]]
- [[error-handling]]
- [[WEEK3-performance]]
