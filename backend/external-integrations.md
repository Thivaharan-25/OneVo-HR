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

### 1. Stripe (Billing & Subscriptions)

| Property | Value |
|:---------|:------|
| **Module** | SharedPlatform |
| **Auth** | API Key (server-side) + Webhooks (signature verification) |
| **Purpose** | Subscription management, payment processing, invoicing |
| **Tables** | `subscription_plans`, `tenant_subscriptions` |

**Key Flows:**
- Trial-to-paid conversion (14-day trial)
- Mid-cycle upgrade/downgrade
- Webhook events: `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`
- Dunning: 4 retries + grace period

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

## Phase 2 Integrations

### 3. Biometric Terminals (Presence Capture)

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

### 4. Google Calendar (Leave Sync)

| Property | Value |
|:---------|:------|
| **Module** | Calendar |
| **Auth** | OAuth 2.0 |
| **Purpose** | Sync approved leave events to Google Calendar |

### 5. Slack (Notifications)

| Property | Value |
|:---------|:------|
| **Module** | Notifications |
| **Auth** | App integration (Bot token) |
| **Purpose** | Real-time notifications for leave approvals, reviews, etc. |

### 6. Microsoft Teams (Work Management Chat + Workspace Sync)

| Property | Value |
|:---------|:------|
| **Module** | Integrations + Work Management Chat + Work Management Foundation |
| **Auth** | Microsoft OAuth 2.0 / Microsoft Graph delegated + tenant-admin approved scopes |
| **Purpose** | Link ONEVO users to Teams accounts, fetch Teams contacts, create or link Teams groups for Work Management workspaces, and two-way sync messages between ONEVO Chat and Teams |
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
