# Legal Entities

**Module:** Org Structure  
**Feature:** Legal Entities

---

## Purpose

Company legal entities with registration and country information.

## Database Tables

### `legal_entities`
Fields: `name`, `registration_number`, `country_id`, `address_json`, `is_active`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/legal-entities` | `settings:admin` | List |
| POST | `/api/v1/legal-entities` | `settings:admin` | Create |

## Related

- [[org-structure|Org Structure Module]]
- [[departments]]
- [[cost-centers]]
- [[job-hierarchy]]
- [[teams]]
- [[multi-tenancy]]
- [[authorization]]
- [[shared-kernel]]
- [[migration-patterns]]
- [[WEEK1-org-structure]]
