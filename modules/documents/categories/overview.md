# Document Categories

**Module:** Documents  
**Feature:** Categories

---

## Purpose

Hierarchical categories for organizing documents. Self-referencing via `parent_category_id`.

## Database Tables

### `document_categories`
Fields: `parent_category_id` (nullable for root), `name`, `applies_to` (`company`, `department`, `employee`), `is_active`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/documents/categories` | `documents:read` | List categories |
| POST | `/api/v1/documents/categories` | `documents:manage` | Create category |

## Related

- [[modules/documents/overview|Documents Module]]
- [[frontend/architecture/overview|Document Management]]
- [[frontend/architecture/overview|Templates]]
- [[frontend/architecture/overview|Access Control]]
- [[frontend/architecture/overview|Acknowledgements]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
