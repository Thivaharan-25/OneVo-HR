# FE Dev 1 — Task 1: Vite Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the bare Vite+React scaffold in `OneVo/` into a production-ready SPA foundation with TypeScript, Tailwind, shadcn/ui, React Router v7, security layer, API client with interceptors, provider stack, shell layout, and shared components — on which all 7 other developers build.

**Architecture:** Vite SPA (CSR only, no SSR). Routes defined in `src/router.tsx` using `createBrowserRouter`. Security lives in `lib/security/` (in-memory tokens, interceptors, route guards). All 8 module API endpoint files are stubs — each dev fills in their own.

**Tech Stack:** Vite 8, React 19, TypeScript 5, Tailwind CSS 4, shadcn/ui, React Router v7, TanStack Query v5, Zustand 4, @microsoft/signalr, DOMPurify, Zod, i18next, react-i18next, web-vitals, @sentry/react, Vitest + RTL

**Dependency:** All other 7 frontend devs are blocked until this plan is complete. Complete and commit before handing off.

---

## File Map

**Create (new files):**
```
OneVo/
├── tsconfig.json
├── tsconfig.node.json
├── tailwind.config.ts
├── components.json                          ← shadcn/ui config
├── .env.example
├── .env.local
├── vite.config.ts                           ← replaces existing
├── package.json                             ← replaces existing
├── src/
│   ├── main.tsx                             ← replaces main.jsx
│   ├── App.tsx                              ← replaces App.jsx
│   ├── router.tsx
│   ├── vite-env.d.ts
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── index.ts
│   │   │   ├── errors.ts
│   │   │   ├── interceptors/
│   │   │   │   ├── auth.interceptor.ts
│   │   │   │   ├── tenant.interceptor.ts
│   │   │   │   ├── correlation.interceptor.ts
│   │   │   │   └── error.interceptor.ts
│   │   │   └── endpoints/
│   │   │       ├── auth.ts
│   │   │       ├── employees.ts
│   │   │       ├── leave.ts
│   │   │       ├── org.ts
│   │   │       ├── workforce.ts
│   │   │       ├── calendar.ts
│   │   │       ├── notifications.ts
│   │   │       ├── settings.ts
│   │   │       ├── admin.ts
│   │   │       ├── agents.ts
│   │   │       ├── identity.ts
│   │   │       └── wms/
│   │   │           ├── projects.ts
│   │   │           ├── tasks.ts
│   │   │           ├── planner.ts
│   │   │           ├── goals.ts
│   │   │           ├── docs.ts
│   │   │           ├── time.ts
│   │   │           └── chat.ts
│   │   ├── security/
│   │   │   ├── token-manager.ts
│   │   │   ├── idle-timeout.ts
│   │   │   ├── sanitizer.ts
│   │   │   └── permission-guard.tsx
│   │   ├── signalr/
│   │   │   └── client.ts
│   │   ├── i18n.ts
│   │   └── utils/
│   │       ├── cn.ts
│   │       ├── format-date.ts
│   │       └── to-params.ts
│   │
│   ├── stores/
│   │   ├── use-auth-store.ts
│   │   ├── use-sidebar-store.ts
│   │   ├── use-filter-store.ts
│   │   └── use-theme-store.ts
│   │
│   ├── types/
│   │   ├── auth.ts
│   │   ├── core-hr.ts
│   │   ├── org.ts
│   │   ├── workforce.ts
│   │   ├── notifications.ts
│   │   ├── settings.ts
│   │   ├── admin.ts
│   │   └── wms/
│   │       ├── projects.ts
│   │       ├── tasks.ts
│   │       ├── goals.ts
│   │       └── chat.ts
│   │
│   ├── hooks/
│   │   └── shared/
│   │       ├── use-debounce.ts
│   │       └── use-permissions.ts
│   │
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── AuthLayout.tsx
│   │   │   ├── LoginPage.tsx            ← stub (Dev 2 fills in)
│   │   │   ├── ForgotPasswordPage.tsx   ← stub
│   │   │   ├── ResetPasswordPage.tsx    ← stub
│   │   │   └── MfaPage.tsx              ← stub
│   │   ├── dashboard/
│   │   │   ├── DashboardLayout.tsx
│   │   │   ├── HomePage.tsx             ← stub
│   │   │   └── [all other pages as stubs — see Task 6]
│   │   └── errors/
│   │       ├── NotFoundPage.tsx
│   │       ├── ForbiddenPage.tsx
│   │       └── ErrorPage.tsx
│   │
│   ├── components/
│   │   ├── ui/                          ← shadcn/ui auto-generated
│   │   ├── layout/
│   │   │   ├── NavRail.tsx
│   │   │   ├── ExpansionPanel.tsx
│   │   │   ├── Topbar.tsx
│   │   │   ├── EntitySwitcher.tsx
│   │   │   └── Breadcrumb.tsx
│   │   └── shared/
│   │       ├── DataTable.tsx
│   │       ├── PageHeader.tsx
│   │       ├── StatusBadge.tsx
│   │       ├── PermissionGate.tsx
│   │       ├── EmptyState.tsx
│   │       ├── TableSkeleton.tsx
│   │       ├── ErrorState.tsx
│   │       └── Avatar.tsx
│   │
│   └── styles/
│       ├── globals.css
│       └── tokens.css
```

**Delete:**
- `src/App.css`, `src/index.css` (replaced by `src/styles/`)
- `src/App.jsx`, `src/main.jsx` (replaced by `.tsx`)
- `src/assets/react.svg`, `src/assets/vite.svg` (default scaffold assets)

---

## Task 1: Package Setup + TypeScript + Vite Config

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.node.json`, `src/vite-env.d.ts`, `.env.example`

- [ ] **Replace `package.json`**

```json
{
  "name": "onevo",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint . --ext ts,tsx",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "@microsoft/signalr": "^8.0.0",
    "@radix-ui/react-dialog": "^1.1.0",
    "@radix-ui/react-dropdown-menu": "^2.1.0",
    "@radix-ui/react-select": "^2.1.0",
    "@radix-ui/react-slot": "^1.1.0",
    "@radix-ui/react-tooltip": "^1.1.0",
    "@sentry/react": "^8.0.0",
    "@tanstack/react-query": "^5.0.0",
    "@tanstack/react-query-devtools": "^5.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "date-fns": "^3.0.0",
    "dompurify": "^3.1.0",
    "i18next": "^23.0.0",
    "i18next-browser-languagedetector": "^7.0.0",
    "i18next-http-backend": "^2.0.0",
    "lucide-react": "^0.400.0",
    "react": "^19.2.5",
    "react-dom": "^19.2.5",
    "react-hook-form": "^7.50.0",
    "react-i18next": "^14.0.0",
    "react-router-dom": "^7.0.0",
    "recharts": "^2.12.0",
    "sonner": "^1.5.0",
    "tailwind-merge": "^2.3.0",
    "web-vitals": "^3.5.0",
    "zod": "^3.22.0",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@eslint/js": "^10.0.1",
    "@playwright/test": "^1.44.0",
    "@testing-library/jest-dom": "^6.4.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/user-event": "^14.5.0",
    "@types/dompurify": "^3.0.5",
    "@types/node": "^20.0.0",
    "@types/react": "^19.2.14",
    "@types/react-dom": "^19.2.3",
    "@vitejs/plugin-react": "^6.0.1",
    "autoprefixer": "^10.4.0",
    "eslint": "^10.2.1",
    "eslint-plugin-react-hooks": "^7.1.1",
    "globals": "^17.5.0",
    "jsdom": "^24.0.0",
    "msw": "^2.3.0",
    "rollup-plugin-visualizer": "^5.12.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "typescript": "^5.4.0",
    "vitest": "^1.6.0"
  }
}
```

- [ ] **Run install**

```bash
cd OneVo
npm install
```

Expected: node_modules populated, no peer dependency errors.

- [ ] **Replace `vite.config.ts`**

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { visualizer } from 'rollup-plugin-visualizer';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    visualizer({ open: false, gzipSize: true }),
  ],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    headers: {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts',
  },
});
```

- [ ] **Create `tsconfig.json`**

```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

- [ ] **Create `tsconfig.app.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"]
}
```

- [ ] **Create `tsconfig.node.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Create `src/vite-env.d.ts`**

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_SIGNALR_URL: string;
  readonly VITE_SENTRY_DSN: string;
  readonly VITE_ENV: 'development' | 'staging' | 'production';
  readonly VITE_APP_VERSION: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

- [ ] **Create `.env.example`**

```
VITE_API_URL=http://localhost:5000
VITE_SIGNALR_URL=http://localhost:5000
VITE_SENTRY_DSN=
VITE_ENV=development
VITE_APP_VERSION=0.1.0
```

