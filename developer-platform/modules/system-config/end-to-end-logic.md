# System Config - End-to-End Logic

## Purpose

System Config manages four categories of encrypted external credential storage plus platform-wide defaults:

1. **AI Provider Configs** - LLM API keys with live model fetch from provider
2. **Payment Gateway Configs** - Stripe/Paddle/PayHere credentials with live account verification and country routing
3. **Platform OAuth App Registrations** - ONEVO's developer app credentials for customer-facing integrations (GitHub, Microsoft, Google, Slack)
4. **Platform Service Keys** - ONEVO's own service keys that the platform uses internally (Resend email, etc.)

Plus: Global Settings for platform-wide defaults. Tenant-specific overrides are edited from Tenant Detail -> Settings so the operator stays in tenant context.

**Route:** `/settings/system`
**Permission:** `platform.system_config.read`

---

## Screen Tabs

- Global Settings
- AI Provider Configuration
- Payment Gateways
- Platform OAuth Apps <- ONEVO's OAuth app registrations for customer integrations
- Platform Service Keys <- Resend and other internal platform services
- Email / SMTP
- Storage Configuration
- Agent Policy Defaults

---

## AI Provider Configuration

### Design

The operator enters an API key, then the system **fetches the available models directly from that provider** and presents them as a dropdown. The operator selects from real models - nothing is hardcoded in ONEVO.

**Why model fetch instead of free text:**
- Prevents typos in model names that cause silent failures
- Reflects what the operator's API key actually has access to (some keys are restricted to certain models)
- Automatically shows new models when the provider adds them - no ONEVO release needed

**Why per-purpose, not per-provider:**
- Different ONEVO features may use different providers or models
- Agentic Chat may use OpenAI while AI Insights uses Anthropic - or both use OpenAI with different models
- A tenant can override one purpose without affecting others

### AI Purpose Registry

| Purpose Key | Label | Used By |
|---|---|---|
| `agentic_chat` | "Agentic Chat" | Chat module - tenant user AI conversations |
| `ai_insights` | "AI Insights Engine" | Exception explanations, analytics summaries |
| `report_generation` | "AI Report Generation" | AI-generated report content |

### Lookup Chain (unchanged from design)

```
IAiProviderResolver.ResolveAsync(tenantId, purpose)

Step 1: tenant_ai_provider_overrides WHERE tenant_id = T AND purpose = P AND is_active = true
Step 2: ai_provider_configs (global) WHERE purpose = P AND is_active = true
Step 3: 503 - feature unavailable for this tenant
```

---

### AI Provider Config - Create / Edit Flow

#### Step 1: Provider Type, Base URL, and API Key

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Config Name | "Configuration Name" | Text input | Yes | e.g. "Primary Chat Provider", "Analytics AI" - operator names it freely |
| Logo | "Provider Logo" | File upload | No | PNG, SVG, or JPEG. Max 500KB. Upload via `POST /admin/v1/uploads/ai-provider-logo` -> returns `logo_url`. Shown in the AI Provider list in System Config. Helps operators distinguish configs at a glance when multiple providers are configured. |
| Purpose | "Purpose" | Dropdown from purpose registry | Yes | Which ONEVO feature this powers |
| Provider API Format | "Provider API Format" | Dropdown | Yes | `openai_compatible` or `anthropic` - determines the HTTP request/response shape only, not the provider |
| API Base URL | "API Base URL" | Text input | **Yes - required** | The full base URL for this provider's API. No default, no fallback. Examples: `https://api.openai.com`, `https://api.anthropic.com`, `https://your-resource.openai.azure.com/openai`, `https://api.mistral.ai`, `http://localhost:11434` |
| API Key | "API Key" | Password input | Yes | Paste whatever the provider gives you. No format validation - the fetch step will tell you if it's wrong. |

**After entering base URL and key -> click "Fetch Available Models" button.**

#### Step 2: Fetch Available Models

**API call from frontend:** `POST /admin/v1/system-config/ai-providers/fetch-models`

```json
{
  "provider_format": "openai_compatible",
  "api_base_url": "https://api.openai.com",
  "api_key": "sk-..."
}
```

