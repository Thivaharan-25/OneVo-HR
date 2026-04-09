# Document Templates — End-to-End Logic

**Module:** Documents
**Feature:** Templates

---

## Create Template

### Flow

```
POST /api/v1/documents/templates
  -> TemplateController.Create(CreateTemplateCommand)
    -> [RequirePermission("documents:manage")]
    -> TemplateService.CreateAsync(command, ct)
      -> 1. Validate template_content (HTML/Markdown)
      -> 2. Parse variables_json: extract merge variables (e.g., {{employee_name}})
      -> 3. INSERT into document_templates
      -> Return Result.Success(templateDto)
```

## Generate Document from Template

### Flow

```
POST /api/v1/documents/templates/{id}/generate
  -> TemplateController.Generate(id, GenerateCommand)
    -> [RequirePermission("documents:write")]
    -> TemplateService.GenerateAsync(templateId, variables, ct)
      -> 1. Load template
      -> 2. Replace merge variables with provided values
      -> 3. Render to PDF/HTML
      -> 4. Upload via IFileService
      -> 5. Create document + version
      -> Return Result.Success(documentDto)
```

## Related

- [[frontend/architecture/overview|Templates Overview]]
- [[frontend/architecture/overview|Document Management]]
- [[frontend/architecture/overview|Categories]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
