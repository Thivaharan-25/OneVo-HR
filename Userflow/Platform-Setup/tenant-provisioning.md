# Tenant Provisioning

**Area:** Platform Setup
**Trigger:** ONEVO operator creates a new tenant after a sales agreement
**Actor:** ONEVO operator via `console.onevo.io`
**Required Permission(s):** platform-admin access on the developer console

> This is not customer self-service. Customers cannot sign up themselves. Tenant creation is internal and operator-only.

## Preconditions

- ONEVO operator account with developer console access.
- Sales agreement confirmed: commercial model, modules, setup services, payment terms, and templates needed.
- Customer profile details confirmed: company name, slug, primary contact email, country, industry, registration/profile name, registration number, company size, timezone, and currency.

## Core Rules

- Tenant creation collects company registration/profile data, country, timezone, and currency as tenant profile data.
- Tenant creation does not write `legal_entities`.
- Separate operating companies are separate tenants.
- The same email can be invited to multiple tenants. Accepting one invitation grants access only to that tenant and does not merge tenant data.
- Owner invite email is sent only by the explicit invite action. Profile creation, commercial selection, setup completion, and activation must not send it automatically.

## Flow Steps

### Step 1: Customer Profile

- **UI:** Company Name, Slug, Primary Contact Email, Country, Industry, Registration/Profile Name, Registration Number, Company Size, Timezone, Currency.
- **API helper:** `GET /admin/v1/reference/countries/{countryCode}/defaults` returns default timezone/currency and supported timezone/currency choices after country selection.
- **API:** `POST /admin/v1/tenants`
- **Backend:** Creates `tenants.status = provisioning`, stores profile/contact metadata, and creates provisioning state.
- **Validation:** unique slug/company where required, valid email, valid country/timezone/currency, valid industry/company size, and registration/profile validation where product requires it.
- **DB:** `tenants`, provisioning state/checklist records.

### Step 2: Commercial Selection

- **UI:** Pick reusable subscription/commercial plan, company-size band, commercial model (`subscription` or `full_license_maintenance`), billing cycle, payment method, gateway/manual collection mode, manual billing evidence/reference, payment exception/grace dates, AI token limit, and Work Management storage limit when required.
- **API:** `PATCH /admin/v1/tenants/{tenantId}/subscription`
- **Backend:** Stores tenant commercial terms, selected modules snapshot, calculated monthly/annual/full-license/maintenance snapshots, overrides, gateway/manual payment state, billing evidence, payment exceptions, and commercial limits.
- **Validation:** plan exists, selected modules valid, AI modules have token limit, Work Management storage-backed modules have storage limit, manual payment has evidence/reference and audit reason.
- **DB:** `tenant_subscriptions`, payment/evidence file references where applicable.

### Step 3: Module Entitlements

- **UI:** Confirm active modules, sales states, trial dates, module-level pricing overrides, and setup-service needs for the selected modules.
- **API:** `PUT /admin/v1/tenants/{tenantId}/modules`
- **Backend:** Writes tenant module entitlement records and module pricing/sales state.
- **Validation:** `available` and `quoted` do not grant tenant-facing access; only valid active commercial states expose permissions.

### Step 4: Roles, Permissions, Templates, And Setup Services

- **UI:** Apply reusable templates or create tenant-specific configuration:
  - Role Templates
  - Configuration Templates
  - Org Structure Templates
  - Job Family Templates
  - Leave Policy Templates
  - Onboarding Templates
  - App Allowlist Templates
  - Monitoring Policy Templates
  - Data Import Mapping Templates
- **APIs:** role-template APIs, tenant role APIs, setup-service APIs, configuration-template APIs.
- **Backend:** Resolves module-filtered permission catalog, applies templates as tenant-specific configuration, and tracks setup services connected to the tenant's entitled modules.
- **Validation:** every permission belongs to exactly one module; disabled/unpurchased module permissions cannot be assigned.

Setup service rule:

- Every setup service is connected to one or more module keys.
- Free/global setup services are auto-added when their module is entitled, can be configured by the operator, and must not create billing.
- Paid setup services must be explicitly selected and can only be applied when their module is included in the tenant's subscription/module entitlement.

### Step 5: Invite Tenant Owner

- **UI:** Admin email and full name. Operator clicks explicit send action.
- **API:** `POST /admin/v1/tenants/{tenantId}/invite-admin`
- **Backend:** Creates invited user in this tenant, assigns a valid tenant owner/admin role, creates invite token/email record, and sends the set-password email.
- **Validation:** email unique within the tenant. Same email can be invited to other tenants separately.
- **DB:** `users`, `user_roles`, `invitation_tokens`.

### Step 6: Activate Tenant

- **API:** `PATCH /admin/v1/tenants/{tenantId}/provision/confirm`
- **Backend:** Sets `tenants.status = active`.
- **Validation:** activation fails until tenant profile, commercial terms, module entitlements, valid owner/admin role, required settings/templates, and required setup services are complete. Owner invite state is tracked separately and is never sent implicitly.

## Module Entitlement And Permission Rules

- Module entitlement is resolved from `tenant_subscriptions`, plan allowed modules, tenant module grants, and tenant feature grants.
- Permission catalogs include only universal permissions and permissions from enabled/entitled modules.
- Each permission belongs to exactly one module. Reassigning a permission to another module requires an explicit Module Catalog ownership change.
- Roles do not require job levels. Job levels and hierarchy affect scoped access, workflow approver resolution, escalation, and organisation-aware policies.

## Related

- [[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]]
- [[developer-platform/modules/tenant-console/overview|Tenant Console]]
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]]
- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions & Billing]]
- [[modules/configuration/app-allowlist/overview|App Allowlist]]
