# Module: Documents

**Namespace:** `ONEVO.Modules.Documents`
**Pillar:** 1 — HR Management
**Owner:** Dev 4 (Week 4)
**Tables:** 5

---

## Purpose

Document management with versioning, categorization (hierarchical), access control, and expiry tracking. Stores metadata in PostgreSQL, files in blob storage via [[infrastructure]] `IFileService`.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `IFileService` | File storage |
| **Depends on** | [[core-hr]] | `IEmployeeService` | Document ownership |

---

## Database Tables (5)

| Table | Purpose | Key Notes |
|:------|:--------|:----------|
| `document_categories` | Hierarchical categories | Self-referencing via `parent_category_id` |
| `documents` | Document metadata | `employee_id`, `category_id`, `status`, `expiry_date` |
| `document_versions` | Version history | `document_id`, `version_number`, `file_record_id`, `uploaded_by_id` |
| `document_access_log` | Who accessed what | Audit trail |
| `document_templates` | Reusable templates (offer letters, contracts) | `template_content`, `variables_json` |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/documents` | `documents:read` | List documents |
| POST | `/api/v1/documents` | `documents:write` | Upload document |
| GET | `/api/v1/documents/{id}` | `documents:read` | Download document |
| GET | `/api/v1/documents/{id}/versions` | `documents:read` | Version history |
| POST | `/api/v1/documents/{id}/versions` | `documents:write` | Upload new version |
| GET | `/api/v1/documents/categories` | `documents:read` | List categories |
| POST | `/api/v1/documents/categories` | `documents:manage` | Create category |

See also: [[module-catalog]], [[core-hr]], [[infrastructure]]
