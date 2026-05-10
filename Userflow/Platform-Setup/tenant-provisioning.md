# Tenant Provisioning

**Area:** Platform Setup
**Trigger:** ONEVO operator creates a new tenant after a sales agreement (operator action — internal only)
**Actor:** ONEVO operator (internal staff only — via `console.onevo.io`)
**Required Permission(s):** `settings:admin` on the developer console
**Related Permissions:** `billing:manage` (to activate subscription after provisioning)

> **This is NOT a customer self-service flow.** Customers cannot sign up themselves. A tenant is only created after a direct sales agreement with ONEVO. The operator uses the developer console (`console.onevo.io`) to provision the tenant with the agreed module set.

---

## Preconditions

- ONEVO operator account with access to the developer console (`console.onevo.io`)
- Sales agreement confirmed: which pillars/modules the customer has purchased
- Valid company registration details provided by the customer
- Required permissions: operator-level `settings:admin` on the admin console

## Flow Steps

### Step 1: Access Tenant Management Console
- **UI:** Super admin navigates to Platform Admin > Tenants > click "Create Tenant"
- **API:** N/A (navigation only)
- **Backend:** Loads the tenant creation form
- **Validation:** Checks that the current user has `settings:admin` permission at platform level
- **DB:** None

### Step 2: Enter Company Details
- **UI:** Form with fields: Company Name, Legal Entity Name, Registration Number, Country, Primary Address, Industry, Company Size (employee count range)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Client-side: all required fields filled, valid registration number format per country
- **DB:** None

### Step 3: Set Default Timezone and Legal Entity Currency
- **UI:** Country selection calls `GET /admin/v1/reference/countries/{countryCode}/defaults` to prefill timezone and currency. Single-timezone countries can auto-fill timezone; multi-timezone countries must show timezone choices.
- **API:** `GET /admin/v1/reference/countries/{countryCode}/defaults`
- **Backend:** Returns country defaults from reference data: default timezone, supported timezones, default currency, and supported currency option(s).
- **Validation:** Timezone must be a valid IANA timezone identifier. Currency must be a valid ISO 4217 code. Currency defaults from country but remains editable for legal/commercial edge cases.
- **DB:** None

### Step 4: Create Draft Tenant
- **UI:** Click "Create Tenant". The tenant enters the provisioning wizard and remains invisible to customer-facing APIs until activation.
- **API:** `POST /admin/v1/tenants`
- **Request body includes:**
  - Company/legal entity details (name, registration number, country, address, currency, timezone)
  - `subscription`: `{ plan_id, billing_cycle, commercial_model, trial_period_days?, unpaid_grace_period_days? }`
  - `tenant_configuration_setup`: `{ setup_options: ["job_family_creation", "employee_invite", "role_permission_configuration"] }`
- **Backend:** `TenantProvisioningService.ProvisionAsync()` → [[modules/infrastructure/overview|Infrastructure]]
  1. Creates a new row in `tenants` table with status `provisioning` and `company_size_range`
  2. Creates the primary `legal_entities` row with `name`, `registration_number`, `country_id`, `currency_code`, and `address_json`
  3. Stores default timezone and remaining tenant settings in `tenant_settings`
  4. Creates `tenant_subscriptions` row from the provided `subscription` block, snapshotting `trial_period_days` and `unpaid_grace_period_days` from the plan (or operator-supplied overrides). Status is set to `trialing` if `trial_period_days > 0`, or `active` if `trial_period_days = 0`.
  5. Seeds the **Owner role** automatically from the subscribed modules — the operator does NOT select or supply a role ID. The Owner role receives all permissions exposed by the enabled module set.
  6. Creates provisioning checklist items from `setup_options` — one checklist record per selected option, assigned to the ONEVO operator to complete before activation.
  7. Uses the shared application schema with tenant-scoped rows; no per-tenant database or schema is created
- **Validation:** Company name must be unique. Registration number validated against country format. Email domain not already registered to another tenant. `plan_id` must exist. `billing_cycle` must be `monthly` or `annual`. `commercial_model` must be `subscription` or `full_license_maintenance`.
- **DB:** `tenants`, `legal_entities`, `tenant_settings`, `tenant_subscriptions`, `roles`, `role_permissions`, `tenant_provisioning_checklist`

#### Setup Options (`tenant_configuration_setup.setup_options`)

