# Performance Improvement Plans

**Module:** Performance  
**Feature:** Improvement Plans

---

## Purpose

Formal PIPs with measurable objectives, timelines, and outcomes.

## Database Tables

### `performance_improvement_plans`
Fields: `employee_id`, `initiated_by_id`, `reason`, `objectives_json`, `start_date`, `end_date`, `status` (`active`, `completed`, `extended`, `terminated`), `outcome` (`improved`, `no_improvement`, `termination`).

## Related

- [[database/performance|Performance Module]]
- [[modules/performance/reviews/overview|Reviews]]
- [[modules/performance/review-cycles/overview|Review Cycles]]
- [[modules/performance/feedback/overview|Feedback]]
- [[modules/performance/goals-okr/overview|Goals Okr]]
- [[modules/performance/recognitions/overview|Recognitions]]
- [[Userflow/Performance/succession-planning|Succession Planning]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[modules/notifications/overview|Notifications]]
- [[security/compliance|Compliance]]
- [[backend/messaging/error-handling|Error Handling]]
- Performance task file (deferred to Phase 2)
