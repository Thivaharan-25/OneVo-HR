# Customer Support

## Purpose

Customer Support lets Super Admins and support agents manage tenant support tickets from the Developer Platform.

## Capabilities

- List support tickets across tenants.
- Filter by category, assigned agent, status, priority, and tenant.
- View request summary, customer information, issue description, attachments, activity timeline, and internal notes.
- Assign or reassign tickets.
- Reply to customers.
- Add internal notes.
- Change ticket category.
- Close tickets as resolved.

## Permissions

| Action | Permission |
|---|---|
| View tickets | `platform.support.read` |
| Assign, reply, categorize, note, close | `platform.support.manage` |

## Rules

- Internal notes are never visible to tenant users.
- Customer replies and status changes are written to the activity timeline.
- Attachments must be scanned and permission-checked before download.
- Ticket closure must preserve the full timeline for audit/support history.

## Storage Model

- `support_tickets` stores the ticket header, issue description, status, assignment, and activity timestamps.
- `support_ticket_messages` stores customer-visible tenant and platform replies.
- `support_ticket_internal_notes` stores platform-only notes and is never returned by tenant-facing APIs.
- `support_ticket_events` stores the activity timeline for assignment, replies, category changes, status changes, attachments, and closure.
- `entity_assets` stores support attachments with `owner_type = support_ticket` or `support_ticket_message` and `asset_purpose = attachment`.
