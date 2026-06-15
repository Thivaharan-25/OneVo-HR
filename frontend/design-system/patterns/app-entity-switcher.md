# App + Entity Switcher Pattern

Shared topbar controls for switching between the Config and Ops apps and switching legal entity context. Both live in the 48px topbar.

---

## App Switcher

### When rendered
Only when the authenticated user has **both** `config:access` and `ops:access` permissions. Single-app users never see the control.

### Structure
A segmented pill in the topbar, left of breadcrumbs:

```
[⚙ Config | ▶ Ops]
```

- Active app: `bg-white/12`, full-opacity text
- Inactive app: ghost, `text-[var(--fg-3)]`
- Width: content-fit, padding `3px 9px` per segment

### States

| State | Visual |
|:------|:-------|
| Config active | Config pill filled, Ops ghost |
| Ops active | Ops pill filled, Config ghost |
| Switching (mid-transition) | Clicked pill shows spinner + `bg-violet-500/18`; topbar tints `bg-violet-500/6`; page content shows overlay with "Switching to [App]…" message |

### Switch behaviour
1. User clicks inactive pill.
2. Pill shows spinner immediately (~150ms visual feedback).
3. Brief overlay over page content (not topbar): blurred, centred "Switching to Operations…" message pill.
4. Browser navigates to target subdomain with last remembered route (from `AppRouteMemoryService`).
5. Session cookie (`Domain=.{tenantSlug}.onevo.com`, `SameSite=Lax`) is valid on arrival — no re-login.

### Last route memory
`AppRouteMemoryService` in the shared library writes the current route to `localStorage` on every Angular Router `NavigationEnd` event.

Key format: `onevo_last_route_{userId}_{config|ops}`

Cleared on logout. Falls back to `/` if no stored route.

---

## Entity Chip

### When rendered
Only when the tenant has more than one legal entity **and** the authenticated user has access to more than one. Single-entity tenants and users with one entity never see the chip.

The chip is **always visible** when rendered — including on tenant-level management pages like the Legal Entities list. On that page, the active entity is highlighted with an "active" badge in the list itself (chip and list reinforce each other).

### Structure
A compact chip in the topbar, right of the search pill:

```
[A Acme Corp ▾]
```

- Logo: 15×15px rounded square with gradient, shows entity initial
- Text: entity name, `font-size: 11px`
- Chevron: `▾` / `▲` indicating closed/open state

### Dropdown
- **Width:** 210px
- **Attached:** directly to chip bottom edge (no gap, top border removed on open)
- **Does not cover page content** — floats at `z-index: 50`, page remains readable
- **Items:** entity logo + name + role label + access badges (`Config` / `Ops`)
- **Selected item:** `bg-violet-500/18` with checkmark
- **Footer link:** "+ Request entity access" (shown when tenant config allows it)

### Entity item access badges

| Badge | Meaning |
|:------|:--------|
| `CONFIG` (violet) | User has `config:access` for this entity |
| `OPS` (green) | User has `ops:access` for this entity |
| `OPS ONLY` (green) | User has only Ops access — Config not available |

### Switching rules

| Scenario | Behaviour |
|:---------|:----------|
| Switch to entity where current app is available | Stay in current app, reload with new entity context |
| Switch to entity where current app is NOT available (e.g. Config → Ops-only entity) | Auto-navigate to available app + toast: "Config not available for [Entity] — switched to Operations" |
| Switch to entity where neither app is available | Item disabled in dropdown (should not occur — access check prevents it) |

### Entity context propagation
Active entity ID is stored in `localStorage` (`onevo_active_entity_{userId}`) and sent on every API call as `X-Entity-Id` request header via the `entityContextInterceptor`. Context persists when switching apps — switching from Config to Ops carries the same active entity.

---

## Responsive behaviour

| Breakpoint | App switcher | Entity chip |
|:-----------|:------------|:------------|
| Desktop ≥ 1024px | Full text pills | Full chip with entity name |
| Tablet 640–1023px | Icon-only (⚙ / ▶) with tooltip | Logo initial only |
| Mobile < 640px | Moved into hamburger drawer (top of drawer, above nav items) | Moved into hamburger drawer |

---

## Shared library components

| Component / Service | Responsibility |
|:-------------------|:--------------|
| `TopbarComponent` | Shell: assembles hamburger, app switcher, breadcrumbs, search, entity chip, icons, avatar |
| `AppSwitcherComponent` | Segmented pill, switching logic, transition state |
| `EntityChipComponent` | Entity dropdown, badge rendering, switching rules |
| `EntityContextService` | `activeEntityId()` signal, localStorage read/write |
| `AppRouteMemoryService` | Last route per app, localStorage read/write, `NavigationEnd` listener |
| `entityContextInterceptor` | Adds `X-Entity-Id` header to all `HttpClient` requests |

## Related
- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]] — full topbar and sidebar spec
- [[docs/superpowers/specs/2026-06-08-dual-app-sso-switcher-design|SSO + Switcher Design Spec]] — approved design with SSO architecture
