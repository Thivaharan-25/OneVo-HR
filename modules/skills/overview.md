# Module: Skills & Learning

**Namespace:** `ONEVO.Modules.Skills`
**Phase:** Mixed — 5 tables Phase 1, 10 tables Phase 2
**Pillar:** 1 — HR Management
**Owner:** Dev 3 + Dev 4
**Tables:** 15 (5 Phase 1 · 10 Phase 2)

> [!NOTE]
> **Phase 1 (build now):** `skill_categories`, `skills`, `job_skill_requirements`, `employee_skills`, `skill_validation_requests` — supports skill taxonomy setup, assigning required skills to job families, manager adding/validating employee skills, and employee skill declarations.
>
> **Phase 2 (deferred):** LMS integrations, courses, course enrollments, quiz-based assessments, development plans, certifications. Do not implement these in Phase 1.

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

## Database Tables (15)

### Phase 1 Tables — Build Now

### `skill_categories`

Skill groupings (e.g., "Technical", "Soft Skills").

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `skills`

Individual skill definitions within a category.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `category_id` | `uuid` | FK → skill_categories |
| `name` | `varchar(100)` | |
| `proficiency_levels` | `jsonb` | Level definitions (labels, descriptions per 1–5) |
| `evidence_required` | `boolean` | Whether proof is needed for validation |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `employee_skills`

Employee-skill mapping with current proficiency level.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `skill_id` | `uuid` | FK → skills |
| `proficiency_level` | `integer` | 1 (Beginner) → 5 (Expert) — check `BETWEEN 1 AND 5` |
| `status` | `varchar(20)` | `pending`, `validated`, `expired` |
| `source` | `varchar(30)` | `self_declared`, `manager_validated`, `wms_observed`, `assessment_result` — default `self_declared`. Required to distinguish WMS-flagged gaps from internal assessments. |
| `validated_by_id` | `uuid` | FK → employees (nullable) |
| `last_assessed_in_review_id` | `uuid` | FK → review_cycles (nullable — **null in Phase 1**) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `job_skill_requirements`

Required skills per job family with minimum proficiency.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `job_family_id` | `uuid` | FK → job_families |
| `skill_id` | `uuid` | FK → skills |
| `min_proficiency` | `integer` | Minimum required level (1–5) — check `BETWEEN 1 AND 5` |
| `is_mandatory` | `boolean` | |
| `created_at` | `timestamptz` | |

> **Note:** HTML ERD uses `job_family_required_skills` — renamed to match module convention.

### Phase 2 Tables — Deferred

### `lms_providers`

External LMS provider connections.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | |
| `provider_type` | `varchar(30)` | e.g., `udemy`, `coursera`, `internal` |
| `sso_enabled` | `boolean` | |
| `status` | `varchar(20)` | `active`, `inactive` |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `courses`

Learning courses (internal or from LMS provider).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `title` | `varchar(255)` | |
| `source` | `varchar(50)` | `internal`, `external` |
| `lms_provider_id` | `uuid` | FK → lms_providers (nullable — null for internal) |
| `content_type` | `varchar(30)` | `video`, `article`, `interactive`, `blended` |
| `duration_minutes` | `integer` | |
| `is_mandatory` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `course_skill_tags`

Links courses to the skills they develop.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `course_id` | `uuid` | FK → courses |
| `skill_id` | `uuid` | FK → skills |

### `course_enrollments`

Employee course enrollment and progress tracking.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `course_id` | `uuid` | FK → courses |
| `employee_id` | `uuid` | FK → employees |
| `assigned_by_id` | `uuid` | FK → employees (nullable — null if self-enrolled) |
| `status` | `varchar(20)` | `assigned`, `in_progress`, `completed`, `dropped` |
| `completion_percent` | `integer` | 0–100 |
| `linked_milestone_id` | `uuid` | FK → development_plan_items (nullable) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

> **Note:** HTML ERD uses `course_assignments` — renamed. Completion tracking is inline (no separate `course_completions` table).

### `development_plans`