- [ ] **Copy `.env.example` to `.env.local`** (fill in local values)

- [ ] **Create `src/test-setup.ts`**

```typescript
import '@testing-library/jest-dom';
```

- [ ] **Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Commit**

```bash
git add package.json vite.config.ts tsconfig*.json src/vite-env.d.ts .env.example src/test-setup.ts
git commit -m "feat: configure Vite + TypeScript + testing foundation"
```

---

## Task 2: Tailwind CSS + Design Tokens

**Files:** `tailwind.config.ts`, `src/styles/globals.css`, `src/styles/tokens.css`

- [ ] **Create `src/styles/tokens.css`** (design tokens from `frontend/design-system/foundations/color-tokens.md`)

```css
:root {
  /* Brand */
  --color-brand-primary: #5B4FE8;
  --color-brand-primary-hover: #4A3FD4;
  --color-brand-secondary: #8C86F2;

  /* Shell — Light */
  --color-shell-bg: #F0F1F7;
  --color-shell-rail: #17181F;
  --color-shell-surface: #FFFFFF;
  --color-shell-border: #E2E3EA;

  /* Text — Light */
  --color-text-primary: #1E2140;
  --color-text-secondary: #6B7194;
  --color-text-muted: #9499B0;
  --color-text-placeholder: #C8CADC;

  /* Semantic */
  --color-success: #22C55E;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 12px;
  --radius-full: 9999px;
}

[data-theme="dark"] {
  --color-shell-bg: #0F1117;
  --color-shell-surface: #17181F;
  --color-shell-border: rgba(255, 255, 255, 0.06);
  --color-text-primary: rgba(255, 255, 255, 0.92);
  --color-text-secondary: rgba(255, 255, 255, 0.55);
  --color-text-muted: rgba(255, 255, 255, 0.35);
  --color-text-placeholder: rgba(255, 255, 255, 0.15);
}
```

- [ ] **Create `src/styles/globals.css`**

```css
@import "tailwindcss";
@import "./tokens.css";

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: var(--color-shell-bg);
  color: var(--color-text-primary);
  font-family: 'Outfit', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--color-shell-border); border-radius: 3px; }
```

- [ ] **Verify dev server starts without CSS errors**

```bash
npm run dev
```

Expected: Server starts on localhost:5173, no CSS parsing errors in console.

- [ ] **Commit**

```bash
git add src/styles/
git commit -m "feat: add Tailwind CSS v4 + design tokens"
```

---

## Task 3: shadcn/ui Init

**Files:** `components.json`, `src/components/ui/` (auto-generated)

- [ ] **Create `components.json`**

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/styles/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils/cn",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

- [ ] **Create `src/lib/utils/cn.ts`**

```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Add core shadcn/ui components**

```bash
npx shadcn@latest add button input label select dialog dropdown-menu tooltip badge card separator avatar skeleton progress
```

Expected: Components appear in `src/components/ui/`.

- [ ] **Verify a component imports cleanly**

```bash
node -e "console.log('ok')"
# Just check the file exists:
ls src/components/ui/button.tsx
```

- [ ] **Commit**

```bash
git add components.json src/components/ui/ src/lib/utils/cn.ts
git commit -m "feat: add shadcn/ui component library"
```

---

## Task 4: Security Layer

**Files:** `src/lib/security/token-manager.ts`, `idle-timeout.ts`, `sanitizer.ts`, `permission-guard.tsx`

- [ ] **Write test for token-manager**

```typescript
// src/lib/security/__tests__/token-manager.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { tokenManager } from '../token-manager';

describe('tokenManager', () => {
  beforeEach(() => tokenManager.clear());

  it('returns null when no token set', () => {
    expect(tokenManager.get()).toBeNull();
  });

  it('stores and retrieves a token', () => {
    tokenManager.set('abc123', 3600);
    expect(tokenManager.get()).toBe('abc123');
  });

  it('isExpiringSoon returns false for fresh token', () => {
    tokenManager.set('abc123', 3600);
    expect(tokenManager.isExpiringSoon()).toBe(false);
  });

  it('isExpiringSoon returns true when within 60s of expiry', () => {
    tokenManager.set('abc123', 30); // expires in 30s — within 60s window
    expect(tokenManager.isExpiringSoon()).toBe(true);
  });

  it('clear wipes the token', () => {
    tokenManager.set('abc123', 3600);
    tokenManager.clear();
    expect(tokenManager.get()).toBeNull();
  });
});
```

- [ ] **Run test — verify it fails**

```bash
npx vitest run src/lib/security/__tests__/token-manager.test.ts
```

Expected: FAIL — module not found.

- [ ] **Implement `src/lib/security/token-manager.ts`**

```typescript
let _accessToken: string | null = null;
let _expiresAt: number | null = null;

export const tokenManager = {
  set(token: string, expirySeconds: number): void {
    _accessToken = token;
    _expiresAt = Date.now() + expirySeconds * 1000;
  },
  get(): string | null {
    return _accessToken;
  },
  isExpiringSoon(): boolean {
    return _expiresAt !== null && Date.now() > _expiresAt - 60_000;
  },
  clear(): void {
    _accessToken = null;
    _expiresAt = null;
  },
};
```

- [ ] **Run test — verify it passes**

```bash
npx vitest run src/lib/security/__tests__/token-manager.test.ts
```

Expected: PASS (5 tests).

- [ ] **Create `src/lib/security/idle-timeout.ts`**

```typescript
const IDLE_MS = 30 * 60 * 1000; // 30 minutes
let _timer: ReturnType<typeof setTimeout> | null = null;
let _onTimeout: (() => void) | null = null;

function reset() {
  if (_timer) clearTimeout(_timer);
  if (!_onTimeout) return;
  _timer = setTimeout(_onTimeout, IDLE_MS);
}

export const idleTimeout = {
  start(onTimeout: () => void): void {
    _onTimeout = onTimeout;
    const events = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'];
    events.forEach(e => window.addEventListener(e, reset, { passive: true }));
    reset();
  },
  stop(): void {
    if (_timer) { clearTimeout(_timer); _timer = null; }
    _onTimeout = null;
  },
};
```

- [ ] **Create `src/lib/security/sanitizer.ts`**

```typescript
import DOMPurify from 'dompurify';

const ALLOWED = {
  ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'blockquote', 'code', 'pre'],
  ALLOWED_ATTR: ['href', 'target', 'rel'],
};

export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, ALLOWED);
}

export function SafeHTML({ html, className }: { html: string; className?: string }) {
  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizeHtml(html) }}
    />
  );
}
```

- [ ] **Create `src/lib/security/permission-guard.tsx`**

```typescript
import { type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/use-auth-store';

interface ProtectedRouteProps {
  permission?: string;
  children: ReactNode;
}

export function ProtectedRoute({ permission, children }: ProtectedRouteProps) {
  const { user, hasPermission } = useAuthStore();
  const location = useLocation();

  if (!user) {
    return (
      <Navigate
        to={`/login?redirect=${encodeURIComponent(location.pathname)}`}
        replace
      />
    );
  }

  if (permission && !hasPermission(permission)) {
    return <Navigate to="/403" replace />;
  }

  return <>{children}</>;
}
```

- [ ] **Commit**

```bash
git add src/lib/security/
git commit -m "feat: add security layer (token-manager, idle-timeout, sanitizer, permission-guard)"
```

---

## Task 5: Zustand Stores

**Files:** `src/stores/use-auth-store.ts`, `use-sidebar-store.ts`, `use-filter-store.ts`, `use-theme-store.ts`

- [ ] **Create `src/stores/use-auth-store.ts`**

```typescript
import { create } from 'zustand';

export interface User {
  id: string;
  email: string;
  fullName: string;
  avatarUrl: string | null;
  tenantId: string;
  activeEntityId: string;
}

interface AuthStore {
  user: User | null;
  permissions: string[];
  features: string[];
  hasPermission: (permission: string) => boolean;
  hasFeature: (feature: string) => boolean;
  setAuth: (user: User, permissions: string[], features: string[]) => void;
  setActiveEntity: (entityId: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  permissions: [],
  features: [],
  hasPermission: (permission) => get().permissions.includes(permission),
  hasFeature: (feature) => get().features.includes(feature),
  setAuth: (user, permissions, features) => set({ user, permissions, features }),
  setActiveEntity: (entityId) =>
    set(state => state.user ? { user: { ...state.user, activeEntityId: entityId } } : {}),
  clear: () => set({ user: null, permissions: [], features: [] }),
}));
```

- [ ] **Create `src/stores/use-sidebar-store.ts`**

```typescript
import { create } from 'zustand';

