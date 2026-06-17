# Topbar Architecture

## Layout

```text
[Tenant / Legal Entity]  |  [Search]  |  [Notifications] [Theme] [Avatar]
```

The topbar must preserve tenant context, legal entity context where relevant, search, notifications, and profile access across all Phase 1 breakpoints.

## Left - Tenant / Legal Entity Context

### What It Shows

The tenant the user is signed into and, when relevant, the active legal entity inside that tenant.

### Rules

- Tenant remains the subscription, branding, authentication, and audit boundary.
- Legal entity is the company/employer context for departments, positions, onboarding, employee import, transfers, policy assignment, and scoped reporting.
- Single-company tenants can hide the legal entity selector and default all legal-entity-scoped forms to the only legal entity.
- Multi-company tenants can show a legal entity selector in Setup / Control and permission-scoped operational views.
- Cross-legal-entity views must be permission-scoped and audit logged.

### Dropdown Example

```text
Acme Group / Acme Sri Lanka Pvt Ltd
-----------------------------------
✓ Acme Sri Lanka Pvt Ltd
  Acme UK Ltd
  All legal entities
  Legal entity settings
-----------------------------------
  Request add-on / license increase
```

### Permission Gating

| Permission | Behavior |
|---|---|
| Any authenticated user | Sees current tenant/legal entity label |
| `org:read` | Can see legal entity context where relevant |
| `org:manage` | Can open Legal Entity Settings in Setup / Control Application |
| `settings:billing` | Can open add-on / license request entry |

### Component

`TenantLegalEntityContextMenu` lives in the topbar layout component.

### Data Source

Tenant context comes from authenticated session metadata. Legal entity entries come from `legal_entities` filtered by the user's permissions and scopes.

## Center - Search

Command palette trigger. Opens on click or keyboard shortcut. Shows quick navigation, recent pages, global people search, and global actions.

## Right - Actions

- Notification bell: unread inbox count.
- Theme toggle: system / light / dark.
- User avatar menu: user name, current position, employee profile link, sign out.

## Responsive Behavior

| Viewport | Behavior |
|:---------|:---------|
| Mobile `<640px` | Show hamburger, concise page title, one primary action, and overflow menu. Legal entity context and search move into the drawer or icon triggers. |
| Tablet `640-1023px` | Show hamburger, active legal entity in compact form, search icon, notifications, and avatar/overflow menu. |
| Laptop `1024-1279px` | Show compact tenant/legal entity context, short breadcrumb, search pill, notifications, theme, and avatar. |
| Desktop `>=1280px` | Show full tenant/legal entity context, breadcrumb, search, notification, theme, and avatar controls. |

Rules:

- Text must truncate safely with tooltips or accessible labels where needed.
- Critical actions cannot disappear; they move into the overflow menu or drawer.
- Search must remain reachable at every viewport.
- Navigation and context menus must be permission-aware.
