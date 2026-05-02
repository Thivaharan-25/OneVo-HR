# FE Documentation Alignment Plan

**Goal:** Bring all frontend architecture docs into sync with the source of truth in `2026-04-28-fe-foundation.md`. The foundation plan defines the complete `src/lib/` structure (API client, interceptors, security layer, stores, signalr, utils) — most docs are silent or partial on this.

**Assumption:** We update the `frontend/` architecture docs (not the foundation plan itself). The foundation plan is read-only source of truth.

**Flow start:** `frontend/architecture/app-structure.md` (currently modified on branch Thiva) → fan out to detail docs.

**Audit result:**

| File | Status | Gap |
|------|--------|-----|
| `frontend/architecture/app-structure.md` | **MAJOR GAP** | Missing full `src/lib/` tree: `api/`, `interceptors/`, `stores/`, `signalr/`, `utils/`, `token-manager`, `permission-guard` |
| `frontend/cross-cutting/security.md` | **GAP** | Missing `lib/security/` folder block, `permission-guard`, `token-manager`, `idle-timeout`, correlation interceptor ref |
| `frontend/cross-cutting/authentication.md` | **GAP** | Missing `token-manager.ts` and `idle-timeout.ts` file-level references |
| `frontend/cross-cutting/authorization.md` | **GAP** | Missing `permission-guard.tsx`, `usePermissions` hook, `PermissionProvider` |
| `frontend/data-layer/real-time.md` | **MINOR** | Missing `lib/signalr/client.ts` path and `@microsoft/signalr` package name |
| `frontend/data-layer/api-integration.md` | ALIGNED ✓ | All 4 interceptors, ApiClient, errors.ts, endpoints/ — complete |
| `frontend/data-layer/state-management.md` | ALIGNED ✓ | Zustand stores, all 3 store files, TanStack Query — complete |
| `frontend/architecture/routing.md` | ALIGNED ✓ | ProtectedRoute, createBrowserRouter, lib/security ref — complete |

---

## Task 1 — `frontend/architecture/app-structure.md`

**Priority: FIRST** (starting point, all other docs cross-link here)

Add a `src/lib/` section directly after the existing `src/` tree block. Insert the full subtree from the foundation plan:

```
src/
├── lib/
│   ├── api/
│   │   ├── client.ts                         # Fetch wrapper — runs interceptor chain
│   │   ├── index.ts                          # Re-exports apiClient + all endpoint modules
│   │   ├── errors.ts                         # ApiError, AuthError, ProblemDetails type
│   │   ├── interceptors/
│   │   │   ├── auth.interceptor.ts           # Attaches Bearer token; triggers refresh when expiring
│   │   │   ├── tenant.interceptor.ts         # Injects X-Entity-Id from active entity in authStore
│   │   │   ├── correlation.interceptor.ts    # Injects X-Correlation-Id (crypto.randomUUID)
│   │   │   └── error.interceptor.ts          # 401 retry after refresh; toast on 4xx/5xx
│   │   └── endpoints/
│   │       ├── auth.ts
│   │       ├── employees.ts
│   │       ├── leave.ts
│   │       ├── org.ts
│   │       ├── workforce.ts
│   │       ├── calendar.ts
│   │       ├── notifications.ts
│   │       ├── settings.ts
│   │       ├── admin.ts
│   │       ├── agents.ts
│   │       ├── identity.ts
│   │       └── wms/
│   │           ├── projects.ts
│   │           ├── tasks.ts
│   │           ├── planner.ts
│   │           ├── goals.ts
│   │           ├── docs.ts
│   │           ├── time.ts
│   │           └── chat.ts
│   ├── security/
│   │   ├── token-manager.ts                  # In-memory access token store + isExpiringSoon()
│   │   ├── idle-timeout.ts                   # Auto-logout after inactivity
│   │   ├── sanitizer.ts                      # DOMPurify wrapper — used on all user-generated HTML
│   │   └── permission-guard.tsx              # <ProtectedRoute> component + redirect to /403
│   ├── signalr/
│   │   └── client.ts                         # HubConnectionBuilder setup; re-export hub instance
│   ├── i18n.ts                               # i18next init (browser language detector + HTTP backend)
│   └── utils/
│       ├── cn.ts                             # clsx + tailwind-merge shorthand
│       ├── format-date.ts                    # date-fns wrappers
│       └── to-params.ts                      # Object → URLSearchParams
│
├── stores/
│   ├── use-auth-store.ts                     # Zustand: current user, activeEntityId, token expiry
│   ├── use-sidebar-store.ts                  # Zustand: expanded pillar, active item
│   └── use-filter-store.ts                   # Zustand: per-module filter state
```

Also add a note below the existing Provider Stack section:

> `PermissionProvider` loads both role-level and per-employee-override permissions on mount and exposes them via `usePermissions()`. `usePermissions().hasPermission(key)` is the only correct way to gate UI — never read role names directly.

---

## Task 2 — `frontend/cross-cutting/security.md`

Add a **Security Layer File Structure** section near the top (after the overview paragraph):

