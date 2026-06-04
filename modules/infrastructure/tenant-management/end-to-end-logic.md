# Tenant Management — End-to-End Logic

**Module:** Infrastructure
**Feature:** Tenant Management

---

## Provision New Tenant

Tenant creation is an internal ONEVO operator flow. Customers cannot self-sign up, and
`POST /api/v1/tenants` must not exist on the tenant-facing API. The canonical
tenant creation workflow is the Developer Platform two-step wizard plus post-creation Manage/Configure:
[[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]].

### Draft Creation Flow

```
POST /admin/v1/tenants
  -> Admin TenantController.CreateDraft(CreateTenantDraftCommand)
    -> Platform-admin endpoint only
    -> TenantProvisioningService.CreateDraftAsync(command, ct)
      -> 1. Validate: company name, slug, primary contact email, country, industry_profile, registration/profile name, registration number, company_size_range, timezone, currency
      -> 2. INSERT into tenants (status = 'provisioning', tenant profile fields)
      -> 3. Store tenant profile/contact metadata captured during account setup
      -> 4. Log to audit_logs: action = "tenant.provisioning_draft_created"
      -> Return tenant_id, status = "provisioning", next_step = "subscription"
```

### Post-Creation Manage / Configure Flow

After Step 2 commercial selection succeeds, the tenant card exposes
Manage/Configure. Operators complete module entitlements, role setup, service
setup, tenant configuration, and owner invite readiness through admin endpoints:

1. Confirm tenant module entitlement records and module pricing/sales state.
2. Resolve the module-filtered permission catalog.
3. Apply reusable role templates or create tenant-specific roles.
4. Select or auto-add module-connected free/global and paid setup services required for the modules bought by the tenant.
5. Apply reusable configuration templates or create tenant-specific template overrides.
6. Mark module/service configuration as ready to use.
7. Optionally invite the first tenant owner with a set-password link.
8. Activate the tenant through `PATCH /admin/v1/tenants/{id}/provision/confirm`.

Activation must fail until tenant details, subscription/commercial terms, active
module entitlements, at least one valid owner/admin role, required settings, and
required module/service configuration are complete. The owner invite is an
explicit operator action and must not be sent automatically by tenant creation,
commercial selection, module configuration, or activation. Operators must not
create or handle the tenant owner's final password.

Tenant profile creation collects country, registration/profile name, registration
number, timezone, and currency as tenant profile fields, but it does not create
deprecated registration-profile rows. Activation/setup seeding
creates one primary legal entity. Additional operating companies under the same customer
account are added as legal entities inside the tenant. Separate tenants are used only
for separate customer accounts that must remain isolated.

Roles are independent tenant-scoped permission containers. They do not require
job levels. Job levels can suggest role assignments for admin confirmation, but
they must not auto-assign permissions. Hierarchy is used later for scoped
access, approval routing, escalation, and organisation-aware access.

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Duplicate slug | Return 409 Conflict |
| Invalid industry_profile | Return 422 |
| Missing provisioning step | Return 422 checklist from provisioning summary |
| Required module/service configuration missing | Block activation |
| Invalid role permission for enabled modules | Block activation |

## Related

- [[modules/infrastructure/tenant-management/overview|Overview]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[modules/infrastructure/reference-data/overview|Reference Data]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]

