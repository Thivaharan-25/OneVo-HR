# Tenant Provisioning

**Area:** Platform Setup
**Trigger:** Super Admin creates new tenant (user action — first-time setup)
**Required Permission(s):** `settings:admin`
**Related Permissions:** `billing:manage` (to activate subscription after provisioning)

---

## Preconditions

- Super admin access to the ONEVO platform management console
- Valid business email and company registration details available
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Access Tenant Management Console
- **UI:** Super admin navigates to Platform Admin > Tenants > click "Create Tenant"
- **API:** N/A (navigation only)
- **Backend:** Loads the tenant creation form
- **Validation:** Checks that the current user has `settings:admin` permission at platform level
- **DB:** None

### Step 2: Enter Company Details
- **UI:** Form with fields: Company Name, Registration Number, Country, Primary Address, Industry, Company Size (employee count range)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Client-side: all required fields filled, valid registration number format per country
- **DB:** None

### Step 3: Set Default Timezone and Currency
- **UI:** Dropdowns for Default Timezone (e.g., UTC, Asia/Colombo) and Default Currency (e.g., USD, LKR, GBP). Option to set fiscal year start month
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Timezone must be a valid IANA timezone identifier. Currency must be a valid ISO 4217 code
- **DB:** None

### Step 4: Submit and Provision Tenant
- **UI:** Click "Provision Tenant" button. Loading spinner with progress steps shown: "Creating schema...", "Seeding defaults...", "Creating admin user..."
- **API:** `POST /api/v1/admin/tenants`
- **Backend:** `TenantProvisioningService.ProvisionAsync()` → [[modules/infrastructure/overview|Infrastructure]]
  1. Creates a new row in `tenants` table with status `provisioning`
  2. Executes database schema provisioning (applies all migrations for the new tenant schema using row-level security with `tenant_id`)
  3. Seeds default data: system roles (Super Admin, Employee), default permissions (all 90+), default leave types, default notification templates
  4. Sets tenant configuration (timezone, currency, fiscal year)
- **Validation:** Company name must be unique. Registration number validated against country format. Email domain not already registered to another tenant
- **DB:** `tenants`, `tenant_settings`, `roles` (system defaults), `role_permissions` (default mappings), `permissions` (references)

### Step 5: Create First Admin User
- **UI:** Form: Admin Email, Admin First Name, Admin Last Name. System auto-generates a temporary password
- **API:** `POST /api/v1/admin/tenants/{tenantId}/first-admin`
- **Backend:** `UserService.CreateAdminAsync()` → [[frontend/cross-cutting/authentication|Authentication]]
  1. Creates user record in `users` table
  2. Assigns the system "Super Admin" role (all permissions)
  3. Creates employee stub record linked to the user
  4. Sends invitation email with temporary password and login link
- **Validation:** Email must be unique across the platform. Email domain should match company domain (warning if not, but allowed)
- **DB:** `users`, `user_roles`, `employees`

### Step 6: Provisioning Complete
- **UI:** Success screen showing: Tenant ID, Login URL, Admin email. "Go to Tenant Dashboard" button
- **API:** `PATCH /api/v1/admin/tenants/{tenantId}/status` (sets status to `active`)
- **Backend:** `TenantProvisioningService.ActivateAsync()` updates tenant status. Publishes `TenantProvisionedEvent`
- **Validation:** All provisioning steps must have completed successfully
- **DB:** `tenants` (status → `active`)

## Variations

### When provisioning fails mid-way
- System rolls back all changes (database transaction)
- Tenant status set to `failed`
- Admin sees error message with option to retry
- Failed provisioning attempt logged in `audit_logs`

### When tenant has custom module selection
- If `billing:manage` permission is also held, admin can pre-select which modules to enable via [[Userflow/Platform-Setup/feature-flag-management|Feature Flags]]
- Only selected modules' seed data is provisioned

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
| Database provisioning timeout | Transaction rolled back, status set to `failed` | "Provisioning timed out. Please try again or contact support" |
| Email delivery fails | Tenant created but admin not notified | Warning: "Tenant created but invitation email failed. Copy the temporary credentials manually" |

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

## Module References

- [[modules/infrastructure/overview|Infrastructure]] — multi-tenancy, schema provisioning
- [[infrastructure/multi-tenancy|Multi Tenancy]] — row-level security, tenant isolation
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] — default configuration values
- [[frontend/cross-cutting/authentication|Authentication]] — first admin user creation
- [[frontend/cross-cutting/authorization|Authorization]] — system roles and permissions seeding
