# Performance — Schema

**Module:** [[modules/performance/overview|Performance]]
**Phase:** Phase 2
**Tables:** 7

---

## `feedback_requests`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `requester_id` | `uuid` | FK → employees |
| `respondent_id` | `uuid` | FK → employees |
| `subject_id` | `uuid` | FK → employees (who is being reviewed) |
| `cycle_id` | `uuid` | FK → review_cycles (nullable — ad hoc) |
| `status` | `varchar(20)` | `pending`, `completed`, `declined` |
| `feedback_text` | `text` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `requester_id` → [[database/schemas/core-hr#`employees`|employees]], `respondent_id` → [[database/schemas/core-hr#`employees`|employees]], `subject_id` → [[database/schemas/core-hr#`employees`|employees]], `cycle_id` → [[#`review_cycles`|review_cycles]]

---

## `goals`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `parent_goal_id` | `uuid` | Self-referencing — cascading goals |
| `title` | `varchar(200)` |  |
| `description` | `text` |  |
| `goal_type` | `varchar(20)` | `individual`, `team`, `company` |
| `target_value` | `decimal(10,2)` |  |
| `current_value` | `decimal(10,2)` |  |
| `unit` | `varchar(20)` | `percentage`, `count`, `currency` |
| `due_date` | `date` |  |
| `status` | `varchar(20)` | `not_started`, `in_progress`, `completed`, `cancelled` |
| `weight` | `decimal(3,2)` | Contribution weight to overall score |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `performance_improvement_plans`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `initiated_by_id` | `uuid` | FK → users |
| `reason` | `text` |  |
| `objectives_json` | `jsonb` | Measurable objectives |
| `start_date` | `date` |  |
| `end_date` | `date` |  |
| `status` | `varchar(20)` | `active`, `completed`, `extended`, `terminated` |
| `outcome` | `varchar(20)` | `improved`, `no_improvement`, `termination` |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `initiated_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `recognitions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `from_employee_id` | `uuid` | FK → employees |
| `to_employee_id` | `uuid` | FK → employees |
| `category` | `varchar(30)` | `teamwork`, `innovation`, `leadership`, `other` |
| `message` | `text` |  |
| `points` | `int` | Reward points |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `from_employee_id` → [[database/schemas/core-hr#`employees`|employees]], `to_employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `review_cycles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Q1 2026 Review" |
| `cycle_type` | `varchar(20)` | `quarterly`, `annual`, `probation` |
| `start_date` | `date` |  |
| `end_date` | `date` |  |
| `status` | `varchar(20)` | `draft`, `active`, `completed` |
| `include_productivity_data` | `boolean` | **NEW** — pull scores from Productivity Analytics |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `reviews`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `cycle_id` | `uuid` | FK → review_cycles |
| `employee_id` | `uuid` | FK → employees |
| `reviewer_id` | `uuid` | FK → employees |
| `review_type` | `varchar(20)` | `self`, `manager`, `peer`, `360` |
| `overall_rating` | `decimal(3,1)` | 1.0–5.0 |
| `productivity_score` | `decimal(5,2)` | **NEW** — from Productivity Analytics (nullable) |
| `comments` | `text` |  |
| `status` | `varchar(20)` | `draft`, `submitted`, `finalized` |
| `submitted_at` | `timestamptz` |  |

**Foreign Keys:** `cycle_id` → [[#`review_cycles`|review_cycles]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `reviewer_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `succession_plans`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `position_id` | `uuid` | FK → job_titles |
| `current_holder_id` | `uuid` | FK → employees |
| `successor_id` | `uuid` | FK → employees |
| `readiness` | `varchar(20)` | `ready_now`, `1_year`, `2_years`, `not_ready` |
| `development_plan_json` | `jsonb` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `position_id` → [[database/schemas/org-structure#`job_titles`|job_titles]], `current_holder_id` → [[database/schemas/core-hr#`employees`|employees]], `successor_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## Related

- [[modules/performance/overview|Performance Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]