interface SidebarStore {
  isExpanded: boolean;
  activePillar: string | null;
  setActivePillar: (pillar: string | null) => void;
  collapse: () => void;
}

export const useSidebarStore = create<SidebarStore>((set) => ({
  isExpanded: false,
  activePillar: null,
  setActivePillar: (pillar) => set({ activePillar: pillar, isExpanded: pillar !== null }),
  collapse: () => set({ activePillar: null, isExpanded: false }),
}));
```

- [ ] **Create `src/stores/use-filter-store.ts`**

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WorkforceFilters {
  department: string | null;
  status: string[];
}

interface FilterStore {
  workforce: WorkforceFilters;
  setWorkforceFilters: (filters: Partial<WorkforceFilters>) => void;
  resetFilters: () => void;
}

const defaults: WorkforceFilters = { department: null, status: [] };

export const useFilterStore = create<FilterStore>()(
  persist(
    (set) => ({
      workforce: defaults,
      setWorkforceFilters: (filters) =>
        set(state => ({ workforce: { ...state.workforce, ...filters } })),
      resetFilters: () => set({ workforce: defaults }),
    }),
    { name: 'onevo-filters' }
  )
);
```

- [ ] **Create `src/stores/use-theme-store.ts`**

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark' | 'system';

interface ThemeStore {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => {
        set({ theme });
        const root = document.documentElement;
        if (theme === 'dark') root.setAttribute('data-theme', 'dark');
        else if (theme === 'light') root.removeAttribute('data-theme');
        else {
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          prefersDark ? root.setAttribute('data-theme', 'dark') : root.removeAttribute('data-theme');
        }
      },
    }),
    { name: 'onevo-theme' }
  )
);
```

- [ ] **Commit**

```bash
git add src/stores/
git commit -m "feat: add Zustand stores (auth, sidebar, filter, theme)"
```

---

## Task 6: API Layer

**Files:** `src/lib/api/errors.ts`, `client.ts`, all 4 interceptors, all endpoint stubs, `index.ts`

- [ ] **Create `src/lib/api/errors.ts`**

```typescript
export interface ProblemDetails {
  type?: string;
  title: string;
  status: number;
  detail: string;
  errors?: Record<string, string[]>;
}

export interface PagedResult<T> {
  items: T[];
  nextCursor: string | null;
  hasMore: boolean;
}

export class ApiError extends Error {
  constructor(public problem: ProblemDetails) {
    super(problem.detail ?? problem.title);
    this.name = 'ApiError';
  }
}

export class AuthError extends Error {
  constructor(message = 'Session expired') {
    super(message);
    this.name = 'AuthError';
  }
}
```

- [ ] **Create `src/lib/api/interceptors/auth.interceptor.ts`**

```typescript
import { tokenManager } from '@/lib/security/token-manager';

// refreshAccessToken will be set by Dev 2 when they implement auth endpoints
let _refreshFn: (() => Promise<void>) | null = null;

export function registerRefreshFn(fn: () => Promise<void>) {
  _refreshFn = fn;
}

export const authInterceptor = {
  async onRequest(request: Request): Promise<Request> {
    if (tokenManager.isExpiringSoon() && _refreshFn) {
      await _refreshFn();
    }
    const token = tokenManager.get();
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    return request;
  },
};
```

- [ ] **Create `src/lib/api/interceptors/tenant.interceptor.ts`**

```typescript
import { useAuthStore } from '@/stores/use-auth-store';

export const tenantInterceptor = {
  onRequest(request: Request): Request {
    const entityId = useAuthStore.getState().user?.activeEntityId;
    if (entityId) {
      request.headers.set('X-Entity-Id', entityId);
    }
    return request;
  },
};
```

- [ ] **Create `src/lib/api/interceptors/correlation.interceptor.ts`**

```typescript
export const correlationInterceptor = {
  onRequest(request: Request): Request {
    request.headers.set('X-Correlation-Id', crypto.randomUUID());
    return request;
  },
};
```

- [ ] **Create `src/lib/api/interceptors/error.interceptor.ts`**

```typescript
import { tokenManager } from '@/lib/security/token-manager';
import { ApiError, AuthError, type ProblemDetails } from '@/lib/api/errors';
import { toast } from 'sonner';

export const errorInterceptor = {
  async onResponse<T>(response: Response, retry: () => Promise<T>): Promise<T> {
    if (response.ok) {
      const text = await response.text();
      return text ? JSON.parse(text) : undefined as T;
    }

    switch (response.status) {
      case 401:
        tokenManager.clear();
        window.location.href = '/login';
        throw new AuthError();

      case 403:
        window.location.href = '/403';
        throw new ApiError({ status: 403, title: 'Forbidden', detail: 'Access denied' });

      case 429: {
        const after = Number(response.headers.get('Retry-After') ?? '5');
        await new Promise(r => setTimeout(r, after * 1000));
        return retry();
      }

      default: {
        const problem: ProblemDetails = await response.json().catch(() => ({
          status: response.status,
          title: 'Error',
          detail: 'An unexpected error occurred',
        }));
        toast.error(problem.detail ?? problem.title);
        throw new ApiError(problem);
      }
    }
  },
};
```

- [ ] **Create `src/lib/api/client.ts`**

```typescript
import { authInterceptor } from './interceptors/auth.interceptor';
import { tenantInterceptor } from './interceptors/tenant.interceptor';
import { correlationInterceptor } from './interceptors/correlation.interceptor';
import { errorInterceptor } from './interceptors/error.interceptor';

class ApiClient {
  private baseUrl = import.meta.env.VITE_API_URL;

  async fetch<T>(path: string, options: RequestInit = {}): Promise<T> {
    let request = new Request(`${this.baseUrl}${path}`, {
      ...options,
      headers: new Headers({
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string> ?? {}),
      }),
      credentials: 'include',
    });

    request = await authInterceptor.onRequest(request);
    request = tenantInterceptor.onRequest(request);
    request = correlationInterceptor.onRequest(request);

    const response = await fetch(request);
    return errorInterceptor.onResponse<T>(response, () => this.fetch(path, options));
  }
}

export const apiClient = new ApiClient();
```

- [ ] **Create all endpoint stubs** (one per module — each dev fills in their own)

```typescript
// src/lib/api/endpoints/auth.ts
import { apiClient } from '@/lib/api/client';
export const authApi = {
  login: (data: { email: string; password: string }) =>
    apiClient.fetch<{ accessToken: string; expiresIn: number }>('/api/v1/auth/login', {
      method: 'POST', body: JSON.stringify(data),
    }),
  refresh: () => apiClient.fetch<{ accessToken: string; expiresIn: number }>('/api/v1/auth/refresh', { method: 'POST' }),
  logout: () => apiClient.fetch<void>('/api/v1/auth/logout', { method: 'POST' }),
  me: () => apiClient.fetch<import('@/stores/use-auth-store').User>('/api/v1/auth/me'),
};
```

```typescript
// src/lib/api/endpoints/employees.ts
// TODO: Dev 1 Task 2 fills this in
import { apiClient } from '@/lib/api/client';
export const employeesApi = {
  list: (_filters: Record<string, unknown>) => apiClient.fetch<{ items: unknown[]; nextCursor: null; hasMore: false }>('/api/v1/employees'),
  get: (id: string) => apiClient.fetch<unknown>(`/api/v1/employees/${id}`),
};
```

Create similar stubs for: `leave.ts`, `org.ts`, `workforce.ts`, `calendar.ts`, `notifications.ts`, `settings.ts`, `admin.ts`, `agents.ts`, `identity.ts`, `wms/projects.ts`, `wms/tasks.ts`, `wms/planner.ts`, `wms/goals.ts`, `wms/docs.ts`, `wms/time.ts`, `wms/chat.ts` — each just exports an object with the module name and a comment `// TODO: [DevN Task N] fills this in`.

- [ ] **Create `src/lib/api/index.ts`**

```typescript
import { authApi } from './endpoints/auth';
import { employeesApi } from './endpoints/employees';
import { leaveApi } from './endpoints/leave';
import { orgApi } from './endpoints/org';
import { workforceApi } from './endpoints/workforce';
import { calendarApi } from './endpoints/calendar';
import { notificationsApi } from './endpoints/notifications';
import { settingsApi } from './endpoints/settings';
import { adminApi } from './endpoints/admin';
import { agentsApi } from './endpoints/agents';
import { identityApi } from './endpoints/identity';
import { projectsApi } from './endpoints/wms/projects';
import { tasksApi } from './endpoints/wms/tasks';
import { plannerApi } from './endpoints/wms/planner';
import { goalsApi } from './endpoints/wms/goals';
import { docsApi } from './endpoints/wms/docs';
import { timeApi } from './endpoints/wms/time';
import { chatApi } from './endpoints/wms/chat';

export const api = {
  auth: authApi,
  employees: employeesApi,
  leave: leaveApi,
  org: orgApi,
  workforce: workforceApi,
  calendar: calendarApi,
  notifications: notificationsApi,
  settings: settingsApi,
  admin: adminApi,
  agents: agentsApi,
  identity: identityApi,
  wms: { projects: projectsApi, tasks: tasksApi, planner: plannerApi, goals: goalsApi, docs: docsApi, time: timeApi, chat: chatApi },
};
```

