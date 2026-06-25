# Customer Support - End-to-End Logic

1. Super Admin opens Customer Support at `/platform/support`.
2. Ticket list shows subject, tenant, category, assigned to, status, created on, and actions.
3. Filters narrow by category, assigned agent, status, priority, and tenant.
4. User opens ticket detail.
5. Detail page shows:
   - Request summary from `support_tickets`
   - Customer information from the tenant user linked by `created_by_user_id`
   - Issue description from `support_tickets.description`
   - Customer-visible conversation from `support_ticket_messages`
   - Attachments from `entity_assets`
   - Activity timeline from `support_ticket_events`
   - Internal notes from `support_ticket_internal_notes`
6. Assign/reassign requires `platform.support.manage`.
7. Reply creates a `support_ticket_messages` row, sends tenant notification/email, updates ticket activity timestamps, and appends a `support_ticket_events` row.
8. Category change updates `support_tickets.category` and appends a `support_ticket_events` row.
9. Internal note creates a `support_ticket_internal_notes` row and is visible only to support/platform users.
10. Close ticket changes status to `resolved`, sets `resolved_by_id`/`resolved_at`, and writes timeline/audit entries.
