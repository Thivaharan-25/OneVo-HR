# Billing & Subscription Management

**Area:** Platform Setup
**Required Permission(s):** `billing:manage`
**Related Permissions:** `settings:admin` (for viewing invoice history and tax settings)

---

## Preconditions

- Tenant has been provisioned via [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning Flow]]
- User has `billing:manage` permission
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Billing
- **UI:** Settings sidebar > Billing & Subscription. Dashboard shows: current plan, billing cycle, next invoice date, payment method, usage summary (active employees count)
- **API:** `GET /api/v1/billing/subscription`
- **Backend:** `BillingService.GetCurrentSubscriptionAsync()` → [[modules/shared-platform/subscriptions-billing/overview|Subscriptions Billing]]
- **Validation:** Permission check for `billing:manage`
- **DB:** `subscriptions`, `billing_plans`

### Step 2: Select or Change Plan
- **UI:** Plan comparison cards showing: Free/Starter/Professional/Enterprise tiers. Each shows: price per employee per month, included modules, feature limits, support level. Current plan highlighted. Click "Upgrade" or "Downgrade"
- **API:** `GET /api/v1/billing/plans` (list available plans)
- **Backend:** `BillingService.GetAvailablePlansAsync()` — filters plans based on tenant's country and active employee count
- **Validation:** Cannot downgrade if current usage exceeds target plan limits (e.g., active modules not available in lower plan)
- **DB:** `billing_plans`

### Step 3: Enter Payment Details
- **UI:** Stripe Elements embedded form: card number, expiry, CVC, billing address. For enterprise: option for invoice-based billing. Previously saved payment methods shown with option to use existing
- **API:** `POST /api/v1/billing/payment-method` (saves Stripe payment method)
- **Backend:** `PaymentService.SavePaymentMethodAsync()` — calls Stripe API to create/attach payment method to Stripe customer. Stores only Stripe payment method ID locally (no card details stored)
- **Validation:** Stripe validates card in real-time. Billing address required for tax calculation
- **DB:** `payment_methods` (stores Stripe reference only), `billing_addresses`

### Step 4: Review and Confirm
- **UI:** Order summary: plan name, price per employee, estimated monthly total (based on current active employee count), proration amount (if mid-cycle change), next billing date. Checkbox: "I agree to the terms of service"
- **API:** `POST /api/v1/billing/subscription`
- **Backend:** `SubscriptionService.CreateOrUpdateSubscriptionAsync()` → [[modules/shared-platform/subscriptions-billing/overview|Subscriptions Billing]]
  1. Creates Stripe subscription via Stripe API
  2. Stores subscription reference in local DB
  3. If upgrade: immediately charges proration
  4. If downgrade: scheduled for next billing cycle
  5. Updates tenant feature flags based on new plan
- **Validation:** Payment method must be valid. Terms must be accepted. Proration amount displayed must match calculated amount
- **DB:** `subscriptions`, `subscription_history`, `tenant_feature_flags`

### Step 5: Activation and Feature Access Update
- **UI:** Success confirmation with new plan details. Page refreshes to show updated plan. Navigation menu may show new modules (if upgrade) or hide modules (if downgrade, effective next cycle)
- **API:** `POST /api/v1/billing/subscription/{id}/activate`
- **Backend:** `SubscriptionService.ActivateAsync()` — publishes `SubscriptionChangedEvent`. Feature flag service updates available modules for the tenant
- **Validation:** Stripe webhook confirms payment success before activation
- **DB:** `subscriptions` (status → `active`), `tenant_feature_flags`

## Variations

### When upgrading mid-cycle
- Proration calculated: remaining days in current cycle charged at difference between old and new plan rate
- New features available immediately after payment confirmation
- Invoice generated for proration amount

### When downgrading
- Downgrade effective at end of current billing cycle
- Warning shown if any active features will be disabled
- Users currently using soon-to-be-disabled features are notified

### When switching from monthly to annual billing
- Annual discount applied (typically 20%)
- Full annual amount charged immediately
- Refund issued for remaining monthly cycle

### Enterprise custom pricing
- "Contact Sales" button instead of self-service checkout
- Sales team configures custom plan with specific module selection and pricing
- Manual approval workflow for enterprise subscriptions

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Card declined | Stripe returns decline code | "Payment declined. Please check your card details or try a different payment method" |
| Insufficient plan for current usage | Downgrade blocked | "Cannot downgrade: you have 150 active employees but the Starter plan supports up to 50" |
| Stripe API unavailable | Transaction deferred | "Payment service temporarily unavailable. Your plan change has been queued and will process shortly" |
| Duplicate subscription attempt | Idempotency check | "You already have an active subscription. Please modify your existing plan instead" |
| Webhook delivery failure | Retry with exponential backoff | No user impact (background process) |

## Events Triggered

- `SubscriptionChangedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by feature flag service and notification module
- `PaymentProcessedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by invoice generation
- `AuditLogEntry` (action: `subscription.changed`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]] — initial tenant setup before billing
- [[Userflow/Platform-Setup/feature-flag-management|Feature Flag Management]] — modules enabled/disabled based on plan
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] — billing address and tax settings

## Module References

- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions Billing]] — billing logic and Stripe integration
- [[backend/external-integrations|External Integrations]] — Stripe payment gateway
- [[modules/configuration/overview|Configuration]] — feature flags per tenant
- [[modules/notifications/overview|Notifications]] — billing-related email notifications
