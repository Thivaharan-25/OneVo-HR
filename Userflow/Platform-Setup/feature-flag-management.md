# Feature Flag Management

**Area:** Platform Setup
**Required Permission(s):** `settings:admin`
**Related Permissions:** `billing:manage` (some features are plan-gated)

---

## Preconditions

- Tenant is active with a valid subscription
- Subscription plan determines which modules are available to toggle
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Feature Flags
- **UI:** Settings > Modules & Features. Page displays a grid of all ONEVO modules organized by pillar: HR Management, Workforce Intelligence, Analytics. Each module card shows: name, description, status (Enabled/Disabled/Plan Required), and toggle switch
- **API:** `GET /api/v1/settings/features`
- **Backend:** `FeatureFlagService.GetAllFlagsAsync()` → [[feature-flags]]
- **Validation:** Permission check for `settings:admin`
- **DB:** `tenant_feature_flags`, `billing_plans` (to determine plan-gated features)

### Step 2: View Available Modules
- **UI:** Module cards organized into categories:
  - **Core (always enabled):** Auth & Security, Core HR, Org Structure
  - **Standard:** Leave Management, Payroll, Performance, Documents, Calendar, Notifications
  - **Advanced:** Skills & Learning, Expense, Grievance, Reporting Engine
  - **Enterprise:** Workforce Presence, Activity Monitoring, Identity Verification, Exception Engine, Productivity Analytics, Agent Gateway
  
  Plan-gated modules show a lock icon with "Upgrade to [Plan Name] to enable". Tooltip explains what each module provides
- **API:** N/A (data loaded in Step 1)
- **Backend:** N/A
- **Validation:** N/A
- **DB:** None

### Step 3: Toggle Module On/Off
- **UI:** Click toggle switch on a module card. If enabling: confirmation dialog shows "Enabling [Module] will make the following features available to users with appropriate permissions: [feature list]". If disabling: warning dialog shows "Disabling [Module] will hide it from all users. Existing data will be preserved but inaccessible"
- **API:** `PUT /api/v1/settings/features/{moduleCode}`
  ```json
  { "enabled": true }
  ```
- **Backend:** `FeatureFlagService.SetFeatureFlagAsync()` → [[feature-flags]]
  1. Updates `tenant_feature_flags` table
  2. Clears feature flag cache for the tenant
  3. Publishes `FeatureFlagChangedEvent`
- **Validation:** Module must be available on the tenant's current plan. Core modules cannot be disabled. If disabling, checks for no in-progress workflows dependent on the module
- **DB:** `tenant_feature_flags`

### Step 4: Confirm Changes
- **UI:** Toast notification: "[Module] has been enabled/disabled". Navigation menu updates in real-time (via SignalR push) for all connected users. Enabled modules appear in the sidebar; disabled modules disappear
- **API:** N/A (SignalR notification to all connected clients)
- **Backend:** `SignalRHub.SendFeatureUpdateAsync()` — pushes navigation update to all connected sessions for this tenant
- **Validation:** N/A
- **DB:** None

## Variations

### When enabling a module for the first time
- Module may require initial configuration before it becomes fully functional
- After enabling, admin is prompted: "Would you like to configure [Module] now?" with a link to the module's setup page
- Example: enabling Workforce Presence prompts shift schedule setup; enabling Payroll prompts tax configuration

### When disabling a module with active data
- Data is preserved but becomes inaccessible through the UI
- API endpoints for the module return `403 Feature Disabled`
- If re-enabled, all data is available again immediately
- Scheduled jobs for the module are paused (e.g., payroll runs, report generation)

### When subscription plan changes
- On upgrade: previously locked modules become available to toggle
- On downgrade: modules not available in the new plan are auto-disabled at the end of the billing cycle
- Admin receives notification listing affected modules

### Bulk toggle
- Admin can select multiple modules and enable/disable them in a single operation
- Confirmation dialog lists all changes before applying

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Module not available on plan | Toggle disabled with lock icon | "Upgrade to Professional plan to enable this module" |
| Core module disable attempt | Toggle disabled, no click action | "Core modules cannot be disabled" |
| Active workflow depends on module | Disable blocked | "Cannot disable Leave Management: 12 leave requests are pending approval. Resolve or cancel them first" |
| Cache clear fails | Stale flags may persist briefly | No error shown; cache expires within 5 minutes naturally |

## Events Triggered

- `FeatureFlagChangedEvent` → [[event-catalog]] — consumed by navigation service, API middleware, and scheduled job manager
- `AuditLogEntry` (action: `feature.enabled` or `feature.disabled`) → [[audit-logging]]

## Related Flows

- [[billing-subscription]] — plan determines available modules
- [[tenant-provisioning]] — initial module selection during setup
- [[tenant-settings]] — other tenant-level configuration

## Module References

- [[feature-flags]] — feature flag implementation details
- [[configuration]] — tenant configuration system
- [[infrastructure]] — caching layer for feature flags
- [[shared-platform]] — navigation menu generation based on flags
