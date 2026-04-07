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

- [[performance|Performance Module]]
- [[reviews]]
- [[review-cycles]]
- [[feedback]]
- [[goals-okr]]
- [[improvement-plans]]
- [[succession-planning]]
- [[multi-tenancy]]
- [[notifications]]
- [[error-handling]]
- [[WEEK3-performance]]
