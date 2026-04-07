# Development Plans

**Module:** Skills & Learning  
**Feature:** Development Plans

---

## Purpose

Individual development plans with milestones linked to skills and courses.

## Database Tables

### `development_plans`
Fields: `employee_id`, `title`, `status`, `linked_review_cycle_id` (nullable).

### `development_plan_items`
Milestones: `plan_id`, `title`, `skill_id`, `linked_course_id`, `status`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/development-plans/{employeeId}` | `skills:read` | Development plan |

## Related

- [[skills|Skills Module]] — parent module
- [[courses-learning]] — courses linked to plan milestones
- [[employee-skills]] — skills targeted by development plan items
- [[certifications]] — certifications as plan completion goals
- [[skill-assessments]] — assessments used to measure plan progress
- [[multi-tenancy]] — tenant-scoped development plans
- [[event-catalog]] — milestone completion and plan status events
- [[error-handling]] — milestone link integrity error patterns
- [[WEEK4-supporting-bridges]] — implementation task
