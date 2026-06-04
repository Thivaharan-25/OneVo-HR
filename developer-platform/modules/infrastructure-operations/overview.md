# Infrastructure Operations

> Phase 2 only as a standalone operations module. Phase 1 may show basic read-only dependency status inside Platform Health, but it must not expose a dedicated Infrastructure Operations screen.

## Purpose

Infrastructure Operations shows platform-level infrastructure capacity and dependency state — database, storage, queue depth, cloud provider metrics, and external service availability.

## Data / Systems Read

| Source | Role |
|---|---|
| Infrastructure health readers | CPU, memory, storage, database connection pool, queue depth |
| Integration health readers | Payment gateway, email provider, storage provider status |
| Tenant registry | Tenant count by region and status (for capacity context) |
| Cloud provider APIs | Region-level metrics and availability |

## Capabilities

- View database capacity (connection pool usage, query latency, storage size)
- View storage capacity (Azure Blob usage %, queue depth)
- View cloud infrastructure metrics (CPU, memory, storage across all instances)
- View external dependency health: payment gateways, Resend, Cloudflare
- Identify degraded dependencies with `detected_at` timestamp showing when degradation started
- Link to Services Monitor and Background Jobs for follow-up

## Navigation

| Route | Permission |
|---|---|
| `/operations/infrastructure` | Phase 2 permission contract |

## Key Rules

- Phase 1 has no standalone Infrastructure Operations screen
- Responses must never contain connection strings, API keys, cloud credentials, or internal IP addresses
- A single unavailable metric shows `status = "unknown"` rather than failing the whole response
- Degraded dependency entries always include `detected_at` — not just current state

## Related

- [[developer-platform/modules/infrastructure-operations/end-to-end-logic|Infrastructure Operations End-to-End Logic]]
- [[developer-platform/modules/platform-health/overview|Platform Health]] — service-level health
- [[developer-platform/modules/services-monitor/overview|Services Monitor]] — per-service investigation
