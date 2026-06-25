# System Config - Testing

## Test Fixtures Required

- Platform account with `platform.system_config.manage`
- Platform account with `platform.system_config.read` only
- At least 1 active tenant
- Mock AI provider endpoint available (for fetch-models tests) or test keys configured

---

## AI Provider - Fetch Models

### TC-SYS-001: Fetch models with valid key returns model list
**Action:** `POST /admin/v1/system-config/ai-providers/fetch-models`
```json
{
  "provider_format": "openai_compatible",
  "api_base_url": "https://api.openai.com",
  "api_key": "<valid_key>"
}
```
**Expected:**
- HTTP 200
- `models` array not empty - at least 1 model object with `id` and `display_name`
- Key is NOT saved - no `ai_provider_configs` row created

### TC-SYS-002: Fetch models with invalid key returns error (not 4xx from ONEVO)
**Action:** `POST /admin/v1/system-config/ai-providers/fetch-models` with wrong API key
**Expected:**
- HTTP 200 (ONEVO returns 200 - the error is in the payload)
- `{"error": "provider_auth_failed", "message": "..."}` - raw provider error message passed through
- No `ai_provider_configs` row created

### TC-SYS-003: Fetch models uses operator-supplied api_base_url - no hardcoded fallback
**Action:** `POST /admin/v1/system-config/ai-providers/fetch-models` with `api_base_url: null`
**Expected:** HTTP 422 - `api_base_url` is required; no default URL is used

### TC-SYS-004: Fetch works for anthropic provider_format at custom base URL
**Action:** `POST /admin/v1/system-config/ai-providers/fetch-models`
```json
{
  "provider_format": "anthropic",
  "api_base_url": "https://api.anthropic.com",
  "api_key": "<valid_anthropic_key>"
}
```
**Expected:** Model list returned using Anthropic API format (different auth headers from openai_compatible)

---

## AI Provider - Save and Encrypt

### TC-SYS-005: Save AI config encrypts key - never returned in responses
**Action:** `POST /admin/v1/system-config/ai-providers`
```json
{
  "config_name": "Primary Chat Provider",
  "purpose": "ai_insights",
  "provider_format": "openai_compatible",
  "api_base_url": "https://api.openai.com",
  "model": "gpt-4o-mini",
  "api_key": "sk-live-test-key-abc123",
  "request_timeout_seconds": 60,
  "max_retries": 2,
  "is_active": true
}
```
**Expected:**
- HTTP 201
- `ai_provider_configs` row created with `api_key_encrypted` (ciphertext, not plaintext)
- GET response for this config: does NOT include `api_key` or `api_key_encrypted`
- Audit log: `action = 'system_config.ai_config_updated'`, `key_rotated: true`

### TC-SYS-006: api_base_url is stored exactly as entered - not modified
**Action:** Save config with `api_base_url: "http://localhost:11434"` (local Ollama)
**Expected:** `ai_provider_configs.api_base_url = "http://localhost:11434"` - stored verbatim

### TC-SYS-007: Duplicate purpose is an upsert - replaces old config
**Setup:** `ai_provider_configs` has a row for `purpose = 'ai_insights'`
**Action:** `POST /admin/v1/system-config/ai-providers` with `purpose = 'ai_insights'` (different provider)
**Expected:** Old config replaced; `UNIQUE(purpose)` enforced; audit log shows key_rotated

---

## AI Provider - Test Connection

### TC-SYS-008: Test connection uses stored api_base_url - not a hardcoded provider URL
**Setup:** Config saved with `api_base_url = "https://api.custom-provider.com"`, `provider_format = "openai_compatible"`
**Action:** `POST /admin/v1/system-config/ai-providers/{configId}/test`
**Expected:**
- Backend calls `POST https://api.custom-provider.com/v1/chat/completions` (not hardcoded OpenAI URL)
- Response shows `status: "healthy"` or `status: "error"` with raw provider message

### TC-SYS-009: Test connection updates last_verified_at
**Action:** `POST /admin/v1/system-config/ai-providers/{configId}/test`
**Expected:** `ai_provider_configs.last_verified_at` updated, `last_verification_status` = `'healthy'` or `'error'`

---

## AI Provider - Per-Tenant Override