**Backend does - determined entirely by `provider_format` and the operator-supplied `api_base_url`:**
- `openai_compatible`: `GET {api_base_url}/v1/models` with header `Authorization: Bearer {api_key}`
- `anthropic`: `GET {api_base_url}/v1/models` with headers `x-api-key: {api_key}` and `anthropic-version: 2023-06-01`

The `api_base_url` is always the operator's input - never defaulted by ONEVO. This means the same `openai_compatible` format works for any provider that follows the OpenAI API spec (OpenAI, Azure OpenAI, Mistral, Groq, local Ollama, or any other compatible endpoint).

- Returns the provider's model list

**Response (success):**
```json
{
  "models": [
    { "id": "gpt-4o", "display_name": "GPT-4o" },
    { "id": "gpt-4o-mini", "display_name": "GPT-4o mini" },
    { "id": "gpt-3.5-turbo", "display_name": "GPT-3.5 Turbo" }
  ],
  "account_info": {
    "organization": "Acme Platform Ltd",
    "tier": "paid"
  }
}
```

**Response (invalid key):**
```json
{
  "error": "provider_auth_failed",
  "message": "The API key is invalid or expired. Check the key and try again."
}
```

**UI behaviour:**
- Success: Model dropdown populates with fetched list. Account info shown as a green confirmation badge.
- Failure: Error callout shown below the API Key field. Operator must fix the key before proceeding.
- The API key is NOT saved at this point - it is only used for the fetch. Save happens in Step 3.

#### Step 3: Select Model and Remaining Fields

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Model | "Model" | Dropdown (populated from fetch) | Yes | Options come from the fetch result - operator selects, not types |
| Request Timeout | "Request Timeout (seconds)" | Number | Yes | Default: 60 |
| Max Retries | "Max Retries on Failure" | Number | Yes | Default: 2 |
| Is Active | "Active" | Toggle | Yes | |

**Save API:** `POST /admin/v1/system-config/ai-providers` (create) or `PUT /admin/v1/system-config/ai-providers/{configId}` (update)

```json
{
  "config_name": "Primary Chat Provider",
  "purpose": "agentic_chat",
  "provider_format": "openai_compatible",
  "api_base_url": "https://api.example-provider.com",
  "model": "<selected from fetch result>",
  "api_key": "<encrypted - never returned>",
  "request_timeout_seconds": 60,
  "max_retries": 2,
  "is_active": true
}
```

**`api_base_url` is always required - no default, no fallback. The operator must enter the provider's URL. `model` is always set from the fetch result dropdown, never typed free-form.**

`api_key` is AES-256 encrypted before writing. Never returned by any GET response.

**State written:** `ai_provider_configs` upserted. Audit log with `key_rotated: true`.

#### Rotate Key (change API key, keep model)

Click "Rotate Key" on existing config row -> opens a panel with only the API Key field and a new "Fetch Models" button to re-verify the new key. Model selection only shown if the new key's available models differ from the saved model (e.g., downgraded key no longer has access to the saved model - forces re-selection).

---

### Per-Tenant AI Override

Same step-by-step flow as global config. Entry from:
1. Tenant Detail -> Settings -> AI Configuration -> Set Override
2. Optional cross-link from System Config -> AI Provider Configuration -> tenant override usage

**Set:** `PUT /admin/v1/tenants/{id}/ai-provider-override/{purpose}`

Same request body as global. Lookup chain applies immediately on next AI call.

**Remove:** `DELETE /admin/v1/tenants/{id}/ai-provider-override/{purpose}` - falls back to global.

---

## Payment Gateway Configuration

### Design

Payment gateways are configured at global level in System Config -> Payment Gateways. System Config owns:
- A live **account verification + capabilities fetch** on credential entry (same principle as AI model fetch)
- Country-to-gateway routing for tenant payment collection
- The global credential model used by country routes during tenant provisioning and billing

### Payment Gateway Credential Entry Flow

#### Step 1: Provider and Credentials

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Logo | "Gateway Logo" | File upload | No | PNG, SVG, or JPEG. Max 500KB. Recommended: 256x256px. Upload via `POST /admin/v1/uploads/gateway-logo` -> returns `logo_url` -> submitted with the form. Shown in the gateway selection dropdown during tenant provisioning Step 3, in the Subscription Plans gateway list, and in the Tenant Detail -> Subscriptions tab. |
| Provider | "Payment Provider" | Dropdown: Stripe / Paddle / PayHere | Yes | Determines which credential fields appear below |
| Display Name | "Configuration Label" | Text input | Yes | e.g. "Paddle Global Production", "PayHere Sri Lanka" |
| Environment | "Environment" | Radio: Sandbox / Production | Yes | |
| Applicable Countries | "Applicable Countries" | Country-name multi-select | Yes | Operator sees country names; backend stores ISO country codes as route rows. One gateway config can be assigned to multiple countries. |

