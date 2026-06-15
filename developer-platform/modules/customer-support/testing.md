# Customer Support - Testing

## Required Tests

- Ticket list requires `platform.support.read`.
- Ticket management actions require `platform.support.manage`.
- Internal notes are not returned by tenant-facing ticket APIs.
- Customer replies generate notification/email.
- Assign/reassign updates assigned agent and timeline.
- Category change updates ticket and timeline.
- Closing ticket changes status to `resolved`.
- Attachments require permission and safe file validation.
- Knowledgebase promotion preserves source ticket reference.

