# Domain Layer Guide

See [[backend/shared-kernel|ONEVO.Domain documentation]] — the full guide lives there (formerly shared-kernel.md).

Quick reference:
- `ONEVO.Domain/Common/BaseEntity.cs` — all entities extend this
- `ONEVO.Domain/Common/IDomainEvent.cs` — marker interface for domain events
- `ONEVO.Domain/Features/{Feature}/Entities/` — business entities
- `ONEVO.Domain/Features/{Feature}/Events/` — domain events
- Zero framework dependencies — no EF, no MediatR attributes