**Paddle credentials:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| API Key | "Paddle API Key" | Password input | Yes | AES-256 encrypted |
| Seller ID | "Paddle Seller ID" | Text input | Yes | Numeric seller ID from Paddle dashboard |
| Webhook Secret | "Paddle Webhook Secret" | Password input | Yes | `pdl_ntfset_...` - validates `Paddle-Signature` header (HMAC-SHA256) |

**PayHere credentials:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Merchant ID | "PayHere Merchant ID" | Text input | Yes | |
| Merchant Secret | "PayHere Merchant Secret" | Password input | Yes | AES-256 encrypted |
| Webhook Secret | "PayHere Webhook Secret" | Password input | Yes | |

#### Step 2: Verify Account

After entering credentials -> click "Verify Account" button.

**API:** `POST /admin/v1/system-config/payment-gateways/verify`

```json
{
  "provider": "paddle",
  "credentials": {
    "api_key": "pdl_test_...",
    "seller_id": "12345",
    "webhook_secret": "pdl_ntfset_..."
  }
}
```

**Backend does:** Calls the provider's account verification endpoint using the entered credentials. The backend knows which endpoint and request format to use based on the `provider` field - the URL is not entered by the operator, it is part of the provider's integration implementation in the backend. Returns account name, country, default currency, and enabled payment methods.

**Response (success):**
```json
{
  "status": "verified",
  "account_name": "Acme Corp Payments Ltd",
  "country": "GB",
  "default_currency": "gbp",
  "enabled_payment_methods": ["card", "bacs_debit", "bank_transfer"],
  "charges_enabled": true,
  "payouts_enabled": true
}
```

**Response (failure):**
```json
{
  "status": "error",
  "message": "No such account: acct_incorrect. Check the Account ID and try again."
}
```

UI shows verified account details as a green confirmation card before allowing save. Operator must see "verified" before Save button becomes active.

#### Step 3: Save Gateway And Country Routes

**API:** `POST /admin/v1/system-config/payment-gateways`

```json
{
  "provider": "paddle",
  "display_name": "Paddle Global Production",
  "environment": "production",
  "country_codes": ["GB", "US", "AU"],
  "credentials": {
    "api_key": "pdl_live_...",
    "seller_id": "12345",
    "webhook_secret": "pdl_ntfset_..."
  },
  "is_active": true
}
```

**Backend does:**
- Saves encrypted credentials in `payment_gateway_configs`.
- Creates one `payment_gateway_country_routes` row per selected country.
- Rejects save if any selected country already has another active route in the same environment.

**Conflict example:**

```json
{
  "error": "gateway_country_route_conflict",
  "message": "Sri Lanka is already assigned to PayHere Sri Lanka Production for production."
}
```

#### Gateway Resolution During Tenant Creation (Step 3 of Wizard)

When operator opens Step 3, the payment gateway is resolved by:
- `is_active = true`
- active `payment_gateway_country_routes.country_code` matches the tenant's country from Step 1
- route `environment` matches the current platform environment

So a tenant in `LK` (Sri Lanka) resolves to the one active production gateway route for Sri Lanka. If Sri Lanka is assigned to PayHere, Stripe cannot also be assigned to Sri Lanka in production unless the PayHere route is deactivated first. This enforces "one country, one active gateway per environment" while still allowing one gateway config to cover many countries.

**API for resolving the gateway:** `GET /admin/v1/payment-gateways/resolve?country={countryCode}`

---

## Platform OAuth App Registrations

### What This Section Is

When a tenant wants to connect GitHub, Microsoft Teams, Google Calendar, or Slack, they click "Connect" in the ONEVO app and go through an OAuth flow. That OAuth flow uses **ONEVO's registered OAuth app** with each provider - ONEVO is the app developer, the tenant is the user authorising access.

This section stores ONEVO's OAuth app credentials (client ID, client secret) for each integration provider. These are **ONEVO's developer credentials**, not the tenant's.

