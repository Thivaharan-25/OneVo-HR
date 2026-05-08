# Domain Layer Guide

See [[backend/shared-kernel|ONEVO.Domain documentation]] for the full Domain-layer guide.

Quick reference:

- `ONEVO.Domain/Common/BaseEntity.cs` - base entity fields and optional domain-event collection support
- `ONEVO.Domain/Common/IDomainEvent.cs` - optional marker for post-save side effects
- `ONEVO.Domain/Features/{Feature}/Entities/` - business entities
- `ONEVO.Domain/Features/{Feature}/Events/` - optional; create only when an event is justified
- Zero framework dependencies - no EF Core attributes and no Infrastructure references

Clean Architecture and CQRS do not require domain events. Most entities should only contain state and business methods.
