# 2026-05-08 - CQRS Folder Structure Cleanup

## Changed

- Made `backend/folder-structure.md` the canonical source for backend feature layout.
- Updated Application feature structure so command validators live beside their command use case.
- Removed feature-level `Validators/` as the recommended pattern.
- Reframed `Events/` and `EventHandlers/` as optional folders used only for justified post-save side effects.
- Updated CQRS, Clean Architecture, module boundary, data-flow, shared-kernel, backend standards, Cursor, Claude, ADE, and AI_CONTEXT guidance to avoid treating events as mandatory.

## Decision

Clean Architecture + CQRS does not require domain events. ONEVO Phase 1 defaults to:

```text
Controller -> Command/Query -> Validator -> Handler -> Repository/Domain -> UnitOfWork -> Response
```

Domain events remain available by exception when decoupled post-save side effects are genuinely useful.
