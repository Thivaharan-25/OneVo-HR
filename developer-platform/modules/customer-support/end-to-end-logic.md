# Customer Support - End-to-End Logic

1. Super Admin opens Customer Support at `/platform/support`.
2. Ticket list shows subject, tenant, category, assigned to, status, created on, and actions.
3. Filters narrow by category, assigned agent, status, priority, and tenant.
4. User opens ticket detail.
5. Detail page shows:
   - Request summary
   - Customer information
   - Issue description
   - Attachments
   - Activity timeline
   - Internal notes
6. Assign/reassign requires `platform.support.manage`.
7. Reply sends tenant notification/email and appends timeline entry.
8. Category change appends timeline entry.
9. Internal note is visible only to support/platform users.
10. Add to knowledgebase creates a draft or published article based on policy.
11. Close ticket changes status to `resolved` and writes timeline/audit entries.
