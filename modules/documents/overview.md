# Module: Documents

**Namespace:** `ONEVO.Modules.Documents`
**Pillar:** 1 — HR Management
**Owner:** Dev 4 (Week 4)
**Tables:** 6

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

## Database Tables (6)

### `document_categories`

Hierarchical categories for organising documents. Self-referencing via `parent_category_id`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `parent_category_id` | `uuid` | FK → document_categories (nullable — null for root) |
| `name` | `varchar(100)` | |
| `applies_to` | `varchar(30)` | `company`, `department`, `employee` |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `documents`

Document metadata. Actual files are stored in blob storage via `IFileService`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `legal_entity_id` | `uuid` | FK → legal_entities (nullable) |
| `category_id` | `uuid` | FK → document_categories |
| `employee_id` | `uuid` | FK → employees (nullable — null for company-wide docs) |
| `title` | `varchar(255)` | |
| `requires_acknowledgement` | `boolean` | Whether employees must acknowledge receipt |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `document_versions`

Version history for a document. Each upload creates a new version.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `document_id` | `uuid` | FK → documents |
| `version_number` | `integer` | Auto-incremented per document |
| `blob_storage_url` | `varchar(500)` | Signed URL or blob path |
| `file_name` | `varchar(255)` | Original file name |
| `effective_date` | `date` | When this version takes effect |
| `expiry_date` | `date` | Nullable |
| `is_current` | `boolean` | Only one current version per document |
| `uploaded_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

### `document_acknowledgements`

Tracks employee acknowledgement of documents that require it.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `document_version_id` | `uuid` | FK → document_versions |
| `employee_id` | `uuid` | FK → employees |
| `acknowledged_by_id` | `uuid` | FK → users (may differ from employee if acknowledged on behalf) |
| `method` | `varchar(20)` | `click`, `e_signature` |
| `acknowledged_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | IPv4/IPv6 for audit |

### `document_access_logs`

Audit trail of who accessed which document versions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `document_version_id` | `uuid` | FK → document_versions |
| `employee_id` | `uuid` | FK → employees |
| `action` | `varchar(20)` | `view`, `download`, `print` |
| `accessed_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | |

### `document_templates`

Reusable templates for generating documents (offer letters, contracts, etc.). Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | |
| `category_id` | `uuid` | FK → document_categories (nullable) |
| `template_content` | `text` | HTML/Markdown template body |
| `variables_json` | `jsonb` | Available merge variables (e.g., `{{employee_name}}`) |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

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

## Features

- [[document-management]] — Document metadata, versioning (`document_versions`), current version tracking
- [[acknowledgements]] — Employee acknowledgement tracking (click or e-signature)
- [[access-control]] — Access log audit trail for document views and downloads
- [[templates]] — Reusable HTML/Markdown document templates with merge variables
- [[categories]] — Hierarchical document categories (self-referencing `parent_category_id`)

---

## Related

- [[multi-tenancy]] — All document metadata is tenant-scoped
- [[compliance]] — Access logs and acknowledgement records for audit
- [[data-classification]] — Files stored in blob storage, never in the database
- [[WEEK4-supporting-bridges]] — Implementation task file

See also: [[module-catalog]], [[core-hr]], [[infrastructure]]
