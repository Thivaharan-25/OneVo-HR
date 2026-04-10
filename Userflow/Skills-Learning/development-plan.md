# Development Plan

**Area:** Skills & Learning  
**Trigger:** Manager or employee creates learning path (user action)
**Required Permission(s):** `skills:manage` (create for team) or `skills:write` (own)  
**Related Permissions:** `performance:manage` (link to performance reviews)

---

## Preconditions

- Skill assessments completed → [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]]
- Courses available in catalog → [[Userflow/Skills-Learning/course-enrollment|Course Enrollment]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Plan
- **UI:** Skills → Development Plans → "Create Plan" → select employee (or self) → set plan name, duration
- **API:** `POST /api/v1/skills/development-plans`

### Step 2: Identify Skill Gaps
- **UI:** System shows current skills vs target role requirements → highlights gaps → add target skills to plan
- Links: [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]], [[Userflow/Org-Structure/job-family-setup|Job Family Setup]]

### Step 3: Assign Learning Actions
- **UI:** For each target skill → assign actions: enroll in course, assign mentor, set stretch project, attend training → set milestones with dates
- **Backend:** DevelopmentPlanService.CreateAsync() → [[modules/skills/development-plans/overview|Development Plans]]
- **DB:** `development_plans`, `development_plan_actions`

### Step 4: Track Progress
- **UI:** Update progress per action → mark milestones complete → overall plan progress percentage shown
- **API:** `PUT /api/v1/skills/development-plans/{id}/actions/{actionId}`

### Step 5: Complete Plan
- **UI:** All actions complete → plan marked as "Completed" → skills auto-updated if courses finished

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Active plan exists | Warning | "Employee has an active development plan" |
| Course unavailable | Warning | "Course [X] is no longer available — select alternative" |

## Events Triggered

- `DevelopmentPlanCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `DevelopmentPlanCompleted` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]]
- [[Userflow/Skills-Learning/course-enrollment|Course Enrollment]]
- [[Userflow/Performance/goal-setting|Goal Setting]]
- [[Userflow/Performance/succession-planning|Succession Planning]]

## Module References

- [[modules/skills/development-plans/overview|Development Plans]]
- [[modules/skills/courses-learning/overview|Courses Learning]]
- [[modules/skills/skill-assessments/overview|Skill Assessments]]
