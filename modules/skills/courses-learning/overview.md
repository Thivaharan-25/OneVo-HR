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
- [[certifications]] — certifications earned upon course completion
- [[employee-skills]] — skills tagged to courses via course_skill_tags
- [[development-plans]] — plan milestones linked to course enrollments
- [[skill-taxonomy]] — skills that courses build
- [[multi-tenancy]] — tenant-scoped course and enrollment data
- [[event-catalog]] — enrollment and completion events
- [[error-handling]] — LMS integration and sync error handling
- [[WEEK4-supporting-bridges]] — implementation task
