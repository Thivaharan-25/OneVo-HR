# Module: Documents

**Namespace:** `ONEVO.Modules.Documents`
**Phase:** 2 — Deferred
**Pillar:** 1 — HR Management
**Owner:** Dev 4 (Week 4)
**Tables:** 6

> [!WARNING]
> **This module is deferred to Phase 2. Do not implement.** Document management and versioning are not core to the employee monitoring product. Specs are preserved here for future reference.

---

## Purpose

Document management with versioning, categorization (hierarchical), access control, and expiry tracking. Stores metadata in PostgreSQL, files in blob storage via [[modules/infrastructure/overview|Infrastructure]] `IFileService`.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `IFileService` | File storage |
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Document ownership |

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/Documents/Entities/
  ONEVO.Domain/Features/Documents/Events/

Application (CQRS):
  ONEVO.Application/Features/Documents/Commands/
  ONEVO.Application/Features/Documents/Queries/
  ONEVO.Application/Features/Documents/DTOs/Requests/
  ONEVO.Application/Features/Documents/DTOs/Responses/
  ONEVO.Application/Features/Documents/Validators/
  ONEVO.Application/Features/Documents/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/Documents/

API endpoints:
  ONEVO.Api/Controllers/Documents/DocumentsController.cs

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

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| `DocumentPublished` | `documents.published` | Document published and made available | [[modules/notifications/overview\|Notifications]] (notify affected employees) |
| `AcknowledgementReceived` | `documents.acknowledged` | Employee acknowledges a document | Audit trail |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| `EmployeeHired` | `core-hr.employee.hired` | [[modules/core-hr/overview\|Core HR]] | Assign onboarding documents to new employee |
| `EmployeeOffboarded` | `core-hr.employee.offboarded` | [[modules/core-hr/overview\|Core HR]] | Trigger offboarding document checklist |

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

- [[modules/documents/document-management/overview|Document Management]] — Document metadata, versioning (`document_versions`), current version tracking
- [[modules/documents/acknowledgements/overview|Acknowledgements]] — Employee acknowledgement tracking (click or e-signature)
- [[modules/documents/access-control/overview|Access Control]] — Access log audit trail for document views and downloads
- [[modules/documents/templates/overview|Templates]] — Reusable HTML/Markdown document templates with merge variables
- [[modules/documents/categories/overview|Categories]] — Hierarchical document categories (self-referencing `parent_category_id`)

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All document metadata is tenant-scoped
- [[security/compliance|Compliance]] — Access logs and acknowledgement records for audit
- [[security/data-classification|Data Classification]] — Files stored in blob storage, never in the database
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[modules/infrastructure/overview|Infrastructure]]
