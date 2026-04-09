# Feature Flags

## Two Types of Flags

| Type | Source | Purpose | Examples |
|:-----|:-------|:--------|:---------|
| **Tenant Feature** | Tenant subscription / config | Module-level gating by plan | `workforceIntelligence`, `payroll`, `advancedReporting` |
| **Release Flag** | Feature flag service (PostHog/LaunchDarkly) | Gradual rollout, A/B tests | `newEmployeeWizard`, `redesignedDashboard` |

## Tenant Features

Tenant features come from the JWT and tenant config API. They gate entire product modules.

```tsx
// stores/use-feature-store.ts
interface FeatureState {
  features: Set<string>;
  hasFeature: (feature: string) => boolean;
  setFeatures: (features: string[]) => void;
}

// Loaded from JWT claims on login
const tenantFeatures = decodedToken.features; // ['workforceIntelligence', 'payroll', 'advancedReporting']
```

### FeatureGate Component

```tsx
interface FeatureGateProps {
  feature: string;
  fallback?: React.ReactNode;  // Default: upgrade banner
  children: React.ReactNode;
}

export function FeatureGate({ feature, fallback, children }: FeatureGateProps) {
  const hasFeature = useFeatureStore(state => state.hasFeature(feature));

  if (!hasFeature) {
    return fallback ?? (
      <UpgradeBanner
        title={`${featureDisplayNames[feature]} is not included in your plan`}
        description="Upgrade to access this feature."
      />
    );
  }

  return <>{children}</>;
}
```

### Usage with Permission Gates

Feature gates and permission gates compose:

```tsx
// Must have the feature AND the permission
<FeatureGate feature="workforceIntelligence">
  <PermissionGate permission="workforce:view">
    <LiveDashboard />
  </PermissionGate>
</FeatureGate>
```

## Release Flags

Release flags control gradual rollout of new features. Evaluated per-user or per-tenant.

```tsx
// hooks/use-feature-flag.ts
export function useFeatureFlag(flag: string): boolean {
  // PostHog example
  const posthog = usePostHog();
  return posthog.isFeatureEnabled(flag) ?? false;
}

// Usage
function EmployeeList() {
  const useNewWizard = useFeatureFlag('new-employee-wizard');

  return (
    <>
      {useNewWizard ? <NewEmployeeWizard /> : <LegacyEmployeeForm />}
    </>
  );
}
```

### Flag Lifecycle

```
1. Create flag (default: off)
2. Enable for internal team (10%)
3. Enable for beta tenants (25%)
4. Enable for all (100%)
5. Remove flag and dead code — flag cleanup PR
```

### Stale Flag Detection

Flags older than 30 days at 100% should be cleaned up. Track in a registry:

```typescript
// lib/feature-flags/registry.ts
export const FEATURE_FLAGS = {
  'new-employee-wizard': {
    description: 'Redesigned multi-step employee creation wizard',
    createdAt: '2026-03-15',
    owner: 'hr-team',
    cleanupBy: '2026-04-30',
  },
  'redesigned-dashboard': {
    description: 'New overview dashboard layout',
    createdAt: '2026-03-20',
    owner: 'platform-team',
    cleanupBy: '2026-05-15',
  },
} as const;
```

## Related

- [[backend/module-boundaries|Module Boundaries]] — feature-gated modules
- [[frontend/cross-cutting/authorization|Authorization]] — permission vs feature distinction
- [[frontend/cross-cutting/analytics|Analytics]] — A/B test measurement
