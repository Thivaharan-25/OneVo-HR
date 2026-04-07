# Backend Architecture

**.NET 9 Modular Monolith** — 22 modules, 163 tables, strict namespace boundaries.

## Quick Links

- [[module-catalog]] — Full module registry + dependency map
- [[module-boundaries]] — 5 core boundary rules
- [[shared-kernel]] — BaseEntity, Result<T>, ITenantContext
- [[api-conventions]] — REST standards, versioning, error format
- [[notification-system]] — 6-step notification pipeline
- [[real-time]] — SignalR architecture
- [[search-architecture]] — PostgreSQL FTS → Meilisearch
- [[monitoring-data-flow]] — Agent → API → Dashboard data flow
- [[external-integrations]] — Bridges, Stripe, Resend

## Messaging & Events

- [[event-catalog]] — 40+ domain events
- [[exchange-topology]] — Transactional outbox pattern
- [[error-handling]] — Result<T>, exception handling

## Related

- [[frontend/README|Frontend]] — Next.js 14
- [[database/README|Database]] — PostgreSQL 16
- [[code-standards/backend-standards|Backend Standards]] — .NET naming + patterns
- [[Userflow/README|User Flows]] — End-to-end feature flows