**These are NOT the same as tenant integration tokens** (which are stored per-tenant when the customer completes OAuth).

### Platform OAuth App List Screen

**Route:** `/settings/system/oauth-apps`

| Column | Description |
|---|---|
| Provider | GitHub / Microsoft / Google / Slack with logo |
| App Name | ONEVO's registered app name with that provider |
| Integrations Enabled | Which ONEVO integrations use this app registration |
| Status | Configured (green) / Not Configured (gray) / Error (red) |
| Last Verified | Timestamp |
| Actions | Edit, Test, Rotate Secret |

### Configure Platform OAuth App - Fields

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Provider Key | "Provider Key (Slug)" | Text input | Yes | Lowercase, hyphens only, unique - operator-set identifier used to link this OAuth app to integration catalog entries. e.g. `github`, `microsoft`, `google`, `slack`. Permanent after integrations use it. |
| Logo | "Provider Logo" | File upload | No | PNG, SVG, or JPEG. Max 500KB. Recommended: 256x256px. Upload via `POST /admin/v1/uploads/oauth-app-logo` -> returns `logo_url`. Shown in the Platform OAuth Apps list, in System Config, and wherever this provider appears in the developer console UI. |
| App Name | "ONEVO App Name at Provider" | Text input | Yes | The name shown to customers on the OAuth consent screen when they authorise ONEVO's app. e.g. "ONEVO Workspace" |
| Client ID | "OAuth Client ID" | Text input | Yes | Public identifier for ONEVO's registered app - not encrypted, used in OAuth redirect URLs |
| Client Secret | "OAuth Client Secret" | Password input | Yes | AES-256 encrypted - never returned by API after save |
| Authorization URL | "Authorization URL" | Text input | Yes | Full URL where customers are redirected to log in and authorise. e.g. `https://github.com/login/oauth/authorize` |
| Token URL | "Token Exchange URL" | Text input | Yes | Full URL ONEVO calls to exchange the OAuth code for tokens. e.g. `https://github.com/login/oauth/access_token` |
| Default Scopes | "OAuth Scopes" | Tag input (space-separated) | Yes | Scopes requested from the customer's account during OAuth. e.g. `repo read:org` for GitHub, `openid profile email` for Google |

**Provider-specific extra fields:**

*GitHub App (additional fields when using GitHub Apps instead of OAuth Apps):*

| Field | Label | Type |
|---|---|---|
| App ID | "GitHub App ID" | Text input |
| Private Key | "GitHub App Private Key (PEM)" | Password textarea - AES-256 encrypted |
| Installation URL | "GitHub App Installation URL" | Text input |

**Save:** `PUT /admin/v1/system-config/oauth-apps/{provider}`

All secrets AES-256 encrypted. Client ID returned in GET responses; secrets never returned.

### Test OAuth App

**API:** `POST /admin/v1/system-config/oauth-apps/{provider}/test`

Validates the stored credentials by calling the provider's app verification endpoint. Returns the app's configured name, scopes, and status as registered with the provider.

### How Customer OAuth Flow Uses This

When a tenant user clicks "Connect GitHub" in the main ONEVO app:
1. ONEVO backend reads `platform_oauth_apps.client_id` for GitHub (not encrypted - safe to use in redirect URL)
2. Redirects user to `github.com/login/oauth/authorize?client_id={client_id}&scope={scopes}&state={csrf_token}`
3. Customer authorises access in their GitHub account
4. GitHub redirects back to ONEVO callback with `code`
5. ONEVO exchanges `code` for tokens using `client_secret` (decrypted in-memory for this request only)
6. Tokens stored in `tenant_integration_credentials` for this tenant - the platform OAuth app credentials are NOT stored per-tenant

---

## Platform Service Keys

### What This Section Is

ONEVO uses some third-party services where ONEVO holds the API key and calls the service on behalf of all tenants. These are not provider-specific integrations - they are ONEVO's own infrastructure.

**Route:** `/settings/system/service-keys`

| Service Key | Service Name | Used For | Managed Here |
|---|---|---|---|
| `resend` | Resend | All system emails - invites, password reset, notifications | Yes |
| `cloudflare` | Cloudflare | Tenant domain routing, DNS, CDN | Yes |
| `azure_blob` | Azure Blob Storage | Document and file storage | Yes |
| `sentry` | Sentry | Error monitoring | Yes |

