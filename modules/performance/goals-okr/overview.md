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

- [[performance|Performance Module]]
- [[review-cycles]]
- [[reviews]]
- [[feedback]]
- [[recognitions]]
- [[improvement-plans]]
- [[succession-planning]]
- [[multi-tenancy]]
- [[error-handling]]
- [[WEEK3-performance]]
