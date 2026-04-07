# Recognitions — End-to-End Logic

**Module:** Performance
**Feature:** Recognitions

---

## Give Recognition

### Flow

```
POST /api/v1/performance/recognitions
  -> RecognitionController.Create(CreateRecognitionCommand)
    -> [RequirePermission("performance:write")]
    -> RecognitionService.CreateAsync(command, ct)
      -> 1. Validate: to_employee_id != from_employee_id (can't self-recognize)
      -> 2. Validate category: teamwork, innovation, leadership, other
      -> 3. INSERT into recognitions
         -> points = configurable per category
      -> 4. Notify recipient via notifications
      -> Return Result.Success(recognitionDto)
```

## Related

- [[recognitions|Recognitions Overview]]
- [[reviews]]
- [[feedback]]
- [[event-catalog]]
- [[error-handling]]
