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
  "slug": "acme",
  "country": "LK",
  "timezone": "Asia/Colombo",
  "currency": "LKR",
  "industryProfile": "office_it"
}
```

The target flow is:

1. `POST /admin/v1/tenants` creates a draft tenant in `provisioning` status.
2. `PATCH /admin/v1/tenants/{id}/subscription` assigns subscription/commercial terms.
3. `PUT /admin/v1/tenants/{id}/modules` records module entitlements and sales state.
4. `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply` applies starter roles.
5. `PATCH /admin/v1/tenants/{id}/settings` writes required settings.
6. `POST /admin/v1/tenants/{id}/invite-admin` sends the tenant owner set-password invite.
7. `PATCH /admin/v1/tenants/{id}/provision/confirm` activates the tenant after all guards pass.

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
