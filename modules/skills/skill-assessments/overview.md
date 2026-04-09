# Skill Assessments

**Module:** Skills & Learning  
**Feature:** Skill Assessments

---

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

- [[skills|Skills Module]] — parent module
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] — skills that assessments evaluate
- [[modules/skills/employee-skills/overview|Employee Skills]] — skill records updated on assessment completion
- [[modules/skills/development-plans/overview|Development Plans]] — plans that include assessment milestones
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped assessment questions and responses
- [[backend/messaging/event-catalog|Event Catalog]] — AssessmentSubmitted events
- [[backend/messaging/error-handling|Error Handling]] — invalid response types and scoring errors
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — implementation task
