# Courses & Learning

**Module:** Skills & Learning  
**Feature:** Courses & Learning

---

## Purpose

Learning course management with LMS provider integration and enrollment tracking.

## Database Tables

### `lms_providers`
External LMS connections: `provider_type` (`udemy`, `coursera`, `internal`), `sso_enabled`, `status`.

### `courses`
Fields: `title`, `source` (`internal`, `external`), `lms_provider_id`, `content_type`, `duration_minutes`, `is_mandatory`.

### `course_skill_tags`
Links courses to skills: `course_id`, `skill_id`.

### `course_enrollments`
Enrollment tracking: `course_id`, `employee_id`, `assigned_by_id`, `status`, `completion_percent`, `linked_milestone_id`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/courses` | `skills:read` | List courses |
| POST | `/api/v1/courses/enroll` | `skills:write` | Enroll |

## Related

- [[skills|Skills Module]] — parent module
- [[modules/skills/certifications/overview|Certifications]] — certifications earned upon course completion
- [[modules/skills/employee-skills/overview|Employee Skills]] — skills tagged to courses via course_skill_tags
- [[modules/skills/development-plans/overview|Development Plans]] — plan milestones linked to course enrollments
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] — skills that courses build
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped course and enrollment data
- [[backend/messaging/event-catalog|Event Catalog]] — enrollment and completion events
- [[backend/messaging/error-handling|Error Handling]] — LMS integration and sync error handling
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — implementation task
