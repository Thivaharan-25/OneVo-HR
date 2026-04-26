# Notification Enrichment

**Module:** Discrepancy Engine
**Feature:** AI Notification Enrichment

---

## Purpose

When a `DiscrepancyCriticalDetected` event fires, this feature enriches the manager notification with a 2-3 sentence neutral AI-generated insight using the employee's 30-day discrepancy history as context. It does NOT participate in detection or severity classification — those remain deterministic.

## What It Does

1. `DiscrepancyEnrichmentHandler` receives `DiscrepancyCriticalDetected` via MediatR
2. Fetches 30-day discrepancy history for the employee
3. If no history: sends a default "first event" message (no AI call)
4. If history exists: makes a single Claude API call (max 300 tokens) to generate neutral narrative
5. Sends a `DiscrepancyAlertEnriched` notification to the manager

## Key Rules

- **AI is NOT in the detection loop.** Claude is called AFTER severity is already classified.
- **Only fires on `critical` severity.** Low/high alerts use the existing non-enriched path.
- **No AI call if no history.** Prevents meaningless insights and saves cost for new employees.
- **Model:** `claude-sonnet-4-6` (cost-efficient at 300 tokens max)
- **System prompt enforces:** neutral tone, no accusation, pattern-focused

## Event Flow

```
DiscrepancyEngineJob publishes DiscrepancyCriticalDetected
    → DiscrepancyEnrichmentHandler.Handle()
        → IDiscrepancyEnrichmentService.EnrichAndNotifyAsync()
            → IDiscrepancyEngineService.GetDiscrepanciesForRangeAsync() (30-day history)
            → IAnthropicInsightProvider.GetInsightAsync() (if history exists)
            → INotificationService.SendAsync(DiscrepancyAlertEnriched)
```

## Interfaces

| Interface | Implementation | Purpose |
|:----------|:---------------|:--------|
| `IAnthropicInsightProvider` | `AnthropicInsightProvider` | Thin wrapper over `AnthropicClient` for testability |
| `IDiscrepancyEnrichmentService` | `DiscrepancyEnrichmentService` | Orchestrates history fetch + AI call + notification |

The service depends on `IAnthropicInsightProvider`, NOT on `AnthropicClient` directly — this keeps unit tests free of real API calls.

## Prompt Template

```
An employee has a {severity} discrepancy alert today with {unaccountedMinutes} unaccounted minutes.

Past 30 days:
- Critical events: {criticalCount}
- High events: {highCount}
- Average unaccounted minutes: {avgUnaccounted}

Provide a 2-3 sentence neutral, factual insight for the manager.
Do not be accusatory. Note whether this is a pattern or an anomaly.
```

## Configuration

Set `ANTHROPIC__APIKEY` in Railway environment variables (never commit to source).

```json
// appsettings.json (key present, value blank — provided via env var in production)
{
  "Anthropic": {
    "ApiKey": ""
  }
}
```

## Registration

`AnthropicClient` is registered as a singleton (one HTTP client). `IAnthropicInsightProvider` and `IDiscrepancyEnrichmentService` are registered as scoped. `DiscrepancyEnrichmentHandler` is auto-registered by MediatR assembly scan.

## Related

- [[modules/discrepancy-engine/overview|Discrepancy Engine Overview]]
- [[modules/discrepancy-engine/statistical-baselines/overview|Statistical Baselines]] — severity classification that triggers `DiscrepancyCriticalDetected`
- [[modules/notifications/overview|Notifications]] — `DiscrepancyAlertEnriched` notification type
- [[backend/messaging/event-catalog|Event Catalog]] — `DiscrepancyCriticalDetected`
