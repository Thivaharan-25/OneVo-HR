# Page: Monitoring Settings

**Route:** `/settings/monitoring`
**Permission:** `monitoring:configure` (edit) or `monitoring:view-settings` (view)

## Purpose

Configure monitoring features, manage employee overrides, set exception rules, configure escalation chains, and manage privacy settings.

## Tabs

### Tab 1: Feature Toggles

Global ON/OFF per monitoring feature.

```
+----------------------------------------------------------+
| Industry Profile: Office/IT (change v)                   |
+----------------------------------------------------------+
| Feature                        | Status                  |
| Activity Monitoring (kb/mouse) | [#### ON ]              |
| Application Tracking           | [#### ON ]              |
| Screenshot Capture             | [---- OFF]              |
| Meeting Time Detection         | [#### ON ]              |
| Device Usage Tracking          | [#### ON ]              |
| Identity Verification (photo)  | [#### ON ]              |
| Biometric / attendance devices | [---- OFF]              |
+----------------------------------------------------------+
```

### Tab 2: Employee Overrides


```
+----------------------------------------------------------+
+----------------------------------------------------------+
| Override List                                            |
| +----------+----------+---------+----------+----------+ |
| | Employee | Activity | App     | Screenshot| Reason   | |
| | John D.  | [ok] ON    | [ok] ON   | [wrong] OFF    | IT staff | |
| | Exec A   | [wrong] OFF   | [wrong] OFF  | [wrong] OFF    | Exempt   | |
| +----------+----------+---------+----------+----------+ |
| [+ Add Override]                                         |
+----------------------------------------------------------+
```

### Tab 3: Exception Rules

```
+----------------------------------------------------------+
| Exception Rules                         [+ Create Rule]  |
+----------------------------------------------------------+
| +-------------------+----------+----------+------------+ |
| | Rule Name         | Type     | Severity | Status     | |
| | Low activity      | low_act  | [critical] Crit | Active     | |
| | Excess idle       | idle     | [warning] Warn  | Active     | |
| | No presence       | no_pres  | [info] Info     | Active     | |
| | Break exceeded    | break    | [warning] Warn  | Inactive   | |
| +-------------------+----------+----------+------------+ |
+----------------------------------------------------------+
```

### Tab 4: Escalation Chains

```
+----------------------------------------------------------+
| Critical Severity:                                       |
|   Step 1: Management coverage owner -> Immediate          |
|   Step 2: Users with exceptions:manage -> After 30 min    |
|   Step 3: Configured escalation resolver -> After 60 min  |
|                                                          |
| Warning Severity:                                        |
|   Step 1: Management coverage owner -> Immediate          |
|   Step 2: Configured escalation resolver -> After 60 min  |
+----------------------------------------------------------+
```

### Tab 5: Privacy & Retention

```
+----------------------------------------------------------+
| Privacy Mode: [Full Transparency v]                      |
|                                                          |
| Data Retention:                                          |
|   Screenshots:        [30] days                          |
|   Verification Photos: [30] days                         |
|   Activity Snapshots:  [90] days (system minimum)        |
|   Daily Summaries:     [730] days (2 years, recommended) |
+----------------------------------------------------------+
```

## Related

- [[frontend/architecture/overview|Tenant Settings Overview]]
- [[frontend/architecture/overview|Monitoring Toggles]]
- [[frontend/architecture/overview|Employee Overrides]]
- [[frontend/architecture/overview|Retention Policies]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