`setup_options` are provisioning checklist items for the ONEVO operator to complete as part of the onboarding service. Supported values in Phase 1:

| Option key | ONEVO operator action |
|:-----------|:----------------------|
| `job_family_creation` | Create job families and levels for the tenant's org structure |
| `employee_invite` | Send initial employee invites on the tenant's behalf |
| `role_permission_configuration` | Configure roles and permission assignments for the tenant |

**Important:** Setup options do NOT directly grant modules or permissions. Module entitlement comes from the subscribed plan. Roles and permissions are seeded/configured as a service — the checklist items track that the operator has completed that service work.

#### Trial and Grace Period

- `trial_period_days` (default: plan value, typically 30) — the number of days a new tenant can use the system before payment is required. Snapshotted onto `tenant_subscriptions` at creation time so plan catalog changes never alter an existing contract.
- `unpaid_grace_period_days` (default: plan value, typically 7) — the number of days a tenant retains access after going unpaid before suspension begins.
- Both values are stored on `TenantSubscription` alongside `TrialStartDate`, `TrialEndDate`, and `AccessEndsAt`.
- The operator may override both per-tenant at creation time; defaults come from the selected plan.

### Step 5: Configure Pricing Overrides, Module Sales States, and Initial Settings
- **UI:** Operator reviews plan-calculated pricing, applies any approved overrides, sets module sales states, configures integration prerequisites, workflow defaults, and optional data-import setup. Role and permission configuration may be handled as a setup-option service (see Step 4) rather than requiring the operator to build roles manually during provisioning.
- **API:** `GET /admin/v1/subscription-plans`, `GET /admin/v1/modules/catalog`, `PATCH /admin/v1/tenants/{tenantId}/subscription`, `PUT /admin/v1/tenants/{tenantId}/modules`, `GET /admin/v1/tenants/{tenantId}/permissions/catalog`, `GET /admin/v1/role-templates`, `POST /admin/v1/role-templates`, `POST /admin/v1/tenants/{tenantId}/role-templates/{templateId}/apply`, `GET /admin/v1/tenants/{tenantId}/roles`, `POST /admin/v1/tenants/{tenantId}/roles`, `PUT /admin/v1/tenants/{tenantId}/roles/{roleId}/permissions`, `PATCH /admin/v1/tenants/{tenantId}/settings`
- **Backend:** Module services validate commercial plan/module choices, pricing terms, module sales states, expose the module-filtered permission catalog, materialize selected role templates, create tenant-specific roles, and write initial settings/workflow/configuration records through their owning modules.
- **Validation:** Role/template permissions must belong to enabled modules. Disabled, available, quoted, unpurchased, or expired module permissions cannot be assigned.
- **DB:** `tenant_subscriptions`, module entitlement/pricing records, `roles`, `role_permissions`, `tenant_settings`, workflow/configuration tables as selected.

### Step 6: Invite Tenant Owner
- **UI:** Form: Admin Email, Admin First Name, Admin Last Name. System sends a set-password link.
- **API:** `POST /admin/v1/tenants/{tenantId}/invite-admin`
- **Backend:** `UserService.CreateAdminAsync()` → [[frontend/cross-cutting/authentication|Authentication]]
  1. Creates user record in `users` table
  2. Assigns the seeded Owner role (auto-created in Step 4 from subscribed modules — the operator does NOT select a role ID here)
  3. Creates employee stub record linked to the user
  4. Sends set-password invitation email with login link
- **Validation:** Email must be unique across the platform. Email domain should match company domain (warning if not, but allowed)
- **DB:** `users`, `user_roles`, `employees`

### Step 7: Provisioning Complete
- **UI:** Success screen showing: Tenant ID, Login URL, Admin email. "Go to Tenant Dashboard" button
- **API:** `PATCH /admin/v1/tenants/{tenantId}/provision/confirm` (sets status to `active`)
- **Backend:** `TenantProvisioningService.ActivateAsync()` updates tenant status. Publishes `TenantProvisionedEvent`
- **Validation:** All provisioning steps must have completed successfully. Activation fails with a checklist until tenant details, commercial terms, active module entitlements, at least one valid tenant owner/admin role, required settings, and owner invite are complete.
- **DB:** `tenants` (status → `active`)

## Variations

### When provisioning fails mid-way
- System rolls back all changes (database transaction)
- If the draft tenant was not committed, no tenant row remains. If a committed draft exists, it stays in `provisioning` and the latest blockers/errors are recorded in `tenant_provisioning_validation_results`.
- Admin sees error message with option to retry
- Failed provisioning attempt logged in `audit_logs`

