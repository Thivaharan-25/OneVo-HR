# Tenant Management — End-to-End Logic

**Module:** Infrastructure
**Feature:** Tenant Management

---

## Provision New Tenant

### Flow

```
POST /api/v1/tenants
  -> TenantController.Provision(CreateTenantCommand)
    -> Public endpoint (signup flow)
    -> TenantService.ProvisionTenantAsync(command, ct)
      -> 1. Validate: name, slug (unique), industry_profile
      -> 2. INSERT into tenants (status = 'trial')
      -> 3. Seed default data:
         -> a. Create default roles (Admin, HR Manager, Manager, Employee)
         -> b. Assign all permissions to Admin role
         -> c. Create monitoring_feature_toggles based on industry_profile
            -> e.g., office_it gets activity_monitoring ON, manufacturing gets biometric ON
         -> d. Create default tenant_settings (timezone, work hours)
         -> e. Create admin user account
      -> 4. Create subscription (trial plan)
      -> 5. Log to audit_logs: action = "tenant.provisioned"
      -> Return Result.Success(tenantDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Duplicate slug | Return 409 Conflict |
| Invalid industry_profile | Return 422 |

## Related

- [[modules/infrastructure/tenant-management/overview|Overview]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[modules/infrastructure/reference-data/overview|Reference Data]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
