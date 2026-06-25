# System Config

## Purpose

System Config manages four categories of encrypted external credentials plus platform-wide operational defaults. It is the central place where ONEVO engineers configure which AI providers, payment gateways, OAuth apps, internal services, email, storage, and agent policy defaults the platform uses.

Tenant-specific overrides are edited from Tenant Detail -> Settings so operators work from the tenant context. System Config may link to those tenant override screens, but it is not the primary per-tenant override workspace.

## What This Module Manages

| Category | Description | Stored In |
|---|---|---|
| AI Provider Configs | LLM API keys (any provider) with live model fetch | `ai_provider_configs` |
| Payment Gateway Configs | Stripe/Paddle/PayHere gateway metadata, credential versions, and country routing | `payment_gateway_configs`, `payment_gateway_credentials`, `payment_gateway_country_routes` |
| Platform OAuth Apps | ONEVO's OAuth app registrations and credential versions for customer integrations (GitHub, Zoom, Microsoft, Google; Slack is Phase 2) | `platform_oauth_apps`, `platform_oauth_app_credentials` |
| Platform Service Keys | ONEVO's own service API keys (Resend email, Cloudflare DNS/WAF, Cloudflare R2) | `platform_service_keys` |
| Global Settings | Platform-wide setting defaults (session TTL, invite expiry, dunning schedule) | `system_settings` |
| Global Policies | Platform-wide auth/security policy defaults such as MFA, login method defaults, and failed-login lockout | `system_settings`, `tenant_auth_policies` |
| Runtime Flag Definitions | Global runtime flag definitions, defaults, rollout percentages, module linkage, and feature-key linkage | `feature_flags` |
| Tenant Override Targets | Setting keys that may be overridden from Tenant Detail -> Settings | `tenant_settings` |

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `ai_provider_configs` | Read + write - global AI credentials encrypted at rest |
| `tenant_ai_provider_overrides` | Read + write - per-tenant AI key overrides |
| `payment_gateway_configs` | Read + write - payment gateway metadata only |
| `payment_gateway_credentials` | Write/rotate - encrypted payment gateway credential versions |
| `payment_gateway_country_routes` | Read + write - country/environment gateway routing |
| `platform_oauth_apps` | Read + write - ONEVO's OAuth developer app metadata |
| `platform_oauth_app_credentials` | Write/rotate - ONEVO OAuth app secret versions |
| `platform_service_keys` | Read + write - Resend, Cloudflare DNS/WAF, Cloudflare R2 keys |
| `system_settings` | Read + write - key-value global defaults |
| `feature_flags` | Read + write - global runtime flag definitions |
| `tenant_settings` | Read + write - tenant-specific setting overrides |
| Audit log | Write every credential or setting change |

## Key Design Points

**AI provider resolution chain:** When ONEVO calls an AI provider for a tenant, the system checks in order: (1) tenant-specific override -> (2) global config -> (3) 503 feature unavailable. Switching a tenant to their own key takes effect on the next request.

**AI model selection:** The operator enters the API key and base URL, then clicks "Fetch Models" - the backend calls the provider's model list endpoint using that key and returns the available models. The operator selects from the real list. Nothing is hardcoded.

**Provider-agnostic:** `provider_format` (`openai_compatible` or `anthropic`) determines only the HTTP request/response shape - not the URL. The same `openai_compatible` format works for OpenAI, Azure OpenAI, Mistral, Groq, local Ollama, or any compatible endpoint. The `api_base_url` is always operator-supplied; no default URL is ever hardcoded.

**Payment gateway routing:** During payment gateway setup, the operator selects one or more applicable countries by country name. The backend stores country codes internally in `payment_gateway_country_routes`. One gateway config can serve many countries, but each country can have only one active gateway route per environment. During tenant provisioning Step 3, the payment gateway is resolved from the tenant's country route; tenant owners do not choose the gateway.

**Platform OAuth Apps vs tenant/employee integration tokens:** `platform_oauth_apps` holds ONEVO's OAuth app metadata such as `client_id`, while `platform_oauth_app_credentials` stores ONEVO's encrypted OAuth app secrets. Tenant-scope connected integration tokens (`connection_scope = 'tenant'`) are stored separately in `tenant_integration_credentials`. Employee-scope tokens (`connection_scope = 'employee'`) such as Google/Outlook Calendar live in `external_calendar_connections` with the user's calendar sync state.

## Capabilities

### AI Provider Configuration
- Configure global AI provider key + model per ONEVO purpose (AI Insights and Report Generation in Phase 1; Agentic Chat in Phase 2)
- Fetch available models live from provider before saving - no hardcoded model names
- Test connection using stored key and base URL
- Support per-tenant AI key overrides edited from Tenant Detail -> Settings; remove overrides to fall back to global

### Payment Gateway
- Configure global Stripe/Paddle/PayHere gateway metadata and credential versions with account verification before save
- Assign one or more countries to the gateway config by country name
- Block a country assignment if that country already has another active gateway route in the same environment

### Platform OAuth Apps
- Register ONEVO's OAuth apps for each integration provider
- Rotate client secrets
- Test OAuth app credentials with provider

### Platform Service Keys
- Store and rotate Resend, Cloudflare DNS/WAF, Cloudflare R2, and other internal service keys
- Test service connection

### Global Settings
- Edit platform-wide defaults (session timeouts, dunning schedule, invite expiry, etc.)
- Define which settings can be overridden from Tenant Detail -> Settings for support escalation

### Global Policies
- Edit, publish, and optionally propagate auth/security policy defaults from System Config -> Global Policies
- Keep monitoring, work-hour, retention, and privacy-mode presets in Template Management, not Global Policies

### Runtime Flag Definitions
- Create, edit, and deactivate global runtime flag definitions from System Config -> Runtime Flags, if this internal screen is exposed.
- Define flag key, owning module, commercial feature key, default value, rollout percentage, phase, and description.
- Tenant-specific ON/OFF overrides are not managed here; they are managed from Tenant Management -> Tenant Detail -> Runtime Overrides.

## Navigation

| Route | Permission |
|---|---|
| `/settings/system` | `platform.system_config.read` |
| Write operations | `platform.system_config.manage` |

## Key Rules

- API keys, client secrets, and merchant secrets are AES-256 encrypted in dedicated credential tables before storage and never returned by any GET response
- `api_base_url` for AI providers is always required - no hardcoded fallback URLs
- Gateway account verification must succeed before Save button becomes active
- All writes audit-logged with previous and new values (credentials show only `key_rotated: true`, not the key itself)

## Related

- [[developer-platform/modules/subscription-manager/overview|Subscription Plans]] - for paid plan catalog management
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog Manager]] - for integration catalog and module-integration links
- [[developer-platform/modules/system-config/end-to-end-logic|System Config End-to-End Logic]]
