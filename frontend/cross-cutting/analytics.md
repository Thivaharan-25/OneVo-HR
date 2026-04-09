# Product Analytics & Event Tracking

## Strategy

Track user behavior to understand feature adoption, identify UX friction, and inform product decisions. **Privacy-first**: no PII in events, tenant-scoped, respects consent.

## Stack

| Concern | Tool | Rationale |
|:--------|:-----|:----------|
| Event tracking | PostHog (self-hosted) or Mixpanel | Product analytics, funnels, retention |
| Session replay | PostHog | Debug UX issues with real sessions |
| Feature flags | PostHog / LaunchDarkly | A/B testing, gradual rollouts |
| Web Vitals | Vercel Analytics or custom | Performance monitoring |

## Event Taxonomy

### Naming Convention

```
{object}.{action}
```

| Event | Fired When | Properties |
|:------|:-----------|:-----------|
| `employee.created` | Employee created | `{ department, role }` |
| `employee.viewed` | Employee detail page opened | `{ source: 'list' \| 'search' }` |
| `leave.requested` | Leave request submitted | `{ leaveType, duration }` |
| `leave.approved` | Leave approved | `{ responseTimeMs }` |
| `leave.rejected` | Leave rejected | `{ responseTimeMs }` |
| `alert.viewed` | Exception alert opened | `{ severity, ruleType }` |
| `alert.acknowledged` | Alert acknowledged | `{ timeToAckMs }` |
| `report.exported` | Report exported | `{ reportType, format }` |
| `search.executed` | Search performed | `{ source: 'global' \| 'table', hasResults }` |
| `page.viewed` | Any page navigation | `{ path, referrer }` |
| `feature.discovered` | First use of a feature | `{ feature }` |
| `error.encountered` | Unhandled error shown to user | `{ errorType, page }` |

### Never Track

- Employee names, emails, or any PII
- Salary or compensation data
- Performance review content
- Activity monitoring data
- Anything that could identify a specific employee

## Implementation

### Analytics Provider

```tsx
// components/providers/analytics-provider.tsx
export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();

  useEffect(() => {
    if (!user) return;

    analytics.identify(user.id, {
      role: user.role,               // 'hr_admin', 'manager', 'employee'
      tenantId: user.tenantId,       // For tenant-level analysis
      plan: user.tenantPlan,         // 'starter', 'professional', 'enterprise'
      // NO PII: no name, email, phone
    });
  }, [user?.id]);

  return <>{children}</>;
}
```

### Track Hook

```tsx
// hooks/use-track.ts
export function useTrack() {
  return useCallback((event: string, properties?: Record<string, any>) => {
    analytics.track(event, {
      ...properties,
      timestamp: new Date().toISOString(),
    });
  }, []);
}

// Usage
function EmployeeList() {
  const track = useTrack();

  function handleRowClick(employee: Employee) {
    track('employee.viewed', { source: 'list' });
    router.push(`/people/employees/${employee.id}`);
  }
}
```

### Page View Tracking

```tsx
// Automatic via layout
function PageTracker() {
  const pathname = usePathname();
  const track = useTrack();

  useEffect(() => {
    track('page.viewed', { path: pathname });
  }, [pathname]);

  return null;
}
```

## Key Funnels

| Funnel | Steps | Goal |
|:-------|:------|:-----|
| Employee Onboarding | Create form opened → Step 1 → Step 2 → Step 3 → Submit | Completion rate |
| Leave Request | Request form → Submit → Manager views → Decision | Time to decision |
| Exception Resolution | Alert created → Viewed → Acknowledged → Resolved | Time to resolution |
| Search to Action | Search → Result clicked → Action taken | Search effectiveness |

## Related

- [[frontend/cross-cutting/feature-flags|Feature Flags]] — A/B testing integration
- [[frontend/cross-cutting/error-monitoring|Error Monitoring]] — error tracking
- [[frontend/performance/monitoring|Performance Monitoring]] — Web Vitals
- [[frontend/cross-cutting/security|Security]] — privacy considerations
