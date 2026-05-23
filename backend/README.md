# Backend Architecture

> Status: backend implementation exists in `../Onevo_Backend`. This folder is the architecture and implementation blueprint, and should stay aligned with the actual solution.

**.NET 10 / C# 14 Clean Architecture + CQRS** - feature folders, single `ApplicationDbContext`, strict layer boundaries.

## Quick Links

- [[backend/folder-structure|Folder Structure]] - canonical backend solution and feature folder layout
- [[backend/cqrs-patterns|CQRS Patterns]] - command/query/validator/handler rules
- [[backend/module-catalog|Module Catalog]] - full feature registry and dependency map
- [[backend/module-boundaries|Module Boundaries]] - layer and feature boundary rules
- [[backend/shared-kernel|Shared Kernel]] - base entities, value objects, `Result<T>`
- [[backend/api-conventions|Api Conventions]] - REST standards, versioning, error format
- [[backend/notification-system|Notification System]] - notification pipeline
- [[backend/real-time|Real-Time Architecture]] - SignalR architecture
- [[backend/search-architecture|Search Architecture]] - PostgreSQL FTS first
- [[backend/monitoring-data-flow|Monitoring Data Flow]] - Agent -> API -> Dashboard data flow
- [[backend/external-integrations|External Integrations]] - Stripe, Resend, biometric terminals, calendar, Slack, Microsoft Teams, payroll, LMS

## Default Backend Flow

```text
Controller -> Command/Query -> Validator -> Handler -> Repository/Domain -> UnitOfWork -> Response
```

Domain events are optional. Use [[backend/domain-events|Domain Events]] only for justified post-save side effects, not as a default feature template.

## Architecture Decisions

- [[docs/decisions/ADR-002-clean-architecture-cqrs|ADR-002]] - Clean Architecture + CQRS
- [[docs/decisions/ADR-003-single-applicationdbcontext|ADR-003]] - Single ApplicationDbContext

## Related

- [[frontend/README|Frontend]] - Angular 21 two-app monorepo
- [[database/README|Database]] - PostgreSQL 16.13 baseline / PostgreSQL 18 target after validation
- [[code-standards/backend-standards|Backend Standards]] - .NET naming and patterns
- [[Userflow/README|User Flows]] - end-to-end feature flows
