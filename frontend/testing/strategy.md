# Frontend Testing Strategy

## Test Stack

| Tool | Purpose | Runs In |
|:-----|:--------|:--------|
| Jest + Angular Testing Library | Unit + component behavior tests | jsdom |
| MSW (Mock Service Worker) | API mocking for component + integration tests | jsdom / browser |
| Playwright | E2E tests (critical user flows) | Real browser |

## Test File Location

Tests live next to the code they test:

```
projects/
├── shared/src/lib/
│   ├── api/endpoints/
│   │   ├── employees.service.ts
│   │   └── employees.service.spec.ts       # Service unit test
│   └── utils/
│       ├── format-date.ts
│       └── format-date.spec.ts             # Utility unit test
├── employee-app/src/app/features/
│   ├── leave/
│   │   ├── leave-overview.component.ts
│   │   └── leave-overview.component.spec.ts # Component test
├── management-app/src/app/features/
│   ├── workforce/
│   │   ├── live-dashboard.component.ts
│   │   └── live-dashboard.component.spec.ts # Component test
e2e/
├── leave-request.spec.ts                    # E2E test
├── exception-management.spec.ts
└── login.spec.ts
```

## Unit Tests (Jest)

For services, utilities, and pure functions.

```typescript
// employees.service.spec.ts
import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { EmployeeApiService } from './employees.service';

describe('EmployeeApiService', () => {
  let service: EmployeeApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        EmployeeApiService,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(EmployeeApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('lists employees with filters', () => {
    service.list({ page: 0, pageSize: 25, search: 'john' }).subscribe(result => {
      expect(result.items).toHaveLength(2);
    });

    const req = httpMock.expectOne(r => r.url.includes('/api/v1/employees'));
    expect(req.request.params.get('search')).toBe('john');
    req.flush({ items: [mockEmployee1, mockEmployee2], nextCursor: null, hasMore: false });
  });
});
```

```typescript
// format-date.spec.ts
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

## Component Tests (Angular Testing Library)

Test behavior from the user's perspective. Never test internal signals, private methods, or Angular lifecycle directly.

```typescript
// live-dashboard.component.spec.ts
import { render, screen } from '@testing-library/angular';
import { userEvent } from '@testing-library/user-event';
import { LiveDashboardComponent } from './live-dashboard.component';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { setupServer } from 'msw/node';
import { workforceHandlers, monitoringDisabledHandler } from '../../../../test/handlers/workforce';

const server = setupServer(...workforceHandlers);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('LiveDashboardComponent', () => {
  const renderComponent = () =>
    render(LiveDashboardComponent, {
      providers: [provideHttpClient(), provideRouter([])],
    });

  it('shows employee count KPIs', async () => {
    await renderComponent();
    expect(await screen.findByText('487')).toBeInTheDocument(); // Total
    expect(screen.getByText('342')).toBeInTheDocument();        // Active
  });

  it('shows monitoring disabled message when monitoring is off', async () => {
    server.use(monitoringDisabledHandler);
    await renderComponent();
    expect(await screen.findByText(/monitoring is not enabled/i)).toBeInTheDocument();
  });

  it('navigates to employee detail on row click', async () => {
    const user = userEvent.setup();
    await renderComponent();

    const row = await screen.findByText('John Doe');
    await user.click(row);

    // Angular Router navigation assertion
    expect(location.pathname).toBe('/workforce/emp-123');
  });
});
```

## MSW Handlers

Centralised mock API handlers — shared across unit and E2E tests:

```typescript
// test/handlers/workforce.ts
import { http, HttpResponse } from 'msw';

