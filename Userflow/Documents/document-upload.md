# Document Upload

**Area:** Documents  
**Required Permission(s):** `documents:write`  
**Related Permissions:** `documents:manage` (set access control)

---

## Preconditions

- Document categories configured → [[modules/documents/categories/overview|Categories]]
- File storage configured (cloud storage) → [[modules/infrastructure/overview|Infrastructure]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Documents
- **UI:** Sidebar → Documents → "Upload Document"
- **API:** `GET /api/v1/documents/categories` (populate category dropdown)

### Step 2: Upload File
- **UI:** Drag-and-drop or browse → select file (PDF, DOCX, XLSX, images) → enter title, description → select category (Policy, Contract, Certificate, Template, General)
- **Validation:** File size ≤ 25MB, allowed file types only

### Step 3: Set Access Level
- **UI:** Choose: Public (all employees), Department-specific, Individual (named employees), Confidential (HR only) → add tags for searchability
- **Backend:** DocumentService.UploadAsync() → [[modules/documents/document-management/overview|Document Management]]
- **DB:** `documents` — metadata, `document_access` — permissions

### Step 4: Upload & Process
- **API:** `POST /api/v1/documents` (multipart form)
- **Backend:** File uploaded to cloud storage → metadata saved → if policy document: triggers acknowledgement workflow → [[Userflow/Documents/document-acknowledgement|Document Acknowledgement]]

## Variations

### Employee-specific documents
- Upload to specific employee's profile (contract, ID copy) → linked to employee record

### Bulk upload
- Upload multiple files at once → same category and access level applied to all

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| File too large | Upload rejected | "Maximum file size is 25MB" |
| Unsupported format | Upload rejected | "File type not supported" |
| Storage full | Upload fails | "Storage quota exceeded — contact admin" |

## Events Triggered

- `DocumentUploaded` → [[backend/messaging/event-catalog|Event Catalog]]
- `AcknowledgementRequired` (if policy) → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Documents/document-access|Document Access]]
- [[Userflow/Documents/document-acknowledgement|Document Acknowledgement]]
- [[Userflow/Documents/document-versioning|Document Versioning]]
- [[Userflow/Documents/template-management|Template Management]]

## Module References

- [[modules/documents/document-management/overview|Document Management]]
- [[modules/documents/categories/overview|Categories]]
- [[modules/documents/access-control/overview|Access Control]]
