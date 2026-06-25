# Module: Documents

**Feature Folder:** `Application/Features/Documents`
**Phase:** Shared - Phase 1
**Pillar:** 3 (WorkSync)
**Owner:** Dev 4 (HR additions) / Dev 8 (Work Collaboration)
**Tables:** 9

---

## Purpose

Document management with versioning, categorization (hierarchical), approval workflow, wiki pages, and expiry tracking. Shared between HR (employee/company documents) and WorkSync (project/workspace documents). Stores metadata in PostgreSQL, files in blob storage via `IFileService`.

The `documents` table is a **shared table** - HR scope uses `employee_id` and company/profile document scope; WorkSync scope uses `workspace_id`/`project_id`. Both scopes coexist in the same table, differentiated by `document_scope`.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `IFileService` | File storage (blob) |
| **Depends on** | [[modules/core-hr/overview\|Core HR]] | `IEmployeeService` | HR document ownership |
| **Depends on** | Work Foundation | `workspaces`, `projects` | WorkSync document scope |

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

## Database Tables (9)

### `document_categories`

Hierarchical categories for organising documents. Self-referencing via `parent_category_id`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `parent_category_id` | `uuid` | FK -> document_categories (nullable - null for root) |
| `name` | `varchar(100)` | |
| `applies_to` | `varchar(30)` | `company`, `department`, `employee`, `project`, `workspace` |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `documents`

Document metadata. Actual files are stored in blob storage via `IFileService`. Shared between HR and WorkSync scopes.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | Optional FK -> legal_entities (nullable - tenant/workspace scope) |
| `employee_id` | `uuid` | FK -> employees (nullable - HR employee-level docs) |
| `workspace_id` | `uuid` | FK -> workspaces (nullable - WorkSync scope) |
| `project_id` | `uuid` | FK -> projects (nullable - WorkSync project-level docs) |
| `document_scope` | `varchar(20)` | `employee`, `company`, `project`, `workspace` |
| `category_id` | `uuid` | FK -> document_categories (nullable) |
| `title` | `varchar(255)` | |
| `status` | `varchar(20)` | `draft`, `in_review`, `approved`, `published`, `archived` |
| `requires_acknowledgement` | `boolean` | Whether employees must acknowledge receipt |
| `locked_at` | `timestamptz` | Set when status -> approved; null otherwise |
| `locked_by` | `uuid` | FK -> users (nullable - the approver who locked) |
| `approved_version_id` | `uuid` | FK -> document_versions (nullable - version locked at approval) |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Approval lock invariant:** When `document_approvals.status` -> `approved`, the following are set **atomically in one transaction**: `documents.status = 'approved'`, `locked_at = now()`, `locked_by = approver_id`, `approved_version_id = latest version id`. Only admins can unlock an approved document.

### `document_versions`

Version history for a document. Each upload creates a new version.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `document_id` | `uuid` | FK -> documents |
| `version_number` | `integer` | Auto-incremented per document (not global) |
| `blob_storage_url` | `varchar(500)` | Signed URL or blob path |
| `file_name` | `varchar(255)` | Original file name |
| `effective_date` | `date` | When this version takes effect |
| `expiry_date` | `date` | Nullable |
| `is_current` | `boolean` | Only one current version per document |
| `uploaded_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |

### `document_approvals`

Approval workflow records. When approved, triggers the document lock atomically.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `document_id` | `uuid` | FK -> documents |
| `document_version_id` | `uuid` | FK -> document_versions (version being approved) |
| `requested_by_id` | `uuid` | FK -> users |
| `approver_id` | `uuid` | FK -> users |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected` |
| `comments` | `text` | Nullable |
| `decided_at` | `timestamptz` | Nullable - set when approved or rejected |
| `created_at` | `timestamptz` | |

### `document_acknowledgements`

