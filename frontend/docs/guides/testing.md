# Frontend Testing Strategy

## Test Stack

| Tool | Purpose | Runs In |
|:-----|:--------|:--------|
| Vitest | Unit tests (hooks, utils, pure logic) | Node |
| React Testing Library | Component behavior tests | jsdom |
| MSW (Mock Service Worker) | API mocking for component + integration tests | jsdom / browser |
| Playwright | E2E tests (critical user flows) | Real browser |

## Test File Location

Tests live next to the code they test:

```
src/
├── hooks/
│   ├── use-employees.ts
│   └── use-employees.test.ts          # Unit test
├── components/
│   ├── workforce/
│   │   ├── live-dashboard.tsx
│   │   └── live-dashboard.test.tsx     # Component test
├── lib/
│   ├── utils/
│   │   ├── format-date.ts
│   │   └── format-date.test.ts         # Unit test
e2e/
├── leave-request.spec.ts              # E2E test
├── exception-management.spec.ts       # E2E test
└── login.spec.ts                      # E2E test
```

## Unit Tests (Vitest)

For hooks, utilities, and pure functions.

```tsx
// use-employees.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useEmployees } from './use-employees';
import { createWrapper } from '@/test/utils'; // provides QueryClientProvider

describe('useEmployees', () => {
  it('fetches employees with filters', async () => {
    const { result } = renderHook(
      () => useEmployees({ department: 'engineering' }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(5);
  });
});
```

```tsx
// format-date.test.ts
import { formatDate, formatRelativeTime } from './format-date';

describe('formatDate', () => {
  it('formats ISO date to display format', () => {
    expect(formatDate('2026-04-06T10:30:00Z')).toBe('Apr 6, 2026');
  });
});

describe('formatRelativeTime', () => {
  it('shows minutes ago for recent times', () => {
    const fiveMinAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString();
    expect(formatRelativeTime(fiveMinAgo)).toBe('5 min ago');
  });
});
```

## Component Tests (RTL)

Test behavior, not implementation. Never test internal state or CSS classes.

```tsx
// live-dashboard.test.tsx
import { render, screen } from '@testing-library/react';
import { LiveDashboard } from './live-dashboard';
import { createWrapper } from '@/test/utils';

describe('LiveDashboard', () => {
  it('shows employee count KPIs', async () => {
    render(<LiveDashboard />, { wrapper: createWrapper() });
    
    expect(await screen.findByText('487')).toBeInTheDocument(); // Total
    expect(screen.getByText('342')).toBeInTheDocument();        // Active
  });

  it('shows monitoring disabled message when monitoring is off', async () => {
    // MSW handler returns monitoring disabled
    server.use(monitoringDisabledHandler);
    
    render(<LiveDashboard />, { wrapper: createWrapper() });
    
    expect(await screen.findByText(/monitoring is not enabled/i)).toBeInTheDocument();
  });

  it('navigates to employee detail on row click', async () => {
    render(<LiveDashboard />, { wrapper: createWrapper() });
    
    const row = await screen.findByText('John Doe');
    await userEvent.click(row);
    
    expect(mockRouter.push).toHaveBeenCalledWith('/workforce/activity/emp-123');
  });
});
```

## MSW Handlers

Centralized mock API handlers:

```tsx
// test/handlers/workforce.ts
import { http, HttpResponse } from 'msw';

export const workforceHandlers = [
  http.get('/api/v1/workforce/presence/live', () => {
    return HttpResponse.json({
      total: 487,
      active: 342,
      idle: 89,
      onLeave: 41,
      absent: 15,
      departments: [
        { name: 'Engineering', activePercent: 82 },
        { name: 'Sales', activePercent: 71 },
      ],
    });
  }),
  
  http.get('/api/v1/exceptions/alerts', ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    return HttpResponse.json({
      items: status === 'new' ? mockNewAlerts : mockAllAlerts,
      totalCount: status === 'new' ? 7 : 42,
    });
  }),
];

export const monitoringDisabledHandler = http.get(
  '/api/v1/workforce/presence/live',
  () => HttpResponse.json(null, { status: 403 })
);
```

## E2E Tests (Playwright)

Critical user flows only — not exhaustive coverage.

```tsx
// e2e/leave-request.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Leave Request Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name=email]', 'hr@test.com');
    await page.fill('[name=password]', 'TestPass123!');
    await page.click('button[type=submit]');
    await page.waitForURL('/overview');
  });

  test('approve a leave request', async ({ page }) => {
    await page.goto('/hr/leave');
    
    // Click pending tab
    await page.click('text=Pending');
    
    // Click first request
    await page.click('text=John Doe');
    
    // Approve
    await page.click('button:has-text("Approve")');
    
    // Verify toast
    await expect(page.locator('.toast')).toContainText('Leave approved');
  });
});
```

### Critical E2E Flows

| Flow | File | What It Tests |
|:-----|:-----|:-------------|
| Login + MFA | `login.spec.ts` | Login, MFA verification, redirect to dashboard |
| Leave approval | `leave-request.spec.ts` | Submit, approve, reject leave |
| Exception management | `exception-management.spec.ts` | View alerts, acknowledge, dismiss |
| Payroll run | `payroll-run.spec.ts` | Create run, calculate, approve |
| Employee CRUD | `employee-crud.spec.ts` | Create, edit, view employee |

## Test Utilities

```tsx
// test/utils.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/components/providers/auth-provider';

export function createWrapper(options?: { permissions?: string[] }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <AuthProvider mockPermissions={options?.permissions}>
          {children}
        </AuthProvider>
      </QueryClientProvider>
    );
  };
}
```

## What NOT to Test

- shadcn/ui component internals (they're already tested)
- CSS/styling (visual regression testing is a separate concern)
- Implementation details (internal state, private methods)
- Snapshot tests (they break on every UI change and catch nothing meaningful)

## Coverage Targets

| Layer | Target | Notes |
|:------|:-------|:------|
| Utils/hooks | 90%+ | Pure logic, easy to test |
| Components | 70%+ | Key behaviors, not every variant |
| E2E | Critical flows | ~10 flows covering the main user journeys |
