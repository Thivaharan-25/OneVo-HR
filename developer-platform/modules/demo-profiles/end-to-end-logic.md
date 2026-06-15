# Demo Profiles - End-to-End Logic

## Create / Edit Demo Profile

1. Super Admin opens `/platform/demo-profiles`.
2. Frontend requires `platform.demo_profiles.read`.
3. Super Admin clicks Create or opens an existing profile.
4. Manage actions require `platform.demo_profiles.manage`.
5. Super Admin enters:
   - Demo profile name
   - Trial duration
   - Auto-expire setting
   - Active status
   - Maximum employees
   - Demo storage limit
   - Demo AI token limit when AI demo features are enabled
6. Super Admin configures module access:
   - Module
   - Access level: Full Access, View Only, Archive
   - Feature permissions/toggles
7. Super Admin configures upgrade options:
   - Allowed subscription plans
   - Allowed optional add-ons from those plans
   - Hidden optional add-ons
   - Add-on visibility: Enabled or Show Only
   - Add-on demo usage limits
8. Backend validates that allowed add-ons exist in selected plans and are not base modules in the same plan.
9. Backend saves profile and writes audit log.

## Demo Tenant Creation

1. Super Admin creates a tenant and selects a Demo Profile, or a demo signup/provisioning flow creates a demo tenant from an active profile.
2. Tenant status becomes `trial`.
3. Trial start/end dates are calculated from the profile.
4. Tenant receives shared demo storage and AI token limits.
5. Tenant module access is limited by profile module access levels and feature permissions.
6. Tenant upgrade screen reads allowed plans/add-ons from the active profile snapshot.

## Trial Expiry

1. `TrialExpiryCheckJob` scans active trial tenants.
2. Expiring soon tenants appear in dashboard Trial Follow-up.
3. Expired tenants move to `trial_expired`.
4. Demo access is blocked except upgrade/support flows where policy allows.
5. Tenant notification and audit log are written.