### Fields Per Service

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Service | Read-only display | - | - | |
| API Key / Connection String | "API Key" or "Connection String" | Password input | Yes | AES-256 encrypted |
| Is Active | "Active" | Toggle | Yes | |

**Save:** `PUT /admin/v1/system-config/service-keys/{serviceKey}`

**Test:** `POST /admin/v1/system-config/service-keys/{serviceKey}/test` - sends a ping to the service API; returns healthy/error with raw provider message.

---

## Global Settings

> **Not yet documented.** See `overview.md` Capabilities → Global Settings for the list of managed keys (session TTL, invite expiry, dunning schedule). APIs: `GET /admin/v1/system-config/global-defaults` and `PATCH /admin/v1/system-config/global-defaults`.

---

## Global Policies

> **Not yet documented.** See `overview.md` Capabilities → Global Policies for coverage scope (MFA enforcement, login method defaults, failed-login lockout). Stored in `system_settings` and `tenant_auth_policies`.

---

## Runtime Flag Definitions

> **Not yet documented.** See `overview.md` Capabilities → Runtime Flag Definitions for field list (flag key, owning module, commercial feature key, default value, rollout percentage, phase, description). Stored in `feature_flags`. Tenant-specific ON/OFF overrides are managed from Tenant Management → Tenant Detail → Runtime Overrides, not here.

---

## Email / SMTP

> **Not yet documented.** This tab manages SMTP relay configuration for system emails. Falls back to the Resend service key (Platform Service Keys tab) if no SMTP override is configured.

---

## Storage Configuration

> **Not yet documented.** This tab manages blob storage configuration overrides. Falls back to the Azure Blob service key (Platform Service Keys tab) if no override is configured.

---

## Agent Policy Defaults

> **Not yet documented.** This tab manages default desktop agent collection policy settings applied to all newly provisioned tenants. Tenant-specific overrides are managed from Tenant Management → Tenant Detail → Agent Policy.

---

## Integration -> Module Catalog Link

### How Integrations Are Gated by Module Entitlements

Every integration in ONEVO is linked to one or more module keys in the module catalog. If a tenant is not entitled to any of the required modules, the integration is not available to them - it does not appear in their Integrations tab in the main app.

**This link is managed in Module Catalog Manager**, not here. System Config shows the integration catalog read-only for reference.

**Integration Catalog (defined in Module Catalog Manager):**

| Integration Key | Integration Name | Type | Required Module Keys | Auth Type |
|---|---|---|---|---|
| `github` | GitHub | Customer OAuth | `worksync_github` | OAuth2 - uses `github` platform OAuth app |
| `microsoft_365` | Microsoft 365 | Customer OAuth | `integrations` | OAuth2 - uses `microsoft` platform OAuth app |
| `microsoft_teams` | Microsoft Teams | Customer OAuth | `worksync_chat` OR `integrations` | OAuth2 - uses `microsoft` platform OAuth app |
| `google_calendar` | Google Calendar | Customer OAuth | `calendar` | OAuth2 - uses `google` platform OAuth app |
| `google_workspace` | Google Workspace | Customer OAuth | `integrations` | OAuth2 - uses `google` platform OAuth app |
| `slack` | Slack | Customer OAuth | `worksync_chat` OR `integrations` | OAuth2 - uses `slack` platform OAuth app |
| `outlook_calendar` | Outlook Calendar | Customer OAuth | `calendar` | OAuth2 - uses `microsoft` platform OAuth app |
| `biometric_terminal` | Biometric Terminal | Platform-managed | `workforce_presence` | Webhook - no customer OAuth |
| `mdm_intune` | Microsoft Intune / MDM | Platform-managed | `agent_gateway` | Platform credential |
| `sso_azure_ad` | Azure AD SSO | Customer OAuth | `auth` (always included) | OAuth2 / SAML |
| `sso_google` | Google SSO | Customer OAuth | `auth` (always included) | OAuth2 |

