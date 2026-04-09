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

- [[modules/documents/overview|Documents Module]]
- [[frontend/architecture/overview|Document Management]]
- [[frontend/architecture/overview|Categories]]
- [[frontend/architecture/overview|Access Control]]
- [[frontend/architecture/overview|Acknowledgements]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
