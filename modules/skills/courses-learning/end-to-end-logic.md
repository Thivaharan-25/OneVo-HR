# Courses & Learning — End-to-End Logic

**Module:** Skills
**Feature:** Courses & Learning

---

## Enroll in Course

### Flow

```
POST /api/v1/courses/enroll
  -> CourseController.Enroll(EnrollCommand)
    -> [RequirePermission("skills:write")]
    -> CourseService.EnrollAsync(command, ct)
      -> 1. Validate course exists and is active
      -> 2. Check not already enrolled
      -> 3. INSERT into course_enrollments
         -> status = 'assigned' or 'in_progress' (self-enroll)
         -> completion_percent = 0
      -> 4. If linked to development plan milestone:
         -> Set linked_milestone_id
      -> Return Result.Success(enrollmentDto)
```

## Update Course Progress

### Flow

```
PUT /api/v1/courses/enrollments/{id}/progress
  -> CourseController.UpdateProgress(id, UpdateProgressCommand)
    -> [Authenticated]
    -> CourseService.UpdateProgressAsync(id, command, ct)
      -> 1. UPDATE completion_percent
      -> 2. If completion_percent = 100:
         -> status = 'completed'
         -> If linked skills: update employee_skills proficiency
         -> If linked milestone: mark milestone completed
      -> Return Result.Success()
```

## Related

- [[courses-learning]] — feature overview
- [[certifications]] — certifications issued on course completion
- [[employee-skills]] — skill tags updated from course completion
- [[event-catalog]] — CourseEnrolled, CourseCompleted events
- [[error-handling]] — LMS provider sync failure and retry patterns
