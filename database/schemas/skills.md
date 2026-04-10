# Skills & Learning — Schema

**Module:** [[modules/skills/overview|Skills & Learning]]
**Phase:** Mixed — 5 tables Phase 1, 10 tables Phase 2
**Tables:** 15 (5 Phase 1 · 10 Phase 2)

> **Phase 1 tables** (built with Phase 1 release): `skill_categories`, `skills`, `job_skill_requirements`, `employee_skills`, `skill_validation_requests`
> **Phase 2 tables** (deferred — LMS, courses, assessments, development plans): all others

---

## `course_enrollments`

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
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `course_id` → [[#`courses`|courses]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `assigned_by_id` → [[database/schemas/core-hr#`employees`|employees]], `linked_milestone_id` → [[#`development_plan_items`|development_plan_items]]

---

## `course_skill_tags`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `course_id` | `uuid` | FK → courses |
| `skill_id` | `uuid` | FK → skills |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `course_id` → [[#`courses`|courses]], `skill_id` → [[#`skills`|skills]]

---

## `courses`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `title` | `varchar(255)` |  |
| `source` | `varchar(50)` | `internal`, `external` |
| `lms_provider_id` | `uuid` | FK → lms_providers (nullable — null for internal) |
| `content_type` | `varchar(30)` | `video`, `article`, `interactive`, `blended` |
| `duration_minutes` | `integer` |  |
| `is_mandatory` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `lms_provider_id` → [[#`lms_providers`|lms_providers]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `development_plan_items`

| Column             | Type           | Notes                                     |
| :----------------- | :------------- | :---------------------------------------- |
| `id`               | `uuid`         | PK                                        |
| `tenant_id`        | `uuid`         | FK → tenants                              |
| `plan_id`          | `uuid`         | FK → development_plans                    |
| `title`            | `varchar(255)` |                                           |
| `skill_id`         | `uuid`         | FK → skills (nullable)                    |
| `linked_course_id` | `uuid`         | FK → courses (nullable)                   |
| `status`           | `varchar(20)`  | `not_started`, `in_progress`, `completed` |
| `created_at`       | `timestamptz`  |                                           |
| `updated_at`       | `timestamptz`  |                                           |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `plan_id` → [[#`development_plans`|development_plans]], `skill_id` → [[#`skills`|skills]], `linked_course_id` → [[#`courses`|courses]]

---

## `development_plans`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `created_by_id` | `uuid` | FK → users |
| `title` | `varchar(255)` |  |
| `status` | `varchar(20)` | `draft`, `active`, `completed`, `cancelled` |
| `linked_review_cycle_id` | `uuid` | FK → review_cycles (nullable) |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]], `linked_review_cycle_id` → [[database/schemas/performance#`review_cycles`|review_cycles]]

---

## `employee_certifications`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `course_id` | `uuid` | FK → courses (nullable — cert may not be from a course) |
| `certification_name` | `varchar(255)` |  |
| `issuing_authority` | `varchar(255)` |  |
| `credential_id` | `varchar(100)` | External credential ID (nullable) |
| `issue_date` | `date` |  |
| `expiry_date` | `date` | Nullable — some certs don't expire |
| `status` | `varchar(20)` | `active`, `expired`, `revoked` |
| `certificate_file_record_id` | `uuid` | FK → file_records (nullable) |
| `renewal_reminder_sent` | `boolean` | Hangfire job sets this 30 days before expiry |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `course_id` → [[#`courses`|courses]], `certificate_file_record_id` → [[database/schemas/infrastructure#`file_records`|file_records]]

---

## `employee_skills`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `skill_id` | `uuid` | FK → skills |
| `proficiency_level` | `integer` | 1 (Beginner) → 5 (Expert) |
| `status` | `varchar(20)` | `pending`, `validated`, `expired` |
| `validated_by_id` | `uuid` | FK → employees (nullable) |
| `last_assessed_in_review_id` | `uuid` | FK → review_cycles (nullable) |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `skill_id` → [[#`skills`|skills]], `validated_by_id` → [[database/schemas/core-hr#`employees`|employees]], `last_assessed_in_review_id` → [[database/schemas/performance#`review_cycles`|review_cycles]]

> **Check constraint:** `proficiency_level BETWEEN 1 AND 5`
> **Phase 1 note:** `last_assessed_in_review_id` is always `null` in Phase 1 — only populated once the Performance module is built.

---

## `job_skill_requirements`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `job_family_id` | `uuid` | FK → job_families |
| `skill_id` | `uuid` | FK → skills |
| `min_proficiency` | `integer` | Minimum required level (1–5) |
| `is_mandatory` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `job_family_id` → [[database/schemas/org-structure#`job_families`|job_families]], `skill_id` → [[#`skills`|skills]]

---

## `lms_providers`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` |  |
| `provider_type` | `varchar(30)` | e.g., `udemy`, `coursera`, `internal` |
| `sso_enabled` | `boolean` |  |
| `status` | `varchar(20)` | `active`, `inactive` |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `skill_assessment_responses`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `question_id` | `uuid` | FK → skill_questions |
| `selected_option_id` | `uuid` | FK → skill_question_options (nullable — for MCQ) |
| `text_answer` | `text` | Nullable — for text-type questions |
| `file_record_id` | `uuid` | FK → file_records (nullable — for file uploads) |
| `submitted_at` | `timestamptz` |  |
| `scored_by_id` | `uuid` | FK → employees (nullable — for manual scoring) |
| `score` | `decimal(5,2)` | Nullable |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `question_id` → [[#`skill_questions`|skill_questions]], `selected_option_id` → [[#`skill_question_options`|skill_question_options]], `file_record_id` → [[database/schemas/infrastructure#`file_records`|file_records]], `scored_by_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `skill_categories`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` |  |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `skill_question_options`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `question_id` | `uuid` | FK → skill_questions |
| `option_text` | `text` |  |
| `is_correct` | `boolean` |  |
| `sort_order` | `integer` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `question_id` → [[#`skill_questions`|skill_questions]]

---

## `skill_questions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `skill_id` | `uuid` | FK → skills |
| `question_text` | `text` |  |
| `question_type` | `varchar(20)` | `multiple_choice`, `text`, `file_upload` |
| `sort_order` | `integer` |  |
| `is_required` | `boolean` |  |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `skill_id` → [[#`skills`|skills]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `skill_validation_requests`

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
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `skill_id` → [[#`skills`|skills]], `validator_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `skills`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `category_id` | `uuid` | FK → skill_categories |
| `name` | `varchar(100)` |  |
| `proficiency_levels` | `jsonb` | Level definitions (labels, descriptions per 1–5) |
| `evidence_required` | `boolean` | Whether proof is needed for validation |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `category_id` → [[#`skill_categories`|skill_categories]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## Related

- [[modules/skills/overview|Skills & Learning Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]