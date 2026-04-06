# Module: Skills & Learning

**Namespace:** `ONEVO.Modules.Skills`
**Pillar:** 1 — HR Management
**Owner:** Dev 3 + Dev 4 (Week 3)
**Tables:** 15

---

## Purpose

Manages skills taxonomy, employee skill assessments, learning courses, LMS provider integrations, certifications, and individual development plans. Supports skill gap analysis for workforce planning.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[core-hr]] | `IEmployeeService` | Employee context |
| **Depends on** | [[org-structure]] | `IOrgStructureService` | Job family skill requirements |

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

| Table | Purpose |
|:------|:--------|
| `skill_categories` | Skill groupings (e.g., "Technical", "Soft Skills") |
| `skills` | Individual skill definitions |
| `employee_skills` | Employee-skill mapping with proficiency level |
| `skill_assessments` | Assessment records (self, manager, peer) |
| `skill_endorsements` | Peer endorsements |
| `job_skill_requirements` | Required skills per job title |
| `courses` | Learning courses |
| `course_enrollments` | Employee course enrollment |
| `course_completions` | Completion records with scores |
| `lms_providers` | External LMS connections |
| `certifications` | Certification definitions |
| `employee_certifications` | Employee certification records with expiry |
| `development_plans` | Individual development plans |
| `development_plan_items` | Plan action items |
| `skill_matrices` | Department skill heat maps |

---

## Key Business Rules

1. **Skill proficiency levels:** 1 (Beginner) → 5 (Expert).
2. **Skill gap analysis** compares `employee_skills` against `job_skill_requirements` for their job title.
3. **`tenant_id`** is used consistently on all tables — no column mapping workarounds needed.
4. **Certification expiry tracking** — Hangfire job alerts 30 days before expiry.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/skills` | `skills:read` | List all skills |
| GET | `/api/v1/skills/employee/{employeeId}` | `skills:read` | Employee skills profile |
| POST | `/api/v1/skills/assess` | `skills:write` | Submit assessment |
| POST | `/api/v1/skills/validate` | `skills:validate` | Validate/endorse skill |
| GET | `/api/v1/courses` | `skills:read` | List courses |
| POST | `/api/v1/courses/enroll` | `skills:write` | Enroll in course |
| GET | `/api/v1/skills/gap-analysis/{employeeId}` | `skills:manage` | Skill gap report |
| GET | `/api/v1/development-plans/{employeeId}` | `skills:read` | Development plan |

See also: [[module-catalog]], [[core-hr]], [[performance]]
