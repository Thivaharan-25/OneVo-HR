# Module: Skills & Learning

**Feature Folder:** `Application/Features/Skills`
**Phase:** Mixed - 5 tables Phase 1, 10 tables Phase 2
**Pillar:** 1 â€” HR Management
**Owner:** Dev 3 + Dev 4
**Tables:** 15 (5 Phase 1, 10 Phase 2)

> [!NOTE]
> **Phase 1 (build now):** `skill_categories`, `skills`, `job_skill_requirements`, `employee_skills`, and `skill_validation_requests` support embedded Job Family required skills plus employee skill requests and manager validation. Skills can be created inline only from `Org Structure -> Job Families -> Required Skills`; employees can request existing tenant skills, especially skills required by their job family.
>
> **No Phase 1 Skills sidebar:** Do not build a customer-facing `Skills -> Taxonomy` area in Phase 1. Full taxonomy management, LMS integrations, courses, course enrollments, quiz-based assessments, development plans, and certifications are Phase 2 unless explicitly pulled forward.

---

## Purpose

Manages skills taxonomy, employee skill assessments, learning courses, LMS provider integrations, certifications, and individual development plans. Supports skill gap analysis for workforce planning.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee context |
| **Depends on** | [[modules/org-structure/overview\|Org Structure]] | `IOrgStructureService` | Job family skill requirements |

---

## Public Interface

```csharp
public interface ISkillsService
{
    Task<Result<List<SkillDto>>> GetEmployeeSkillsAsync(Guid employeeId, CancellationToken ct);
    Task<Result<SkillAssessmentDto>> AssessSkillAsync(AssessSkillCommand command, CancellationToken ct);
    Task<Result<List<CourseDto>>> GetRecommendedCoursesAsync(Guid employeeId, CancellationToken ct);
    Task<Result<List<SkillGapDto>>> GetSkillGapAnalysisAsync(Guid employeeId, CancellationToken ct);
}
```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/Skills/Entities/
  ONEVO.Domain/Features/Skills/Events/

Application (CQRS):
  ONEVO.Application/Features/Skills/Commands/
  ONEVO.Application/Features/Skills/Queries/
  ONEVO.Application/Features/Skills/DTOs/Requests/
  ONEVO.Application/Features/Skills/DTOs/Responses/
  ONEVO.Application/Features/Skills/Validators/
  ONEVO.Application/Features/Skills/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/Skills/

API endpoints:
  ONEVO.Api/Controllers/Skills/SkillsController.cs

---

## Database Tables (15)

### Phase 1 Tables - Build Now

### `skill_categories`

Skill groupings (e.g., "Technical", "Soft Skills").

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `name` | `varchar(100)` | |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK â†’ users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `skills`

Individual skill definitions within a category.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `category_id` | `uuid` | FK â†’ skill_categories |
| `name` | `varchar(100)` | |
| `proficiency_levels` | `jsonb` | Level definitions (labels, descriptions per 1â€“5) |
| `evidence_required` | `boolean` | Whether proof is needed for validation |
| `created_by_id` | `uuid` | FK â†’ users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |


### `job_skill_requirements`

Required skills per job family with minimum proficiency.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `job_family_id` | `uuid` | FK â†’ job_families |
| `skill_id` | `uuid` | FK â†’ skills |
| `min_proficiency` | `integer` | Minimum required level (1â€“5) â€” check `BETWEEN 1 AND 5` |
| `is_mandatory` | `boolean` | |
| `created_at` | `timestamptz` | |

> **Note:** HTML ERD uses `job_family_required_skills` â€” renamed to match module convention.

### `employee_skills`

Employee-skill mapping with current proficiency level.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK to tenants |
| `employee_id` | `uuid` | FK to employees |
| `skill_id` | `uuid` | FK to skills |
| `proficiency_level` | `integer` | 1 (Beginner) to 5 (Expert) - check `BETWEEN 1 AND 5` |
| `status` | `varchar(20)` | `pending`, `validated`, `expired` |
| `source` | `varchar(30)` | `self_declared`, `manager_validated`, `wms_observed`, `assessment_result` - default `self_declared` |
| `validated_by_id` | `uuid` | FK to employees (nullable) |
| `last_assessed_in_review_id` | `uuid` | FK to review_cycles (nullable - null until Performance review integration is enabled) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `skill_validation_requests`

