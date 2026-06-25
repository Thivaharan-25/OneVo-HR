# Subscriptions & Billing - End-to-End Logic

## Purpose

This flow supports demo-to-paid upgrade, invoice generation, payment, shared resource limit calculation, and billing audit history.

## Load Demo Upgrade Options

```text
GET /api/v1/demo/upgrade/options
  -> Validate tenant is demo/trial
  -> Load active Demo Profile snapshot
  -> Return only allowed active subscription plans
  -> Return only allowed optional add-ons from those plans
  -> Hide add-ons already included as base modules
  -> Return allowed resource-only add-ons
```

## Generate Quote

```text
POST /api/v1/demo/upgrade/quote
  -> Validate selected plan is allowed by Demo Profile
  -> Validate selected add-ons are allowed by Demo Profile
  -> Validate no duplicate module entitlement or charge
  -> Select company-size pricing bracket from confirmed employee count
  -> Calculate monthly amount
  -> Calculate annual amount when annual billing is selected
  -> Calculate shared storage and AI allowance
  -> Return quote summary
```

Monthly amount:

```text
selected plan monthly price by company size
+ selected optional module add-on prices
+ selected resource-only add-on prices
x confirmed employee count where pricing is user-based
```

Resource limits:

```text
base plan shared storage/AI
+ selected module add-on storage/AI contribution
+ selected resource add-on storage/AI contribution
+ approved tenant-specific overrides
```

## Submit Upgrade

```text
POST /api/v1/demo/upgrade/submit
  -> Validate quote inputs again server-side
  -> Store selected plan, add-ons, billing cycle, confirmed employee count, quote snapshot, company details, and billing contact
  -> Generate first invoice from the matching company-size price bracket
  -> Move tenant to pending_payment until the first invoice is paid
```

The tenant remains payment-limited until the first invoice is paid. Requests Center is not part of paid activation.

Grace period is not part of this first-invoice flow. Grace period applies only after a tenant has already been active and then hits a renewal/payment failure.

## Payment

```text
POST /api/v1/billing/payment
  -> Validate invoice belongs to tenant
  -> Validate invoice is payable
  -> Process or record payment according to configured billing policy
  -> Mark invoice paid when payment succeeds
  -> Activate paid tenant if this is the first invoice for a submitted demo upgrade
  -> Write billing audit log
```

## Invoices

```text
GET /api/v1/billing/invoices
  -> Return tenant-scoped invoice list
```

## Trial Extension Request

```text
POST /api/v1/trial-extension/request
  -> Validate tenant is demo/trial
  -> Create trial extension request
  -> Notify Requests Center
```

## Cancellation Blocking

Cancellation or renewal changes must be blocked while unpaid seat dues or unpaid added-seat dues exist.

## Grace Period After Activation

```text
Active tenant renewal/payment failure
  -> Enter grace/past-due billing state according to billing policy
  -> Keep or limit access according to the active subscription policy
  -> Suspend tenant if grace period expires without payment
```

This state must not activate a tenant that is still waiting for its first invoice payment.

## Tests

- Demo profile only exposes allowed plans.
- Demo profile only exposes allowed add-ons.
- Add-ons already included as base modules are hidden.
- Tenant cannot be charged twice for the same module.
- Storage is one shared tenant pool.
- AI token limit is one shared tenant allowance.
- Resource add-ons increase shared limits.
- First invoice payment moves demo tenant to active paid tenant.
- Trial extension updates tenant trial end date.
- Unpaid seat dues block cancellation.
