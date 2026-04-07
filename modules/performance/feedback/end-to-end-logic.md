# Feedback — End-to-End Logic

**Module:** Performance
**Feature:** Feedback Requests

---

## Request Feedback

### Flow

```
POST /api/v1/performance/feedback/request
  -> FeedbackController.Request(RequestFeedbackCommand)
    -> [RequirePermission("performance:write")]
    -> FeedbackService.RequestAsync(command, ct)
      -> 1. Validate: respondent_id is active employee
      -> 2. INSERT into feedback_requests
         -> status = 'pending'
         -> cycle_id nullable (can be ad-hoc)
      -> 3. Notify respondent via notifications
      -> Return Result.Success(requestDto)
```

## Submit Feedback

### Flow

```
PUT /api/v1/performance/feedback/{id}
  -> FeedbackController.Submit(id, SubmitFeedbackCommand)
    -> [Authenticated] (respondent only)
    -> FeedbackService.SubmitAsync(id, command, ct)
      -> 1. Verify caller is the respondent
      -> 2. UPDATE feedback_text, status = 'completed'
      -> Return Result.Success()
```

## Related

- [[feedback|Feedback Overview]]
- [[review-cycles]]
- [[reviews]]
- [[event-catalog]]
- [[error-handling]]
