# Document Access

**Area:** Documents  
**Required Permission(s):** `documents:read` (own accessible docs) or `documents:manage` (all docs)  
**Related Permissions:** `employees:read-own` (own employee documents)

---

## Preconditions

- Documents uploaded → [[document-upload]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Browse Documents
- **UI:** Sidebar → Documents → browse by category or search by title/tags
- **API:** `GET /api/v1/documents?category={cat}&search={term}`
- **Backend:** Only returns documents user has access to (based on access level + department)

### Step 2: View Document
- **UI:** Click document → inline preview (PDF/images) or download link → see metadata (uploaded by, date, version, category)
- **API:** `GET /api/v1/documents/{id}`
- **DB:** Access logged in `document_access_logs`

### Step 3: Download
- **UI:** Click "Download" → file downloaded from cloud storage
- **API:** `GET /api/v1/documents/{id}/download`

## Variations

### Employee's own documents
- Employee Profile → Documents tab → sees contracts, certificates, etc. linked to their profile

### With `documents:manage`
- Can see all documents regardless of access level → manage access settings

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No access | 403 Forbidden | "You don't have access to this document" |
| Document deleted | 404 | "Document not found" |

## Events Triggered

- `DocumentAccessed` → audit trail (not domain event)

## Related Flows

- [[document-upload]]
- [[profile-management]]

## Module References

- [[document-management]]
- [[access-control]]
- [[audit-logging]]
