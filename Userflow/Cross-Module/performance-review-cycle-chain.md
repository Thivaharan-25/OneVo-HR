# Performance Review Cycle — Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** Scheduled review cycle start date (system-scheduled) or HR Admin manually launches cycle  
**Required Permission(s):** `performance:manage` (admin), `performance:write` (employee/manager), `employees:read` (participant list)  
**Modules Involved:** Performance, Employee-Management, Skills-Learning, Payroll, Notifications, Workflow Engine

---

## Context

A performance review cycle isn't just self-assessments and manager ratings. It pulls employee data (role, tenure, goals), feeds into compensation decisions (salary revision, bonus), may trigger learning plans (skill gaps), and drives succession planning. This doc maps the full lifecycle from cycle launch to downstream actions.

## Preconditions

- Review cycle template configured → [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]]
- Employee reporting lines defined (who reviews whom)
- Goals/OKRs set for the review period → [[Userflow/Performance/goal-setting|Goal Setting]]

---

## Chain Reaction Flow

### Phase 1: Cycle Launch

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Performance** | Review cycle created: defines period, participants, deadlines, review form template | HR Admin launches or scheduled trigger | `ReviewCycleLaunched` |
| 2 | **Employee-Management** | Participant list generated: all active employees matching cycle criteria (entity, department, employment type) | `ReviewCycleLaunched` | `ParticipantListGenerated` |
| 3 | **Notifications** | All participants notified: employees (self-assessment due), managers (team reviews due), with deadlines | `ReviewCycleLaunched` | `NotificationSent` |

### Phase 2: Assessment Collection

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 4 | **Performance** | Employees complete self-assessments against goals and competencies | Employee submits | `SelfAssessmentCompleted` |
| 5 | **Performance** | Peer feedback collected (if 360-degree review enabled) | Peers submit | `PeerFeedbackCompleted` |
| 6 | **Performance** | Manager completes review: rates employee, adds comments, recommends rating | Manager submits | `ManagerReviewCompleted` |
| 7 | **Workflow Engine** | Calibration workflow triggered: HR/leadership reviews ratings for consistency across teams | All manager reviews in | `CalibrationStarted` |

### Phase 3: Finalization & Downstream

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 8 | **Performance** | Final ratings confirmed after calibration | Calibration approved | `ReviewFinalized` |
| 9 | **Notifications** | Employees notified that review is complete, can view results | `ReviewFinalized` | `NotificationSent` |
| 10 | **Payroll** | Compensation recommendations generated: salary revision percentage and bonus amount based on rating band mapping | `ReviewFinalized` + rating-to-comp mapping | `CompensationRecommendationCreated` |
| 11 | **Skills-Learning** | Skill gap analysis triggered: areas rated below threshold generate suggested learning paths | `ReviewFinalized` + competency scores | `LearningPlanSuggested` |
| 12 | **Performance** | Succession planning data updated: high performers flagged, at-risk performers flagged | `ReviewFinalized` | `SuccessionDataUpdated` |
| 13 | **Performance** | Improvement plans auto-created for employees below threshold → [[Userflow/Performance/improvement-plan\|Improvement Plan]] | `ReviewFinalized` + low rating | `ImprovementPlanCreated` |

---

## Dependency Chain

```
Cycle Launch (Step 1)
├── Participant list (Step 2) — needs cycle criteria
├── Notifications (Step 3) — needs participant list from Step 2
│
Assessment Collection (Steps 4-6) — parallel, independent
│
Calibration (Step 7) — needs all manager reviews from Step 6
│
Finalization (Step 8)
├── Employee notification (Step 9) — independent
├── Compensation recommendations (Step 10) — independent
├── Learning plan suggestions (Step 11) — independent
├── Succession data update (Step 12) — independent
└── Improvement plans (Step 13) — independent
```

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Participant list incomplete | Some employees excluded from cycle | HR Admin manually adds missing employees |
| Self-assessment deadline missed | Manager can still review, but without self-input | HR extends deadline or manager reviews without self-assessment |
| Calibration stalls | Ratings not finalized, downstream actions blocked | HR escalates to leadership for sign-off |
| Compensation recommendation fails | Salary revisions not generated | HR manually creates via [[Userflow/Employee-Management/employee-promotion\|Employee Promotion]] |
| Learning plan suggestion fails | Employee misses development opportunity | Manager manually creates via [[Userflow/Skills-Learning/development-plan\|Development Plan]] |

---

## Related Individual Flows

- [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]] — cycle configuration
- [[Userflow/Performance/self-assessment|Self Assessment]] — employee self-review
- [[Userflow/Performance/manager-review|Manager Review]] — manager evaluation
- [[Userflow/Performance/peer-feedback|Peer Feedback]] — 360-degree feedback
- [[Userflow/Performance/goal-setting|Goal Setting]] — goals being reviewed against
- [[Userflow/Performance/improvement-plan|Improvement Plan]] — PIP creation
- [[Userflow/Performance/succession-planning|Succession Planning]] — high-performer tracking
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] — compensation change
- [[Userflow/Skills-Learning/development-plan|Development Plan]] — learning paths

## Module References

- [[modules/performance/overview|Performance]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/skills/overview|Skills & Learning]]
- [[modules/payroll/overview|Payroll]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
