# Tenant Branding - End-to-End Logic

**Module:** Shared Platform
**Feature:** Tenant Branding

---

## Update Branding

### Flow

```
PUT /api/v1/branding
  -> BrandingController.Update(UpdateBrandingCommand)
    -> [RequirePermission("settings:admin")]
    -> BrandingService.UpdateAsync(command, ct)
      -> 1. If logo file provided: upload via IFileService
      -> 2. UPSERT into tenant_branding
         -> primary_color, accent_color, logo_file_id
      -> 3. Invalidate branding cache
      -> Return Result.Success(brandingDto)

```

## Default Tenant URL Resolution

```
Browser opens https://{tenantSlug}.onevo.com
  -> Cloudflare wildcard DNS (*.onevo.com) routes traffic to Azure
  -> Azure forwards request to ONEVO.Api/frontend host
  -> TenantResolutionMiddleware reads Host header
  -> Extract slug from subdomain
  -> Load active tenant by tenants.slug
  -> Set ITenantContext
  -> Continue auth, entitlement, and permission checks
```

Rules:

- The default tenant URL is generated from `tenants.slug`.
- Blocked system slugs such as `www`, `api`, `console`, `admin`, `status`, `support`, `assets`, `cdn`, `mail`, and `app` cannot be used as tenant slugs.
- Unknown slugs return a tenant-not-found response without leaking tenant data.

## Related

- [[frontend/design-system/theming/tenant-branding|Overview]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[modules/infrastructure/file-management/overview|File Management]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
