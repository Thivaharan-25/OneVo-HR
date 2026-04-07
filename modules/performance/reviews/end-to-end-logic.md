# Reviews — End-to-End Logic

**Module:** Performance
**Feature:** Reviews

---

## Submit Review

### Flow

```
POST /api/v1/performance/reviews
  -> ReviewController.Submit(SubmitReviewCommand)
    -> [RequirePermission("performance:write")]
    -> ReviewService.SubmitAsync(command, ct)
      -> 1. Load review record, verify status = 'draft'
      -> 2. Validate: overall_rating 1.0-5.0, comments required
      -> 3. UPDATE review: overall_rating, comments, status = 'submitted'
      -> 4. If all reviews for employee in cycle are submitted:
         -> Calculate average rating across all reviewers
      -> Return Result.Success(reviewDto)
```

### Key Rules

- **Review types:** self, manager, peer, 360 — each has its own review record.
- **Productivity score** is optional — only populated if cycle has `include_productivity_data = true`.

## Related

- [[reviews|Reviews Overview]]
- [[review-cycles]]
- [[feedback]]
- [[goals-okr]]
- [[event-catalog]]
- [[error-handling]]