Requests for skill level validation (replaces previous `skill_assessments` + `skill_endorsements` concepts).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `employee_id` | `uuid` | FK â†’ employees |
| `skill_id` | `uuid` | FK â†’ skills |
| `from_level` | `integer` | Current proficiency |
| `to_level` | `integer` | Requested proficiency |
| `evidence_url` | `varchar(500)` | Supporting evidence link (nullable) |
| `validator_id` | `uuid` | FK â†’ employees (manager/peer) |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected` |
| `review_note` | `text` | Validator feedback (nullable) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |


### Phase 2 Tables â€” Deferred


### `lms_providers`

External LMS provider connections.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `name` | `varchar(100)` | |
| `provider_type` | `varchar(30)` | e.g., `udemy`, `coursera`, `internal` |
| `sso_enabled` | `boolean` | |
| `status` | `varchar(20)` | `active`, `inactive` |
| `created_by_id` | `uuid` | FK â†’ users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `courses`

Learning courses (internal or from LMS provider).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `title` | `varchar(255)` | |
| `source` | `varchar(50)` | `internal`, `external` |
| `lms_provider_id` | `uuid` | FK â†’ lms_providers (nullable â€” null for internal) |
| `content_type` | `varchar(30)` | `video`, `article`, `interactive`, `blended` |
| `duration_minutes` | `integer` | |
| `is_mandatory` | `boolean` | |
| `created_by_id` | `uuid` | FK â†’ users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `course_skill_tags`

Links courses to the skills they develop.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `course_id` | `uuid` | FK â†’ courses |
| `skill_id` | `uuid` | FK â†’ skills |

### `course_enrollments`

Employee course enrollment and progress tracking.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `course_id` | `uuid` | FK â†’ courses |
| `employee_id` | `uuid` | FK â†’ employees |
| `assigned_by_id` | `uuid` | FK â†’ employees (nullable â€” null if self-enrolled) |
| `status` | `varchar(20)` | `assigned`, `in_progress`, `completed`, `dropped` |
| `completion_percent` | `integer` | 0â€“100 |
| `linked_milestone_id` | `uuid` | FK â†’ development_plan_items (nullable) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

> **Note:** HTML ERD uses `course_assignments` â€” renamed. Completion tracking is inline (no separate `course_completions` table).

### `development_plans`

Individual development plans, optionally linked to a review cycle.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `employee_id` | `uuid` | FK â†’ employees |
| `created_by_id` | `uuid` | FK â†’ users |
| `title` | `varchar(255)` | |
| `status` | `varchar(20)` | `draft`, `active`, `completed`, `cancelled` |
| `linked_review_cycle_id` | `uuid` | FK â†’ review_cycles (nullable) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `development_plan_items`

Milestones/action items within a development plan.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `plan_id` | `uuid` | FK â†’ development_plans |
| `title` | `varchar(255)` | |
| `skill_id` | `uuid` | FK â†’ skills (nullable) |
| `linked_course_id` | `uuid` | FK â†’ courses (nullable) |
| `status` | `varchar(20)` | `not_started`, `in_progress`, `completed` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

> **Note:** HTML ERD uses `development_milestones` â€” renamed to match module convention.


### `skill_questions`

Assessment questions per skill for quiz-based evaluation.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `skill_id` | `uuid` | FK â†’ skills |
| `question_text` | `text` | |
| `question_type` | `varchar(20)` | `multiple_choice`, `text`, `file_upload` |
| `sort_order` | `integer` | |
| `is_required` | `boolean` | |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK â†’ users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `skill_question_options`

Answer options for multiple-choice skill questions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `question_id` | `uuid` | FK â†’ skill_questions |
| `option_text` | `text` | |
| `is_correct` | `boolean` | |
| `sort_order` | `integer` | |

### `skill_assessment_responses`

Employee responses to skill assessment questions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `employee_id` | `uuid` | FK â†’ employees |
| `question_id` | `uuid` | FK â†’ skill_questions |
| `selected_option_id` | `uuid` | FK â†’ skill_question_options (nullable â€” for MCQ) |
| `text_answer` | `text` | Nullable â€” for text-type questions |
| `file_record_id` | `uuid` | FK â†’ file_records (nullable â€” for file uploads) |
| `submitted_at` | `timestamptz` | |
| `scored_by_id` | `uuid` | FK â†’ employees (nullable â€” for manual scoring) |
| `score` | `decimal(5,2)` | Nullable |

### `employee_certifications`

Employee certification records with expiry tracking.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `employee_id` | `uuid` | FK â†’ employees |
| `course_id` | `uuid` | FK â†’ courses (nullable â€” cert may not be from a course) |
| `certification_name` | `varchar(255)` | |
| `issuing_authority` | `varchar(255)` | |
| `credential_id` | `varchar(100)` | External credential ID (nullable) |
| `issue_date` | `date` | |
| `expiry_date` | `date` | Nullable â€” some certs don't expire |
| `status` | `varchar(20)` | `active`, `expired`, `revoked` |
| `certificate_file_record_id` | `uuid` | FK â†’ file_records (nullable) |
| `renewal_reminder_sent` | `boolean` | Hangfire job sets this 30 days before expiry |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

> **Note:** No separate `certifications` definition table â€” certification metadata is stored inline on `employee_certifications`. If reusable cert definitions are needed later, extract to a separate table.

---

## Domain Events (intra-module â€” MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | â€” | â€” |

## Cross-Module Events (cross-module â€” MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `SkillValidated` | Manager validates employee skill level | [[modules/notifications/overview\|Notifications]] (notify employee) |
| `CourseCompleted` | Employee completes a learning course | [[modules/notifications/overview\|Notifications]] (notify employee), skill gap recalculation |
| `CertificationEarned` | Employee earns a new certification | [[modules/notifications/overview\|Notifications]] (notify manager and employee) |
| `CertificationExpiring` | Certification within 30 days of expiry | [[modules/notifications/overview\|Notifications]] (send renewal reminder) |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `EmployeeHired` | [[modules/core-hr/overview\|Core HR]] | Seed initial skill gap analysis for new employee based on job family requirements |
| `ReviewCompleted` | [[modules/performance/overview\|Performance]] | Update skill assessments that were part of the review cycle |

---

## Key Business Rules

1. **Skill proficiency levels:** 1 (Beginner) â†’ 5 (Expert).
2. **Skill gap analysis** compares `employee_skills` against `job_skill_requirements` for the employee's job family.
3. **`tenant_id`** is used consistently on all tables â€” no column mapping workarounds needed.
4. **Certification expiry tracking** â€” Hangfire job alerts 30 days before expiry, sets `renewal_reminder_sent` flag.
5. **Skill request and validation (Phase 1)** - employees request existing tenant skills for their profile; the manager reviews, approves, adjusts proficiency, or rejects.
6. **Quiz-based assessment (Phase 2)** - `skill_questions` + `skill_question_options` + `skill_assessment_responses` support MCQ, text, and file-upload question types.

---

## API Endpoints

### Phase 1

| Method | Route | Permission | Description |
| :----- | :---- | :--------- | :---------- |
| GET    | `/api/v1/org/job-families/{familyId}/skill-requirements` | `skills:read` | Required skills for a job family |
| POST   | `/api/v1/org/job-families/{familyId}/skill-requirements` | `skills:manage` | Select an existing skill or create a simple skill inline, then attach it to the job family |
| DELETE | `/api/v1/org/job-families/{familyId}/skill-requirements/{id}` | `skills:manage` | Remove skill requirement from job family |
| GET    | `/api/v1/employees/me/skills` | `skills:read` | Employee's own skill profile |
| POST   | `/api/v1/employees/me/skills` | `skills:write` | Employee requests an existing tenant skill for their profile |
| GET    | `/api/v1/skills/validation-requests` | `skills:validate` | Manager's pending employee skill requests |
| PUT    | `/api/v1/employees/{employeeId}/skills/{skillId}/validate` | `skills:validate` | Manager validates, adjusts, or rejects an employee skill request |

### Phase 2 (deferred)

| Method | Route | Permission | Description |
| :----- | :---- | :--------- | :---------- |
| GET    | `/api/v1/courses` | `skills:read` | List courses |
| POST   | `/api/v1/courses/enroll` | `skills:write` | Enroll in course |
| GET    | `/api/v1/development-plans/{employeeId}` | `skills:read` | Development plan |

## Features

### Phase 1
- Embedded Required Skills in [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]] - assign mandatory/optional skills with minimum proficiency level to job families.
- Inline skill search/create - create simple tenant skills only from the Job Family Required Skills flow when the skill does not already exist.
- [[modules/skills/employee-skills/overview|Employee Skills]] - employees request existing tenant skills for their profile; managers validate, adjust, or reject those requests.

### Phase 2 (deferred)
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] - full taxonomy management UI and APIs for skill categories, skill definitions, proficiency labels, and cleanup.
- [[modules/skills/skill-assessments/overview|Skill Assessments]] - Phase 2 quiz-based assessments (MCQ, text, file upload). Basic manager validation of employee skill requests is Phase 1 under Employee Skills.
- [[modules/skills/courses-learning/overview|Courses Learning]] - internal and LMS-linked courses with enrollment and progress tracking.
- [[modules/skills/certifications/overview|Certifications]] - certification records with expiry tracking and renewal reminders.
- [[modules/skills/development-plans/overview|Development Plans]] - individual development plans with milestones and linked courses.

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] â€” All skill and learning data is tenant-scoped
- [[security/compliance|Compliance]] â€” Certification expiry tracking supports regulatory compliance
- [[security/data-classification|Data Classification]] â€” Certificate files stored in blob storage via `file_records`
- [[current-focus/DEV3-skills-core|DEV3: Skills Core]] - Phase 1 Required Skills and employee skill validation implementation task (5 core tables)

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[database/performance|Performance]]










