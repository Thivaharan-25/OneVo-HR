# Topbar Architecture

## Layout

```
[■ Acme Malaysia Sdn Bhd  ▾]  |  [  Search...  ⌘K  ]  |  🔔  ☀  [Avatar ▾]
Left (fixed width ~200px)        Center (flex-grow)       Right (fixed width)
```

Height: 48px (`h-12`). Spans full width above both the icon rail and expansion panel.

## Left — Legal Entity Switcher

### What it shows
The legal entity the user currently operates within — the registered company or business unit their data access is scoped to. Not a generic "workspace" or "tenant" name.

### Why legal entity, not workspace name
ONEVO's permission model is hierarchy-scoped. A Super Admin may govern multiple entities (e.g., "Acme Malaysia Sdn Bhd", "Acme Singapore Pte Ltd", "Acme Group"). Their data access changes depending on which entity they are operating in. The topbar makes this context explicit and switchable.

### Switcher dropdown anatomy

```
[■ Acme Malaysia Sdn Bhd  ▾]
─────────────────────────────────
✓  Acme Malaysia Sdn Bhd         ← current (checkmark)
   Acme Group                    ← parent entity (if user has access)
   Acme Singapore Pte Ltd        ← sibling entity (if user has access)
─────────────────────────────────
   + Add Entity                  ← only visible with org:manage permission
```

Only entities within the user's hierarchy-scoped access appear. A regular employee sees only their own entity — the label is static, no dropdown triggered.

### Entity switching behavior
When user selects a different entity:
1. Auth session updates the active entity context
2. All scoped data re-fetches (employees, projects, reports visible in this entity)
3. App redirects to `/` (Home) — prevents showing stale data on the current page
4. Active entity persists in session across page refreshes

### Permission gating
| Permission | Behavior |
|---|---|
| `org:read` | User sees their own entity name as a static label — no dropdown |
| Any user with access to 2+ entities | Switcher dropdown is active |
| `org:manage` | Dropdown includes "+ Add Entity" option |

### Component
`EntitySwitcher` — lives in the topbar layout component.

### Data source
Entities are created and managed at Org → Legal Entities (`/org/legal-entities`). The switcher reads from this list filtered to the user's hierarchy access scope.

## Center — Search

Command palette trigger. Opens on click or keyboard shortcut (⌘K on Mac, Ctrl+K on Windows).

Shows: quick nav to any page, recent pages, global people search, global actions (create task, request leave, etc.).

## Right — Actions

**Notification Bell (`🔔`):** Badge count of unread inbox items. Click navigates to `/inbox`.

**Theme Toggle (`☀`):** Cycles system → light → dark.

**User Avatar Menu:** Dropdown showing user name, job title, link to their employee profile, and Sign Out.

## Related

- [[frontend/architecture/sidebar-nav|Sidebar Nav Map]] — full pillar and permission reference
- [[Userflow/Org/legal-entities|Legal Entity Management]] — where entities are created
