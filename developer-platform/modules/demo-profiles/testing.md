# Demo Profiles - Testing

## Required Tests

- Creating a demo profile requires `platform.demo_profiles.manage`.
- Viewing demo profiles requires `platform.demo_profiles.read`.
- Inactive demo profiles cannot be selected for new demo tenants.
- Demo tenant created from profile receives status `trial`.
- Trial end date is calculated from profile duration.
- Demo storage limit and AI token limit are applied to shared tenant resource limits.
- Module access level blocks actions beyond the configured level.
- Feature permissions hide and reject disabled demo features.
- Allowed upgrade plans are visible to demo tenants.
- Plans not allowed by the Demo Profile are hidden and rejected by backend.
- Add-ons already included as base modules are hidden.
- Show Only add-ons are visible but not functional and prompt upgrade.
- Trial expiry moves tenant to `trial_expired`.
- Direct trial extension updates trial end date and writes audit log.
- Direct trial expiry blocks demo access and writes audit log.