- [ ] **Create utility files**

```typescript
// src/lib/utils/to-params.ts
export function toParams(obj: Record<string, unknown>): string {
  const params = new URLSearchParams();
  Object.entries(obj).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') {
      params.set(k, String(v));
    }
  });
  return params.toString();
}
```

```typescript
// src/lib/utils/format-date.ts
import { format, formatDistanceToNow } from 'date-fns';

export const formatDate = (date: string | Date) =>
  format(new Date(date), 'dd MMM yyyy');

export const formatDateTime = (date: string | Date) =>
  format(new Date(date), 'dd MMM yyyy, HH:mm');

export const formatRelative = (date: string | Date) =>
  formatDistanceToNow(new Date(date), { addSuffix: true });
```

- [ ] **Commit**

```bash
git add src/lib/api/ src/lib/utils/
git commit -m "feat: add API client with interceptor chain + all endpoint stubs"
```

---

## Task 7: SignalR Client + i18n

**Files:** `src/lib/signalr/client.ts`, `src/lib/i18n.ts`

- [ ] **Create `src/lib/signalr/client.ts`**

```typescript
import { HubConnectionBuilder, LogLevel, type HubConnection } from '@microsoft/signalr';
import { tokenManager } from '@/lib/security/token-manager';

let _connection: HubConnection | null = null;

export const signalRClient = {
  async connect(tenantId: string): Promise<HubConnection> {
    const connection = new HubConnectionBuilder()
      .withUrl(`${import.meta.env.VITE_SIGNALR_URL}/hubs/main`, {
        accessTokenFactory: () => tokenManager.get() ?? '',
      })
      .withAutomaticReconnect({
        nextRetryDelayInMilliseconds: (ctx) => {
          const delays = [0, 2000, 5000, 10000, 30000];
          return delays[Math.min(ctx.previousRetryCount, delays.length - 1)];
        },
      })
      .configureLogging(LogLevel.Warning)
      .build();

    await connection.start();
    await connection.invoke('JoinTenantGroup', tenantId);
    _connection = connection;
    return connection;
  },

  get(): HubConnection | null {
    return _connection;
  },

  async disconnect(): Promise<void> {
    if (_connection) {
      await _connection.stop();
      _connection = null;
    }
  },
};
```

- [ ] **Create `src/lib/i18n.ts`**

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'ta', 'si'],
    ns: ['common', 'auth', 'employees', 'leave', 'workforce', 'org', 'settings'],
    defaultNS: 'common',
    backend: { loadPath: '/locales/{{lng}}/{{ns}}.json' },
    detection: { order: ['localStorage', 'navigator'], caches: ['localStorage'] },
    interpolation: { escapeValue: false },
  });

export default i18n;
```

- [ ] **Create base locale files**

```bash
mkdir -p public/locales/en
```

```json
// public/locales/en/common.json
{
  "save": "Save",
  "cancel": "Cancel",
  "delete": "Delete",
  "search": "Search...",
  "loading": "Loading...",
  "noResults": "No results found",
  "required": "Required",
  "error": "Something went wrong",
  "retry": "Try again"
}
```

- [ ] **Commit**

```bash
git add src/lib/signalr/ src/lib/i18n.ts public/locales/
git commit -m "feat: add SignalR client + i18n setup"
```

---

## Task 8: Provider Stack + Router

**Files:** `src/main.tsx`, `src/App.tsx`, `src/router.tsx`, all stub page files

- [ ] **Create stub page components** (empty placeholders — each dev fills in their own)

Create these files, each with the same stub pattern:

```typescript
// src/pages/dashboard/HomePage.tsx
export function HomePage() {
  return <div className="p-6"><h1 className="text-2xl font-semibold">Home</h1></div>;
}
```

Create identical stubs for every page listed in the File Map above. Naming follows `XxxPage.tsx` pattern.

- [ ] **Create `src/pages/errors/NotFoundPage.tsx`**

```tsx
import { Link } from 'react-router-dom';
export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-muted-foreground">Page not found</p>
      <Link to="/" className="text-brand underline">Go home</Link>
    </div>
  );
}
```

- [ ] **Create `src/pages/errors/ForbiddenPage.tsx`**

```tsx
export function ForbiddenPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <h1 className="text-4xl font-bold">403</h1>
      <p className="text-muted-foreground">You don't have permission to view this page</p>
    </div>
  );
}
```

- [ ] **Create `src/pages/errors/ErrorPage.tsx`**

```tsx
export function ErrorPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <h1 className="text-2xl font-bold">Something went wrong</h1>
      <button onClick={() => window.location.reload()} className="underline">Reload</button>
    </div>
  );
}
```

- [ ] **Create `src/pages/auth/AuthLayout.tsx`**

```tsx
import { Outlet } from 'react-router-dom';
export function AuthLayout() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-shell-bg)]">
      <div className="w-full max-w-[400px] p-8 bg-white dark:bg-[#17181F] rounded-[12px] border border-[var(--color-shell-border)] shadow-lg">
        <div className="mb-8 flex justify-center">
          <span className="text-2xl font-bold text-[var(--color-brand-primary)]">OneVo</span>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
```

- [ ] **Create `src/pages/auth/LoginPage.tsx`** (stub — Dev 2 implements)

```tsx
export function LoginPage() {
  return <div className="text-center text-muted-foreground">Login form — Dev 2 implements</div>;
}
```

Same pattern for `ForgotPasswordPage.tsx`, `ResetPasswordPage.tsx`, `MfaPage.tsx`.

- [ ] **Create `src/router.tsx`**

```tsx
import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/lib/security/permission-guard';
import { AuthLayout } from '@/pages/auth/AuthLayout';
import { DashboardLayout } from '@/pages/dashboard/DashboardLayout';
import { LoginPage } from '@/pages/auth/LoginPage';
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage';
import { ResetPasswordPage } from '@/pages/auth/ResetPasswordPage';
import { MfaPage } from '@/pages/auth/MfaPage';
import { HomePage } from '@/pages/dashboard/HomePage';
import { NotFoundPage } from '@/pages/errors/NotFoundPage';
import { ForbiddenPage } from '@/pages/errors/ForbiddenPage';

// Lazy-loaded heavy pages
const ProjectBoardPage    = lazy(() => import('@/pages/dashboard/workforce/projects/ProjectBoardPage').then(m => ({ default: m.ProjectBoardPage })));
const ProjectRoadmapPage  = lazy(() => import('@/pages/dashboard/workforce/projects/ProjectRoadmapPage').then(m => ({ default: m.ProjectRoadmapPage })));
const OrgPage             = lazy(() => import('@/pages/dashboard/org/OrgPage').then(m => ({ default: m.OrgPage })));
const WorkforceAnalyticsPage = lazy(() => import('@/pages/dashboard/workforce/WorkforceAnalyticsPage').then(m => ({ default: m.WorkforceAnalyticsPage })));

const P = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<div className="flex items-center justify-center h-full">Loading...</div>}>
    {children}
  </Suspense>
);

