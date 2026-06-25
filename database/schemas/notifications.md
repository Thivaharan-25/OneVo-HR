# Notifications - Schema

**Module:** [[modules/notifications/overview|Notifications]]
**Phase:** Phase 1
**Tables:** 0 owned tables

> Notifications module owns delivery behavior. Shared Platform owns all physical notification tables. Do not create separate notification tables in the Notifications module.

---

## Owned Tables

None.

## Referenced Tables

- [[database/schemas/shared-platform#`notifications`|notifications]] — In-app notification records (`recipient_user_id`, `type`, `title`, `message`, `severity`, `delivery_surface`, `is_read`)
- [[database/schemas/shared-platform#`notification_templates`|notification_templates]]
- [[database/schemas/shared-platform#`notification_channels`|notification_channels]]

---

## Related

- [[modules/notifications/overview|Notifications Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
