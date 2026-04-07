# Tenant Provisioning

**Area:** Platform Setup
**Required Permission(s):** `settings:admin`
**Related Permissions:** `billing:manage` (to activate subscription after provisioning)

---

## Preconditions

- Super admin access to the ONEVO platform management console
- Valid business email and company registration details available
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

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
- **Backend:** `TenantProvisioningService.ProvisionAsync()` → [[infrastructure]]
  1. Creates a new row in `tenants` table with status `provisioning`
  2. Executes database schema provisioning (applies all migrations for the new tenant schema using row-level security with `tenant_id`)
  3. Seeds default data: system roles (Super Admin, Employee), default permissions (all 90+), default leave types, default notification templates
  4. Sets tenant configuration (timezone, currency, fiscal year)
- **Validation:** Company name must be unique. Registration number validated against country format. Email domain not already registered to another tenant
- **DB:** `tenants`, `tenant_settings`, `roles` (system defaults), `role_permissions` (default mappings), `permissions` (references)

### Step 5: Create First Admin User
- **UI:** Form: Admin Email, Admin First Name, Admin Last Name. System auto-generates a temporary password
- **API:** `POST /api/v1/admin/tenants/{tenantId}/first-admin`
- **Backend:** `UserService.CreateAdminAsync()` → [[authentication]]
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
- If `billing:manage` permission is also held, admin can pre-select which modules to enable via [[feature-flag-management|Feature Flags]]
- Only selected modules' seed data is provisioned

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate company name | `409 Conflict` returned | "A tenant with this company name already exists" |
| Invalid registration number | Validation fails | "Registration number format is invalid for the selected country" |
| Email domain already registered | `409 Conflict` returned | "This email domain is already associated with another tenant" |
| Database provisioning timeout | Transaction rolled back, status set to `failed` | "Provisioning timed out. Please try again or contact support" |
| Email delivery fails | Tenant created but admin not notified | Warning: "Tenant created but invitation email failed. Copy the temporary credentials manually" |

## Events Triggered

- `TenantProvisionedEvent` → [[event-catalog]] — consumed by billing module to start trial period
- `UserCreatedEvent` → [[event-catalog]] — consumed by notification module
- `AuditLogEntry` (action: `tenant.provisioned`) → [[audit-logging]]

## Related Flows

- [[billing-subscription]] — activate subscription after provisioning
- [[sso-configuration]] — configure SSO for the new tenant
- [[feature-flag-management]] — enable/disable modules
- [[tenant-branding]] — customize look and feel
- [[user-invitation]] — invite additional users

## Module References

- [[infrastructure]] — multi-tenancy, schema provisioning
- [[multi-tenancy]] — row-level security, tenant isolation
- [[tenant-settings]] — default configuration values
- [[authentication]] — first admin user creation
- [[authorization]] — system roles and permissions seeding
