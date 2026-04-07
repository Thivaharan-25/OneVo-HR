# Template Management

**Area:** Documents  
**Required Permission(s):** `documents:manage`  
**Related Permissions:** `employees:read` (merge employee data into templates)

---

## Preconditions

- Document system configured → [[document-upload]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Template
- **UI:** Documents → Templates → "Create Template" → enter name (e.g., "Offer Letter", "Employment Contract", "Warning Letter")
- **API:** `POST /api/v1/documents/templates`

### Step 2: Build Template
- **UI:** Rich text editor → insert merge fields: `{{employee.name}}`, `{{employee.title}}`, `{{employee.department}}`, `{{employee.salary}}`, `{{employee.start_date}}`, `{{company.name}}`, `{{today}}` → format layout → set output format (PDF)
- **Backend:** TemplateService.CreateAsync() → [[templates]]
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

- `DocumentGenerated` → [[event-catalog]]

## Related Flows

- [[document-upload]]
- [[employee-onboarding]]
- [[employee-offboarding]]

## Module References

- [[templates]]
- [[document-management]]
