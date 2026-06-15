# Demo Profiles

## Purpose

Demo Profiles define how demo/trial tenants behave before they become paid active tenants. A Demo Profile controls trial duration, auto-expiry, demo resource limits, demo module access, feature-level permissions, and which subscription plans/add-ons are available during upgrade.

Demo Profiles do not create paid subscriptions. They configure the limited demo state and the upgrade choices that a demo customer can see. Demo Profiles do not directly grant arbitrary Module Catalog feature keys; the selected demo plan and selected allowed add-ons produce the tenant's subscription snapshot.

## Data / Systems Controlled

| Table / System | Role |
|---|---|
| `demo_profiles` | Read/write profile identity, trial duration, auto-expiry, active status, resource limits |
| `demo_profile_modules` | Read/write module access levels and feature permissions |
| `demo_profile_upgrade_options` | Read/write allowed plans, allowed add-ons, hidden add-ons, add-on visibility |
| `tenants` | Read demo tenants using the profile |
| `tenant_resource_limits` | Apply demo storage and AI limits to new demo tenants |
| Audit log | Write every profile and limit change |

## Capabilities

- Create and edit demo profiles.
- Configure trial duration and auto-expire behavior.
- Configure maximum employees, demo storage limit, and demo AI token limit.
- Configure module access per module: Full Access, View Only, or Archive.
- Configure feature permissions per module.
- Choose allowed subscription plans for demo upgrade.
- Choose allowed optional add-ons from those plans.
- Hide add-ons that are not approved for the demo profile or are already included as base modules.
- Configure add-on visibility: Enabled or Show Only.
- View demo tenants using the profile.

## Rules

- Only active Demo Profiles can be used for new demo tenants.
- Demo tenants created from a profile inherit its trial duration, limits, module access, and upgrade options.
- Demo users can only upgrade to plans allowed by the active Demo Profile.
- Demo users can only select optional add-ons allowed by the active Demo Profile.
- Add-ons already included as base modules in the selected plan must be hidden.
- Demo storage and AI limits are enforced as shared tenant-level limits.
- Resource-only add-ons selected during demo upgrade increase limits only and must not create module or feature access.
- Feature access after demo upgrade comes from the resulting `tenant_subscriptions.selected_feature_keys`, not directly from the Demo Profile or Module Catalog.
- Profile changes affect new demo tenants unless a separate migration/apply action is explicitly approved.
