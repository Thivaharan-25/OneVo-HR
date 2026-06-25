# Collaboration - End-to-End Logic

**Module:** WorkSync
**Feature:** Collaboration (Documents, Wiki, Task Docs)

---

## Upload Document Version

```
POST /api/v1/documents/{id}/versions
  -> [RequirePermission("documents:write")]
  -> UploadDocumentVersionHandler
    -> 1. Verify document exists, user has workspace access
    -> 2. Verify document.status != "approved"
         If approved: return 403 DOCUMENT_LOCKED
         (must unlock first)
    -> 3. Upload file to blob storage via IFileService
         -> returns blob_storage_url
    -> 4. BEGIN TRANSACTION
         a. SELECT MAX(version_number) + 1 FROM document_versions
                WHERE document_id = ? (per-document auto-increment)
         b. UPDATE document_versions SET is_current = false WHERE document_id = ?
         c. INSERT document_versions (version_number, blob_storage_url,
                file_name, is_current=true, uploaded_by_id)
    -> 5. COMMIT
    -> Return Result<DocumentVersionDto>
```

## Document Approval Flow

```
POST /api/v1/documents/{id}/approvals
  body: { approver_id }
  -> SubmitForApprovalHandler
    -> 1. Verify document.status in ("draft", "in_review")
    -> 2. Load current version (is_current = true)
    -> 3. INSERT document_approvals:
             document_version_id = current_version.id
             requested_by_id = caller
             approver_id = body.approver_id
             status = "pending"
    -> 4. UPDATE documents.status = "in_review"
    -> 5. Notify approver via Notifications module
    -> Return 201

PATCH /api/v1/documents/{id}/approvals/{approvalId}/approve
  -> ApproveDocumentHandler (caller must be approver_id)
    -> 1. Verify approval status = "pending"
    -> 2. BEGIN TRANSACTION (ATOMIC - all 4 fields or nothing)
         a. UPDATE document_approvals:
                status = "approved"
                decided_at = now()
         b. UPDATE documents:
                status = "approved"
                locked_at = now()
                locked_by = approver.user_id
                approved_version_id = approval.document_version_id
    -> 3. COMMIT
    -> 4. Publish DocumentApprovedEvent
    -> Return Result<DocumentDto>
```

## Unlock Approved Document

```
POST /api/v1/documents/{id}/unlock
  -> [RequirePermission("documents:admin")]
  -> UnlockDocumentHandler
    -> 1. Verify document.status = "approved"
    -> 2. UPDATE documents:
             status = "draft"
             locked_at = null
             locked_by = null
             approved_version_id = null
    -> 3. New approval required before publishing
    -> Return Result<DocumentDto>
```

## Wiki Page - Cycle Guard

```
PATCH /api/v1/wiki/{pageId}
  body: { parent_page_id }
  -> UpdateWikiPageHandler
    -> 1. If parent_page_id is being changed:
         -> Walk ancestor chain of proposed parent_page_id
           while (current.parent_page_id != null):
             if current.id == pageId: return 422 CYCLE_DETECTED
             current = load(current.parent_page_id)
    -> 2. Update wiki_pages row
    -> Return Result<WikiPageDto>
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Upload to approved document | 403 | Document is locked - unlock before editing |
| Approve already-approved doc | 409 | Document already has an approved version |
| Unlock without admin permission | 403 | Forbidden |
| Wiki cycle detected | 422 | Circular parent reference detected |
| Version upload: file too large | 413 | File exceeds maximum size |

### Edge Cases

- Concurrent approval requests: two approvers submit simultaneously. DB constraint on (document_id, status=approved) allows only one approved row. Second approver gets 409.
- version_number race: use `SELECT FOR UPDATE` or optimistic lock on the document row when incrementing version_number to prevent duplicate numbers.

## Related

- [[modules/work-management/collaboration/overview|Collaboration Overview]]
- [[modules/documents/overview|Documents Module]] - shared table full spec
- [[modules/work-management/collaboration/testing|Collaboration Testing]]