```markdown
## Security Layer (`src/lib/security/`)

| File | Responsibility |
|------|---------------|
| `token-manager.ts` | Stores access token in memory only (never localStorage). Exposes `getToken()`, `setToken()`, `clearToken()`, `isExpiringSoon()`. |
| `idle-timeout.ts` | Listens to `mousemove`/`keydown`. Clears token and redirects to `/login` after configurable inactivity window. |
| `sanitizer.ts` | DOMPurify wrapper. All user-generated HTML (doc content, comments, chat) must pass through `sanitize(html)` before rendering. |
| `permission-guard.tsx` | `<ProtectedRoute permission="key">` — checks `hasPermission()` and redirects to `/403` if denied. Wraps individual routes in `router.tsx`. |
```

Add to the existing **Request Security** section (or create it):

```markdown
### Correlation Tracking
Every outbound request gets a unique `X-Correlation-Id` header (via `correlation.interceptor.ts`) to enable end-to-end request tracing across backend services.
```

---

## Task 3 — `frontend/cross-cutting/authentication.md`

Add a **Token Storage** subsection under the existing auth flow section:

```markdown
### Token Storage (`src/lib/security/token-manager.ts`)
Access tokens live **in memory only** — never in `localStorage` or `sessionStorage`. `token-manager.ts` exposes:
- `setToken(token, expiresIn)` — stores token + calculates expiry timestamp
- `getToken()` — returns current token string or null
- `clearToken()` — wipes on logout or session expiry
- `isExpiringSoon()` — returns true if token expires within 60 s (used by `auth.interceptor` to pre-emptively refresh)
```

Add an **Idle Timeout** subsection:

```markdown
### Idle Timeout (`src/lib/security/idle-timeout.ts`)
Registers `mousemove` and `keydown` listeners. After the configured idle window (default: 30 min), calls `tokenManager.clearToken()` and redirects to `/login`. Activated inside `AuthProvider` on mount.
```

---

## Task 4 — `frontend/cross-cutting/authorization.md`

Add a **Route Guard** section:

```markdown
## Route Guard (`src/lib/security/permission-guard.tsx`)

`<ProtectedRoute>` wraps any route that requires auth or a specific permission:

```tsx
// Auth-only (no permission key required)
<ProtectedRoute><DashboardLayout /></ProtectedRoute>

// Permission-gated
<ProtectedRoute permission="employees:read"><EmployeesPage /></ProtectedRoute>
```

Behavior:
- Not authenticated → redirect to `/login`
- Authenticated but missing permission → redirect to `/403`
```

Add a **Hook** section:

```markdown
## usePermissions Hook

Provided by `PermissionProvider` in `App.tsx`. Evaluates **both** role permissions and per-employee overrides in a single call:

```tsx
const { hasPermission } = usePermissions();
const canApprove = hasPermission('leave:approve');
```

Never read raw role names from the auth store for permission checks.
```

---

## Task 5 — `frontend/data-layer/real-time.md`

Add the file path and package reference at the top of the SignalR section:

```markdown
## SignalR Client (`src/lib/signalr/client.ts`)

Package: `@microsoft/signalr`

Builds and exports a shared `HubConnection` instance using `HubConnectionBuilder`. `SignalRProvider` (in `App.tsx`) manages connection lifecycle (start on auth, stop on logout).
```

---

## Execution Order

```
1. app-structure.md       ← do first; all other docs reference this as canonical file map
2. security.md            ← security layer structure (token-manager, sanitizer, permission-guard, correlation)
3. authentication.md      ← token-manager + idle-timeout detail
4. authorization.md       ← permission-guard + usePermissions + PermissionProvider
5. real-time.md           ← lib/signalr/client.ts path + package name
```

## Files NOT Changing

- `frontend/data-layer/api-integration.md` — fully aligned, all 4 interceptors documented
- `frontend/data-layer/state-management.md` — stores/ tree and Zustand usage fully documented
- `frontend/architecture/routing.md` — ProtectedRoute, createBrowserRouter, lib/security ref all present

---

## Responsive Phase 1 Alignment

**Reason:** The product requirement is that the application UI must be responsive by design from Phase 1, adapting smoothly across mobile, tablet, laptop, and desktop. Frontend docs must not defer mobile usability to Phase 2.

**Files to keep aligned:**

| File | Required alignment |
|------|--------------------|
| `frontend/design-system/README.md` | Canonical Phase 1 responsive requirement and viewport definitions |
| `frontend/design-system/patterns/layout-patterns.md` | Mobile/tablet/laptop/desktop shell and page behavior |
| `frontend/design-system/components/shell-layout.md` | Responsive shell implementation, including `MobileNavDrawer` |
| `frontend/design-system/patterns/navigation-patterns.md` | Shared responsive navigation states |
| `frontend/design-system/patterns/table-patterns.md` | Mobile card/list behavior and controlled table overflow |
| `frontend/design-system/patterns/form-patterns.md` | Single-column mobile forms, tablet behavior, sticky wizard actions |
| `frontend/architecture/app-structure.md` | Shared responsive layout components |
| `frontend/architecture/topbar.md` | Responsive topbar behavior |
| `frontend/architecture/sidebar-nav.md` | Shared route map for sidebar and drawer |
| `frontend/testing/strategy.md` | Required viewport QA and Playwright coverage |
| `frontend/performance/budget.md` | Mobile/responsive performance budget |

**Guardrail:** Do not reintroduce language that says mobile is not optimized or deferred to Phase 2. Phase 2 may deepen native/mobile-specific polish, but Phase 1 web UI must already be usable on mobile.