export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      { path: '/login',            element: <LoginPage /> },
      { path: '/forgot-password',  element: <ForgotPasswordPage /> },
      { path: '/reset-password',   element: <ResetPasswordPage /> },
      { path: '/mfa',              element: <MfaPage /> },
    ],
  },
  {
    element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
    children: [
      { index: true, element: <HomePage /> },
      { path: '/people/employees',      element: <ProtectedRoute permission="employees:read"><P><div>Employees — Dev 1 Task 2</div></P></ProtectedRoute> },
      { path: '/people/employees/new',  element: <ProtectedRoute permission="employees:write"><P><div>New Employee</div></P></ProtectedRoute> },
      { path: '/people/employees/:id',  element: <ProtectedRoute permission="employees:read"><P><div>Employee Detail</div></P></ProtectedRoute> },
      { path: '/people/leave',          element: <ProtectedRoute permission="leave:read"><P><div>Leave</div></P></ProtectedRoute> },
      { path: '/people/leave/calendar', element: <ProtectedRoute permission="leave:read"><P><div>Leave Calendar</div></P></ProtectedRoute> },
      { path: '/people/leave/balances', element: <ProtectedRoute permission="leave:read"><P><div>Leave Balances</div></P></ProtectedRoute> },
      { path: '/people/leave/policies', element: <ProtectedRoute permission="leave:manage"><P><div>Leave Policies</div></P></ProtectedRoute> },
      { path: '/workforce',             element: <ProtectedRoute permission="workforce:read"><P><div>Workforce</div></P></ProtectedRoute> },
      { path: '/workforce/:employeeId', element: <ProtectedRoute permission="workforce:read"><P><div>Employee Activity</div></P></ProtectedRoute> },
      { path: '/workforce/analytics',   element: <ProtectedRoute permission="analytics:read"><P><WorkforceAnalyticsPage /></P></ProtectedRoute> },
      { path: '/workforce/projects',         element: <ProtectedRoute permission="projects:read"><P><div>Projects</div></P></ProtectedRoute> },
      { path: '/workforce/projects/new',     element: <ProtectedRoute permission="projects:write"><P><div>New Project</div></P></ProtectedRoute> },
      { path: '/workforce/projects/:id',         element: <ProtectedRoute permission="projects:read"><P><div>Project</div></P></ProtectedRoute> },
      { path: '/workforce/projects/:id/board',   element: <ProtectedRoute permission="tasks:read"><P><ProjectBoardPage /></P></ProtectedRoute> },
      { path: '/workforce/projects/:id/sprints', element: <ProtectedRoute permission="planning:read"><P><div>Sprints</div></P></ProtectedRoute> },
      { path: '/workforce/projects/:id/roadmap', element: <ProtectedRoute permission="planning:read"><P><ProjectRoadmapPage /></P></ProtectedRoute> },
      { path: '/workforce/my-work',  element: <ProtectedRoute permission="tasks:read"><P><div>My Work</div></P></ProtectedRoute> },
      { path: '/workforce/planner',  element: <ProtectedRoute permission="planning:read"><P><div>Planner</div></P></ProtectedRoute> },
      { path: '/workforce/goals',    element: <ProtectedRoute permission="goals:read"><P><div>Goals</div></P></ProtectedRoute> },
      { path: '/workforce/goals/:id',element: <ProtectedRoute permission="goals:read"><P><div>Goal</div></P></ProtectedRoute> },
      { path: '/workforce/docs',     element: <ProtectedRoute permission="docs:read"><P><div>Docs</div></P></ProtectedRoute> },
      { path: '/workforce/docs/:id', element: <ProtectedRoute permission="docs:read"><P><div>Doc</div></P></ProtectedRoute> },
      { path: '/workforce/time',         element: <ProtectedRoute permission="time:read"><P><div>Time</div></P></ProtectedRoute> },
      { path: '/workforce/time/reports', element: <ProtectedRoute permission="time:read"><P><div>Time Reports</div></P></ProtectedRoute> },
      { path: '/chat',               element: <ProtectedRoute permission="chat:read"><P><div>Chat</div></P></ProtectedRoute> },
      { path: '/inbox',              element: <P><div>Inbox</div></P> },
      { path: '/org',                element: <ProtectedRoute permission="org:read"><P><OrgPage /></P></ProtectedRoute> },
      { path: '/org/departments',    element: <ProtectedRoute permission="org:read"><P><div>Departments</div></P></ProtectedRoute> },
      { path: '/org/teams',          element: <ProtectedRoute permission="org:read"><P><div>Teams</div></P></ProtectedRoute> },
      { path: '/org/job-families',   element: <ProtectedRoute permission="org:manage"><P><div>Job Families</div></P></ProtectedRoute> },
      { path: '/org/job-families/:id',    element: <ProtectedRoute permission="org:manage"><P><div>Job Family</div></P></ProtectedRoute> },
      { path: '/org/legal-entities',      element: <ProtectedRoute permission="org:manage"><P><div>Legal Entities</div></P></ProtectedRoute> },
      { path: '/org/legal-entities/:id',  element: <ProtectedRoute permission="org:manage"><P><div>Legal Entity</div></P></ProtectedRoute> },
      { path: '/calendar',            element: <ProtectedRoute permission="calendar:read"><P><div>Calendar</div></P></ProtectedRoute> },
      { path: '/calendar/schedule',   element: <ProtectedRoute permission="schedule:read"><P><div>Schedule</div></P></ProtectedRoute> },
      { path: '/calendar/attendance', element: <ProtectedRoute permission="attendance:read"><P><div>Attendance</div></P></ProtectedRoute> },
      { path: '/calendar/overtime',   element: <ProtectedRoute permission="overtime:read"><P><div>Overtime</div></P></ProtectedRoute> },
      { path: '/notifications',             element: <P><div>Notifications</div></P> },
      { path: '/notifications/preferences', element: <P><div>Notification Preferences</div></P> },
      { path: '/admin/users',      element: <ProtectedRoute permission="admin:users"><P><div>Users</div></P></ProtectedRoute> },
      { path: '/admin/roles',      element: <ProtectedRoute permission="admin:roles"><P><div>Roles</div></P></ProtectedRoute> },
      { path: '/admin/audit',      element: <ProtectedRoute permission="admin:audit"><P><div>Audit</div></P></ProtectedRoute> },
      { path: '/admin/agents',     element: <ProtectedRoute permission="admin:agents"><P><div>Agents</div></P></ProtectedRoute> },
      { path: '/admin/agents/:id', element: <ProtectedRoute permission="admin:agents"><P><div>Agent</div></P></ProtectedRoute> },
      { path: '/admin/devices',    element: <ProtectedRoute permission="admin:devices"><P><div>Devices</div></P></ProtectedRoute> },
      { path: '/admin/compliance', element: <ProtectedRoute permission="admin:compliance"><P><div>Compliance</div></P></ProtectedRoute> },
      { path: '/settings/general',       element: <ProtectedRoute permission="settings:read"><P><div>General</div></P></ProtectedRoute> },
      { path: '/settings/system',        element: <ProtectedRoute permission="settings:system"><P><div>System</div></P></ProtectedRoute> },
      { path: '/settings/notifications', element: <ProtectedRoute permission="settings:notifications"><P><div>Notifications Settings</div></P></ProtectedRoute> },
      { path: '/settings/integrations',  element: <ProtectedRoute permission="settings:integrations"><P><div>Integrations</div></P></ProtectedRoute> },
      { path: '/settings/branding',      element: <ProtectedRoute permission="settings:branding"><P><div>Branding</div></P></ProtectedRoute> },
      { path: '/settings/billing',       element: <ProtectedRoute permission="settings:billing"><P><div>Billing</div></P></ProtectedRoute> },
      { path: '/settings/alert-rules',   element: <ProtectedRoute permission="settings:alerts"><P><div>Alerts</div></P></ProtectedRoute> },
    ],
  },
  { path: '/403', element: <ForbiddenPage /> },
  { path: '*',    element: <NotFoundPage /> },
]);
```

- [ ] **Create `src/App.tsx`**

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { RouterProvider } from 'react-router-dom';
import { Toaster } from 'sonner';
import { router } from './router';
import { AuthError } from '@/lib/api/errors';
import './lib/i18n';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (count, error) => !(error instanceof AuthError) && count < 3,
      staleTime: 30_000,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster position="bottom-right" richColors />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

- [ ] **Create `src/main.tsx`**

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './styles/globals.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

- [ ] **Verify app loads at localhost:5173 with no console errors**

```bash
npm run dev
```

Expected: App renders, navigating to `/login` shows AuthLayout with "Login form — Dev 2 implements". No TypeScript or runtime errors.

- [ ] **Commit**

```bash
git add src/main.tsx src/App.tsx src/router.tsx src/pages/
git commit -m "feat: add provider stack, router with all routes, page stubs"
```

---

## Task 9: Shell Layout (NavRail + ExpansionPanel + Topbar + DashboardLayout)

**Files:** `src/pages/dashboard/DashboardLayout.tsx`, `src/components/layout/NavRail.tsx`, `src/components/layout/ExpansionPanel.tsx`, `src/components/layout/Topbar.tsx`, `src/components/layout/EntitySwitcher.tsx`, `src/components/layout/Breadcrumb.tsx`

Reference: `frontend/design-system/components/shell-layout.md`, `frontend/design-system/components/nav-rail.md`, `frontend/design-system/components/expansion-panel.md`, `frontend/architecture/topbar.md`, `frontend/architecture/sidebar-nav.md`

- [ ] **Create `src/pages/dashboard/DashboardLayout.tsx`**

```tsx
import { Outlet } from 'react-router-dom';
import { NavRail } from '@/components/layout/NavRail';
import { ExpansionPanel } from '@/components/layout/ExpansionPanel';
import { Topbar } from '@/components/layout/Topbar';
import { useSidebarStore } from '@/stores/use-sidebar-store';