### Module entitlement selection (always required)
- During provisioning, the operator selects which modules are enabled for this tenant based on the commercial agreement: HR Management modules, Workforce Intelligence modules, WorkSync modules, or any combination
- Only selected pillars' seed data and feature flags are provisioned — e.g., a tenant without Workforce Intelligence gets no monitoring tables seeded and no `/workforce/*` routes visible
- Module entitlement is resolved from `tenant_subscriptions`, plan allowed modules, and tenant-level module/feature grants, then checked server-side on every API request and client-side for route visibility
- When ONEVO releases a new module in the future, an operator manually enables it for tenants that have paid for the upgrade — no automatic upgrade

### Role template and permission catalog selection (always required)
- After module selection, Developer Platform loads a tenant permission catalog from `/admin/v1/tenants/{tenantId}/permissions/catalog`.
- The catalog includes only universal permissions and permissions from modules enabled for that tenant.
- The operator applies ONEVO starter role templates, creates reusable operator-managed templates, or creates tenant-specific roles from that filtered catalog.
- Applied templates create normal tenant-scoped `roles` and `role_permissions`; they are starter configuration, not a separate runtime authorization model.
- Tenant owners can later create or edit roles in the tenant app, but they are still limited to permissions exposed by enabled modules.
- Roles do not require job levels. Job levels and hierarchy only affect scoped access, workflow approver resolution, escalation, and organisation-aware policies.

### When Workforce Intelligence (monitoring) is enabled
Recommended setup sequence after provisioning completes:

```
1. Monitoring Toggles → enable application_tracking, set allowlist_mode = blocklist
2. Deploy agent to pilot group (20–30% of employees) → agent-deployment flow
3. Wait 5–7 days for observed_applications to populate
4. App Allowlist Setup → review Discovered Apps + Browse Catalog → approve/block apps
5. Monitoring Toggles → switch allowlist_mode = allowlist
6. Exception Rule Setup → create non_allowed_app rule with violation_threshold_minutes
7. Full agent rollout to remaining employees
```

See [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]] for the full allowlist configuration flow.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate company name | `409 Conflict` returned | "A tenant with this company name already exists" |
| Invalid registration number | Validation fails | "Registration number format is invalid for the selected country" |
| Email domain already registered | `409 Conflict` returned | "This email domain is already associated with another tenant" |
| Database provisioning timeout | Transaction rolled back. If a draft was already committed, it remains `provisioning` with blocker details in provisioning validation results. | "Provisioning timed out. Please try again or contact support" |
| Email delivery fails | Tenant owner invite remains unsent or failed | Warning: "Tenant created but invitation email failed. Fix email delivery and resend the set-password invite." |

## Events Triggered

- `TenantProvisionedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by billing module to start trial period
- `UserCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by notification module
- `AuditLogEntry` (action: `tenant.provisioned`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Platform-Setup/billing-subscription|Billing Subscription]] — activate subscription after provisioning
- [[Userflow/Platform-Setup/sso-configuration|Sso Configuration]] — configure SSO for the new tenant
- [[Userflow/Platform-Setup/feature-flag-management|Feature Flag Management]] — enable/disable modules
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — customize look and feel
- [[Userflow/Auth-Access/user-invitation|User Invitation]] — invite additional users
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]] — configure monitoring + allowlist mode after provisioning
- [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]] — build app allowlist before enabling enforcement
- [[developer-platform/modules/role-template-manager|Role Template Manager]] — create and apply role templates during provisioning
- [[Userflow/Auth-Access/role-creation|Role Creation]] — tenant owner role management after activation
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] — permission override and effective permission behavior
- [[modules/data-import/overview|Data Import]] — CSV/Excel/PeopleHR migration path
- [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]] — raw-first PeopleHR migration
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]] — approval workflow defaults
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]] — job families and default role mapping

## Module References

- [[modules/infrastructure/overview|Infrastructure]] — multi-tenancy, schema provisioning
- [[infrastructure/multi-tenancy|Multi Tenancy]] — row-level security, tenant isolation
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] — default configuration values
- [[frontend/cross-cutting/authentication|Authentication]] — first admin user creation
- [[frontend/cross-cutting/authorization|Authorization]] — system roles and permissions seeding