**Rule:** A tenant gains access to an integration when ALL of its `required_module_keys` are in `active or purchased/subscription-included state in `tenant_module_entitlements`. If any required module is `disabled`, `quoted`, or `available`, the integration is hidden.

**Rule for Module Catalog Manager operators:** When disabling a module for a tenant, the system must warn: "Disabling [module] will also disconnect [integration list]" and require confirmation.

---

## Database Tables

### ai_provider_configs

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `config_name` | varchar(80) | NOT NULL |
| `purpose` | varchar(40) | UNIQUE NOT NULL |
| `provider_type` | varchar(30) | NOT NULL - `'openai_compatible' \| 'anthropic'` |
| `api_base_url` | varchar(500) | NOT NULL - always required; no hardcoded default |
| `model` | varchar(120) | NOT NULL - set from fetched model list |
| `api_key_encrypted` | text | NOT NULL - AES-256 |
| `request_timeout_seconds` | int | NOT NULL |
| `max_retries` | int | NOT NULL |
| `is_active` | boolean | NOT NULL |
| `last_verified_at` | timestamptz | Nullable |
| `last_verification_status` | varchar(20) | Nullable |
| `updated_by_id` | uuid | FK -> platform_users |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `UNIQUE(purpose)`

### tenant_ai_provider_overrides

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants |
| `purpose` | varchar(40) | NOT NULL |
| `config_name` | varchar(80) | NOT NULL |
| `provider_type` | varchar(30) | NOT NULL |
| `api_base_url` | varchar(500) | NOT NULL - always required; no hardcoded default |
| `model` | varchar(120) | NOT NULL |
| `api_key_encrypted` | text | NOT NULL |
| `request_timeout_seconds` | int | NOT NULL |
| `max_retries` | int | NOT NULL |
| `is_active` | boolean | NOT NULL |
| `set_by_id` | uuid | FK -> platform_users |
| `set_at` | timestamptz | NOT NULL |

**Unique:** `(tenant_id, purpose)`

### platform_oauth_apps

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `provider` | varchar(30) | UNIQUE NOT NULL - operator-set slug (lowercase, hyphens only); no fixed enum enforced at DB level |
| `app_name` | varchar(100) | NOT NULL - shown in OAuth consent screen |
| `client_id` | varchar(200) | NOT NULL - not encrypted (used in redirect URLs) |
| `client_secret_encrypted` | text | NOT NULL - AES-256 |
| `additional_config_encrypted` | text | Nullable - GitHub App private key, etc. |
| `authorization_url` | varchar(500) | NOT NULL |
| `token_url` | varchar(500) | NOT NULL |
| `default_scopes` | text[] | NOT NULL |
| `is_active` | boolean | NOT NULL |
| `last_verified_at` | timestamptz | Nullable |
| `updated_by_id` | uuid | FK -> platform_users |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `UNIQUE(provider)`

### platform_service_keys

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `service_key` | varchar(50) | UNIQUE NOT NULL - e.g. `'resend'`, `'cloudflare'` |
| `display_name` | varchar(80) | NOT NULL |
| `api_key_encrypted` | text | NOT NULL - AES-256 |
| `is_active` | boolean | NOT NULL |
| `last_verified_at` | timestamptz | Nullable |
| `updated_by_id` | uuid | FK -> platform_users |
| `updated_at` | timestamptz | NOT NULL |

### integration_catalog

| Column | Type | Notes |
|---|---|---|
| `integration_key` | varchar(50) | PRIMARY KEY |
| `display_name` | varchar(100) | NOT NULL |
| `category` | varchar(30) | NOT NULL - `'customer_oauth' \| 'platform_managed'` |
| `required_module_keys` | text[] | NOT NULL - ALL must be entitled for integration to be available |
| `auth_type` | varchar(30) | NOT NULL - `'oauth2' \| 'webhook' \| 'platform_credential' \| 'saml'` |
| `oauth_provider_key` | varchar(30) | Nullable FK -> platform_oauth_apps(provider) |
| `is_active` | boolean | NOT NULL |

### tenant_integration_credentials

Stores per-tenant OAuth tokens and connection state for customer-managed integrations.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants, NOT NULL |
| `integration_key` | varchar(50) | FK -> integration_catalog, NOT NULL |
| `access_token_encrypted` | text | Nullable - AES-256; refreshed automatically before expiry |
| `refresh_token_encrypted` | text | Nullable - AES-256 |
| `token_expires_at` | timestamptz | Nullable |
| `scopes_granted` | text[] | Scopes the customer actually granted during OAuth |
| `external_account_id` | varchar(200) | Nullable - GitHub org ID, Microsoft tenant ID, etc. |
| `external_account_name` | varchar(200) | Nullable - human-readable account name |
| `status` | varchar(20) | NOT NULL - `'connected' \| 'error' \| 'expired' \| 'disconnected'` |
| `last_sync_at` | timestamptz | Nullable |
| `error_message` | text | Nullable |
| `connected_at` | timestamptz | NOT NULL |
| `connected_by_user_id` | uuid | FK -> users - which tenant user connected it |
| `disconnected_at` | timestamptz | Nullable |

**Unique:** `(tenant_id, integration_key)`

---

## APIs - Full Catalog

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/system-config/global-defaults` | List global defaults | `platform.system_config.read` |
| PATCH | `/admin/v1/system-config/global-defaults` | Update global defaults | `platform.system_config.manage` |
| GET | `/admin/v1/system-config/ai-providers` | List AI configs (no keys) | `platform.system_config.read` |
| POST | `/admin/v1/system-config/ai-providers/fetch-models` | Fetch model list from provider using entered key | `platform.system_config.manage` |
| POST | `/admin/v1/system-config/ai-providers` | Create AI config | `platform.system_config.manage` |
| PUT | `/admin/v1/system-config/ai-providers/{id}` | Update / rotate key | `platform.system_config.manage` |
| DELETE | `/admin/v1/system-config/ai-providers/{id}` | Deactivate | `platform.system_config.manage` |
| GET | `/admin/v1/tenants/{id}/ai-provider-override` | Tenant AI overrides | `platform.system_config.read` |
| PUT | `/admin/v1/tenants/{id}/ai-provider-override/{purpose}` | Set tenant AI override | `platform.system_config.manage` |
| DELETE | `/admin/v1/tenants/{id}/ai-provider-override/{purpose}` | Remove tenant AI override | `platform.system_config.manage` |
| GET | `/admin/v1/system-config/oauth-apps` | List OAuth app registrations | `platform.system_config.read` |
| PUT | `/admin/v1/system-config/oauth-apps/{provider}` | Set OAuth app credentials | `platform.system_config.manage` |
| POST | `/admin/v1/system-config/oauth-apps/{provider}/test` | Test OAuth app | `platform.system_config.manage` |
| GET | `/admin/v1/system-config/service-keys` | List service keys (no secrets) | `platform.system_config.read` |
| PUT | `/admin/v1/system-config/service-keys/{serviceKey}` | Set service key | `platform.system_config.manage` |
| POST | `/admin/v1/system-config/service-keys/{serviceKey}/test` | Test service key | `platform.system_config.manage` |
| POST | `/admin/v1/system-config/payment-gateways/verify` | Verify gateway credentials before save (credentials sent in body) | `platform.system_config.manage` |
| GET | `/admin/v1/tenants/{id}/integrations` | Tenant integration status | `platform.tenants.read` |
| POST | `/admin/v1/tenants/{id}/integrations/{key}/disconnect` | Disconnect a tenant integration | `platform.tenants.manage` |
| GET | `/admin/v1/tenants/{id}/settings-override` | Tenant setting overrides | `platform.system_config.read` |
| PATCH | `/admin/v1/tenants/{id}/settings-override` | Set tenant setting override | `platform.system_config.manage` |
| DELETE | `/admin/v1/tenants/{id}/settings-override/{key}` | Clear tenant setting override | `platform.system_config.manage` |
| POST | `/admin/v1/system-config/ai-providers/{id}/test` | Test AI provider connection using stored key | `platform.system_config.manage` |
| POST | `/admin/v1/system-config/payment-gateways` | Save verified gateway config and country routes | `platform.system_config.manage` |
| GET | `/admin/v1/payment-gateways/resolve` | Resolve active gateway for a country (`?country={code}`) — used during tenant wizard Step 3 | `platform.tenants.manage` |
| POST | `/admin/v1/uploads/ai-provider-logo` | Upload AI provider logo; returns `logo_url` | `platform.system_config.manage` |
| POST | `/admin/v1/uploads/gateway-logo` | Upload payment gateway logo; returns `logo_url` | `platform.system_config.manage` |
| POST | `/admin/v1/uploads/oauth-app-logo` | Upload OAuth app logo; returns `logo_url` | `platform.system_config.manage` |



