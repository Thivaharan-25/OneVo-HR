# Feature Flags — End-to-End Logic

**Module:** Shared Platform
**Feature:** Feature Flags

---

## Check Feature Flag

### Flow

```
Internal call from any module:
  -> IFeatureFlagService.IsEnabledAsync(flagKey, ct)
    -> 1. Check Redis cache first
    -> 2. If cache miss: query feature_flags WHERE flag_key AND tenant_id
    -> 3. Evaluate conditions (percentage rollout, user segment)
    -> 4. Cache result (TTL: 5 min)
    -> Return true/false
```

## Toggle Feature Flag

### Flow

```
PUT /api/v1/feature-flags/{key}
  -> FeatureFlagController.Toggle(key, ToggleCommand)
    -> [RequirePermission("settings:admin")]
    -> FeatureFlagService.ToggleAsync(key, isEnabled, ct)
      -> UPDATE feature_flags SET is_enabled = @value
      -> Invalidate Redis cache for this flag
      -> Return Result.Success()

```

## Related

- [[feature-flags|Overview]]
- [[tenant-management]]
- [[subscriptions-billing]]
- [[event-catalog]]
- [[error-handling]]
