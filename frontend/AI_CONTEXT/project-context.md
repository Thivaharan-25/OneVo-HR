# Project Context: ONEVO Frontend

## What It Is

The ONEVO Frontend is a React/Next.js application that serves as the web interface for the ONEVO platform. It covers both HR Management (Pillar 1) and Workforce Intelligence (Pillar 2).

## Architecture Overview

```
Next.js 14 App Router
├── (auth)/          — Public pages (login, forgot password, MFA)
├── (dashboard)/     — Authenticated pages (sidebar + topbar layout)
│   ├── overview/    — Landing dashboard
│   ├── hr/          — Pillar 1: HR Management
│   ├── workforce/   — Pillar 2: Workforce Intelligence
│   ├── org/         — Org Structure
│   └── settings/    — Tenant Configuration
├── (employee)/      — Employee self-service (limited nav)
└── api/             — API route handlers (BFF pattern for sensitive ops)
```

## Key Design Principles

1. **Permission-based rendering** — every feature gated by RBAC permissions
2. **Real-time where it matters** — SignalR for live workforce dashboard, exception alerts
3. **Polling where it's enough** — 30s polling for non-critical updates
4. **Responsive but desktop-first** — monitoring dashboards are primarily desktop
5. **Tenant-scoped everything** — all API calls include tenant context from JWT
6. **Feature flag aware** — UI adapts to what features the tenant has enabled

## Product Configurations Affect UI

| Config | What's Visible |
|:-------|:---------------|
| HR Only | `/hr/*`, `/org/*`, `/settings/*` (no `/workforce/*`) |
| HR + Workforce Intelligence | Full UI including `/workforce/*` |
| HR + Work Management | `/hr/*` + bridge data in dashboards |
| Full Suite | Everything |

## Backend API

The frontend consumes the ONEVO REST API at `/api/v1/*`. See the backend brain's `AI_CONTEXT/rules.md` for API design patterns.

- **Auth:** JWT in memory (access token) + HttpOnly cookie (refresh token)
- **Pagination:** Cursor-based, max 100 items
- **Errors:** RFC 7807 Problem Details
- **Real-time:** SignalR hub at `/hubs/notifications`

## Development Phase

The frontend is built AFTER the backend foundation is complete. See `AI_CONTEXT/current-focus.md` for timeline.
