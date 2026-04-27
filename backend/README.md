# Backend Architecture

**.NET 9 Clean Architecture + CQRS** — 23 modules, 170 tables, strict namespace boundaries.

## Quick Links

- [[backend/module-catalog|Module Catalog]] — Full module registry + dependency map
- [[backend/module-boundaries|Module Boundaries]] — 5 core boundary rules
- [[backend/shared-kernel|Shared Kernel]] — BaseEntity, Result<T>, ITenantContext
- [[backend/api-conventions|Api Conventions]] — REST standards, versioning, error format
- [[backend/notification-system|Notification System]] — 6-step notification pipeline
- [[backend/real-time|Real-Time Architecture]] — SignalR architecture
- [[backend/search-architecture|Search Architecture]] — PostgreSQL FTS → Meilisearch
- [[backend/monitoring-data-flow|Monitoring Data Flow]] — Agent → API → Dashboard data flow
- [[backend/external-integrations|External Integrations]] — Bridges, Stripe, Resend

## Messaging & Events

- [[backend/domain-events|Domain Events]] — Event handling and domain event propagation
- [[backend/domain-events|Domain Events]] — Result<T>, exception handling

## Architecture Decisions

- [[docs/decisions/ADR-001-per-module-database-and-event-bus|ADR-001]] — Per-module DbContext + IDomainEvent abstraction (microservice-forward design)

## Related

- [[frontend/README|Frontend]] — Next.js 14
- [[database/README|Database]] — PostgreSQL 16
- [[code-standards/backend-standards|Backend Standards]] — .NET naming + patterns
- [[Userflow/README|User Flows]] — End-to-end feature flows
