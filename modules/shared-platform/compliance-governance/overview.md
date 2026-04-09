# Compliance & Data Governance

**Module:** Shared Platform  
**Feature:** Compliance & Data Governance

---

## Purpose

Legal holds, retention policies, and GDPR subject access requests.

## Database Tables

### `legal_holds`
Prevents data deletion: `resource_type`, `resource_id`, `reason`, `placed_by_id`, `released_by_id`.

### `retention_policies`
Per resource type: `retention_days`, `action_on_expiry` (`delete`, `anonymize`, `archive`), `compliance_framework`.

### `compliance_exports`
GDPR requests: `export_type` (`subject_access`, `data_portability`, `erasure`), `scope`, `target_user_id`, `status`, `file_url`.

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[frontend/cross-cutting/feature-flags|Feature Flags]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[security/compliance|Compliance]]
- [[security/data-classification|Data Classification]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