export const workforceHandlers = [
  http.get('/api/v1/workforce/presence/live', () =>
    HttpResponse.json({
      total: 487, active: 342, idle: 89, onLeave: 41, absent: 15,
      departments: [
        { name: 'Engineering', activePercent: 82 },
        { name: 'Sales', activePercent: 71 },
      ],
    })
  ),

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

## Permission Testing Helper

Provide a mock `AuthService` with specific permissions to test gated UI:

```typescript
// test/mock-auth.service.ts
export function provideMockAuth(permissions: string[] = [], modules: string[] = []) {
  return {
    provide: AuthService,
    useValue: {
      user: signal({ id: 'u1', name: 'Test User', tenantSlug: 'test-co' }),
      isAuthenticated: signal(true),
      hasPermission: (p: string) => computed(() => permissions.includes(p)),
      hasFeature: (f: string) => computed(() => modules.includes(f)),
      hasAnyPermission: (...ps: string[]) => computed(() => ps.some(p => permissions.includes(p))),
      isSuperAdmin: computed(() => false),
    } satisfies Partial<AuthService>,
  };
}

// Usage in test
render(EmployeeDetailComponent, {
  providers: [
    provideMockAuth(['employees:read', 'payroll:read']),
    provideHttpClient(),
  ],
});
```

## Responsive QA

Responsive behavior must be verified before any page is considered complete.

### Required Viewports

| Viewport | Width |
|:---------|:------|
| Small mobile | `375px` |
| Large mobile | `430px` |
| Tablet | `768px` |
| Laptop | `1024px` |
| Desktop | `1280px` |
| Wide desktop | `1440px` |

### Checks

- No horizontal page overflow
- Topbar actions remain reachable
- Navigation usable through drawer, rail, or full panel depending on viewport
- Tables switch to card/list layout on mobile
- Forms remain readable, touch-safe, and completable
- Modals, drawers, and menus fit within the viewport and trap focus correctly

### Playwright Viewport Pattern

```typescript
for (const width of [375, 430, 768, 1024, 1280, 1440]) {
  test(`dashboard is usable at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/');
    await expect(page.locator('app-root')).toBeVisible();
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    expect(scrollWidth).toBeLessThanOrEqual(width);
  });
}
```

## E2E Tests (Playwright)

Critical user flows only — not exhaustive coverage.

```typescript
// e2e/leave-request.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Leave Request Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name=email]', 'hr@test.com');
    await page.fill('[name=password]', 'TestPass123!');
    await page.click('button[type=submit]');
    await page.waitForURL('/home');
  });

  test('approve a leave request', async ({ page }) => {
    await page.goto('/leave');
    await page.click('text=Pending');
    await page.click('text=John Doe');
    await page.click('button:has-text("Approve")');
    await expect(page.locator('mat-snack-bar-container')).toContainText('Leave approved');
  });
});
```

### Critical E2E Flows

| Flow | File | What It Tests |
|:-----|:-----|:-------------|
| Login + MFA | `login.spec.ts` | Login, MFA verification, redirect to home |
| Leave approval | `leave-request.spec.ts` | Submit, approve, reject leave |
| Exception management | `exception-management.spec.ts` | View alerts, acknowledge, dismiss |
| Employee CRUD | `employee-crud.spec.ts` | Create, edit, view employee |
| App context switch | `context-switch.spec.ts` | Switch between employee-app and management-app |

## What NOT to Test

- Angular Material component internals (already tested by Angular team)
- CSS/styling (visual regression is a separate concern)
- Implementation details (internal signals, private methods, lifecycle hooks)
- Snapshot tests (break on every UI change, catch nothing meaningful)

## Coverage Targets

| Layer | Target | Notes |
|:------|:-------|:------|
| Utils / pure functions | 90%+ | Pure logic, easy to test |
| Services (API, auth) | 80%+ | Key behaviors with HttpTestingController |
| Components | 70%+ | Key behaviors via Angular Testing Library |
| E2E | Critical flows | ~10 flows covering main user journeys |

## Run Commands

```bash
ng test employee-app          # Jest unit + component tests
ng test management-app
ng test shared
ng e2e                        # Playwright E2E
```

## Related

- [[frontend/coding-standards|Coding Standards]]
- [[frontend/design-system/components/component-catalog|Component Catalog]]
