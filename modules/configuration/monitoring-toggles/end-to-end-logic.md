# Monitoring Toggles — End-to-End Logic

**Module:** Configuration
**Feature:** Monitoring Feature Toggles

---

## Get Monitoring Toggles

### Flow

```
GET /api/v1/settings/monitoring
  -> MonitoringController.GetToggles()
    -> [RequirePermission("monitoring:view-settings")]
    -> ConfigurationService.GetMonitoringTogglesAsync(tenantId, ct)
      -> Query monitoring_feature_toggles WHERE tenant_id
      -> Map to MonitoringTogglesDto
      -> Return Result.Success(togglesDto)
```

## Update Monitoring Toggles

### Flow

```
PUT /api/v1/settings/monitoring
  -> MonitoringController.UpdateToggles(UpdateTogglesCommand)
    -> [RequirePermission("monitoring:configure")]
    -> ConfigurationService.UpdateMonitoringTogglesAsync(command, ct)
      -> 1. Load existing toggles
      -> 2. Apply changes
      -> 3. UPDATE monitoring_feature_toggles
      -> 4. Invalidate monitoring toggle cache (Redis)
      -> 5. Log to audit_logs
      -> 6. Note: Agent policy changes take effect on next agent poll (up to 5 min)
      -> Return Result.Success(updatedDto)
```

### Key Rules

- **Industry profile sets defaults at tenant signup** — admin can change any toggle anytime.
- **Server must double-validate** toggles even though agent checks policy on login.
- **Toggle changes propagate to agents** on next policy poll (pull-based, up to 5 min delay).

## Related

- [[frontend/architecture/overview|Monitoring Toggles Overview]]
- [[frontend/architecture/overview|Employee Overrides]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
