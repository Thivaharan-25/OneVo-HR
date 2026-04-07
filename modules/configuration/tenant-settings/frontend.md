# Page: Monitoring Settings

**Route:** `/settings/monitoring`
**Permission:** `monitoring:configure` (edit) or `monitoring:view-settings` (view)

## Purpose

Configure monitoring features, manage employee overrides, set exception rules, configure escalation chains, and manage privacy settings.

## Tabs

### Tab 1: Feature Toggles

Global ON/OFF per monitoring feature.

```
┌──────────────────────────────────────────────────────────┐
│ Industry Profile: Office/IT (change ▼)                   │
├──────────────────────────────────────────────────────────┤
│ Feature                        │ Status                  │
│ Activity Monitoring (kb/mouse) │ [████ ON ]              │
│ Application Tracking           │ [████ ON ]              │
│ Screenshot Capture             │ [░░░░ OFF]              │
│ Meeting Time Detection         │ [████ ON ]              │
│ Device Usage Tracking          │ [████ ON ]              │
│ Identity Verification (photo)  │ [████ ON ]              │
│ Biometric (fingerprint)        │ [░░░░ OFF]              │
└──────────────────────────────────────────────────────────┘
```

### Tab 2: Employee Overrides

Per-employee or bulk (department/team) overrides.

```
┌──────────────────────────────────────────────────────────┐
│ [Search employee] [Bulk: By Department ▼] [By Team ▼]   │
├──────────────────────────────────────────────────────────┤
│ Override List                                            │
│ ┌──────────┬──────────┬─────────┬──────────┬──────────┐ │
│ │ Employee │ Activity │ App     │ Screenshot│ Reason   │ │
│ │ John D.  │ ✅ ON    │ ✅ ON   │ ❌ OFF    │ IT staff │ │
│ │ CEO      │ ❌ OFF   │ ❌ OFF  │ ❌ OFF    │ Exempt   │ │
│ │ WH team  │ ❌ OFF   │ ❌ OFF  │ ❌ OFF    │ Non-desk │ │
│ └──────────┴──────────┴─────────┴──────────┴──────────┘ │
│ [+ Add Override]                                         │
└──────────────────────────────────────────────────────────┘
```

### Tab 3: Exception Rules

```
┌──────────────────────────────────────────────────────────┐
│ Exception Rules                         [+ Create Rule]  │
├──────────────────────────────────────────────────────────┤
│ ┌───────────────────┬──────────┬──────────┬────────────┐ │
│ │ Rule Name         │ Type     │ Severity │ Status     │ │
│ │ Low activity      │ low_act  │ 🔴 Crit  │ Active     │ │
│ │ Excess idle       │ idle     │ 🟡 Warn  │ Active     │ │
│ │ No presence       │ no_pres  │ 🔵 Info  │ Active     │ │
│ │ Break exceeded    │ break    │ 🟡 Warn  │ Inactive   │ │
│ └───────────────────┴──────────┴──────────┴────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Tab 4: Escalation Chains

```
┌──────────────────────────────────────────────────────────┐
│ Critical Severity:                                       │
│   Step 1: Reporting Manager → Immediate                  │
│   Step 2: HR Admin → After 30 min                        │
│   Step 3: CEO → After 60 min                             │
│                                                          │
│ Warning Severity:                                        │
│   Step 1: Reporting Manager → Immediate                  │
│   Step 2: HR Admin → After 60 min                        │
└──────────────────────────────────────────────────────────┘
```

### Tab 5: Privacy & Retention

```
┌──────────────────────────────────────────────────────────┐
│ Privacy Mode: [Full Transparency ▼]                      │
│                                                          │
│ Data Retention:                                          │
│   Screenshots:        [30] days                          │
│   Verification Photos: [30] days                         │
│   Activity Snapshots:  [90] days (system minimum)        │
│   Daily Summaries:     [730] days (2 years, recommended) │
└──────────────────────────────────────────────────────────┘
```

## Related

- [[configuration/tenant-settings/overview|Tenant Settings Overview]]
- [[configuration/monitoring-toggles/overview|Monitoring Toggles]]
- [[configuration/employee-overrides/overview|Employee Overrides]]
- [[configuration/retention-policies/overview|Retention Policies]]
- [[multi-tenancy]]
- [[WEEK1-shared-platform]]
