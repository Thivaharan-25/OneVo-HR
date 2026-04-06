# Technology Stack: ONEVO Frontend

## Core

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Framework | Next.js | 14+ | App Router, Server Components, Vercel deployment |
| Language | TypeScript | 5.x | Strict mode enabled |
| Runtime | Node.js | 20 LTS | |
| Package Manager | pnpm | 8.x | Workspace support |

## UI & Styling

| Category | Technology | Purpose |
|:---------|:-----------|:--------|
| CSS Framework | Tailwind CSS 3.x | Utility-first styling |
| Component Library | shadcn/ui | Unstyled Radix primitives, copy-paste, enterprise-grade |
| Icons | Lucide React | Consistent icon set |
| Charts | Recharts | Standard charts (line, bar, pie, area) |
| Dashboard Blocks | Tremor | Pre-built dashboard components (KPI cards, sparklines) |
| Animation | Framer Motion | Page transitions, micro-interactions |
| Theming | CSS Custom Properties | Light/dark mode, tenant branding |

## State Management

| Category | Technology | Purpose |
|:---------|:-----------|:--------|
| Server State | TanStack Query v5 | API data fetching, caching, mutations, optimistic updates |
| Client State | Zustand 4.x | Sidebar, filters, UI preferences, monitoring config cache |
| URL State | nuqs | Filters, pagination, search params in URL |
| Forms | React Hook Form + Zod | Form state + validation (mirrors backend FluentValidation) |

## Data Fetching

| Pattern | When |
|:--------|:-----|
| TanStack Query | All API calls — provides caching, deduplication, background refresh |
| Server Components | Initial page data (SSR for SEO-irrelevant dashboards = minimal use) |
| SignalR | Live workforce dashboard, exception alerts, agent status |
| Polling (30s) | Non-critical dashboard updates as fallback |

## Real-time

| Technology | Purpose |
|:-----------|:--------|
| @microsoft/signalr | WebSocket connection to ONEVO backend |
| SignalR channels | `workforce-live`, `exception-alerts`, `notifications-{userId}`, `agent-status` |
| Reconnection | Auto-reconnect with exponential backoff |

## Testing

| Technology | Purpose |
|:-----------|:--------|
| Vitest | Unit tests for utilities, hooks, stores |
| React Testing Library | Component tests |
| Playwright | E2E tests for critical flows |
| MSW (Mock Service Worker) | API mocking for component/integration tests |

## Build & Deploy

| Category | Technology |
|:---------|:-----------|
| Hosting | Vercel |
| CI/CD | GitHub Actions |
| Linting | ESLint + Prettier |
| Type Checking | TypeScript strict mode |
| Bundle Analysis | @next/bundle-analyzer |

## Key Dependencies

```json
{
  "@microsoft/signalr": "latest",
  "@tanstack/react-query": "^5",
  "@radix-ui/react-*": "latest",
  "zustand": "^4",
  "nuqs": "latest",
  "react-hook-form": "latest",
  "zod": "latest",
  "recharts": "latest",
  "@tremor/react": "latest",
  "lucide-react": "latest",
  "framer-motion": "latest",
  "date-fns": "latest",
  "class-variance-authority": "latest",
  "clsx": "latest",
  "tailwind-merge": "latest"
}
```