### TC-SYS-010: Tenant override takes precedence over global config (same purpose)
**Setup:**
- Global: `ai_insights` uses Provider A at `base_url_A`
- Tenant T override: `ai_insights` uses Provider B at `base_url_B`
**Action:** AI Insights makes AI call for tenant T
**Expected:** Call goes to `base_url_B` (tenant override), not `base_url_A` (global)

### TC-SYS-011: Removing tenant override falls back to global immediately
**Setup:** Tenant T has AI override for `ai_insights`
**Action:** `DELETE /admin/v1/tenants/{id}/ai-provider-override/ai_insights`
**Expected:**
- `tenant_ai_provider_overrides` row deleted
- Next AI call for tenant T uses global `ai_provider_configs` for `ai_insights`
- Audit log: action recorded

### TC-SYS-012: Tenant override with inactive flag falls back to global
**Setup:** Tenant T has override with `is_active = false`
**Action:** AI call for tenant T, purpose `ai_insights`
**Expected:** Global config used - inactive override is treated as no override

---

## Payment Gateway Override

### TC-SYS-013: Gateway verify does NOT save credentials
**Action:** `POST /admin/v1/system-config/payment-gateways/verify` with gateway credentials
**Expected:**
- HTTP 200 with verified account info or error
- No new `payment_gateway_configs` row created - verify is a pre-save check only
- No new `payment_gateway_credentials` row created

### TC-SYS-014: Gateway save stores metadata and credential separately
**Action:** `POST /admin/v1/system-config/payment-gateways` with verified gateway credentials and country codes
**Expected:**
- `payment_gateway_configs` row contains metadata only
- `payment_gateway_credentials` row contains encrypted secret fields
- `payment_gateway_country_routes` rows contain country routing
- GET response does not include encrypted secrets

### TC-SYS-015: Gateway credential update creates a new active credential row
**Setup:** Gateway config has one active credential row
**Action:** Save new credentials for the same gateway config
**Expected:**
- Previous `payment_gateway_credentials.is_active = false`
- New `payment_gateway_credentials.is_active = true`
- New row has `rotated_at` and `rotated_by_id`
- `payment_gateway_configs.id` is unchanged

## Platform OAuth Apps

### TC-SYS-016: OAuth app client_id is NOT encrypted (used in redirect URLs)
**Action:** `PUT /admin/v1/system-config/oauth-apps/github` with `client_id: "abc123"`, `client_secret: "secret_xyz"`
**Expected:**
- `platform_oauth_apps.client_id = "abc123"` (stored plaintext)
- `platform_oauth_app_credentials.client_secret_encrypted` = AES-256 ciphertext
- GET response: `client_id: "abc123"` returned, `client_secret` absent

### TC-SYS-016B: OAuth secret update creates credential row
**Setup:** OAuth app `github` exists
**Action:** Update `client_secret`
**Expected:**
- Existing active `platform_oauth_app_credentials` row is deactivated
- New active `platform_oauth_app_credentials` row is created
- New row has `rotated_at` and `rotated_by_id`
- `platform_oauth_apps.id` is unchanged

### TC-SYS-017: OAuth app provider key is operator-set - no fixed enum
**Action:** `PUT /admin/v1/system-config/oauth-apps/my_custom_provider`
**Expected:** HTTP 200 - `my_custom_provider` is a valid provider key slug; no fixed list enforced

---

## Global Settings

### TC-SYS-018: Global default change is audit-logged with old and new values
**Setup:** `invite.expiry_hours = 72`
**Action:** `PATCH /admin/v1/system-config/global-defaults` `{"settings": [{"key": "invite.expiry_hours", "value": "48"}], "reason": "Security policy update"}`
**Expected:** Audit log: `previous_value: "72"`, `new_value: "48"`, `reason`, actor

### TC-SYS-019: Invalid setting key rejected
**Action:** `PATCH /admin/v1/system-config/global-defaults` with `key: "this.does.not.exist"`
**Expected:** HTTP 422 - unknown setting key

### TC-SYS-020: Read-only account cannot change settings
**Setup:** Account with `platform.system_config.read` only
**Action:** `PATCH /admin/v1/system-config/global-defaults`
**Expected:** HTTP 403
