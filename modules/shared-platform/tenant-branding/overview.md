# Tenant Branding

**Module:** Shared Platform  
**Feature:** Tenant Branding

---

## Purpose

Custom branding per tenant and per-user UI preferences.

## Database Tables

### `tenant_branding`
Fields: `custom_domain`, `logo_file_id`, `primary_color`, `accent_color`, `metadata`.

### `user_preferences`
Per-user: `preference_key` (`theme`, `locale`, `timezone`), `preference_value` (jsonb).

## Related

- [[shared-platform|Shared Platform Module]]
- [[tenant-management]]
- [[file-management]]
- [[user-management]]
- [[multi-tenancy]]
- [[authorization]]
- [[WEEK1-shared-platform]]
