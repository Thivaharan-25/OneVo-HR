# Tenant Management

## Purpose

Tenant Management lets Super Admins create, view, edit, suspend, reactivate, and manage demo and active tenants. It also provides the focused demo tenant view for trial/resource/upgrade state.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `tenants` | Read + write tenant identity, type, lifecycle status, subdomain, and metadata |
| `tenant_subscriptions` | Read + write selected plan, billing cycle, selected optional add-ons, selected resource-only add-ons, and commercial snapshots |
| `tenant_subscription_modules` | Read + write resolved module entitlements for the tenant |
| `tenant_subscription_addons` | Read + write selected optional module add-ons and resource-only add-ons |
| `tenant_resource_limits` | Read + write shared storage and AI limits |
| `demo_tenants` | Read + write demo/trial metadata |
| `audit_logs` | Write lifecycle and trial actions |

## Required Tenant List Summary

- Total tenants
- Active tenants
- Trial tenants
- Suspended tenants

## Required Table Columns

- Tenant name
- Domain/subdomain
- Subscription plan
- Type
- Status
- Primary admin
- Created on
- Actions

## Row Actions

- View details
- Edit tenant
- Broadcast to admin
- Suspend/reactivate

## Create Tenant Form Sections

### Tenant Information

- Company / tenant name
- Tenant URL/subdomain
- Account type
- Customer type

### Primary Admin Details

- Full name
- Email
- Phone
- Role

### Plan / Demo Setup

- Demo profile
- Trial duration
- Trial end date
- Max employees
- Enabled status

### Module Access

- Enabled modules
- Add-on modules

### Billing Contact

- Billing contact name
- Billing email
- Company address

## Tenant Detail Sections

- Tenant information
- Primary admin
- Plan and demo details
- Module access
- Additional metadata
- Latest activity
- Audit history

## Tenant Actions

- Edit tenant
- Resend admin invite
- Suspend tenant
- Reactivate tenant
- Extend trial
- Expire trial
- Broadcast to admin

## Demo Tenant Individual View

The demo tenant view must show:

- Trial start date
- Trial end date
- Days remaining
- Trial expiry status
- Max employees
- Storage used vs allocated
- AI tokens used vs allocated
- Demo profile name and limits
- Upgrade / activation status
- Primary admin name, email, status, last login, account created date
- Activity log

Direct trial extension and expiry are allowed from this view and must be audit logged.

## Commercial Rules

- Tenant paid access comes from one selected subscription plan.
- Optional module add-ons can be selected only when allowed by the plan and Demo Profile.
- Resource-only add-ons increase shared storage and AI limits but do not create module entitlements.
- A tenant cannot be entitled twice to the same module.
- A tenant cannot be charged twice for the same module.
- Shared storage and shared AI limits are resolved into `tenant_resource_limits`.

## Navigation

| Route | Permission |
|---|---|
| `/platform/tenants` | `platform.tenants.read` |
| Write operations | `platform.tenants.manage` |
| Subscription plan changes | `platform.subscriptions.manage` |

## Related

- [[developer-platform/modules/subscription-manager/overview|Subscription Plans]]
- [[developer-platform/modules/demo-profiles/overview|Demo Profiles]]
- [[developer-platform/modules/requests-center/overview|Requests Center]]
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog]]
