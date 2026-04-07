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

- [[documents|Documents Module]]
- [[documents/document-management/overview|Document Management]]
- [[documents/templates/overview|Templates]]
- [[documents/access-control/overview|Access Control]]
- [[documents/acknowledgements/overview|Acknowledgements]]
- [[auth-architecture]]
- [[data-classification]]
- [[multi-tenancy]]
- [[event-catalog]]
- [[WEEK4-supporting-bridges]]
