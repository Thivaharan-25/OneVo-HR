# Course Enrollment

**Area:** Skills & Learning  
**Required Permission(s):** `skills:read` (to browse courses) + employee self-enrollment  
**Related Permissions:** `skills:manage` (admin can assign courses), `skills:write` (to update skills on completion)

---

## Preconditions

- Learning module is enabled for the tenant
- At least one course has been created by an admin
- Employee has an active employment record
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Browse Course Catalog
- **UI:** Learning → Course Catalog. Grid/list view showing available courses. Each course card displays: Title, Category (e.g., "Technical", "Leadership", "Compliance"), Duration (e.g., "4 hours", "2 weeks"), Difficulty level, Skills covered (tags), Enrollment count, Rating (if peer-rated), Thumbnail image. Filter sidebar: Category, Skill, Duration range, Difficulty. Search bar with full-text search. Tabs: "All Courses", "Recommended for You" (based on skill gaps), "Mandatory" (compliance)
- **API:** `GET /api/v1/learning/courses?page=1&pageSize=20&category={cat}&search={query}`
- **Backend:** `CourseService.GetCatalogAsync()` → [[skills]]
- **Validation:** Permission check for `skills:read`
- **DB:** `courses`, `course_skills`, `course_enrollments` (for enrollment count)

### Step 2: View Course Details
- **UI:** Click course card → course detail page. Sections: Overview (description, learning objectives), Curriculum (modules/chapters list with durations), Prerequisites (other courses or skills required), Skills You'll Gain (linked to taxonomy with proficiency level), Instructor info, Reviews/Ratings, Enrollment status. "Enroll" button if not enrolled. "Continue" button if in progress. "Completed" badge if finished
- **API:** `GET /api/v1/learning/courses/{courseId}`
- **Backend:** `CourseService.GetDetailAsync()` → [[skills]]
- **Validation:** Check if employee meets prerequisites
- **DB:** `courses`, `course_modules`, `course_skills`, `course_prerequisites`, `course_enrollments`

### Step 3: Check Prerequisites
- **UI:** If prerequisites exist: green checkmarks for met prerequisites, red X for unmet. If all met: "Enroll" button enabled. If unmet: "Enroll" button disabled with message: "Complete these prerequisites first: [list]". Link to prerequisite courses. Manager override option: manager can waive prerequisites
- **API:** `GET /api/v1/learning/courses/{courseId}/prerequisites/check`
- **Backend:** `CoursePrerequisiteService.CheckAsync()` → [[skills]]
- **Validation:** Cross-references employee's completed courses and validated skills against course prerequisites
- **DB:** `course_prerequisites`, `course_enrollments`, `employee_skills`

### Step 4: Enroll in Course
- **UI:** Click "Enroll" button. Confirmation dialog: "Enroll in [Course Name]? Estimated time: [Duration]". Click "Confirm". Course added to "My Learning" section. Toast: "Successfully enrolled in [Course Name]". Calendar event optionally created for scheduled courses
- **API:** `POST /api/v1/learning/courses/{courseId}/enroll`
- **Backend:** `CourseEnrollmentService.EnrollAsync()` → [[skills]]
  1. Validate prerequisites are met (server-side)
  2. Check enrollment capacity (if limited)
  3. Create `course_enrollments` record with status `enrolled`
  4. Add to employee's learning plan
  5. If scheduled course: create calendar event via [[modules/calendar/calendar-events/overview|Calendar Events]]
  6. Notify manager of enrollment (optional based on settings)
  7. Publish `CourseEnrollmentEvent`
  8. Create audit log entry
- **Validation:** Prerequisites must be met. Course must be active. Employee not already enrolled. Capacity not exceeded
- **DB:** `course_enrollments`, `learning_plans`, `calendar_events`, `audit_logs`

### Step 5: Track Progress
- **UI:** My Learning → shows enrolled courses with progress. Click course → learning interface: module list with completion checkboxes, progress bar (e.g., "3/8 modules completed — 37%"), time spent tracking, Resume button (opens last incomplete module). Each module: mark as complete when finished. Quiz modules: must pass with minimum score
- **API:** `PUT /api/v1/learning/enrollments/{enrollmentId}/progress`
  ```json
  {
    "moduleId": "uuid",
    "status": "completed",
    "timeSpentMinutes": 45,
    "quizScore": 85
  }
  ```
