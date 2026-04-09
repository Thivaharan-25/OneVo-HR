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
- [[modules/skills/courses-learning/overview|Courses Learning]] — courses linked to plan milestones
- [[modules/skills/employee-skills/overview|Employee Skills]] — skills targeted by development plan items
- [[modules/skills/certifications/overview|Certifications]] — certifications as plan completion goals
- [[modules/skills/skill-assessments/overview|Skill Assessments]] — assessments used to measure plan progress
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped development plans
- [[backend/messaging/event-catalog|Event Catalog]] — milestone completion and plan status events
- [[backend/messaging/error-handling|Error Handling]] — milestone link integrity error patterns
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — implementation task