export function DashboardLayout() {
  const { isExpanded } = useSidebarStore();

  return (
    // Floating-cards layout: 8px body padding, 6px gaps
    <div className="flex flex-col h-screen bg-[var(--color-shell-bg)] p-2 gap-1.5 overflow-hidden">
      {/* Topbar — full width, 40px */}
      <Topbar />

      {/* Bottom row: rail + optional panel + main content */}
      <div className="flex flex-1 gap-1.5 min-h-0">
        {/* Icon Rail — 52px */}
        <NavRail />

        {/* Expansion Panel — 210px, animated */}
        {isExpanded && <ExpansionPanel />}

        {/* Main content area */}
        <main className="flex-1 overflow-auto rounded-[10px] bg-white dark:bg-[#17181F] p-4 min-h-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Create `src/components/layout/NavRail.tsx`**

Reference `frontend/design-system/components/nav-rail.md` for exact icon names, dimensions, and permission keys from `frontend/architecture/sidebar-nav.md`.

```tsx
import { useLocation } from 'react-router-dom';
import {
  House, Inbox, Users, LayoutDashboard, Network,
  Calendar, MessageCircle, Shield, Settings,
} from 'lucide-react';
import { useSidebarStore } from '@/stores/use-sidebar-store';
import { useAuthStore } from '@/stores/use-auth-store';
import { cn } from '@/lib/utils/cn';

const PILLARS = [
  { id: 'home',      icon: House,            route: '/',              permission: null,              hasPanel: false },
  { id: 'inbox',     icon: Inbox,            route: '/inbox',         permission: null,              hasPanel: false },
  { id: 'people',    icon: Users,            route: '/people/employees', permission: 'employees:read', hasPanel: true },
  { id: 'workforce', icon: LayoutDashboard,  route: '/workforce',     permission: 'workforce:read',  hasPanel: true },
  { id: 'org',       icon: Network,          route: '/org',           permission: 'org:read',        hasPanel: true },
  { id: 'calendar',  icon: Calendar,         route: '/calendar',      permission: 'calendar:read',   hasPanel: true },
  { id: 'chat',      icon: MessageCircle,    route: '/chat',          permission: 'chat:read',       hasPanel: false },
] as const;

const ADMIN_PILLARS = [
  { id: 'admin',    icon: Shield,   route: '/admin/users',    permission: 'admin:read',    hasPanel: true },
  { id: 'settings', icon: Settings, route: '/settings/general', permission: 'settings:read', hasPanel: true },
] as const;

export function NavRail() {
  const { pathname } = useLocation();
  const { activePillar, setActivePillar, collapse } = useSidebarStore();
  const { hasPermission } = useAuthStore();

  const activePath = pathname.split('/')[1] || 'home';

  function handlePillarClick(pillar: typeof PILLARS[number] | typeof ADMIN_PILLARS[number]) {
    if (!pillar.hasPanel) {
      collapse();
      return;
    }
    if (activePillar === pillar.id) {
      collapse();
    } else {
      setActivePillar(pillar.id);
    }
  }

  function RailItem({ pillar }: { pillar: typeof PILLARS[number] | typeof ADMIN_PILLARS[number] }) {
    if (pillar.permission && !hasPermission(pillar.permission)) return null;
    const isActive = activePath === pillar.id || (pillar.id === 'home' && activePath === '');
    const Icon = pillar.icon;

    return (
      <button
        onClick={() => handlePillarClick(pillar)}
        className={cn(
          'w-8 h-8 rounded-[8px] flex items-center justify-center transition-colors duration-150 border-none cursor-pointer',
          isActive
            ? 'bg-[var(--color-brand-primary)] text-white'
            : 'text-white/40 hover:bg-white/[0.08] hover:text-white/80'
        )}
        title={pillar.id.charAt(0).toUpperCase() + pillar.id.slice(1)}
      >
        <Icon size={16} strokeWidth={1.75} aria-hidden="true" />
      </button>
    );
  }

  return (
    // 52px wide, dark floating card
    <nav
      className="w-[52px] shrink-0 flex flex-col items-center py-3 gap-1 rounded-[12px] bg-[#17181F]"
      aria-label="Main navigation"
    >
      {PILLARS.map(p => <RailItem key={p.id} pillar={p} />)}

      {/* Separator before Admin */}
      <div className="w-6 h-px bg-white/[0.08] my-1" />

      {ADMIN_PILLARS.map(p => <RailItem key={p.id} pillar={p} />)}
    </nav>
  );
}
```

- [ ] **Create `src/components/layout/ExpansionPanel.tsx`**

Reference `frontend/design-system/components/expansion-panel.md` and `frontend/architecture/sidebar-nav.md` for exact panel items per pillar.

```tsx
import { Link, useLocation } from 'react-router-dom';
import { useSidebarStore } from '@/stores/use-sidebar-store';
import { useAuthStore } from '@/stores/use-auth-store';
import { cn } from '@/lib/utils/cn';

const PANEL_ITEMS: Record<string, { label: string; route: string; permission: string | null }[]> = {
  people: [
    { label: 'Employees', route: '/people/employees', permission: 'employees:read' },
    { label: 'Leave',     route: '/people/leave',     permission: 'leave:read' },
  ],
  workforce: [
    { label: 'Presence',   route: '/workforce',            permission: 'workforce:read' },
    { label: 'Projects',   route: '/workforce/projects',   permission: 'projects:read' },
    { label: 'My Work',    route: '/workforce/my-work',    permission: 'tasks:read' },
    { label: 'Planner',    route: '/workforce/planner',    permission: 'planning:read' },
    { label: 'Goals',      route: '/workforce/goals',      permission: 'goals:read' },
    { label: 'Docs',       route: '/workforce/docs',       permission: 'docs:read' },
    { label: 'Timesheets', route: '/workforce/time',       permission: 'time:read' },
    { label: 'Analytics',  route: '/workforce/analytics',  permission: 'analytics:read' },
  ],
  org: [
    { label: 'Org Chart',      route: '/org',                    permission: 'org:read' },
    { label: 'Departments',    route: '/org/departments',         permission: 'org:read' },
    { label: 'Teams',          route: '/org/teams',               permission: 'org:read' },
    { label: 'Job Families',   route: '/org/job-families',        permission: 'org:manage' },
    { label: 'Legal Entities', route: '/org/legal-entities',      permission: 'org:manage' },
  ],
  calendar: [
    { label: 'Calendar',    route: '/calendar',            permission: 'calendar:read' },
    { label: 'Schedules',   route: '/calendar/schedule',   permission: 'schedule:read' },
    { label: 'Attendance',  route: '/calendar/attendance', permission: 'attendance:read' },
    { label: 'Overtime',    route: '/calendar/overtime',   permission: 'overtime:read' },
  ],
  admin: [
    { label: 'People Access', route: '/admin/users',      permission: 'admin:users' },
    { label: 'Permissions',   route: '/admin/roles',      permission: 'admin:roles' },
    { label: 'Activity Trail',route: '/admin/audit',      permission: 'admin:audit' },
    { label: 'Agents',        route: '/admin/agents',     permission: 'admin:agents' },
    { label: 'Devices',       route: '/admin/devices',    permission: 'admin:devices' },
    { label: 'Data & Privacy',route: '/admin/compliance', permission: 'admin:compliance' },
  ],
  settings: [
    { label: 'General',       route: '/settings/general',       permission: 'settings:read' },
    { label: 'Alerts',        route: '/settings/alert-rules',   permission: 'settings:alerts' },
    { label: 'Notifications', route: '/settings/notifications', permission: 'settings:notifications' },
    { label: 'Integrations',  route: '/settings/integrations',  permission: 'settings:integrations' },
    { label: 'Branding',      route: '/settings/branding',      permission: 'settings:branding' },
    { label: 'Billing',       route: '/settings/billing',       permission: 'settings:billing' },
    { label: 'System',        route: '/settings/system',        permission: 'settings:system' },
  ],
};

export function ExpansionPanel() {
  const { activePillar } = useSidebarStore();
  const { pathname } = useLocation();
  const { hasPermission } = useAuthStore();

  const items = activePillar ? PANEL_ITEMS[activePillar] ?? [] : [];

  return (
    // 210px wide, animated opacity+width
    <div className="w-[210px] shrink-0 rounded-[12px] bg-white dark:bg-[#17181F] border border-[var(--color-shell-border)] py-3 overflow-hidden">
      <nav className="flex flex-col gap-0.5 px-2">
        {items
          .filter(item => !item.permission || hasPermission(item.permission))
          .map(item => (
            <Link
              key={item.route}
              to={item.route}
              className={cn(
                'flex items-center px-3 py-2 rounded-[7px] text-[13px] font-medium transition-colors duration-100 no-underline',
                pathname === item.route || pathname.startsWith(item.route + '/')
                  ? 'bg-[var(--color-brand-primary)]/10 text-[var(--color-brand-primary)]'
                  : 'text-[var(--color-text-secondary)] hover:bg-[#F4F5F8] dark:hover:bg-white/[0.06] hover:text-[var(--color-text-primary)]'
              )}
            >
              {item.label}
            </Link>
          ))
        }
      </nav>
    </div>
  );
}
```

- [ ] **Create `src/components/layout/Topbar.tsx`** (pixel-precise per `frontend/architecture/topbar.md`)

```tsx
import { Bell, CircleHelp, Moon, Sun, ChevronDown, Search } from 'lucide-react';
import { useAuthStore } from '@/stores/use-auth-store';
import { useThemeStore } from '@/stores/use-theme-store';
import { Breadcrumb } from './Breadcrumb';
import { EntitySwitcher } from './EntitySwitcher';

export function Topbar() {
  const { user } = useAuthStore();
  const { theme, setTheme } = useThemeStore();

  const initials = user
    ? (user.fullName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase())
    : '??';

  function toggleTheme() {
    setTheme(theme === 'dark' ? 'light' : theme === 'light' ? 'system' : 'dark');
  }

  return (
    <header className="h-10 shrink-0 bg-white dark:bg-[#17181F] rounded-[10px] border border-[#E2E3EA] dark:border-white/[0.06] shadow-[0_1px_3px_rgba(0,0,0,0.06)] dark:shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex items-center px-[10px] gap-2">

      {/* Left: entity + breadcrumb */}
      <div className="flex items-center gap-1 shrink-0">
        <EntitySwitcher />
        <Breadcrumb />
      </div>

      {/* Center: search */}
      <div className="flex-1 max-w-[280px] mx-auto flex items-center gap-[7px] bg-[#F4F5F8] dark:bg-white/[0.07] border border-[#E2E3EA] dark:border-white/[0.07] rounded-[11px] px-[10px] py-1 hover:border-[#C8CADC] cursor-pointer">
        <Search size={13} strokeWidth={1.75} className="text-[#9499B0] dark:text-white/[0.22] shrink-0" aria-hidden="true" />
        <span className="text-[12px] text-[#9499B0] dark:text-white/[0.22]">Search…</span>
        <kbd className="ml-auto text-[10px] font-mono text-[#C8CADC] dark:text-white/[0.15]">⌘K</kbd>
      </div>

      {/* Right: actions */}
      <div className="flex items-center gap-px ml-auto">
        {[Bell, CircleHelp].map((Icon, i) => (
          <button
            key={i}
            className="w-7 h-7 rounded-[6px] flex items-center justify-center text-[#6B7194] dark:text-white/[0.30] hover:bg-[#F4F5F8] dark:hover:bg-white/[0.07] hover:text-[#1E2140] dark:hover:text-white/[0.70] transition-[background,color] duration-[120ms] border-none cursor-pointer bg-transparent"
          >
            <Icon size={14} strokeWidth={1.75} aria-hidden="true" />
          </button>
        ))}

        <button
          onClick={toggleTheme}
          className="w-7 h-7 rounded-[6px] flex items-center justify-center text-[#6B7194] dark:text-white/[0.30] hover:bg-[#F4F5F8] dark:hover:bg-white/[0.07] hover:text-[#1E2140] dark:hover:text-white/[0.70] transition-[background,color] duration-[120ms] border-none cursor-pointer bg-transparent"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Moon size={14} strokeWidth={1.75} aria-hidden="true" /> : <Sun size={14} strokeWidth={1.75} aria-hidden="true" />}
        </button>

        <div className="w-px h-4 bg-[#E2E3EA] dark:bg-white/[0.08] mx-[3px]" />

        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[#5B4FE8] to-[#8C86F2] flex items-center justify-center text-[9px] font-bold text-white cursor-pointer ml-[3px] select-none">
          {initials}
        </div>
      </div>
    </header>
  );
}
```

- [ ] **Create `src/components/layout/EntitySwitcher.tsx`** (stub — Dev 3 fills in entity list)

```tsx
import { ChevronDown } from 'lucide-react';
import { useAuthStore } from '@/stores/use-auth-store';

export function EntitySwitcher() {
  const { user } = useAuthStore();
  // TODO: Dev 3 Task 1 wires up entity list from org API
  return (
    <div className="flex items-center gap-1.5 px-[7px] py-[3px] rounded-[7px] cursor-pointer hover:bg-[#F4F5F8] dark:hover:bg-white/[0.07] shrink-0">
      <span className="text-[12px] font-semibold text-[#1E2140] dark:text-white/[0.82] whitespace-nowrap max-w-[180px] truncate">
        {user?.activeEntityId ?? 'Loading…'}
      </span>
      <ChevronDown size={11} strokeWidth={2} className="text-[#9499B0] dark:text-white/[0.28]" aria-hidden="true" />
    </div>
  );
}
```

- [ ] **Create `src/components/layout/Breadcrumb.tsx`**

```tsx
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils/cn';

const LABELS: Record<string, string> = {
  people: 'People', employees: 'Employees', leave: 'Leave',
  workforce: 'Workforce', projects: 'Projects', 'my-work': 'My Work',
  planner: 'Planner', goals: 'Goals', docs: 'Docs', time: 'Timesheets',
  analytics: 'Analytics', chat: 'Chat', inbox: 'Inbox',
  org: 'Organization', departments: 'Departments', teams: 'Teams',
  'job-families': 'Job Families', 'legal-entities': 'Legal Entities',
  calendar: 'Calendar', schedule: 'Schedules', attendance: 'Attendance', overtime: 'Overtime',
  notifications: 'Notifications', preferences: 'Preferences',
  admin: 'Admin', users: 'People Access', roles: 'Permissions',
  audit: 'Activity Trail', agents: 'Agents', devices: 'Devices', compliance: 'Data & Privacy',
  settings: 'Settings', general: 'General', system: 'System', integrations: 'Integrations',
  branding: 'Branding', billing: 'Billing', 'alert-rules': 'Alerts',
};

export function Breadcrumb() {
  const { pathname } = useLocation();
  const segments = pathname.split('/').filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <div className="flex items-center gap-[3px] shrink-0">
      {segments.map((seg, i) => {
        const isCurrent = i === segments.length - 1;
        const href = '/' + segments.slice(0, i + 1).join('/');
        const label = LABELS[seg] ?? seg;

        return (
          <span key={href} className="flex items-center gap-[3px]">
            <span className="text-[14px] text-[#C8CADC] dark:text-white/[0.15]">/</span>
            {isCurrent ? (
              <span className="text-[12px] font-semibold text-[#1E2140] dark:text-white/[0.85] px-[5px] py-[2px] whitespace-nowrap">
                {label}
              </span>
            ) : (
              <Link
                to={href}
                className="text-[12px] font-medium text-[#9499B0] dark:text-white/[0.35] px-[5px] py-[2px] rounded-[5px] hover:text-[#1E2140] hover:bg-[#F4F5F8] dark:hover:text-white/[0.70] dark:hover:bg-white/[0.06] whitespace-nowrap no-underline"
              >
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </div>
  );
}
```

- [ ] **Smoke test shell layout**

```bash
npm run dev
```

Open `http://localhost:5173`. Expected:
- 40px topbar with "Search…" bar and avatar initials
- 52px dark NavRail on the left
- Main content area renders "Home"
- Clicking a rail pillar shows the ExpansionPanel
- Clicking a panel item navigates and updates breadcrumb
- No console errors

- [ ] **Commit**

```bash
git add src/pages/dashboard/DashboardLayout.tsx src/components/layout/
git commit -m "feat: add shell layout (NavRail, ExpansionPanel, Topbar, Breadcrumb)"
```

---

## Task 10: Shared Components

**Files:** `src/components/shared/` (DataTable, PageHeader, StatusBadge, PermissionGate, EmptyState, TableSkeleton, ErrorState, Avatar)

- [ ] **Create `src/components/shared/PermissionGate.tsx`**

```tsx
import type { ReactNode } from 'react';
import { useAuthStore } from '@/stores/use-auth-store';

interface Props {
  permission: string;
  fallback?: ReactNode;
  children: ReactNode;
}

export function PermissionGate({ permission, fallback = null, children }: Props) {
  const { hasPermission } = useAuthStore();
  return hasPermission(permission) ? <>{children}</> : <>{fallback}</>;
}
```

- [ ] **Create `src/components/shared/TableSkeleton.tsx`**

```tsx
import { Skeleton } from '@/components/ui/skeleton';

export function TableSkeleton({ rows = 10, columns = 5 }: { rows?: number; columns?: number }) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex gap-4 pb-2 border-b border-[var(--color-shell-border)]">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex gap-4">
          {Array.from({ length: columns }).map((_, c) => (
            <Skeleton key={c} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Create `src/components/shared/EmptyState.tsx`**

```tsx
interface Props {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
      <p className="text-[15px] font-medium text-[var(--color-text-primary)]">{title}</p>
      {description && <p className="text-[13px] text-[var(--color-text-muted)] max-w-sm">{description}</p>}
      {action}
    </div>
  );
}
```

- [ ] **Create `src/components/shared/ErrorState.tsx`**

```tsx
import { Button } from '@/components/ui/button';

interface Props {
  message?: string;
  retry?: () => void;
}

export function ErrorState({ message = 'Failed to load data', retry }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3">
      <p className="text-[13px] text-[var(--color-error)]">{message}</p>
      {retry && <Button variant="outline" size="sm" onClick={retry}>Try again</Button>}
    </div>
  );
}
```

- [ ] **Create `src/components/shared/StatusBadge.tsx`**

```tsx
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils/cn';

