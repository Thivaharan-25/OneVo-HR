# Tenant Branding — End-to-End Logic

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
         -> primary_color, accent_color, custom_domain, logo_file_id
      -> 3. Invalidate branding cache
      -> Return Result.Success(brandingDto)

```

## Related

- [[frontend/design-system/theming/tenant-branding|Overview]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[modules/infrastructure/file-management/overview|File Management]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
