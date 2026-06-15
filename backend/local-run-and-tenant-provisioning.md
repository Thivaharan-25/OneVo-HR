# Local Run And Tenant Provisioning

## Runtime Requirements

To run the backend locally:

- .NET SDK 9
- PostgreSQL reachable by `ConnectionStrings:DefaultConnection`
- Applied EF Core migrations for `ApplicationDbContext`
- JWT environment variables:
  - `JWT_PRIVATE_KEY`
  - `JWT_SCOPED_TOKEN_SECRET`
  - `JWT_ISSUER`
  - `JWT_AUDIENCE`
- Platform-admin JWT variables for tenant creation:
  - `ADMIN_JWT_PUBLIC_KEY`
  - `ADMIN_JWT_ISSUER`
  - `ADMIN_JWT_AUDIENCE`
- Optional Redis connection string. If omitted, permission versioning uses the in-memory/fail-open fallback.
- Optional email settings for password reset:
  - `RESEND_API_KEY`
  - `EMAIL_FROM`
  - `APP_BASE_URL`

`Program.cs` loads `.env` automatically in Development.

## Database

The API uses:

```json
"DefaultConnection": "Host=localhost;Port=5432;Database=onevo;Username=postgres;Password=..."
```

The entitlement migration seeds the default plans:

- `starter`
- `professional`
- `enterprise`

Tenant provisioning needs one of those plan codes to exist and be active.

## Tenant Creation Flow

Tenant creation is an operator/platform-admin flow:

```http
POST /admin/v1/tenants
Authorization: Bearer <platform-admin-jwt>
Content-Type: application/json
```

Target draft-creation body:

```json
{
  "companyName": "Acme Ltd",
  "legalEntityName": "Acme Lanka Pvt Ltd",
  "registrationNumber": "PV12345",
  "slug": "acme",
  "companySizeRange": "51-200",
  "country": "LK",
  "timezone": "Asia/Colombo",
  "currency": "LKR",
  "industryProfile": "office_it"
}
```

The target flow is:

1. `GET /admin/v1/subscription-plans` loads reusable plan catalog records.
2. `GET /admin/v1/modules/catalog` loads reusable module catalog and default pricing.
3. `GET /admin/v1/tenants/validate` validates slug/company/domain/registration details when needed.
4. `POST /admin/v1/tenants` creates a draft tenant in `provisioning` status, saves `company_size_range` on `tenants`, stores default timezone in tenant settings, and activation/setup seeding creates the primary `legal_entities` row with country and currency.
5. `PATCH /admin/v1/tenants/{id}/subscription` assigns one reusable plan plus tenant-specific commercial terms.
6. `PUT /admin/v1/tenants/{id}/modules` records module entitlements, sales state, pricing, currency, and trial/expiry dates.
7. `GET /admin/v1/tenants/{id}/permissions/catalog` returns permissions filtered by enabled modules.
8. `GET /admin/v1/role-templates` loads reusable global role templates.
9. `POST /admin/v1/role-templates` optionally creates a reusable operator-managed template.
10. `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply` applies starter roles.
11. `GET /admin/v1/tenants/{id}/roles`, `POST /admin/v1/tenants/{id}/roles`, and `PUT /admin/v1/tenants/{id}/roles/{roleId}/permissions` allow tenant-specific role creation/editing during provisioning.
12. `PATCH /admin/v1/tenants/{id}/settings` writes required settings.
13. `POST /admin/v1/tenants/{id}/invite-admin` sends the tenant owner set-password invite and assigns a valid owner/admin role.
14. `GET /admin/v1/tenants/{id}/provisioning-summary` returns review data and activation blockers.
15. `PATCH /admin/v1/tenants/{id}/provision/confirm` activates the tenant after all guards pass.

Plan and role rules:

- Operators do not create a new plan for every tenant. Plans are reusable catalog records; tenant-specific price, discount, billing cycle, selected optional add-ons, selected resource-only add-ons, shared resource limits, and module pricing overrides are stored on tenant commercial records.
- Operators can create reusable role templates and assign them to many tenants.
- Operators can also create tenant-specific roles during provisioning without saving them as reusable templates.
- Roles do not require job levels. Job levels must not auto-assign permissions; they can only suggest assignments that an authorized admin confirms. Hierarchy affects scoped access, workflow routing, approvals, and escalation logic.
- `available` and `quoted` modules do not grant tenant-facing access. `purchased`, `trial`, and `subscription_included` can grant access while valid.

> Implementation gap: the current backend may still support direct `adminPassword` on tenant creation. That is temporary only and must be replaced before production. Operators must not choose or copy the tenant owner's final password; the owner sets it through the invite link.

The draft creation endpoint returns:

```json
{
  "tenantId": "..."
}
```

## End-To-End Login After Provisioning

After provisioning, the new admin can log in through:

```http
POST /api/v1/auth/login
```

after completing the set-password invite with:

```json
{
  "tenantSlug": "acme",
  "email": "admin@acme.com",
  "password": "<password chosen by tenant owner>"
}
```

The backend also seeds a local default tenant/admin at startup:

- tenant slug: `onevo`
- admin email: `admin@onevo.com`
- password: `Admin@123`

That default seed is for local development only.