- **Backend:** `CourseProgressService.UpdateModuleProgressAsync()` → [[skills]]
  1. Update `course_module_progress` record
  2. Recalculate overall course progress percentage
  3. If quiz: validate minimum passing score
  4. Publish `CourseProgressUpdatedEvent`
- **Validation:** Module must belong to enrolled course. Quiz score must meet minimum if applicable
- **DB:** `course_module_progress`, `course_enrollments`

### Step 6: Complete Course and Update Skills
- **UI:** When all modules completed → course status changes to `completed`. Completion certificate generated (if configured). Skills covered by course auto-suggested for declaration or proficiency update. Dialog: "You've completed [Course Name]! Update your skills?" — shows linked skills with suggested proficiency levels. Employee confirms or adjusts. Completion badge shown on profile
- **API:** `POST /api/v1/learning/enrollments/{enrollmentId}/complete`
- **Backend:** `CourseCompletionService.CompleteAsync()` → [[skills]]
  1. Validate all modules are completed (and quizzes passed)
  2. Update `course_enrollments` status to `completed`
  3. Set `completed_at` timestamp
  4. Generate completion certificate via [[modules/documents/overview|Documents]]
  5. Auto-update linked employee skills (if auto-update enabled):
     - New skill: create `employee_skills` record at course-defined proficiency
     - Existing skill: suggest proficiency upgrade if course level is higher
  6. Notify manager of completion via [[backend/notification-system|Notification System]]
  7. Publish `CourseCompletedEvent`
  8. Update learning plan progress
- **Validation:** All required modules must be completed. Minimum quiz scores must be met
- **DB:** `course_enrollments`, `employee_skills`, `learning_plans`, `notifications`, `audit_logs`

## Variations

### When manager assigns a course to an employee
- Manager navigates to Team → Learning → select employee → "Assign Course"
- Employee notified: "Your manager has assigned you [Course Name]"
- Assigned courses shown with "Assigned" badge and optional due date
- API: `POST /api/v1/learning/courses/{courseId}/assign` with `employeeId` and `dueDate`

### When course is mandatory (compliance)
- Course flagged as mandatory by admin for specific departments or all employees
- Appears in "Mandatory" tab with due date
- Overdue courses flagged in reports and exception engine
- Manager dashboard shows team compliance percentage

### When re-enrolling after course update
- If course content updated, previously completed employees may be asked to re-certify
- System creates new enrollment, previous completion retained in history

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Prerequisites not met | `400 Bad Request` | "You must complete [Course Name] before enrolling in this course" |
| Course at capacity | `409 Conflict` | "This course is currently full. You have been added to the waitlist" |
| Already enrolled | `409 Conflict` | "You are already enrolled in this course" |
| Course inactive | `400 Bad Request` | "This course is no longer available" |
| Quiz score too low | Progress not saved as complete | "You scored 55%. Minimum passing score is 70%. Please retry" |

## Events Triggered

- `CourseEnrollmentEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by learning analytics, notification service
- `CourseProgressUpdatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by learning plan tracking
- `CourseCompletedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by skill auto-update, notification service, certificate generation
- `AuditLogEntry` (action: `course.enrolled`, `course.completed`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Skills-Learning/skill-taxonomy-setup|Skill Taxonomy Setup]] — skills linked to courses
- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]] — skills updated on course completion
- [[Userflow/Skills-Learning/development-plan|Development Plan]] — courses assigned as part of development goals
- [[Userflow/Skills-Learning/certification-tracking|Certification Tracking]] — certifications earned from courses

## Module References

- [[skills]] — skills module overview
- [[modules/skills/courses-learning/overview|Courses Learning]] — course data model, catalog, and enrollment logic
- [[modules/skills/employee-skills/overview|Employee Skills]] — skill updates on completion
- [[modules/calendar/calendar-events/overview|Calendar Events]] — scheduled course events
- [[backend/notification-system|Notification System]] — enrollment and completion notifications
- [[modules/documents/overview|Documents]] — certificate generation
