# Billing And Demo Upgrade

## Purpose

Support customer upgrade from demo tenant to active paid tenant using the corrected Subscription Plans model.

## Customer Upgrade Steps

1. Customer enters company and billing details.
2. Customer confirms actual employee count/company size.
3. Customer selects one allowed subscription plan.
4. Customer selects optional add-ons allowed by the Demo Profile.
5. Customer selects resource-only add-ons if allowed.
6. Customer selects billing cycle: monthly or annual.
7. Customer reviews final price.
8. Backend generates the first invoice from the confirmed employee count/company-size bracket.
9. Customer pays first invoice.
10. Tenant becomes active paid tenant after successful payment handling.

## Billing Calculation

Monthly amount:

```text
selected plan monthly price by company size
+ selected optional module add-on prices
+ selected resource-only add-on prices
x confirmed employee count where pricing is user-based
```

Annual amount:

```text
annual base = monthly amount x 12
```

Then apply:

- Annual override if configured
- Annual discount if configured
- Add-on annual pricing rules

## Resource Limits

Storage and AI limits are calculated as:

```text
base plan shared storage/AI
+ selected module add-on storage/AI contribution
+ selected resource add-on storage/AI contribution
+ approved tenant-specific overrides
```

Storage is one shared tenant pool. AI token limit is one shared tenant allowance.

## Demo Upgrade Rules

- Demo users can only upgrade to plans allowed by the active Demo Profile.
- Demo users can only select add-ons allowed by the active Demo Profile.
- Add-ons already included as base modules must be hidden.
- Inactive subscription plans are not available for new upgrades.
- Inactive catalog modules are not available in new plan/add-on choices.

## Seat And Cancellation Rules

- Monthly tenants can add users beyond purchased seats.
- Extra seats become due on the next monthly invoice.
- Annual added seats are charged for remaining months in the annual term.
- Cancellation is blocked while unpaid dues exist.
- Renewal changes are blocked while unpaid added-seat dues exist.

## Tenant-Facing APIs

| Step | API |
|---|---|
| Load allowed upgrade options | `GET /api/v1/demo/upgrade/options` |
| Generate quote | `POST /api/v1/demo/upgrade/quote` |
| Generate first invoice | `POST /api/v1/demo/upgrade/submit` |
| List invoices | `GET /api/v1/billing/invoices` |
| Pay invoice | `POST /api/v1/billing/payment` |
| Request trial extension | `POST /api/v1/trial-extension/request` |
| Support tickets | `GET /api/v1/support/tickets`, `GET /api/v1/support/tickets/{id}`, `POST /api/v1/support/tickets`, `POST /api/v1/support/tickets/{id}/replies` |

## Audit Events

- Upgrade options viewed where required by policy
- Upgrade quote generated
- Demo upgrade submitted
- First invoice generated
- Payment recorded
- Tenant activated
- Subscription changed
- Cancellation blocked due to unpaid dues

## Related

- [[developer-platform/modules/subscription-manager/overview|Subscription Plans]]
- [[developer-platform/modules/demo-profiles/overview|Demo Profiles]]
- [[developer-platform/modules/requests-center/overview|Requests Center]] - demo access and trial extension requests only; paid activation does not enter this queue
- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions & Billing]]
