# Goals (OKR)

**Module:** Performance  
**Feature:** Goals & OKR

---

## Purpose

OKR-style goals with parent-child hierarchy (company → team → individual).

## Database Tables

### `goals`
Key columns: `employee_id`, `parent_goal_id` (self-referencing), `title`, `goal_type` (`individual`, `team`, `company`), `target_value`, `current_value`, `unit`, `due_date`, `status`, `weight`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/performance/goals` | `performance:read` | List goals |
| POST | `/api/v1/performance/goals` | `performance:write` | Create goal |
| PUT | `/api/v1/performance/goals/{id}` | `performance:write` | Update progress |
| GET | `/api/v1/performance/goals/me` | `performance:read-team` | Own goals |

## Related

- [[database/performance|Performance Module]]
- [[modules/performance/review-cycles/overview|Review Cycles]]
- [[modules/performance/reviews/overview|Reviews]]
- [[modules/performance/feedback/overview|Feedback]]
- [[modules/performance/recognitions/overview|Recognitions]]
- [[modules/performance/improvement-plans/overview|Improvement Plans]]
- [[Userflow/Performance/succession-planning|Succession Planning]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- Performance task file (deferred to Phase 2)
