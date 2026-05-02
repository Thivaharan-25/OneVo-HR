# Collaboration (Documents, Wiki, Task Docs)

**Module:** WorkSync
**Feature:** Collaboration
**Namespace:** `WorkSync.Collaboration`
**Owner:** DEV8
**Tables:** 5 (shared with HR Documents module)

---

## Purpose

WorkSync Collaboration extends the shared `documents` table with workspace/project scope, adds an approval workflow with document locking, wiki pages for structured knowledge, and `task_documents` for linking documents to tasks. The `documents` table is shared infrastructure — HR Documents and WorkSync Collaboration coexist in the same table.

---

## Database Tables

### `documents` (WorkSync columns only — shared with HR Documents)

WorkSync adds these columns to the shared table:
- `workspace_id` (FK → workspaces, nullable)
- `project_id` (FK → projects, nullable)
- `document_scope` (`employee`, `company`, `project`, `workspace`)
- `status` extended: `draft` / `in_review` / **`approved`** / `published` / `archived`
- `locked_at` (timestamptz, nullable)
- `locked_by` (uuid, FK → users, nullable)
- `approved_version_id` (uuid, FK → document_versions, nullable)

See [[modules/documents/overview|Documents Module]] for full column list.

### `document_versions`
Version history. Key columns: `document_id`, `version_number` (auto-incremented per document — NOT global), `blob_storage_url`, `file_name`, `effective_date`, `expiry_date`, `is_current`, `uploaded_by_id`.

### `document_approvals`
Approval workflow. Key columns: `document_id`, `document_version_id`, `requested_by_id`, `approver_id`, `status` (`pending`, `approved`, `rejected`), `comments`, `decided_at`.

When status → `approved`: set `documents.status = 'approved'`, `locked_at`, `locked_by`, `approved_version_id` atomically in one transaction.

### `wiki_pages`
Workspace/project wiki. Key columns: `workspace_id`, `project_id` (nullable — workspace-level pages), `parent_page_id` (FK → wiki_pages, nullable — unlimited nesting, no cycles allowed), `title`, `content` (Markdown), `created_by_id`, `last_edited_by_id`, `is_published`.

### `task_documents`
Editor-created links from tasks to documents. Key columns: `task_id`, `document_id`, `linked_by_id`, `created_at`.

File attachments use the existing `attachments` table — `task_documents` is for document-editor links only.

---

## Key Business Rules

1. **Document approval lock (atomic transaction):** `document_approvals.status → approved` triggers: `documents.status = 'approved'`, `locked_at = now()`, `locked_by = approver_id`, `approved_version_id = latest version id`. All four fields in one DB transaction.
2. **Approved document editing:** Only admins can unlock. Unlocking requires explicit `POST /unlock`, clears lock fields, sets status back to `draft`, re-approval required.
3. **version_number:** Auto-incremented per document via `SELECT MAX(version_number) + 1 FROM document_versions WHERE document_id = ?` inside the upload transaction.
4. **wiki_pages cycle check:** Application layer must verify no ancestor cycle before inserting/updating `parent_page_id`. Unlimited depth is allowed; cycles are forbidden.
5. HR `documents` columns (`employee_id`, `legal_entity_id`) must never be dropped — shared table.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `DocumentApprovedEvent` | document_approvals status → approved | Sets document lock (atomically) |
| `DocumentPublishedEvent` | documents.status → published | Notifications module |
| `WikiPagePublishedEvent` | wiki_pages.is_published = true | Notifications |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workspaces/{wsId}/documents` | `documents:read` | List workspace documents |
| POST | `/api/v1/workspaces/{wsId}/documents` | `documents:write` | Create document |
| POST | `/api/v1/documents/{id}/versions` | `documents:write` | Upload new version |
| POST | `/api/v1/documents/{id}/approvals` | `documents:approve` | Submit/approve/reject |
| POST | `/api/v1/documents/{id}/unlock` | `documents:admin` | Unlock approved doc |
| GET | `/api/v1/workspaces/{wsId}/wiki` | `wiki:read` | List wiki pages |
| POST | `/api/v1/workspaces/{wsId}/wiki` | `wiki:write` | Create wiki page |
| PATCH | `/api/v1/wiki/{pageId}` | `wiki:write` | Update wiki page |
| POST | `/api/v1/tasks/{taskId}/documents` | `tasks:write` | Link document to task |

---

## Related

- [[Userflow/Work-Management/collaboration-flow|WorkSync Collaboration]] — workspace documents and wiki user flow

- [[modules/documents/overview|Documents Module]] — full shared table spec including HR columns
- [[modules/work-management/tasks/overview|Task Management]] — task_documents FK
- [[database/schemas/wms-collaboration|WMS Collaboration Schema]]
- [[current-focus/DEV8-documents-github-ide|DEV8 Task 1]]
