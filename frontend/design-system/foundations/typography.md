# Typography

## Font

- **Display/Headings:** Outfit (variable, 400–800 weight) — rounded, friendly, professional. Strong character for dashboards.
- **Body/UI Text:** Geist (400–500 weight) — clean, readable, modern. Pairs with Outfit for contrast.
- **Monospace:** JetBrains Mono — code snippets, IDs, timestamps

### Font Loading

```tsx
// app/layout.tsx
import { Outfit, JetBrains_Mono } from 'next/font/google';
import localFont from 'next/font/local';

const outfit = Outfit({ subsets: ['latin'], variable: '--font-display' });
const geist = localFont({ src: './fonts/Geist-Variable.woff2', variable: '--font-body' });
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' });
```

## Scale

| Name | Size | Weight | Font | Usage |
|:-----|:-----|:-------|:-----|:------|
| `h1` | 2rem (32px) | 700 | Outfit | Page titles |
| `h2` | 1.5rem (24px) | 600 | Outfit | Section headers |
| `h3` | 1.25rem (20px) | 600 | Outfit | Card titles |
| `h4` | 1.125rem (18px) | 600 | Outfit | Subsection headers |
| `body` | 0.875rem (14px) | 400 | Geist | Default body text |
| `body-sm` | 0.8125rem (13px) | 400 | Geist | Table cells, secondary text |
| `caption` | 0.75rem (12px) | 400 | Geist | Labels, timestamps, badges |
| `metric` | 2rem (32px) | 700 | Outfit | KPI numbers |
| `metric-sm` | 1.5rem (24px) | 600 | Outfit | Secondary metrics |

## Tailwind Classes

```tsx
// Page title
<h1 className="font-display text-2xl font-bold tracking-tight">Employees</h1>

// Section header
<h2 className="font-display text-lg font-semibold">Department Overview</h2>

// Card title
<h3 className="font-display text-base font-semibold">Active Employees</h3>

// Body text
<p className="font-body text-sm text-foreground">...</p>

// Secondary text
<p className="font-body text-sm text-muted-foreground">...</p>

// Caption/label
<span className="font-body text-xs text-muted-foreground">Last updated 30s ago</span>

// KPI metric
<p className="font-display text-2xl font-bold tabular-nums">1,247</p>

// Monospace (IDs, timestamps)
<code className="font-mono text-xs">emp-a1b2c3d4</code>
```

## Line Heights

- Headings: `leading-tight` (1.25)
- Body: `leading-normal` (1.5)
- Captions: `leading-none` (1)
- Metrics: `leading-none` (1)

## Related

- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — color system
- [[frontend/design-system/components/component-catalog|Component Catalog]] — component library
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — page layouts
