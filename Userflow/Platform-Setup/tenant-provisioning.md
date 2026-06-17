# Tenant Provisioning

**Area:** Platform Setup
**Trigger:** ONEVO operator creates a new tenant after a sales agreement
**Actor:** ONEVO operator via `console.onevo.io`
**Required Permission(s):** platform-admin access on the developer console

> This is not customer self-service. Customers cannot sign up themselves. Tenant creation is internal and operator-only.

## Preconditions

- ONEVO operator account with developer console access.
- Sales agreement confirmed: allowed subscription plans, setup services, payment gateway route, negotiated discounts or overrides, and templates needed.
- Customer profile details confirmed: company name, slug, primary contact email, country, industry, registration/profile name, registration number, estimated total employee count, timezone, and currency.

## Core Rules

- Tenant creation collects company registration/profile data, country, timezone, and currency as tenant profile data.
- Tenant creation does not write deprecated registration-profile rows.
- Activation seeds one primary legal entity from the tenant profile so Setup / Control has a starting point.
- Additional operating companies that belong to the same customer account are added as legal entities inside the same tenant.
- Separate tenants are used only for separate customer accounts that must remain isolated.
- The same email can be invited to multiple tenants. Accepting one invitation grants access only to that tenant and does not merge tenant data.
- Owner invite email is sent only by the explicit invite action. Profile creation, commercial selection, setup completion, and activation must not send it automatically.

## Flow Steps

### Step 1: Customer Profile

- **UI:** Company Name, Slug, Primary Contact Email, Country, Industry, Registration/Profile Name, Registration Number, Estimated Total Employee Count, Timezone, Currency.
- **API helper:** `GET /admin/v1/reference/countries/{countryCode}/defaults` returns default timezone/currency and supported timezone/currency choices after country selection.
- **API:** `POST /admin/v1/tenants`
- **Backend:** Creates `tenants.status = provisioning`, stores profile/contact metadata, and creates provisioning state.
- **Validation:** unique slug/company where required, valid email, valid country/timezone/currency, valid industry, positive estimated employee count when supplied, and registration/profile validation where product requires it.
- **DB:** `tenants`, provisioning state/checklist records. Primary `legal_entities` is created during activation/setup seeding.

### Step 2: Operator Commercial Boundary

- **UI:** Select the subscription plans the tenant owner is allowed to choose from, optionally mark one as recommended/default, review the payment gateway resolved from the tenant country route, add one-time setup charges, set negotiated discounts/overrides when applicable, and set AI token / Work Management storage limits when required.
- **API:** `PATCH /admin/v1/tenants/{tenantId}/subscription`
- **Backend:** Stores tenant commercial boundaries: allowed plan ids, optional recommended plan id, resolved payment gateway config, one-time setup charges, negotiated overrides/discounts, and commercial limits. It does not finalize billing cycle or first invoice quantity.
- **Validation:** allowed plans exist and are active, recommended plan is in the allowed set, AI modules have token limit, Work Management storage-backed modules have storage limit, and the tenant country has exactly one active payment gateway route for the current environment.
- **DB:** `tenant_subscriptions`, gateway invoice/payment references where applicable.

Tenant owner choice rule:

- Tenant owner may choose only from the operator-allowed plans.
- Tenant owner chooses billing cycle (`monthly` or `annual`) during onboarding/plan confirmation.
- Tenant owner confirms total employee count before the first real invoice is generated.
- Tenant owner does not choose Stripe, Paddle, or PayHere. Payment gateway selection is resolved from System Config country routing and reviewed by the ONEVO operator in Developer Platform.
- Paid tenant provisioning does not set trial duration directly. Demo/trial tenants are created from Demo Profiles; paid activation and billing are driven by the selected subscription plan, selected add-ons, generated first invoice, and payment state.

### Step 3: Module Entitlements

- **UI:** Confirm active modules, sales states, module-level pricing overrides, and setup-service needs for the allowed/selected modules.
- **API:** `PUT /admin/v1/tenants/{tenantId}/modules`
- **Backend:** Writes tenant module entitlement records and module pricing/sales state.
- **Validation:** `available` and `quoted` do not grant tenant-facing access; only valid active commercial states expose permissions.

### Step 4: Roles, Permissions, Templates, And Setup Services

- **UI:** Apply reusable templates or create tenant-specific configuration:
  - Role Templates
  - Configuration Templates
  - Org Structure Templates
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

- Module entitlement is resolved from `tenant_module_entitlements` and the current `tenant_subscriptions` record.
- Feature availability is resolved from `tenant_subscriptions.selected_feature_keys` plus runtime feature flags.
- Permission catalogs include only universal permissions and permissions from enabled/entitled modules and selected feature keys.
- Each permission belongs to exactly one module. Reassigning a permission to another module requires an explicit Module Catalog ownership change.
- Roles do not require job levels. Job levels and hierarchy affect scoped access, workflow approver resolution, escalation, and organisation-aware policies.

## Related

- [[developer-platform/userflow/provisioning-flow|Operator Customer Provisioning Flow]]
- [[developer-platform/modules/tenant-console/overview|Tenant Management]]
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]]
- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions & Billing]]
- [[modules/configuration/app-allowlist/overview|App Allowlist]]

