# Notifications — Schema

**Module:** [[modules/notifications/overview|Notifications]]
**Phase:** Phase 1
**Tables:** 2

> These tables are also listed under [[database/schemas/shared-platform|Shared Platform]] since the entities are configured in the shared `AppDbContext`. They are included here for module-level reference.

---

## `notification_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `event_type` | `varchar(50)` | e.g., `leave.approved`, `exception.alert.created`, `alert.escalated` |
| `channel` | `varchar(20)` | `email`, `in_app`, `push`, `signalr` |
| `subject_template` | `varchar(255)` | |
| `body_template` | `text` | Liquid/Handlebars template |
| `is_active` | `boolean` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `notification_channels`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `channel_type` | `varchar(20)` | `email`, `slack`, `webhook` |
| `config_json` | `jsonb` | Channel-specific config |
| `credentials_encrypted` | `bytea` | API keys etc. |
| `is_active` | `boolean` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## Related

- [[modules/notifications/overview|Notifications Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
