# Feature Flag Management

**Area:** Platform Setup
**Trigger:** Tenant admin views module/feature availability (read-only)
**Required Permission(s):** `settings:admin`
**Related Permissions:** `billing:manage` (some features are plan-gated)

---

## Preconditions

- Tenant is active with a valid subscription
- Subscription plan/custom contract determines which modules and feature keys are commercially included
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Feature Flags
- **UI:** Settings > Modules & Features. Page displays a grid of all ONEVO modules organized by customer-facing area: People, Time Off, Time & Attendance, Work, Monitoring, Calendar, Inbox, Settings, and Analytics where enabled. Each module card shows: name, description, status (Enabled/Disabled/Plan Required), and read-only availability state
- **API:** `GET /api/v1/settings/features`
- **Backend:** `FeatureFlagService.GetAllFlagsAsync()` -> [[frontend/cross-cutting/feature-flags|Feature Flags]]
- **Validation:** Permission check for `settings:admin`
- **DB:** `tenant_module_entitlements`, `tenant_subscriptions.selected_feature_keys`, `feature_flags`, `feature_flag_overrides`

### Step 2: View Available Modules
- **UI:** Module cards organized into categories:
  - **Core (always enabled):** Auth & Security, Core HR, Org Structure
  - **Standard:** Time Off Management, Calendar, Notifications
  - **Advanced:** Time & Attendance, Activity Monitoring, Identity Verification, Exception Engine, Productivity Analytics
  - **Enterprise:** Work Management, Chat, Agentic Chat, Integrations
  
  Plan-gated modules show a lock icon with "Upgrade to [Plan Name] to enable". Tooltip explains what each module provides
- **API:** N/A (data loaded in Step 1)
- **Backend:** N/A
- **Validation:** N/A
- **DB:** None

### Step 3: Request Module or Feature Change
- **UI:** Tenant admin uses contact/support or billing upgrade action. No tenant-facing API toggles runtime flags or module runtime status.
- **API:** N/A for runtime mutation. Developer Platform operators use `/admin/v1/feature-flags/*` for feature overrides and `/admin/v1/tenants/{id}/modules/{moduleKey}/runtime-status` for runtime module disables.
- **Backend:** Tenant-facing services only read effective state.
- **Validation:** Module must be available on the tenant's current plan before Developer Platform operators can enable runtime access. Core module disable remains blocked by admin policy.
- **DB:** No tenant-facing write. Developer Platform writes `tenant_module_entitlements.runtime_override` for module runtime status or `feature_flag_overrides.value` for feature flag overrides.

### Step 4: Confirm Changes
- **UI:** When Developer Platform changes runtime state, navigation menu updates in real-time (via SignalR push) for all connected users. Enabled modules appear in the sidebar; disabled modules disappear
- **API:** N/A (SignalR notification to all connected clients)
- **Backend:** `SignalRHub.SendFeatureUpdateAsync()` - pushes navigation update to all connected sessions for this tenant
- **Validation:** N/A
- **DB:** None

## Variations

### When enabling a module for the first time
- Module may require initial configuration before it becomes fully functional
- After enabling, admin is prompted: "Would you like to configure [Module] now?" with a link to the module's setup page
- Example: enabling Time & Attendance prompts shift schedule setup; enabling Payroll prompts tax configuration

### When disabling a module with active data
- Data is preserved but becomes inaccessible through the UI
- API endpoints for the module return `403 Feature Disabled`
- If re-enabled, all data is available again immediately
- Scheduled jobs for the module are paused (e.g., payroll runs, report generation)

### When subscription plan changes
- On upgrade: previously locked modules become available to toggle
- On downgrade: modules not available in the new plan are auto-disabled at the end of the billing cycle
- Admin receives notification listing affected modules

### Bulk runtime changes
- Bulk runtime changes are Developer Platform operations, not tenant-facing settings actions.
- Confirmation dialog lists all changes before applying in the Developer Platform UI.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Module not available on plan | Toggle disabled with lock icon | "Upgrade to Professional plan to enable this module" |
| Core module disable attempt | Toggle disabled, no click action | "Core modules cannot be disabled" |
| Active workflow depends on module | Disable blocked | "Cannot disable Time Off Management: 12 Time Off requests are pending approval. Resolve or cancel them first" |
| Cache clear fails | Stale flags may persist briefly | No error shown; cache expires within 5 minutes naturally |

## Events Triggered

- `FeatureFlagChangedEvent` -> [[backend/messaging/event-catalog|Event Catalog]] - consumed by navigation service, API middleware, and scheduled job manager
- `AuditLogEntry` (action: `feature.enabled` or `feature.disabled`) -> [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Platform-Setup/billing-subscription|Billing Subscription]] - plan determines available modules
- [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]] - initial module selection during setup
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] - other tenant-level configuration

## Module References

- [[frontend/cross-cutting/feature-flags|Feature Flags]] - feature flag implementation details
- [[modules/configuration/overview|Configuration]] - tenant configuration system
- [[modules/infrastructure/overview|Infrastructure]] - caching layer for feature flags
- [[modules/shared-platform/overview|Shared Platform]] - navigation menu generation based on flags
