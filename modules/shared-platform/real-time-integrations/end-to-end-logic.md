# Real-Time Integrations — End-to-End Logic

**Module:** Shared Platform
**Feature:** Real-Time Integrations (API Keys, Webhooks, Rate Limits)

---

## Create API Key

### Flow

```
POST /api/v1/integrations/api-keys
  -> ApiKeyController.Create(CreateApiKeyCommand)
    -> [RequirePermission("settings:admin")]
    -> ApiKeyService.CreateAsync(command, ct)
      -> 1. Generate random API key
      -> 2. Hash with SHA-256 -> store key_hash
      -> 3. Store key_prefix (first 8 chars) for identification
      -> 4. INSERT into api_keys
      -> Return plaintext key (shown once only)
```

## Register Webhook Endpoint

### Flow

```
POST /api/v1/integrations/webhooks
  -> WebhookController.Register(RegisterWebhookCommand)
    -> [RequirePermission("settings:admin")]
    -> WebhookService.RegisterAsync(command, ct)
      -> 1. Validate URL is reachable (optional health check)
      -> 2. Generate HMAC signing secret
      -> 3. INSERT into webhook_endpoints
         -> events: array of subscribed event types
      -> Return Result.Success(endpointDto with signing secret)
```

## Deliver Webhook

### Flow

```
When domain event fires and webhook_endpoints subscribe to it:
  -> WebhookDeliveryService.DeliverAsync(event, ct)
    -> 1. Find matching webhook_endpoints by event type
    -> 2. For each endpoint:
       -> Sign payload with HMAC-SHA256
       -> POST to endpoint URL
       -> Log delivery in webhook_deliveries
       -> If failure: retry up to 3 times with exponential backoff

```

## Related

- [[modules/shared-platform/real-time-integrations/overview|Overview]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[modules/shared-platform/sso-authentication/overview|Sso Authentication]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
