# Report Templates — End-to-End Logic

**Module:** Reporting Engine
**Feature:** Report Templates

---

## Manage Templates

### Flow

```
Report templates define column structure and default filters:
  -> columns_json: array of { field, label, width, format }
  -> filters_json: default filter configuration

System templates (is_system = true) are pre-seeded:
  -> "Employee Directory" (headcount)
  -> "Leave Utilization Summary"
  -> "Daily Productivity Report"
  -> "Weekly Workforce Summary"
  -> "Exception Alert Summary"

Custom templates can be created by admins.
```

### Key Rules

- **System templates cannot be deleted** — only customized via tenant-specific overrides.
- **Templates are reusable** — one template can be used by multiple report definitions.

## Related

- [[frontend/architecture/overview|Report Templates Overview]]
- [[frontend/architecture/overview|Report Definitions]]
- [[frontend/architecture/overview|Report Execution]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
