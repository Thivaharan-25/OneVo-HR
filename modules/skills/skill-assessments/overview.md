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
- [[skill-taxonomy]] — skills that assessments evaluate
- [[employee-skills]] — skill records updated on assessment completion
- [[development-plans]] — plans that include assessment milestones
- [[multi-tenancy]] — tenant-scoped assessment questions and responses
- [[event-catalog]] — AssessmentSubmitted events
- [[error-handling]] — invalid response types and scoring errors
- [[WEEK4-supporting-bridges]] — implementation task
