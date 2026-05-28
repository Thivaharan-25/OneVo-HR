# System Config

## Purpose

System Config manages four categories of encrypted external credentials plus platform-wide operational defaults. It is the central place where ONEVO engineers configure which AI providers, payment gateways, OAuth apps, and internal services the platform uses â€” and where those can be overridden per tenant.

It is also the escalation tool for support engineers who need to adjust a tenant's settings without involving the tenant's own admin.

## What This Module Manages

| Category | Description | Stored In |
|---|---|---|
| AI Provider Configs | LLM API keys (any provider) with live model fetch | `ai_provider_configs` |
| Payment Gateway Configs | Stripe/Paddle/PayHere credentials with account verification | `payment_gateway_configs` |
| Platform OAuth Apps | ONEVO's OAuth app registrations for customer integrations (GitHub, Microsoft, Google, Slack) | `platform_oauth_apps` |
| Platform Service Keys | ONEVO's own service API keys (Resend email, Cloudflare, Azure Blob) | `platform_service_keys` |
| Global Defaults | Platform-wide setting defaults (session TTL, invite expiry, dunning schedule) | `system_settings` |
| Per-Tenant Overrides | Setting value overrides for individual tenants | `tenant_settings` |

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `ai_provider_configs` | Read + write â€” global AI credentials encrypted at rest |
| `tenant_ai_provider_overrides` | Read + write â€” per-tenant AI key overrides |
| `platform_oauth_apps` | Read + write â€” ONEVO's OAuth developer app registrations |
| `platform_service_keys` | Read + write â€” Resend, Cloudflare, Azure Blob keys |
| `system_settings` | Read + write â€” key-value global defaults |
| `tenant_settings` | Read + write â€” tenant-specific setting overrides |
| Audit log | Write every credential or setting change |

## Key Design Points

**AI provider resolution chain:** When ONEVO calls an AI provider for a tenant, the system checks in order: (1) tenant-specific override â†’ (2) global config â†’ (3) 503 feature unavailable. Switching a tenant to their own key takes effect on the next request.

**AI model selection:** The operator enters the API key and base URL, then clicks "Fetch Models" â€” the backend calls the provider's model list endpoint using that key and returns the available models. The operator selects from the real list. Nothing is hardcoded.

**Provider-agnostic:** `provider_format` (`openai_compatible` or `anthropic`) determines only the HTTP request/response shape â€” not the URL. The same `openai_compatible` format works for OpenAI, Azure OpenAI, Mistral, Groq, local Ollama, or any compatible endpoint. The `api_base_url` is always operator-supplied; no default URL is ever hardcoded.

**Payment gateway gating:** During tenant provisioning Step 3, the gateway dropdown is filtered by the tenant's country (via `country_codes` on the gateway config). A tenant in Sri Lanka sees only PayHere gateways; a tenant in the UK sees only Stripe gateways.

**Platform OAuth Apps vs tenant integration tokens:** `platform_oauth_apps` holds ONEVO's developer credentials (client_id, client_secret) used to initiate OAuth flows. The customer's resulting access tokens are stored separately in `tenant_integration_credentials` â€” these are different things in different tables.

## Capabilities

### AI Provider Configuration
- Configure global AI provider key + model per ONEVO purpose (Agentic Chat, AI Insights, Report Generation)
- Fetch available models live from provider before saving â€” no hardcoded model names
- Test connection using stored key and base URL
- Set per-tenant AI key overrides; remove overrides to fall back to global

### Payment Gateway
- Configure global Stripe/Paddle/PayHere credentials with account verification before save

### Platform OAuth Apps
- Register ONEVO's OAuth apps for each integration provider
- Rotate client secrets
- Test OAuth app credentials with provider

### Platform Service Keys
- Store and rotate Resend, Cloudflare, Azure Blob, and other internal service keys
- Test service connection

### Global Defaults and Per-Tenant Overrides
- Edit platform-wide defaults (session timeouts, dunning schedule, invite expiry, etc.)
- Override any global default for a specific tenant for support escalation

## Navigation

| Route | Permission |
|---|---|
| `/settings/system` | `platform.system_config.read` |
| Write operations | `platform.system_config.manage` |

## Key Rules

- API keys, client secrets, and merchant secrets are AES-256 encrypted before storage and never returned by any GET response
- `api_base_url` for AI providers is always required â€” no hardcoded fallback URLs
- Gateway account verification must succeed before Save button becomes active
- All writes audit-logged with previous and new values (credentials show only `key_rotated: true`, not the key itself)

## Related

- [[developer-platform/modules/subscription-manager/overview|Subscription Manager]] â€” for global payment gateway catalog management
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog Manager]] â€” for integration catalog and module-integration links
- [[developer-platform/modules/system-config/end-to-end-logic|System Config End-to-End Logic]]