type Status = 'active' | 'inactive' | 'pending' | 'on_leave' | 'terminated' | 'approved' | 'rejected' | 'cancelled';

const STATUS_STYLES: Record<Status, string> = {
  active:     'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  approved:   'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  inactive:   'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
  pending:    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  on_leave:   'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  terminated: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  rejected:   'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  cancelled:  'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
};

const STATUS_LABELS: Record<Status, string> = {
  active: 'Active', inactive: 'Inactive', pending: 'Pending', on_leave: 'On Leave',
  terminated: 'Terminated', approved: 'Approved', rejected: 'Rejected', cancelled: 'Cancelled',
};

export function StatusBadge({ status }: { status: Status }) {
  return (
    <Badge variant="outline" className={cn('text-[11px] font-medium border-0', STATUS_STYLES[status])}>
      {STATUS_LABELS[status]}
    </Badge>
  );
}
```

- [ ] **Create `src/components/shared/Avatar.tsx`**

```tsx
import { cn } from '@/lib/utils/cn';

interface Props {
  src?: string | null;
  name: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const SIZES = { sm: 'w-6 h-6 text-[9px]', md: 'w-8 h-8 text-[11px]', lg: 'w-10 h-10 text-[13px]' };

export function Avatar({ src, name, size = 'md', className }: Props) {
  const initials = name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();

  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className={cn('rounded-full object-cover', SIZES[size], className)}
      />
    );
  }

  return (
    <div className={cn(
      'rounded-full bg-gradient-to-br from-[#5B4FE8] to-[#8C86F2] flex items-center justify-center font-bold text-white select-none',
      SIZES[size],
      className
    )}>
      {initials}
    </div>
  );
}
```

- [ ] **Create `src/components/shared/PageHeader.tsx`**

```tsx
import type { ReactNode } from 'react';

