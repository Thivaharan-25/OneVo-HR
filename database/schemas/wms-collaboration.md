# Schema: Work Management — Collaboration (Documents + Wiki + Task-Document Links)

**Module:** `Work Management.Collaboration`
**Phase:** 1
**Owner:** DEV8

---

## `documents` — Phase 1 (Extended)

> The `documents` table is shared with the HR Documents module. Work Management extends it with `workspace_id`, `project_id`, `document_scope`, lock fields, and `approved` status. Do not create a separate Work Management documents table.

**Columns added to existing `documents` table:**

| Column | Type | Notes |
|---|---|---|
| `workspace_id` | uuid | FK → workspaces, nullable — Work Management scope |
| `project_id` | uuid | FK → projects, nullable — project scope |
| `document_scope` | varchar(30) | company / legal_entity / employee / workspace / project |
| `locked_at` | timestamptz | nullable — set when document is approved and locked |
| `locked_by` | uuid | FK → users, nullable — who approved and locked |
| `approved_version_id` | uuid | FK → document_versions, nullable — the locked version |

**`status` enum extended:** draft / in_review / **approved** / published / archived

> `approved` status means the document has passed the approval workflow and is locked. Only admins can unlock. The `locked_at` + `locked_by` + `approved_version_id` together constitute the approval lock record.

---

## `document_versions` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `document_id` | uuid | FK → documents |
| `version_number` | int | Auto-incremented per document |
| `content_snapshot` | text | Full content at this version (or Azure Blob key for large docs) |
| `change_summary` | varchar(500) | nullable — optional description of changes |
| `created_by_id` | uuid | FK → users |
| `created_at` | timestamptz | |

**Unique:** `(document_id, version_number)`
**Index:** `(document_id, version_number DESC)`

---

## `document_approvals` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `document_id` | uuid | FK → documents |
| `requested_by_id` | uuid | FK → users |
| `approver_id` | uuid | FK → users |
| `status` | varchar(20) | pending / approved / rejected |
| `comment` | text | nullable |
| `decided_at` | timestamptz | nullable |

**On approve:** Set `documents.status = approved`, `documents.locked_at = now()`, `documents.locked_by = approver_id`, `documents.approved_version_id = latest version id`

---

## `wiki_pages` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK → projects |
| `parent_page_id` | uuid | FK → wiki_pages, nullable — hierarchical structure |
| `title` | varchar(255) | |
| `content` | text | Markdown / rich text |
| `author_id` | uuid | FK → users |
| `last_edited_by` | uuid | FK → users, nullable |
| `version_number` | int | Auto-incremented on each save |
| `is_published` | boolean | default true |
| `position` | int | Order among siblings |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Index:** `(project_id)`, `(parent_page_id)`

---

## `task_documents` — Phase 1

Durable relationship between a Work Management task and an editable document. This is for document-editor links, not file attachments (file attachments use the existing `attachments` table).

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK → tasks |
| `document_id` | uuid | FK → documents |
| `linked_by_id` | uuid | FK → users |
| `linked_at` | timestamptz | |

**Unique:** `(task_id, document_id)`
