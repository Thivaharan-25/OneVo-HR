# Tenant Branding

**Area:** Platform Setup
**Required Permission(s):** `settings:admin`
**Related Permissions:** None

---

## Preconditions

- Tenant is active with a valid subscription
- Logo file ready (PNG/SVG, recommended 200x50px for header, 512x512px for favicon)
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Branding Settings
- **UI:** Settings > Appearance > Branding. Page shows current branding: logo preview, color scheme preview, custom domain status, and a live preview panel on the right side
- **API:** `GET /api/v1/settings/branding`
- **Backend:** `BrandingService.GetBrandingAsync()` → [[tenant-branding]]
- **Validation:** Permission check for `settings:admin`
- **DB:** `tenant_branding`

### Step 2: Upload Logo
- **UI:** Two upload zones: "Header Logo" (displayed in top navigation, max 2MB) and "Favicon" (browser tab icon, max 500KB). Drag-and-drop or click to browse. Accepted formats: PNG, SVG, ICO (favicon only). Image cropper appears after upload for positioning
- **API:** `POST /api/v1/settings/branding/logo` (multipart form data)
- **Backend:** `BrandingService.UploadLogoAsync()` → [[tenant-branding]]
  1. Validates file type and size
  2. Resizes image to standard dimensions (header: 200x50, favicon: 32x32 and 192x192)
  3. Uploads to blob storage (Azure Blob / S3) with tenant-scoped path
  4. Stores blob URL in `tenant_branding` table
  5. Generates CDN-cached URL
- **Validation:** File type must be PNG, SVG, or ICO. Max file size enforced. Image dimensions validated after upload
- **DB:** `tenant_branding` (logo_url, favicon_url)

### Step 3: Set Brand Colors
- **UI:** Color picker fields:
  - **Primary Color:** Main brand color used for headers, buttons, links (default: #2563EB)
  - **Accent Color:** Secondary color for highlights, badges, active states (default: #7C3AED)
  - **Sidebar Background:** Navigation sidebar color (default: #1E293B)
  - **Sidebar Text:** Navigation text color (default: #F8FAFC)
  
  Each color change updates the live preview panel in real-time. "Reset to defaults" button available
- **API:** N/A (client-side preview only, saved in Step 5)
- **Backend:** N/A
- **Validation:** Valid hex color codes required. Contrast ratio check: text on background must meet WCAG AA accessibility standard (4.5:1 ratio). Warning shown if contrast is insufficient
- **DB:** None (saved in Step 5)

### Step 4: Configure Custom Domain (Optional)
- **UI:** Input field for custom domain (e.g., `hr.acmecorp.com`). Instructions panel: "Add a CNAME record pointing to `{tenantSlug}.onevo.app`". Status indicator: "DNS Pending" / "DNS Verified" / "SSL Active". "Verify DNS" button to check configuration
- **API:** `POST /api/v1/settings/branding/domain`
- **Backend:** `DomainService.ConfigureCustomDomainAsync()` → [[tenant-branding]]
  1. Validates domain format
  2. Stores domain in `tenant_branding`
  3. Initiates DNS verification (checks CNAME record)
  4. If DNS verified: provisions SSL certificate via Let's Encrypt / Azure managed certificate
  5. Configures reverse proxy routing for the custom domain
- **Validation:** Domain must be a valid FQDN. Domain must not already be registered to another tenant. DNS CNAME must point to correct target
- **DB:** `tenant_branding` (custom_domain, domain_status, ssl_status)

### Step 5: Preview and Save
- **UI:** Full preview panel shows: login page with logo and colors, dashboard header, sidebar navigation. "Save Changes" button. Option to "Preview as Employee" (opens preview in new tab)
- **API:** `PUT /api/v1/settings/branding`
  ```json
  {
    "primaryColor": "#2563EB",
    "accentColor": "#7C3AED",
    "sidebarBg": "#1E293B",
    "sidebarText": "#F8FAFC",
    "customDomain": "hr.acmecorp.com"
  }
  ```
- **Backend:** `BrandingService.SaveBrandingAsync()` → [[tenant-branding]]
  1. Updates `tenant_branding` table
  2. Invalidates CDN cache for tenant's static assets
  3. Pushes branding update to all connected clients via SignalR
- **Validation:** All color values must be valid hex codes. If custom domain is set, DNS must be verified
- **DB:** `tenant_branding`

## Variations

### When custom domain DNS is not yet propagated
- Domain saved with status `dns_pending`
- Background job checks DNS every 15 minutes for up to 72 hours
- Admin receives email notification when DNS is verified and SSL is active
- Users can continue using the default `{tenant}.onevo.app` URL

### When reverting to default branding
- Click "Reset to Defaults" button
- All custom colors reset to ONEVO defaults
- Logo removed (ONEVO logo shown instead)
- Custom domain can be retained or removed separately

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Logo file too large | Upload rejected | "File size exceeds 2MB limit. Please compress or resize your logo" |
| Unsupported file format | Upload rejected | "Unsupported file format. Please upload a PNG or SVG file" |
| Poor color contrast | Warning shown | "Warning: The selected text color has insufficient contrast against the background (ratio: 2.1:1). Minimum recommended: 4.5:1" |
| DNS verification fails | Domain stays pending | "DNS verification failed. Please ensure a CNAME record for hr.acmecorp.com points to {tenant}.onevo.app" |
| SSL provisioning fails | Domain verified but no SSL | "DNS verified but SSL certificate provisioning failed. HTTPS will be available once the certificate is issued (usually within 1 hour)" |

## Events Triggered

- `BrandingUpdatedEvent` → [[event-catalog]] — consumed by CDN cache invalidation
- `CustomDomainVerifiedEvent` → [[event-catalog]] — triggers SSL provisioning
- `AuditLogEntry` (action: `branding.updated`) → [[audit-logging]]

## Related Flows

- [[tenant-provisioning]] — branding typically configured after initial setup
- [[tenant-settings]] — other tenant configuration options

## Module References

- [[tenant-branding]] — branding implementation details
- [[tenant-settings]] — tenant-level settings storage
- [[infrastructure]] — CDN, blob storage, SSL provisioning
- [[configuration]] — tenant configuration management
