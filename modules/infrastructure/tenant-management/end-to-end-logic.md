# Tenant Management — End-to-End Logic

**Module:** Infrastructure
**Feature:** Tenant Management

---

## Provision New Tenant

Tenant creation is an internal ONEVO operator flow. Customers cannot self-sign up, and
`POST /api/v1/tenants` must not exist on the tenant-facing API. The canonical
provisioning workflow is the Developer Platform wizard:
[[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]].

### Draft Creation Flow

```
POST /admin/v1/tenants
  -> Admin TenantController.CreateDraft(CreateTenantDraftCommand)
    -> Platform-admin endpoint only
    -> TenantProvisioningService.CreateDraftAsync(command, ct)
      -> 1. Validate: company name, slug, legal entity, country, timezone, currency, industry_profile, company_size_range
      -> 2. INSERT into tenants (status = 'provisioning', company_size_range)
      -> 3. INSERT primary legal_entities row (name, registration_number, country_id, currency_code, address_json)
      -> 4. Store default timezone and initial tenant_settings captured during account setup
      -> 5. Log to audit_logs: action = "tenant.provisioning_draft_created"
      -> Return tenant_id, status = "provisioning", next_step = "subscription"
```

### Provisioning Completion Flow

After draft creation, the Developer Platform wizard completes the commercial and
access setup through admin endpoints:

1. Assign one reusable subscription plan and tenant-specific commercial terms.
2. Save tenant module entitlement records and module pricing/sales state.
3. Resolve the module-filtered permission catalog.
4. Apply reusable role templates or create tenant-specific roles.
5. Save required tenant settings and module defaults.
6. Invite the first tenant owner with a set-password link.
7. Activate the tenant through `PATCH /admin/v1/tenants/{id}/provision/confirm`.

Activation must fail until tenant details, subscription/commercial terms, active
module entitlements, at least one valid owner/admin role, required settings, and
the owner invite are complete. Operators must not create or handle the tenant
owner's final password.

Roles are independent tenant-scoped permission containers. They do not require
job levels. Job levels and hierarchy are used later for scoped permissions,
approval routing, escalation, and organisation-aware access.

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Duplicate slug | Return 409 Conflict |
| Invalid industry_profile | Return 422 |
| Missing provisioning step | Return 422 checklist from provisioning summary |
| Tenant owner invite missing | Block activation |
| Invalid role permission for enabled modules | Block activation |

## Related

- [[modules/infrastructure/tenant-management/overview|Overview]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[modules/infrastructure/reference-data/overview|Reference Data]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