Tracks employee acknowledgement of documents that require it.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `document_version_id` | `uuid` | FK -> document_versions |
| `employee_id` | `uuid` | FK -> employees |
| `acknowledged_by_id` | `uuid` | FK -> users (may differ from employee if on behalf) |
| `method` | `varchar(20)` | `click`, `e_signature` |
| `acknowledged_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | IPv4/IPv6 for audit |

### `document_access_logs`

Audit trail of who accessed which document versions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `document_version_id` | `uuid` | FK -> document_versions |
| `user_id` | `uuid` | FK -> users |
| `action` | `varchar(20)` | `view`, `download`, `print` |
| `accessed_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | |

### `document_templates`

Reusable templates for generating documents (offer letters, contracts, etc.).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(100)` | |
| `category_id` | `uuid` | FK -> document_categories (nullable) |
| `template_content` | `text` | HTML/Markdown template body |
| `variables_json` | `jsonb` | Available merge variables (e.g. `{{employee_name}}`) |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `wiki_pages`

Workspace/project wiki pages. Unlimited nesting via self-FK; cycles are forbidden.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `workspace_id` | `uuid` | FK -> workspaces |
| `project_id` | `uuid` | FK -> projects (nullable - workspace-level pages have null) |
| `parent_page_id` | `uuid` | FK -> wiki_pages (nullable - null for root pages) |
| `title` | `varchar(255)` | |
| `content` | `text` | Markdown body |
| `created_by_id` | `uuid` | FK -> users |
| `last_edited_by_id` | `uuid` | FK -> users (nullable) |
| `is_published` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Cycle invariant:** Application layer must verify no ancestor chain loops before inserting or updating `parent_page_id`.

### `task_documents`

Links tasks to documents (editor-created links only). File attachments use the separate `attachments` table.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `task_id` | `uuid` | FK -> tasks |
| `document_id` | `uuid` | FK -> documents |
| `linked_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |

---

## Domain Events (MediatR)

| Event | Published When | Handler |
|:------|:---------------|:--------|
| `DocumentApprovedEvent` | `document_approvals.status` -> `approved` | Sets document lock atomically (status, locked_at, locked_by, approved_version_id) |
| `DocumentPublishedEvent` | `documents.status` -> `published` | Notifications module - notify affected employees/workspace members |
| `DocumentAcknowledgedEvent` | Employee acknowledges a document | Audit log entry |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/documents` | `documents:read` | List documents (scope-filtered) |
| POST | `/api/v1/documents` | `documents:write` | Create document metadata |
| GET | `/api/v1/documents/{id}` | `documents:read` | Get document + current version |
| GET | `/api/v1/documents/{id}/versions` | `documents:read` | Version history |
| POST | `/api/v1/documents/{id}/versions` | `documents:write` | Upload new version |
| POST | `/api/v1/documents/{id}/approvals` | `documents:approve` | Submit for approval / approve / reject |
| POST | `/api/v1/documents/{id}/unlock` | `documents:admin` | Unlock an approved document (admin only) |
| GET | `/api/v1/documents/categories` | `documents:read` | List categories |
| POST | `/api/v1/documents/categories` | `documents:manage` | Create category |
| GET | `/api/v1/workspaces/{wsId}/wiki` | `wiki:read` | List wiki pages |
| POST | `/api/v1/workspaces/{wsId}/wiki` | `wiki:write` | Create wiki page |
| GET | `/api/v1/workspaces/{wsId}/wiki/{pageId}` | `wiki:read` | Get wiki page |
| PATCH | `/api/v1/workspaces/{wsId}/wiki/{pageId}` | `wiki:write` | Update wiki page |
| POST | `/api/v1/tasks/{taskId}/documents` | `tasks:write` | Link document to task |

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] - All document metadata is tenant-scoped
- [[security/compliance|Compliance]] - Access logs and acknowledgement records for audit
- [[security/data-classification|Data Classification]] - Files stored in blob storage, never in the database
- [[current-focus/DEV8-documents-github-ide|DEV8: Documents, GitHub, IDE]] - Implementation task file
- [[modules/work-management/collaboration/overview|Work Collaboration]] - wiki_pages and task_documents context

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core HR]], [[modules/infrastructure/overview|Infrastructure]]
