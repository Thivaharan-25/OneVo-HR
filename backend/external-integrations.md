# External Integrations: ONEVO

## Integration Strategy

All external integrations follow a consistent pattern with circuit breakers, retries, and fallbacks via Polly.

### Resilience Pattern

```csharp
// All external HTTP calls use HttpClientFactory + Polly
services.AddHttpClient<IBiometricClient>("BiometricApi")
    .AddPolicyHandler(Policy.HandleResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
        .WaitAndRetryAsync(3, attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt))))
    .AddPolicyHandler(Policy.HandleResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
        .CircuitBreakerAsync(5, TimeSpan.FromMinutes(1)));
```

## Phase 1 Integrations

### 0. PeopleHR (Onboarding Migration)

| Property | Value |
|:---------|:------|
| **Module** | DataImport |
| **Auth** | API Key, stored encrypted, optional IP restrictions configured in PeopleHR |
| **Purpose** | Initial tenant migration from PeopleHR into ONEVO canonical HR modules |
| **Tables** | `migration_runs`, `peoplehr_migration_runs`, `peoplehr_raw_records`, `peoplehr_mapping_profiles`, `peoplehr_mapping_results`, `peoplehr_external_id_links`, `peoplehr_validation_errors`, `peoplehr_reconciliation_items` |

**Key Flows:**
- API permission preflight before fetch.
- Raw PeopleHR payload staging before transformation.
- Source-to-canonical mapping across employees, org structure, salary, leave/absence, timesheets, documents, training, benefits, appraisals, work patterns, and custom fields.
- Dry-run reconciliation before commit.
- Raw archive for unsupported fields so no source data is silently lost.
- Final audit report with imported, skipped, failed, needs-review, and raw-archived counts.

See [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]].

### 1. Payment Gateways (Billing & Subscriptions)

ONEVO supports **Stripe**, **Paddle**, and **PayHere** for payment collection.

Use `gateway_provider = "stripe"` for direct Stripe-backed recurring subscriptions, invoices, and payment methods. Use `gateway_provider = "paddle"` when Paddle is the merchant of record for international SaaS billing and tax handling. Use `gateway_provider = "payhere"` for Sri Lanka/local payment collection and gateway callbacks. The provider is selected by the ONEVO operator during tenant creation/commercial setup; tenant owners do not choose the gateway.

Full-license customers may pay the one-time license manually/offline, but recurring maintenance/support fees should still use one of the configured payment gateways when possible.

#### Stripe

| Property | Value |
|:---------|:------|
| **Module** | SharedPlatform |
| **Auth** | API Key (server-side) + Webhooks (signature verification) |
| **Purpose** | Subscription management, payment processing, invoicing |
| **Tables** | `subscription_plans`, `tenant_subscriptions`, `payment_gateway_configs`, `subscription_invoices`, `payment_methods` |

**Key Flows:**
- Subscription checkout/payment confirmation
- Mid-cycle upgrade/downgrade
- Webhook events: `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`
- Dunning: 4 retries + grace period

#### Paddle

| Property | Value |
|:---------|:------|
| **Module** | SharedPlatform |
| **Auth** | API Key (server-side) + Webhooks (signature verification) |
| **Purpose** | Merchant-of-record subscription billing, tax handling, hosted invoice PDFs |
| **Tables** | `payment_gateway_configs`, `tenant_subscriptions`, `subscription_invoices`, `payment_methods` |

**Key Flows:**
- Operator-selected gateway for tenants where Paddle is the commercial/payment route
- Hosted checkout/payment confirmation
- Webhook events update invoice and subscription state
- Paddle invoice URL stored for tenant invoice download

#### PayHere

| Property | Value |
|:---------|:------|
| **Module** | SharedPlatform |
| **Auth** | Merchant ID + Merchant Secret (server-side, encrypted) + Webhooks/notify URL signature verification |
| **Purpose** | Sri Lanka/local payment collection, recurring subscriptions where supported, maintenance fee collection |
| **Tables** | `payment_gateway_configs`, `tenant_subscriptions`, `subscription_invoices`, `payment_methods` |

**Key Flows:**
- Tenant subscription checkout through PayHere when selected by operator
- Full-license maintenance collection through PayHere recurring/payment flow
- Webhook/notify callbacks update invoice and subscription state
- Gateway references stored in `gateway_customer_ref`, `gateway_subscription_ref`, and invoice/payment provider refs

#### Gateway Configuration

Payment gateway credentials must not be hardcoded. Store gateway configuration in encrypted form and expose only safe metadata to admin APIs.

Required config concepts:

- `provider`: `stripe`, `paddle`, or `payhere`
- `mode`: `test` or `live`
- encrypted credentials: Stripe secret/webhook secret; Paddle API/webhook secret; PayHere merchant secret
- public identifiers: Stripe publishable key, Paddle seller/account identifier, or PayHere merchant ID
- webhook/notify URL and active state
- environment-specific separation between staging and production