interface Props {
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, description, actions }: Props) {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-[20px] font-semibold text-[var(--color-text-primary)]">{title}</h1>
        {description && (
          <p className="text-[13px] text-[var(--color-text-muted)] mt-0.5">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}
```

- [ ] **Create `src/components/shared/DataTable.tsx`** (generic, TanStack Table wrapper)

```tsx
import { useState } from 'react';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
  type PaginationState,
} from '@tanstack/react-table';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils/cn';

interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  isLoading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  className?: string;
}

export function DataTable<T>({ data, columns, isLoading, hasMore, onLoadMore, className }: DataTableProps<T>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
  });

  return (
    <div className={cn('space-y-3', className)}>
      <div className="overflow-x-auto rounded-[8px] border border-[var(--color-shell-border)]">
        <table className="w-full text-[13px]">
          <thead>
            {table.getHeaderGroups().map(hg => (
              <tr key={hg.id} className="border-b border-[var(--color-shell-border)] bg-[#F8F9FC] dark:bg-white/[0.03]">
                {hg.headers.map(header => (
                  <th
                    key={header.id}
                    className="text-left px-3 py-2.5 text-[12px] font-medium text-[var(--color-text-muted)] whitespace-nowrap"
                  >
                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map(row => (
              <tr
                key={row.id}
                className="border-b border-[var(--color-shell-border)] last:border-0 hover:bg-[#F8F9FC] dark:hover:bg-white/[0.02] transition-colors"
              >
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-3 py-2.5 text-[var(--color-text-primary)]">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {hasMore && onLoadMore && (
        <div className="flex justify-center pt-2">
          <Button variant="outline" size="sm" onClick={onLoadMore} disabled={isLoading}>
            {isLoading ? 'Loading…' : 'Load more'}
          </Button>
        </div>
      )}
    </div>
  );
}
```

Install TanStack Table:
```bash
npm install @tanstack/react-table
```

- [ ] **Run all tests**

```bash
npx vitest run
```

Expected: All tests pass (token-manager tests + any others added).

- [ ] **Final smoke test — verify full shell renders**

```bash
npm run dev
```

Expected: Dashboard layout renders with nav rail, expansion panel, topbar with correct pixel specs from `frontend/architecture/topbar.md`. No TypeScript errors. All routes accessible (show stubs).

- [ ] **Commit**

```bash
git add src/components/shared/ src/hooks/
git commit -m "feat: add shared components (DataTable, PageHeader, StatusBadge, PermissionGate, EmptyState, TableSkeleton, ErrorState, Avatar)"
```

---

## Task 11: Shared Hooks + Final TypeScript Check

**Files:** `src/hooks/shared/use-debounce.ts`, `src/hooks/shared/use-permissions.ts`

- [ ] **Create `src/hooks/shared/use-debounce.ts`**

```typescript
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delayMs = 300): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}
```

- [ ] **Create `src/hooks/shared/use-permissions.ts`**

```typescript
import { useAuthStore } from '@/stores/use-auth-store';

export function usePermissions() {
  const { hasPermission, hasFeature, permissions } = useAuthStore();
  return { hasPermission, hasFeature, permissions };
}
```

- [ ] **Create base type files** (stubs — each dev fills their own)

```typescript
// src/types/auth.ts
export interface User {
  id: string;
  email: string;
  fullName: string;
  avatarUrl: string | null;
  tenantId: string;
  activeEntityId: string;
}

export interface AuthSession {
  user: User;
  permissions: string[];
  features: string[];
  accessToken: string;
  expiresIn: number;
}
```

```typescript
// src/types/core-hr.ts — stub, Dev 1 Task 2 fills this in
export interface Employee {
  id: string;
  employeeNumber: string;
  firstName: string;
  lastName: string;
  email: string;
  departmentId: string;
  jobTitleId: string;
  status: 'active' | 'inactive' | 'on_leave' | 'terminated';
  startDate: string;
  avatarUrl: string | null;
  managerId: string | null;
  tenantId: string;
}

export interface EmployeeFilters {
  search?: string;
  departmentId?: string;
  status?: string;
  cursor?: string;
}
```

Create stub `export interface` files for: `org.ts`, `workforce.ts`, `notifications.ts`, `settings.ts`, `admin.ts`, `wms/projects.ts`, `wms/tasks.ts`, `wms/goals.ts`, `wms/chat.ts`.

- [ ] **Full TypeScript check**

```bash
npx tsc --noEmit
```

Expected: Zero errors.

- [ ] **Full test run**

```bash
npx vitest run
```

Expected: All tests pass.

- [ ] **Final commit**

```bash
git add src/hooks/ src/types/
git commit -m "feat: complete Vite foundation — all shared hooks, types, and TypeScript clean"
```

---

## Handoff Checklist

Before marking this task complete and unblocking other devs, verify:

- [ ] `npm run dev` starts with no console errors
- [ ] Navigating to `/login` shows centered AuthLayout card
- [ ] Navigating to `/people/employees` redirects to `/login` (ProtectedRoute works)
- [ ] After manually setting a mock user in useAuthStore devtools, dashboard shell renders
- [ ] NavRail, ExpansionPanel, Topbar all visible with correct pixel dimensions
- [ ] `npx tsc --noEmit` — zero errors
- [ ] `npx vitest run` — all tests pass
- [ ] `VITE_API_URL` is in `.env.local` (real or mock value)
- [ ] All 18 endpoint files exist in `src/lib/api/endpoints/`
- [ ] All page stubs exist (no 404s on direct URL navigation except genuinely missing routes)
- [ ] Commit history is clean — one commit per task above

**Signal to team:** Push branch to remote. Other 7 devs pull and run `npm install && npm run dev` to verify foundation works before starting their tasks.
