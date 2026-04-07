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

- [[shared-platform|Shared Platform Module]]
- [[feature-flags]]
- [[workflow-engine]]
- [[notification-infrastructure]]
- [[gdpr-consent]]
- [[audit-logging]]
- [[compliance]]
- [[data-classification]]
- [[multi-tenancy]]
- [[migration-patterns]]
- [[WEEK1-shared-platform]]
