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

## Phase 4 Integrations (with Payroll)

### 6. ADP / Oracle (Payroll Sync)

| Property | Value |
|:---------|:------|
| **Module** | Payroll |
| **Auth** | OAuth + REST |
| **Purpose** | Sync payroll runs to external payroll providers |
| **Tables** | `payroll_providers`, `payroll_connections` |

### 7. LMS Providers (Learning Content)

| Property | Value |
|:---------|:------|
| **Module** | Skills |
| **Auth** | SSO + API |
| **Purpose** | Course catalog sync, completion tracking |
| **Tables** | `lms_providers`, `courses` |

## WorkManage Pro Bridge Interfaces

These are NOT external integrations — they are internal API contracts for the other team:

| Bridge | Direction | API Contract |
|:-------|:----------|:-------------|
| **People Sync** | HR → Work | `GET /api/v1/bridges/people-sync/employees` (paginated employee data) |
| **Availability** | HR → Work | `GET /api/v1/bridges/availability/{employeeId}` (leave + presence data) |
| **Performance** | Work → HR | `POST /api/v1/bridges/performance/metrics` (work metrics for reviews) |
| **Skills** | Bidirectional | `GET/POST /api/v1/bridges/skills/{employeeId}` (skill data exchange) |
| **Work Activity** (NEW) | Work → HR | `POST /api/v1/bridges/work-activity/time-logs` (time logged per task/project, active task context) |

**What HR needs from Work Management:**
1. Task time logs — hours per task, correlate with app usage
2. Project assignments — current projects per employee
3. Task completion metrics — velocity, completion rate for Performance reviews
4. Active task identifier — which task is being worked on (real-time dashboard context)

Bridge endpoints are authenticated via API key + tenant context. See [[security/auth-architecture|Auth Architecture]] for details.

## Related

- [[backend/module-catalog|Module Catalog]] — which modules own each integration
- [[backend/notification-system|Notification System]] — Resend email pipeline
- [[AI_CONTEXT/tech-stack|Tech Stack]] — integration technology choices
- [[backend/messaging/error-handling|Error Handling]] — retry and circuit breaker patterns for external calls
- [[AI_CONTEXT/known-issues|Known Issues]] — WorkManage Pro bridge gotchas
