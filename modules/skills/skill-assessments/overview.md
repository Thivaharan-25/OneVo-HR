# Skill Assessments

**Module:** Skills & Learning  
**Feature:** Skill Assessments

---

## Phase Rule

This feature is Phase 2 for quiz-based skill assessments. Basic manager validation of employee skill requests is Phase 1 and belongs to [[modules/skills/employee-skills/overview|Employee Skills]].

## Purpose

Quiz-based skill evaluation with MCQ, text, and file upload question types.

## Database Tables

### `skill_questions`
Fields: `skill_id`, `question_text`, `question_type` (`multiple_choice`, `text`, `file_upload`), `sort_order`, `is_required`.

### `skill_question_options`
MCQ options: `question_id`, `option_text`, `is_correct`, `sort_order`.

### `skill_assessment_responses`
Employee responses: `employee_id`, `question_id`, `selected_option_id`, `text_answer`, `file_record_id`, `score`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/skills/assess` | `skills:write` | Submit assessment |

## Related

- [[skills|Skills Module]] â€” parent module
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] â€” skills that assessments evaluate
- [[modules/skills/employee-skills/overview|Employee Skills]] â€” skill records updated on assessment completion
- [[modules/skills/development-plans/overview|Development Plans]] â€” plans that include assessment milestones
- [[infrastructure/multi-tenancy|Multi Tenancy]] â€” tenant-scoped assessment questions and responses
- [[backend/messaging/event-catalog|Event Catalog]] â€” AssessmentSubmitted events
- [[backend/messaging/error-handling|Error Handling]] â€” invalid response types and scoring errors
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] â€” implementation task


