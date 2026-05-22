# Feature Flags

## Two Types of Flags

| Type | Source | Purpose | Examples |
|:-----|:-------|:--------|:---------|
| **Tenant Feature** | Tenant subscription / module entitlement | Module-level gating by plan | `workforceIntelligence`, `payroll`, `advancedReporting` |
| **Release Flag** | Feature flag service (PostHog/LaunchDarkly) | Gradual rollout, A/B tests | `newEmployeeWizard`, `redesignedDashboard` |

## Tenant Features

Tenant features come from the backend session metadata (`activeModules`). They gate entire product modules. The `AuthService` in `@onevo/shared` exposes them as signals.

```typescript
// AuthService.hasFeature() returns a computed signal
const hasWorkforce = this.auth.hasFeature('workforceIntelligence');
// hasWorkforce() → boolean (reactive)
```

### Template Gating

```html
<!-- Structural directive — hide entire section if feature not enabled -->
<nav-section *hasFeature="'workforceIntelligence'" label="Workforce">
  ...
</nav-section>

<!-- New control flow -->
@if (auth.hasFeature('wms:projects')()) {
  <a routerLink="/worksync/projects">Projects</a>
}
```

### Composing Feature + Permission Gates

Both must pass — feature decides what the tenant has bought, permission decides what the user can do within it:

```html
<!-- Must have the module AND the permission -->
@if (auth.hasFeature('workforceIntelligence')() && auth.hasPermission('workforce:view')()) {
  <app-live-dashboard />
}

<!-- Or with structural directive composition -->
<ng-container *hasFeature="'workforceIntelligence'">
  <app-live-dashboard *hasPermission="'workforce:view'" />
</ng-container>
```

### Upgrade Banner

When a tenant doesn't have a module, show an upgrade prompt instead of hiding silently:

```typescript
// shared/src/lib/ui/feedback/feature-gate.component.ts
@Component({
  selector: 'app-feature-gate',
  standalone: true,
  template: `
    @if (auth.hasFeature(feature())()) {
      <ng-content />
    } @else {
      @if (showUpgradeBanner()) {
        <app-upgrade-banner [feature]="feature()" />
      }
    }
  `,
})
export class FeatureGateComponent {
  feature = input.required<string>();
  showUpgradeBanner = input(true);
  auth = inject(AuthService);
}
```

```html
<app-feature-gate feature="workforceIntelligence">
  <app-live-dashboard />
</app-feature-gate>
```

## Release Flags

Release flags control gradual rollout of new features within an already-entitled module. Evaluated per-user or per-tenant by a flag service.

```typescript
// shared/src/lib/feature-flags/feature-flag.service.ts
@Injectable({ providedIn: 'root' })
export class FeatureFlagService {
  private flags = signal<Record<string, boolean>>({});

  isEnabled(flag: string): Signal<boolean> {
    return computed(() => this.flags()[flag] ?? false);
  }

  loadFlags(userId: string) {
    // Fetch from PostHog / LaunchDarkly / backend endpoint
    this.flagsClient.getFlags(userId).then(flags => this.flags.set(flags));
  }
}
```

Usage in a component:

```typescript
export class EmployeeListComponent {
  private flagService = inject(FeatureFlagService);
  useNewWizard = this.flagService.isEnabled('new-employee-wizard');
}
```

```html
@if (useNewWizard()) {
  <app-new-employee-wizard />
} @else {
  <app-legacy-employee-form />
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

Flags older than 30 days at 100% rollout must be cleaned up. Track them in a registry:

```typescript
// shared/src/lib/feature-flags/registry.ts
export const FEATURE_FLAGS = {
  'new-employee-wizard': {
    description: 'Redesigned multi-step employee creation wizard',
    createdAt: '2026-03-15',
    owner: 'hr-team',
    cleanupBy: '2026-04-30',
  },
} as const;
```

## Related

- [[frontend/cross-cutting/authorization|Authorization]] — permission vs feature distinction
- [[frontend/architecture/routing|Routing]] — `featureGuard` functional guard
- [[frontend/cross-cutting/analytics|Analytics]] — A/B test measurement
