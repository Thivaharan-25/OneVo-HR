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

- [[skill-assessments]] — feature overview
- [[skill-taxonomy]] — skills and question banks
- [[employee-skills]] — proficiency updated from assessment score
- [[event-catalog]] — AssessmentSubmitted, SkillLevelUpdated events
- [[error-handling]] — invalid answer type and duplicate submission errors
