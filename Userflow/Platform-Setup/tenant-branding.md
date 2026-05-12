# Tenant Branding

**Area:** Platform Setup
**Trigger:** Admin navigates to branding settings (user action - configuration)
**Required Permission(s):** `settings:admin`

---

## Preconditions

- Tenant is active with a valid subscription
- Logo file ready (PNG/SVG, recommended 200x50px for header, 512x512px for favicon)
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Branding Settings

- **UI:** Settings > Appearance > Branding. Page shows current branding, logo preview, color scheme preview, default tenant URL (`{tenantSlug}.onevo.com`), and a live preview panel.
- **API:** `GET /api/v1/settings/branding`
- **Backend:** `BrandingService.GetBrandingAsync()`
- **Validation:** Permission check for `settings:admin`
- **DB:** `tenant_branding`, `tenants.slug`

### Step 2: Upload Logo

- **UI:** Upload zones for header logo and favicon. Accepted formats: PNG, SVG, ICO for favicon.
- **API:** `POST /api/v1/settings/branding/logo`
- **Backend:** `BrandingService.UploadLogoAsync()`
  1. Validates file type and size.
  2. Resizes image to standard dimensions.
  3. Uploads binary file to Cloudflare R2 object storage with tenant-scoped path.
  4. Stores metadata in `file_records`.
  5. Links the logo file from `tenant_branding.logo_file_id`.
- **Validation:** File type, file size, and image dimensions are validated.
- **DB:** `file_records`, `tenant_branding`

### Step 3: Set Brand Colors

- **UI:** Color picker fields for primary color, accent color, sidebar background, and sidebar text. Live preview updates immediately.
- **API:** N/A until save.
- **Backend:** N/A until save.
- **Validation:** Valid hex color codes. Contrast warning if selected colors do not meet WCAG AA.
- **DB:** None until save.

### Step 4: View Default Tenant URL

- **UI:** Shows the default ONEVO-owned tenant URL, for example `https://acme.onevo.com`.
- **API:** N/A
- **Backend:** N/A
- **Validation:** Tenant slug is validated during tenant provisioning.
- **DB:** `tenants.slug`

### Step 5: Preview and Save

- **UI:** Full preview panel shows login page, dashboard header, and sidebar navigation. Admin clicks "Save Changes".
- **API:** `PUT /api/v1/settings/branding`

```json
{
  "primaryColor": "#2563EB",
  "accentColor": "#7C3AED",
  "sidebarBg": "#1E293B",
  "sidebarText": "#F8FAFC"
}
```

- **Backend:** `BrandingService.SaveBrandingAsync()`
  1. Updates `tenant_branding`.
  2. Invalidates branding/static asset cache.
  3. Pushes branding update to connected clients via SignalR.
- **Validation:** All color values must be valid hex codes.
- **DB:** `tenant_branding`

## Variations

### When reverting to default branding

- Admin clicks "Reset to Defaults".
- All custom colors reset to ONEVO defaults.
- Logo is removed and ONEVO logo is shown.
- Default tenant URL remains unchanged because it comes from `tenants.slug`.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Logo file too large | Upload rejected | "File size exceeds the limit. Please compress or resize your logo." |
| Unsupported file format | Upload rejected | "Unsupported file format. Please upload a PNG, SVG, or ICO file." |
| Poor color contrast | Warning shown | "The selected colors may be hard to read. Minimum recommended contrast is 4.5:1." |

## Events Triggered

- `BrandingUpdatedEvent` -> consumed by cache invalidation.
- `AuditLogEntry` with action `branding.updated`.

## Related Flows

- [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- [[Userflow/Configuration/tenant-settings|Tenant Settings]]

## Module References

- [[modules/shared-platform/tenant-branding/overview|Tenant Branding]]
- [[modules/infrastructure/file-management/overview|File Management]]
- [[modules/configuration/overview|Configuration]]