Individual development plans, optionally linked to a review cycle.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `created_by_id` | `uuid` | FK → users |
| `title` | `varchar(255)` | |
| `status` | `varchar(20)` | `draft`, `active`, `completed`, `cancelled` |
| `linked_review_cycle_id` | `uuid` | FK → review_cycles (nullable) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `development_plan_items`

Milestones/action items within a development plan.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `plan_id` | `uuid` | FK → development_plans |
| `title` | `varchar(255)` | |
| `skill_id` | `uuid` | FK → skills (nullable) |
| `linked_course_id` | `uuid` | FK → courses (nullable) |
| `status` | `varchar(20)` | `not_started`, `in_progress`, `completed` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

> **Note:** HTML ERD uses `development_milestones` — renamed to match module convention.

### `skill_validation_requests`

Requests for skill level validation (replaces previous `skill_assessments` + `skill_endorsements` concepts).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `skill_id` | `uuid` | FK → skills |
| `from_level` | `integer` | Current proficiency |
| `to_level` | `integer` | Requested proficiency |
| `evidence_url` | `varchar(500)` | Supporting evidence link (nullable) |
| `validator_id` | `uuid` | FK → employees (manager/peer) |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected` |
| `review_note` | `text` | Validator feedback (nullable) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `skill_questions`

Assessment questions per skill for quiz-based evaluation.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `skill_id` | `uuid` | FK → skills |
| `question_text` | `text` | |
| `question_type` | `varchar(20)` | `multiple_choice`, `text`, `file_upload` |
| `sort_order` | `integer` | |
| `is_required` | `boolean` | |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `skill_question_options`

Answer options for multiple-choice skill questions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `question_id` | `uuid` | FK → skill_questions |
| `option_text` | `text` | |
| `is_correct` | `boolean` | |
| `sort_order` | `integer` | |

### `skill_assessment_responses`

Employee responses to skill assessment questions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `question_id` | `uuid` | FK → skill_questions |
| `selected_option_id` | `uuid` | FK → skill_question_options (nullable — for MCQ) |
| `text_answer` | `text` | Nullable — for text-type questions |
| `file_record_id` | `uuid` | FK → file_records (nullable — for file uploads) |
| `submitted_at` | `timestamptz` | |
| `scored_by_id` | `uuid` | FK → employees (nullable — for manual scoring) |
| `score` | `decimal(5,2)` | Nullable |

### `employee_certifications`

Employee certification records with expiry tracking.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `course_id` | `uuid` | FK → courses (nullable — cert may not be from a course) |
| `certification_name` | `varchar(255)` | |
| `issuing_authority` | `varchar(255)` | |
| `credential_id` | `varchar(100)` | External credential ID (nullable) |
| `issue_date` | `date` | |
| `expiry_date` | `date` | Nullable — some certs don't expire |
| `status` | `varchar(20)` | `active`, `expired`, `revoked` |
| `certificate_file_record_id` | `uuid` | FK → file_records (nullable) |
| `renewal_reminder_sent` | `boolean` | Hangfire job sets this 30 days before expiry |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

> **Note:** No separate `certifications` definition table — certification metadata is stored inline on `employee_certifications`. If reusable cert definitions are needed later, extract to a separate table.

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| `SkillValidated` | `skills.validated` | Manager validates employee skill level | [[modules/notifications/overview\|Notifications]] (notify employee) |
| `CourseCompleted` | `skills.course` | Employee completes a learning course | [[modules/notifications/overview\|Notifications]] (notify employee), skill gap recalculation |
| `CertificationEarned` | `skills.cert.earned` | Employee earns a new certification | [[modules/notifications/overview\|Notifications]] (notify manager and employee) |
| `CertificationExpiring` | `skills.cert.expiring` | Certification within 30 days of expiry | [[modules/notifications/overview\|Notifications]] (send renewal reminder) |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| `EmployeeHired` | `core-hr.employee.hired` | [[modules/core-hr/overview\|Core HR]] | Seed initial skill gap analysis for new employee based on job family requirements |
| `ReviewCompleted` | `performance.review.completed` | [[modules/performance/overview\|Performance]] | Update skill assessments that were part of the review cycle |

---

## Key Business Rules

1. **Skill proficiency levels:** 1 (Beginner) → 5 (Expert).
2. **Skill gap analysis** compares `employee_skills` against `job_skill_requirements` for the employee's job family.
3. **`tenant_id`** is used consistently on all tables — no column mapping workarounds needed.
4. **Certification expiry tracking** — Hangfire job alerts 30 days before expiry, sets `renewal_reminder_sent` flag.
5. **Skill validation** — employees request level upgrades via `skill_validation_requests`; a manager/peer reviews and approves/rejects.
6. **Quiz-based assessment** — `skill_questions` + `skill_question_options` + `skill_assessment_responses` support MCQ, text, and file-upload question types.

---

## API Endpoints

### Phase 1

| Method | Route | Permission | Description |
| :----- | :---- | :--------- | :---------- |
| GET    | `/api/v1/skills` | `skills:read` | List all skills (taxonomy) |
| GET    | `/api/v1/skills/categories` | `skills:read` | List skill categories |
| POST   | `/api/v1/skills/categories` | `skills:manage` | Create skill category |
| POST   | `/api/v1/skills` | `skills:manage` | Create skill in category |
| GET    | `/api/v1/job-families/{familyId}/skill-requirements` | `skills:read` | Required skills for a job family |
| POST   | `/api/v1/job-families/{familyId}/skill-requirements` | `skills:manage` | Assign required skill to job family |
| DELETE | `/api/v1/job-families/{familyId}/skill-requirements/{id}` | `skills:manage` | Remove skill requirement from job family |
| GET    | `/api/v1/employees/{employeeId}/skills` | `skills:read` | Employee skills profile |
| POST   | `/api/v1/employees/me/skills` | `skills:write` | Employee self-declares a skill |
| POST   | `/api/v1/employees/{employeeId}/skills` | `skills:write-team` | Manager directly adds skill to employee profile |
| PUT    | `/api/v1/employees/{employeeId}/skills/{skillId}/validate` | `skills:validate` | Manager validates employee skill |
| GET    | `/api/v1/skills/gap-analysis/{employeeId}` | `skills:manage` | Skill gap vs job family requirements |
| GET    | `/api/v1/skills/validation-requests` | `skills:validate` | Pending validation requests for team |

### Phase 2 (deferred)

| Method | Route | Permission | Description |
| :----- | :---- | :--------- | :---------- |
| GET    | `/api/v1/courses` | `skills:read` | List courses |
| POST   | `/api/v1/courses/enroll` | `skills:write` | Enroll in course |
| GET    | `/api/v1/development-plans/{employeeId}` | `skills:read` | Development plan |

## Features

### Phase 1
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] — Skill categories and individual skill definitions with proficiency level labels (1–5)
- [[modules/skills/employee-skills/overview|Employee Skills]] — Employee-skill mapping with current proficiency and validation status; supports employee self-declaration, manager direct-add, and manager validation
- Job Skill Requirements — Assign mandatory/optional skills with minimum proficiency level to job families

### Phase 2 (deferred)
- [[modules/skills/skill-assessments/overview|Skill Assessments]] — Quiz-based assessments (MCQ, text, file upload) and validation requests
- [[modules/skills/courses-learning/overview|Courses Learning]] — Internal and LMS-linked courses with enrollment and progress tracking
- [[modules/skills/certifications/overview|Certifications]] — Certification records with expiry tracking and renewal reminders
- [[modules/skills/development-plans/overview|Development Plans]] — Individual development plans with milestones and linked courses

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All skill and learning data is tenant-scoped
- [[security/compliance|Compliance]] — Certification expiry tracking supports regulatory compliance
- [[security/data-classification|Data Classification]] — Certificate files stored in blob storage via `file_records`
- [[current-focus/DEV3-skills-core|DEV3: Skills Core]] — Phase 1 implementation task (5 core tables)

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[database/performance|Performance]]
