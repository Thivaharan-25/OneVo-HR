# Module: Performance

**Namespace:** `ONEVO.Modules.Performance`
**Phase:** 2 — Deferred
**Pillar:** 1 — HR Management
**Owner:** Dev 2 (Week 3)
**Tables:** 7
**Task File:** Performance task file (deferred to Phase 2)

> [!WARNING]
> **This module is deferred to Phase 2. Do not implement.** Performance reviews are not core to the employee monitoring product. Specs are preserved here for future reference.

---

## Purpose

Manages performance review cycles, multi-rater reviews, peer feedback, goals (OKR), recognition, and succession planning. **Enhanced** in the two-pillar architecture to optionally receive productivity scores from [[modules/productivity-analytics/overview|Productivity Analytics]] for data-informed reviews.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/core-hr/overview|Core Hr]] | `IEmployeeService` | Employee context |
| **Depends on** | [[modules/org-structure/overview|Org Structure]] | `IOrgStructureService` | Department hierarchy for cascade goals |
| **Depends on** | [[modules/productivity-analytics/overview|Productivity Analytics]] | `IProductivityAnalyticsService` | Optional productivity scores for reviews |

---

## Public Interface

```csharp
public interface IPerformanceService
{
    Task<Result<ReviewCycleDto>> GetActiveCycleAsync(CancellationToken ct);
    Task<Result<List<ReviewDto>>> GetEmployeeReviewsAsync(Guid employeeId, CancellationToken ct);
    Task<Result<List<GoalDto>>> GetGoalsAsync(Guid employeeId, CancellationToken ct);
    Task<Result<GoalDto>> CreateGoalAsync(CreateGoalCommand command, CancellationToken ct);
}
```

---

## Database Tables (7)

### `review_cycles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Q1 2026 Review" |
| `cycle_type` | `varchar(20)` | `quarterly`, `annual`, `probation` |
| `start_date` | `date` | |
| `end_date` | `date` | |
| `status` | `varchar(20)` | `draft`, `active`, `completed` |
| `include_productivity_data` | `boolean` | **NEW** — pull scores from Productivity Analytics |
| `created_at` | `timestamptz` | |

### `reviews`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `cycle_id` | `uuid` | FK → review_cycles |
| `employee_id` | `uuid` | FK → employees |
| `reviewer_id` | `uuid` | FK → employees |
| `review_type` | `varchar(20)` | `self`, `manager`, `peer`, `360` |
| `overall_rating` | `decimal(3,1)` | 1.0–5.0 |
| `productivity_score` | `decimal(5,2)` | **NEW** — from Productivity Analytics (nullable) |
| `comments` | `text` | |
| `status` | `varchar(20)` | `draft`, `submitted`, `finalized` |
| `submitted_at` | `timestamptz` | |

### `goals`

OKR-style goals with parent-child hierarchy.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `parent_goal_id` | `uuid` | Self-referencing — cascading goals |
| `title` | `varchar(200)` | |
| `description` | `text` | |
| `goal_type` | `varchar(20)` | `individual`, `team`, `company` |
| `target_value` | `decimal(10,2)` | |
| `current_value` | `decimal(10,2)` | |
| `unit` | `varchar(20)` | `percentage`, `count`, `currency` |
| `due_date` | `date` | |
| `status` | `varchar(20)` | `not_started`, `in_progress`, `completed`, `cancelled` |
| `weight` | `decimal(3,2)` | Contribution weight to overall score |
| `created_at` | `timestamptz` | |

### `recognitions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `from_employee_id` | `uuid` | FK → employees |
| `to_employee_id` | `uuid` | FK → employees |
| `category` | `varchar(30)` | `teamwork`, `innovation`, `leadership`, `other` |
| `message` | `text` | |
| `points` | `int` | Reward points |
| `created_at` | `timestamptz` | |

### `succession_plans`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `position_id` | `uuid` | FK → job_titles |
| `current_holder_id` | `uuid` | FK → employees |
| `successor_id` | `uuid` | FK → employees |
| `readiness` | `varchar(20)` | `ready_now`, `1_year`, `2_years`, `not_ready` |
| `development_plan_json` | `jsonb` | |
| `created_at` | `timestamptz` | |

### `feedback_requests`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `requester_id` | `uuid` | FK → employees |
| `respondent_id` | `uuid` | FK → employees |
| `subject_id` | `uuid` | FK → employees (who is being reviewed) |
| `cycle_id` | `uuid` | FK → review_cycles (nullable — ad hoc) |
| `status` | `varchar(20)` | `pending`, `completed`, `declined` |
| `feedback_text` | `text` | |
| `created_at` | `timestamptz` | |

### `performance_improvement_plans`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `initiated_by_id` | `uuid` | FK → users |
| `reason` | `text` | |
| `objectives_json` | `jsonb` | Measurable objectives |
| `start_date` | `date` | |
| `end_date` | `date` | |
| `status` | `varchar(20)` | `active`, `completed`, `extended`, `terminated` |
| `outcome` | `varchar(20)` | `improved`, `no_improvement`, `termination` |
| `created_at` | `timestamptz` | |

---

## Key Business Rules

1. **Productivity score integration is optional** — controlled by `include_productivity_data` on review cycles. When enabled, `IProductivityAnalyticsService.GetProductivityScoreAsync()` is called during review creation.
2. **Goals are hierarchical** — parent_goal_id forms cascading OKRs (company → team → individual).
3. **`tenant_id`** is used consistently on all tables — no column mapping workarounds needed.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/performance/cycles` | `performance:read` | List review cycles |
| POST | `/api/v1/performance/cycles` | `performance:manage` | Create cycle |
| GET | `/api/v1/performance/reviews/{employeeId}` | `performance:read` | Employee reviews |
| POST | `/api/v1/performance/reviews` | `performance:write` | Submit review |
| GET | `/api/v1/performance/goals` | `performance:read` | List goals |
| POST | `/api/v1/performance/goals` | `performance:write` | Create goal |
| PUT | `/api/v1/performance/goals/{id}` | `performance:write` | Update goal progress |
| GET | `/api/v1/performance/goals/me` | `performance:read-team` | Own goals |
| POST | `/api/v1/performance/recognitions` | `performance:write` | Give recognition |

## Features

- [[modules/performance/review-cycles/overview|Review Cycles]] — Review cycle management (quarterly, annual, probation) with productivity data toggle — frontend: [[modules/performance/review-cycles/frontend|Frontend]]
- [[modules/performance/reviews/overview|Reviews]] — Multi-rater reviews (self, manager, peer, 360) with optional productivity score
- [[modules/performance/goals-okr/overview|Goals Okr]] — OKR-style goals with hierarchical parent-child cascade
- [[modules/performance/feedback/overview|Feedback]] — Ad-hoc and cycle-linked peer feedback requests
- [[modules/performance/recognitions/overview|Recognitions]] — Peer recognition with category and reward points
- [[modules/performance/improvement-plans/overview|Improvement Plans]] — Performance improvement plans with measurable objectives
- [[Userflow/Performance/succession-planning|Succession Planning]] — Succession plans with readiness levels per position

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All performance data is tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] — Review cycle status drives calendar events
- Performance task file (deferred to Phase 2) — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[modules/productivity-analytics/overview|Productivity Analytics]], [[skills]]
