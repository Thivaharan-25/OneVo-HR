# ONEVO Frontend — Secondary Brain

This is the AI-optimized knowledge base for the ONEVO Frontend (React/Next.js) development team.

## Tech Stack

- **Framework:** Next.js 14+ (App Router, Server Components)
- **Language:** TypeScript 5.x (strict mode)
- **Styling:** Tailwind CSS 3.x
- **Components:** shadcn/ui (Radix primitives)
- **Charts:** Recharts + Tremor (dashboard blocks)
- **Server State:** TanStack Query v5
- **Client State:** Zustand 4.x
- **Forms:** React Hook Form + Zod
- **URL State:** nuqs
- **Real-time:** @microsoft/signalr
- **Testing:** Vitest + React Testing Library + Playwright

## Two Pillars

The frontend serves both product pillars:

| Pillar | Routes | Key Pages |
|:-------|:-------|:----------|
| HR Management | `/hr/*` | Employees, Leave, Performance, Payroll, Skills, Documents |
| Workforce Intelligence | `/workforce/*` | Live Dashboard, Activity Detail, Reports, Exceptions |
| Settings | `/settings/*` | General, Monitoring Config, Notifications, Integrations |
| Self-Service | `/my-*` | Own Dashboard, Own Leave, Own Profile |

## Reading Order

1. `AI_CONTEXT/project-context.md` — what the frontend does
2. `AI_CONTEXT/tech-stack.md` — technologies
3. `AI_CONTEXT/rules.md` — coding standards
4. `docs/architecture/` — app structure, state management, API integration, real-time
5. `docs/design-system/` — components, layout, tokens
6. `docs/pages/` — page specs (one per page)
7. `docs/security/` — auth flow, RBAC
8. Backend brain: `AI_CONTEXT/` — API contracts, module architecture
