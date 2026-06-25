# General Settings

**Area:** Configuration
**Trigger:** Admin opens Settings > General
**Required Permission(s):** `settings:admin`
**Related Permissions:** `settings:read` (view only)

---

## Preconditions

- Tenant provisioned -> [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]
- Company context is selected from the topbar tenant/company dropdown.

## Canonical Scope

Settings > General is Company-scoped. It is not free-floating tenant configuration.

- User-facing term: Company.
- Internal storage term: `legal_entities`.
- Switching Company in the topbar reloads this page for the selected Company.
- If selected Company = `All`, hide the Company General form and show a "Select a company to edit General settings" empty state.

Tenant-wide shell settings, if needed, are separate from this page. Tenant shell settings may hold fallback branding or platform defaults, but they must not own Company office location, Company identity, or Company-specific employment context.

## Flow Steps

### Step 1: Navigate to General Settings

- **UI:** Sidebar -> Settings -> General
- **Context:** Read selected Company from topbar context.

### Step 2: Load Company General Settings

- **API:** `GET /api/v1/org/legal-entities/{selectedLegalEntityId}/general`
- **DB:** `legal_entities`
- **Rule:** Do not load editable Company fields when selected Company = `All`.

### Step 3: Edit Company General Fields

Under Settings > General, for the selected Company:

- Company name
- Company display name
- Logo / branding reference
- Timezone
- Default language
- Date format
- Week start day
- Office address label
- Latitude
- Longitude
- Allowed radius in meters
- Status

The office location fields define the Company's single office location for onsite work-location verification. There is no office-location CRUD page and no branch/sub-office list in Phase 1.

### Step 4: Save

- **API:** `PUT /api/v1/org/legal-entities/{selectedLegalEntityId}/general`
- **Backend:** `LegalEntityService.UpdateGeneralAsync()`
- **Result:** Changes apply to the selected Company context.

## Variations

### With `settings:read` only

- Can view selected Company General settings but cannot edit.

### Selected Company = `All`

- Company-scoped forms are hidden.
- User sees an empty state explaining that a Company must be selected before editing General settings.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid timezone | Validation fails | "Invalid timezone selected" |
| Selected Company is `All` | Edit form is hidden | "Select a company to edit General settings" |
| Missing latitude/longitude for onsite verification | Validation fails when onsite verification is enabled | "Office location is required for onsite verification" |
| Missing allowed radius for onsite verification | Validation fails when onsite verification is enabled | "Allowed radius is required for onsite verification" |

## Events Triggered

- `LegalEntityGeneralSettingsUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[Userflow/Org-Structure/legal-entity-setup|Company Setup]]

## Module References

- [[modules/configuration/overview|Configuration]]
- [[modules/org-structure/legal-entities/overview|Companies / Legal Entities]]
