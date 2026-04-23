# Backend Architecture

**.NET 9 Modular Monolith** — 23 modules, 170 tables, strict namespace boundaries.

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

- [[backend/messaging/event-catalog|Event Catalog]] — 40+ domain events
- [[backend/messaging/exchange-topology|Exchange Topology]] — Transactional outbox pattern
- [[backend/messaging/error-handling|Error Handling]] — Result<T>, exception handling

## Related

- [[frontend/README|Frontend]] — Next.js 14
- [[database/README|Database]] — PostgreSQL 16
- [[code-standards/backend-standards|Backend Standards]] — .NET naming + patterns
- [[Userflow/README|User Flows]] — End-to-end feature flows
