# Customer Support - Testing

## Required Tests

- Ticket list requires `platform.support.read`.
- Ticket management actions require `platform.support.manage`.
- Internal notes are not returned by tenant-facing ticket APIs.
- Creating a tenant ticket writes `support_tickets.description` and a `support_ticket_events` creation row.
- Customer/platform replies create `support_ticket_messages`, update ticket activity timestamps, append `support_ticket_events`, and generate notification/email.
- Internal notes create `support_ticket_internal_notes` and append `support_ticket_events`.
- Assign/reassign updates assigned agent and appends `support_ticket_events`.
- Category change updates ticket and appends `support_ticket_events`.
- Closing ticket changes status to `resolved`, sets `resolved_by_id` and `resolved_at`, and appends `support_ticket_events`.
- Attachments use `entity_assets` with `owner_type = support_ticket` or `support_ticket_message`, require permission checks, and require safe file validation.
