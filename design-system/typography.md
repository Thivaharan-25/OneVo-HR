# Typography

## Font

- **Primary:** Inter (variable font) — clean, readable, good for data-dense UIs
- **Monospace:** JetBrains Mono — code snippets, IDs, timestamps

## Scale

| Name | Size | Weight | Usage |
|:-----|:-----|:-------|:------|
| `h1` | 2rem (32px) | 700 | Page titles |
| `h2` | 1.5rem (24px) | 600 | Section headers |
| `h3` | 1.25rem (20px) | 600 | Card titles |
| `h4` | 1.125rem (18px) | 600 | Subsection headers |
| `body` | 0.875rem (14px) | 400 | Default body text |
| `body-sm` | 0.8125rem (13px) | 400 | Table cells, secondary text |
| `caption` | 0.75rem (12px) | 400 | Labels, timestamps, badges |
| `metric` | 2rem (32px) | 700 | KPI numbers |
| `metric-sm` | 1.5rem (24px) | 600 | Secondary metrics |

## Tailwind Classes

```tsx
// Page title
<h1 className="text-2xl font-bold tracking-tight">Employees</h1>

// Section header
<h2 className="text-lg font-semibold">Department Overview</h2>

// Card title
<h3 className="text-base font-semibold">Active Employees</h3>

// Body text
<p className="text-sm text-foreground">...</p>

// Secondary text
<p className="text-sm text-muted-foreground">...</p>

// Caption/label
<span className="text-xs text-muted-foreground">Last updated 30s ago</span>

// KPI metric
<p className="text-2xl font-bold tabular-nums">1,247</p>

// Monospace (IDs, timestamps)
<code className="font-mono text-xs">emp-a1b2c3d4</code>
```

## Line Heights

- Headings: `leading-tight` (1.25)
- Body: `leading-normal` (1.5)
- Captions: `leading-none` (1)
- Metrics: `leading-none` (1)

## Related

- [[color-tokens]] — color system
- [[component-catalog]] — component library
- [[layout-patterns]] — page layouts
