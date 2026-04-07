# Frontend Architecture

## App Structure

```
app/
├── (auth)/                       # Public — no sidebar
│   ├── login/page.tsx
│   ├── forgot-password/page.tsx
│   └── mfa/page.tsx
│
├── (dashboard)/                  # Authenticated — sidebar + topbar
│   ├── layout.tsx                # DashboardLayout with Sidebar + Topbar
│   ├── overview/page.tsx         # Landing dashboard
│   │
│   ├── hr/                       # Pillar 1: HR Management
│   │   ├── employees/
│   │   │   ├── page.tsx          # Employee list
│   │   │   ├── [id]/page.tsx     # Employee detail
│   │   │   └── new/page.tsx      # Create employee
│   │   ├── leave/
│   │   │   ├── page.tsx          # Leave requests
│   │   │   ├── calendar/page.tsx # Leave calendar
│   │   │   └── policies/page.tsx # Leave policies (admin)
│   │   ├── performance/
│   │   │   ├── page.tsx          # Review cycles
│   │   │   ├── goals/page.tsx    # Goals
│   │   │   └── [id]/page.tsx     # Review detail
│   │   ├── payroll/
│   │   │   ├── page.tsx          # Payroll runs
│   │   │   └── [id]/page.tsx     # Payroll run detail
│   │   ├── skills/page.tsx
│   │   ├── documents/page.tsx
│   │   ├── grievance/page.tsx
│   │   └── expense/page.tsx
│   │
│   ├── workforce/                # Pillar 2: Workforce Intelligence
│   │   ├── live/page.tsx         # Real-time workforce dashboard
│   │   ├── activity/
│   │   │   └── [employeeId]/page.tsx  # Employee activity detail
│   │   ├── reports/page.tsx      # Daily/weekly/monthly reports
│   │   ├── exceptions/page.tsx   # Exception alert management
│   │   └── verification/page.tsx # Identity verification logs
│   │
│   ├── org/                      # Org Structure
│   │   ├── departments/page.tsx
│   │   ├── teams/page.tsx
│   │   └── job-families/page.tsx
│   │
│   └── settings/                 # Tenant Configuration
│       ├── general/page.tsx
│       ├── monitoring/page.tsx   # Feature toggles + employee overrides
│       ├── notifications/page.tsx
│       ├── integrations/page.tsx
│       └── billing/page.tsx
│
├── (employee)/                   # Employee self-service (limited nav)
│   ├── layout.tsx                # Simplified layout
│   ├── my-dashboard/page.tsx     # Own activity data
│   ├── my-leave/page.tsx
│   ├── my-profile/page.tsx
│   └── my-performance/page.tsx
│
└── layout.tsx                    # Root layout (providers, fonts)
```

## Layout System

### Dashboard Layout
- **Sidebar:** Collapsible, permission-gated navigation sections
- **Topbar:** Search, notifications bell (badge count), user menu
- **Main Content:** Page content with breadcrumbs
- **Sidebar sections:** Gated by product config (HR Only = no Workforce section)

### Employee Self-Service Layout
- Simplified sidebar (own data only)
- No admin navigation
- "What's being tracked" transparency footer (per privacy mode)

## Provider Stack (Root Layout)

```tsx
// app/layout.tsx
<QueryClientProvider>
  <AuthProvider>
    <SignalRProvider>
      <ThemeProvider>
        <ToastProvider>
          {children}
        </ToastProvider>
      </ThemeProvider>
    </SignalRProvider>
  </AuthProvider>
</QueryClientProvider>
```

## Related Docs

- [[app-structure]] — detailed page-by-page breakdown
- [[state-management]] — TanStack Query + Zustand patterns
- [[api-integration]] — API client, error handling, pagination
- [[real-time]] — SignalR setup and channels
- [[monitoring-data-flow]] — how Workforce Intelligence data flows to UI
