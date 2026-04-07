# Document Templates

**Module:** Documents  
**Feature:** Templates

---

## Purpose

Reusable templates for generating documents (offer letters, contracts, etc.) with merge variables.

## Database Tables

### `document_templates`
Fields: `name`, `category_id`, `template_content` (HTML/Markdown), `variables_json` (e.g., `{{employee_name}}`), `is_active`.

## Related

- [[documents|Documents Module]]
- [[documents/document-management/overview|Document Management]]
- [[documents/categories/overview|Categories]]
- [[documents/access-control/overview|Access Control]]
- [[documents/acknowledgements/overview|Acknowledgements]]
- [[auth-architecture]]
- [[data-classification]]
- [[multi-tenancy]]
- [[event-catalog]]
- [[WEEK4-supporting-bridges]]