### 2. Resend (Transactional Email)

| Property | Value |
|:---------|:------|
| **Module** | Notifications |
| **Auth** | API Key |
| **Purpose** | Password reset, welcome emails, leave approval notifications |
| **Tables** | `notification_templates`, `notification_channels` |

**Key Flows:**
- Template-based emails using `notification_templates`
- Per-tenant sender configuration via `notification_channels`
- Delivery tracking (future: `email_delivery_logs`)

### 3. Google Calendar + Outlook Calendar (User Calendar Sync)

| Property | Value |
|:---------|:------|
| **Module** | Calendar |
| **Auth** | OAuth 2.0 (Google Identity / Microsoft Graph) |
| **Purpose** | User-level pull/push/two-way sync of calendar events between ONEVO and Google Calendar or Outlook Calendar |
| **Tables** | `external_calendar_connections`, `external_calendar_event_links` |

**Key Flows:**
- User connects via OAuth consent; backend stores encrypted access + refresh tokens.
- User selects sync mode: `pull_only`, `push_only`, `two_way`, or `disabled`.
- Hangfire recurring job (every 15 min) processes active connections.
- Deduplication via `external_event_id` + etag; conflict resolution on etag mismatch (external wins inbound, ONEVO wins outbound).

See [[Userflow/Calendar/calendar-integrations|Calendar Integrations Flow]].

## Additional / Optional Integrations

### 4. Biometric Terminals (Presence Capture)

| Property | Value |
|:---------|:------|
| **Module** | IdentityVerification (device management) → WorkforcePresence (event consumption) |
| **Auth** | HMAC-SHA256 signed webhooks |
| **Purpose** | Clock-in/out events from physical terminals |
| **Tables** | `biometric_devices`, `biometric_enrollments`, `biometric_events` (in [[modules/identity-verification/overview\|Identity Verification]]) |

**Webhook Verification:**
```csharp
public bool VerifyWebhookSignature(string payload, string signature, string apiKey)
{
    using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(apiKey));
    var computed = Convert.ToBase64String(hmac.ComputeHash(Encoding.UTF8.GetBytes(payload)));
    return CryptographicOperations.FixedTimeEquals(
        Encoding.UTF8.GetBytes(computed), Encoding.UTF8.GetBytes(signature));
}
```

### 5. Slack (Notifications)

| Property | Value |
|:---------|:------|
| **Module** | Notifications |
| **Auth** | App integration (Bot token) |
| **Purpose** | Real-time notifications for leave approvals, reviews, etc. |

### 6. Microsoft Teams (Chat + Workspace Sync)

| Property | Value |
|:---------|:------|
| **Module** | Integrations + Work Management Chat + Work Management Foundation |
| **Auth** | Microsoft OAuth 2.0 / Microsoft Graph delegated + tenant-admin approved scopes |
| **Purpose** | Phase 1 optional link between ONEVO users/channels/workspaces and Microsoft Teams for two-way chat sync; broader Graph features can expand later |
| **Tables** | `external_account_connections`, `microsoft_graph_tokens`, `teams_webhook_subscriptions`, `teams_delta_sync_state`, `workspace_teams_links`, `channel_teams_links`, `teams_message_sync_state` |

**Key Flows:**
- User links Microsoft Teams account to ONEVO account.
- Workspace creation offers a checkbox to create a Microsoft Team/group.
- Workspace admin can search and link an existing Team with matching members.
- ONEVO sends linked-channel messages to Teams.
- Teams webhooks/delta sync import Teams messages into ONEVO chat.
- Sync failures are retained and retried without creating duplicate messages.

See [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]].

## Phase 4 Integrations (with Payroll)

### 7. ADP / Oracle (Payroll Sync)

| Property | Value |
|:---------|:------|
| **Module** | Payroll |
| **Auth** | OAuth + REST |
| **Purpose** | Sync payroll runs to external payroll providers |
| **Tables** | `payroll_providers`, `payroll_connections` |

### 8. LMS Providers (Learning Content)

| Property | Value |
|:---------|:------|
| **Module** | Skills |
| **Auth** | SSO + API |
| **Purpose** | Course catalog sync, completion tracking |
| **Tables** | `lms_providers`, `courses` |

## Related

- [[backend/module-catalog|Module Catalog]] — which modules own each integration
- [[backend/notification-system|Notification System]] — Resend email pipeline
- [[AI_CONTEXT/tech-stack|Tech Stack]] — integration technology choices
- [[backend/domain-events|Domain Events]] — retry and circuit breaker patterns for external calls
- [[AI_CONTEXT/known-issues|Known Issues]] - integration gotchas; Work Management is internal
