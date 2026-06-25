# Entity Context Pattern

ONEVO Phase 1 uses one merged `customer-app` plus the internal `dev-console`. There is no customer-facing app switcher.

This pattern covers legal-entity context inside `customer-app` only.

---

## Entity Chip

### When Rendered

Render the entity chip only when both are true:

- The tenant has more than one legal entity.
- The authenticated user can access more than one legal entity.

Single-entity tenants and users with one legal-entity context do not see the chip.

### Structure

A compact chip appears in the topbar, right of search:

```text
[A Acme Corp v]
```

- Logo: 15x15px rounded square with entity initial.
- Text: entity name, 11px.
- Chevron indicates closed/open state.

### Dropdown

- Width: 210px.
- Attached directly to chip bottom edge.
- Floats over the page at `z-index: 50`.
- Items show entity logo, name, and access badges.
- Selected item uses highlighted background and checkmark.
- Optional footer: `Request entity access`, when tenant policy allows it.

### Switching Rules

| Scenario | Behaviour |
|:---------|:----------|
| User switches legal entity | Stay in `customer-app`, reload route data with new legal-entity context |
| Current route is not valid for selected entity | Redirect to the nearest valid route and show a toast |
| User lacks access to entity | Do not render the entity as selectable |

### API Context

Active entity ID is held by `EntityContextService` and sent on relevant customer-app API calls as `X-Entity-Id`.

The backend remains authoritative. The frontend context chip must never bypass authorization or tenant isolation.

---

## Shared Components

| Component / Service | Responsibility |
|:-------------------|:--------------|
| `TopbarComponent` | Shell: hamburger, breadcrumbs, search, entity chip, icons, avatar |
| `EntityChipComponent` | Entity dropdown, selected state, switching rules |
| `EntityContextService` | `activeEntityId()` signal and persistence |
| `entityContextInterceptor` | Adds `X-Entity-Id` header where relevant |

## Related

- [[frontend/architecture/app-structure|App Structure]]
- [[frontend/architecture/topbar|Topbar Architecture]]
- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]]
