# Customer Support User Flow

## Purpose

Super Admin and support agents manage tenant support tickets.

## Flow

1. Open Customer Support directly from the Developer Platform sidebar.
2. Filter tickets by category, assigned agent, status, priority, or tenant.
3. Open ticket details.
4. Review request summary, customer information, issue description, attachments, activity timeline, and internal notes.
5. Assign or reassign the ticket.
6. Reply to the customer.
7. Add internal notes when needed.
8. Change category if the issue was filed incorrectly.
9. Close the ticket when resolved.

## Rules

Internal notes are not visible to tenant users. Every support action is recorded in the activity timeline or audit history.

## Database Entities

- `support_tickets` stores the tenant ticket, issue description, status, assignment, and resolution timestamps.
- `support_ticket_messages` stores tenant/platform replies that are visible to the customer.
- `support_ticket_internal_notes` stores platform-only notes.
- `support_ticket_events` stores the activity timeline.
- `entity_assets` stores attachments for tickets and ticket messages.
