# Skill Assessments — End-to-End Logic

**Module:** Skills
**Feature:** Skill Assessments (Quiz & Validation)

---

## Take Skill Assessment (Quiz)

### Flow

```
POST /api/v1/skills/assess
  -> SkillAssessmentController.Submit(SubmitAssessmentCommand)
    -> [RequirePermission("skills:write")]
    -> SkillAssessmentService.SubmitAsync(command, ct)
      -> 1. Load skill_questions for the skill
      -> 2. For each response:
         -> INSERT into skill_assessment_responses
         -> Auto-score MCQ: check selected_option_id.is_correct
      -> 3. Calculate overall score
      -> 4. If score meets threshold:
         -> UPDATE employee_skills proficiency_level
      -> Return Result.Success(assessmentResultDto)
```

## Request Skill Validation

### Flow

```
POST /api/v1/skills/validate
  -> SkillValidationController.Request(RequestValidationCommand)
    -> [RequirePermission("skills:write")]
    -> SkillValidationService.RequestAsync(command, ct)
      -> 1. INSERT into skill_validation_requests
         -> from_level (current), to_level (requested)
         -> validator_id (manager or peer)
      -> 2. Notify validator
      -> Return Result.Success(requestDto)
```

## Related

- [[modules/skills/skill-assessments/overview|Skill Assessments]] — feature overview
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] — skills and question banks
- [[modules/skills/employee-skills/overview|Employee Skills]] — proficiency updated from assessment score
- [[backend/messaging/event-catalog|Event Catalog]] — AssessmentSubmitted, SkillLevelUpdated events
- [[backend/messaging/error-handling|Error Handling]] — invalid answer type and duplicate submission errors
