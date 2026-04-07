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

- [[performance|Performance Module]]
- [[reviews]]
- [[feedback]]
- [[goals-okr]]
- [[recognitions]]
- [[improvement-plans]]
- [[succession-planning]]
- [[multi-tenancy]]
- [[notifications]]
- [[error-handling]]
- [[WEEK3-performance]]
