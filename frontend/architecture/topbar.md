# Topbar Architecture

## Layout

```text
[Tenant / Legal Entity]  |  [Search]  |  [Notifications] [Theme] [Avatar]
```

The topbar must preserve tenant context, legal entity context where relevant, search, notifications, and profile access across all Phase 1 breakpoints.

## Left - Tenant / Company Context

### What It Shows

The tenant the user is signed into and, when relevant, the active Company context inside that tenant. Internally, Company maps to a `legal_entities` record.

### Rules

- Tenant remains the subscription, branding, authentication, and audit boundary.
- Company is the employer context for departments, positions, onboarding, employee import, transfers, policy assignment, and scoped reporting.
- Single-company tenants can hide the Company selector and default all Company-scoped forms to the only Company.
- Multi-company tenants can show a Company selector in setup and permission-scoped operational route groups inside customer-app.
- Cross-company views must be permission-scoped and audit logged.
- The dropdown is a Company context switcher. Users switch Company context there.
- **Add company** is launched from this dropdown.
- Settings > General is Company-scoped. Switching Company reloads the General page for the selected Company.
- Do not create a separate entity-settings destination. Company settings are edited from Settings > General after selecting a Company.
- If selected Company = `All`, Company-scoped forms such as Settings > General are hidden or rendered as a read-only empty state. `All` is a viewing context, not an editing context.

### Dropdown Example

```text
Acme Group / Acme Sri Lanka Pvt Ltd
-----------------------------------
[done] Acme Sri Lanka Pvt Ltd
  Acme UK Ltd
  All companies
-----------------------------------
  Add company
  Request add-on / license increase
```

### Permission Gating

| Permission | Behavior |
|---|---|
| Any authenticated user | Sees current tenant/legal entity label |
| `org:read` | Can see legal entity context where relevant |
| `org:manage` | Can switch Company context, add Company, and edit Company-scoped General settings for the selected Company |
| `settings:billing` | Can open add-on / license request entry |

### Component

`TenantCompanyContextMenu` lives in the topbar layout component.

Company creation is not an Org sub-sidebar item. In multi-company mode, admins use the topbar tenant/company dropdown and click **Add company**. In single-company mode, the default Company is created during tenant setup and the selector may be hidden.

### Data Source

Tenant context comes from authenticated session metadata. Company entries come from `legal_entities` filtered by the user's permissions and scopes.

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
