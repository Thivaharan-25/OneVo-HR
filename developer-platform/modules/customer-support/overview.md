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
- Add useful issue/resolution details to the knowledgebase.
- Close tickets as resolved.

## Permissions

| Action | Permission |
|---|---|
| View tickets | `platform.support.read` |
| Assign, reply, categorize, note, promote, close | `platform.support.manage` |

## Rules

- Internal notes are never visible to tenant users.
- Customer replies and status changes are written to the activity timeline.
- Attachments must be scanned and permission-checked before download.
- Ticket closure must preserve the full timeline for audit/support history.

