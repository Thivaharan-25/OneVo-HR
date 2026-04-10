# Template Management

**Area:** Documents  
**Trigger:** Admin creates or manages document templates (user action — configuration)
**Required Permission(s):** `documents:manage`  
**Related Permissions:** `employees:read` (merge employee data into templates)

---

## Preconditions

- Document system configured → [[Userflow/Documents/document-upload|Document Upload]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Template
- **UI:** Documents → Templates → "Create Template" → enter name (e.g., "Offer Letter", "Employment Contract", "Warning Letter")
- **API:** `POST /api/v1/documents/templates`

### Step 2: Build Template
- **UI:** Rich text editor → insert merge fields: `{{employee.name}}`, `{{employee.title}}`, `{{employee.department}}`, `{{employee.salary}}`, `{{employee.start_date}}`, `{{company.name}}`, `{{today}}` → format layout → set output format (PDF)
- **Backend:** TemplateService.CreateAsync() → [[modules/documents/templates/overview|Templates]]
- **DB:** `document_templates`

### Step 3: Generate Document
- **UI:** Select template → select employee → preview with merged data → generate PDF → auto-saved to employee's documents
- **API:** `POST /api/v1/documents/templates/{id}/generate`

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid merge field | Generation fails | "Merge field {{employee.xyz}} not recognized" |
| Missing employee data | Warning | "Employee is missing: salary — field will be blank" |

## Events Triggered

- `DocumentGenerated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Documents/document-upload|Document Upload]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]]

## Module References

- [[modules/documents/templates/overview|Templates]]
- [[modules/documents/document-management/overview|Document Management]]
