# Document Versioning

**Area:** Documents  
**Trigger:** Admin uploads new version of existing document (user action)
**Required Permission(s):** `documents:write`  
**Related Permissions:** `documents:manage` (rollback versions)

---

## Preconditions

- Document exists → [[Userflow/Documents/document-upload|Document Upload]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Upload New Version
- **UI:** Navigate to document → "Upload New Version" → select new file → add changelog note
- **API:** `POST /api/v1/documents/{id}/versions`
- **Backend:** DocumentService.UploadVersionAsync() → [[modules/documents/document-management/overview|Document Management]]
- **DB:** Previous version preserved in `document_versions`, document points to new version

### Step 2: Version History
- **UI:** View version history → see all versions with: version number, upload date, uploader, changelog → download any previous version
- **API:** `GET /api/v1/documents/{id}/versions`

### Step 3: Re-notify (if policy document)
- **Backend:** If document has acknowledgement requirement → all previous acknowledgements reset → employees re-notified
- Links: [[Userflow/Documents/document-acknowledgement|Document Acknowledgement]]

## Variations

### Rollback
- With `documents:manage`: click "Rollback to this version" → latest version replaced → changelog entry added

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Same file uploaded | Warning | "This file is identical to the current version" |

## Events Triggered

- `DocumentVersionCreated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Documents/document-upload|Document Upload]]
- [[Userflow/Documents/document-acknowledgement|Document Acknowledgement]]

## Module References

- [[modules/documents/document-management/overview|Document Management]]
