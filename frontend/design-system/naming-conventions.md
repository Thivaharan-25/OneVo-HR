# Naming Conventions

## Principle

Every user-facing label passes the "would a non-technical HR manager understand this in 1 second?" test. If a label needs explanation, it's wrong.

## System → User-Facing Label Map

| System/Module Name | User-Facing Label | Why |
|:-------------------|:------------------|:----|
| Exception Engine | Alerts | Users think in alerts, not exceptions |
| Workforce Intelligence | Workforce | "Intelligence" sounds like surveillance |
| Data Visualization | Charts & Graphs | Everyone knows what a chart is |
| Command Palette | Quick Search | Human label for ⌘K |
| Compensation | Pay & Benefits | What people actually call it |
| Grievance | Complaints | Less legal-sounding, or "Employee Concerns" |
| Presence | Online Status | Instant understanding |
| Verification | ID Checks | Says what it does |
| Productivity Dashboard | Work Insights | Less "Big Brother" energy |
| Approvals | Inbox | Personal action center, broader than just approvals |
| Micro-interactions | Animations | Self-explanatory |

## Rules

1. **No jargon** — if a word is only used by developers or HR software vendors, find a simpler one
2. **Action-oriented** — labels should hint at what the user can DO there (Inbox → act on items, not just view them)
3. **Consistent** — once we name something, use that name everywhere (docs, code, UI, userflows)
4. **Short** — one or two words maximum for navigation labels

## Related

- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]] — sidebar labels
- [[Userflow/README|Userflow Overview]] — naming in userflows
