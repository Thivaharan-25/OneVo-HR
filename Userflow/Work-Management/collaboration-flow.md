# WorkSync Collaboration

**Area:** WorkSync -> Documents and Wiki  
**Trigger:** User creates, edits, approves, or links workspace knowledge  
**Required Permission(s):** `documents:read`, `documents:write`, `wiki:read`, `wiki:write`  
**Related Permissions:** `documents:approve`, `documents:admin`

---

## Flow Steps

### Step 1: Open Workspace Documents or Wiki
- **UI:** WorkSync -> Workspace -> Documents or Wiki
- **API:** `GET /api/v1/workspaces/{wsId}/documents`, `GET /api/v1/workspaces/{wsId}/wiki`
- **Backend:** Returns only documents/wiki pages visible to the workspace/project scope

### Step 2: Create Document or Wiki Page
- **Document API:** `POST /api/v1/workspaces/{wsId}/documents`
- **Wiki API:** `POST /api/v1/workspaces/{wsId}/wiki`
- **Backend:** Creates draft document or wiki page

### Step 3: Upload or Edit Version
- **Document API:** `POST /api/v1/documents/{id}/versions`
- **Wiki API:** `PATCH /api/v1/wiki/{pageId}`
- **Result:** Document version history or wiki edit metadata is updated

### Step 4: Submit Document for Approval
- **API:** `POST /api/v1/documents/{id}/approvals`
- **Backend:** Creates approval record for the current version
- **UI:** Approver sees the request in Inbox/notifications

### Step 5: Approve and Lock
- **Backend:** Approval updates document status, lock fields, and approved version atomically
- **Rule:** Approved documents require admin unlock before editing

### Step 6: Link Document to Task
- **UI:** Task detail -> Add document
- **API:** `POST /api/v1/tasks/{taskId}/documents`
- **Result:** Task shows linked workspace document

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| User lacks document permission | API returns 403 | Permission error |
| Document is locked | Edit blocked | "This document is approved and locked" |
| Wiki parent creates cycle | Save rejected | "Page cannot be moved under itself" |
| Approval rejected | Document returns to draft/rework state | Rejection comments |

## Events Triggered

- `DocumentApprovedEvent`
- `DocumentPublishedEvent`
- `WikiPagePublishedEvent`

## Related Flows

- [[Userflow/Documents/document-upload|Document Upload]]
- [[Userflow/Documents/document-versioning|Document Versioning]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Notifications/inbox|Inbox]]

## Module References

- [[modules/work-management/collaboration/overview|Collaboration]]
- [[modules/documents/overview|Documents]]
- [[database/schemas/wms-collaboration|WMS Collaboration Schema]]
