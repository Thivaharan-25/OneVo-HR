# Document Versioning

**Area:** Documents  
**Required Permission(s):** `documents:write`  
**Related Permissions:** `documents:manage` (rollback versions)

---

## Preconditions

- Document exists → [[document-upload]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Upload New Version
- **UI:** Navigate to document → "Upload New Version" → select new file → add changelog note
- **API:** `POST /api/v1/documents/{id}/versions`
- **Backend:** DocumentService.UploadVersionAsync() → [[document-management]]
- **DB:** Previous version preserved in `document_versions`, document points to new version

### Step 2: Version History
- **UI:** View version history → see all versions with: version number, upload date, uploader, changelog → download any previous version
- **API:** `GET /api/v1/documents/{id}/versions`

### Step 3: Re-notify (if policy document)
- **Backend:** If document has acknowledgement requirement → all previous acknowledgements reset → employees re-notified
- Links: [[document-acknowledgement]]

## Variations

### Rollback
- With `documents:manage`: click "Rollback to this version" → latest version replaced → changelog entry added

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Same file uploaded | Warning | "This file is identical to the current version" |

## Events Triggered

- `DocumentVersionCreated` → [[event-catalog]]

## Related Flows

- [[document-upload]]
- [[document-acknowledgement]]

## Module References

- [[document-management]]
