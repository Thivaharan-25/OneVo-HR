# Color Tokens

## CSS Custom Properties

All colors defined as CSS custom properties for light/dark mode support.

```css
/* globals.css */
:root {
  /* Brand — Violet Electric */
  --primary: 263 70% 50.4%;           /* #7c3aed */
  --primary-hover: 263 78% 50.2%;     /* #6d28d9 */
  --primary-light: 258 90% 66.3%;     /* #8b5cf6 */
  --primary-muted: 258 90% 76.1%;     /* #a78bfa */
  --primary-foreground: 0 0% 98%;
  --primary-subtle: 258 90% 66.3% / 0.04;
  --primary-glow: 258 90% 66.3% / 0.25;

  /* Backgrounds */
  --background: 240 10% 3.9%;          /* #09090b */
  --foreground: 0 0% 98%;              /* #fafafa */
  --card: 240 5.9% 10%;                /* #18181b */
  --card-foreground: 0 0% 98%;
  --muted: 240 3.7% 15.9%;             /* #27272a */
  --muted-foreground: 240 5% 64.9%;    /* #a1a1aa */

  /* Borders */
  --border: 0 0% 100% / 0.06;
  --border-hover: 0 0% 100% / 0.1;
  --ring: 263 70% 50.4%;

  /* Status (fixed, not theme-dependent) */
  --status-active: 142 71% 45.3%;      /* #22c55e */
  --status-warning: 38 92% 50.2%;      /* #f59e0b */
  --status-critical: 0 84.2% 60.2%;    /* #ef4444 */
  --status-info: 189 94% 42.7%;        /* #06b6d4 */
  --status-partial: 24.6 95% 53.1%;    /* #f97316 */

  /* Severity */
  --severity-info: 189 94% 42.7%;
  --severity-warning: 38 92% 50.2%;
  --severity-critical: 0 84.2% 60.2%;

  /* Sidebar */
  --sidebar-background: 240 10% 3.9% / 0.85;
  --sidebar-foreground: 0 0% 98%;

  /* Glass surfaces */
  --glass-bg: 240 33% 5% / 0.85;
  --glass-border: 0 0% 100% / 0.06;
  --glass-glow: 263 70% 50.4% / 0.15;
}

.light {
  --background: 0 0% 98%;              /* #fafafa */
  --foreground: 240 10% 3.9%;          /* #09090b */
  --card: 0 0% 100%;                   /* #ffffff */
  --card-foreground: 240 10% 3.9%;
  --muted: 240 4.8% 95.9%;             /* #f4f4f5 */
  --muted-foreground: 240 3.8% 46.1%;  /* #71717a */
  --border: 240 5.9% 90%;              /* #e4e4e7 */
  --border-hover: 240 5.9% 85%;
  --sidebar-background: 0 0% 100% / 0.7;
  --glass-bg: 0 0% 100% / 0.7;
  --glass-border: 0 0% 0% / 0.06;
}
```

## Semantic Color Usage

| Purpose | Token | CSS Variable |
|:--------|:------|:-------------|
| Primary actions | `text-primary`, `bg-primary` | `--primary` |
| Primary hover | `hover:bg-primary-hover` | `--primary-hover` |
| Active/selected accent | `text-primary-light` | `--primary-light` |
| Muted accent text | `text-primary-muted` | `--primary-muted` |
| Subtle hover tint | `bg-primary-subtle` | `--primary-subtle` |
| Glow effects | `shadow-primary-glow` | `--primary-glow` |
| Page background | `bg-background` | `--background` |
| Card surface | `bg-card` | `--card` |
| Subtle background | `bg-muted` | `--muted` |
| Secondary text | `text-muted-foreground` | `--muted-foreground` |
| Borders | `border` | `--border` |
| Glass surface | `bg-glass` | `--glass-bg` |
| Glass border | `border-glass` | `--glass-border` |
| Active/online | `text-status-active` | `--status-active` |
| Warning | `text-status-warning` | `--status-warning` |
| Critical/error | `text-status-critical` | `--status-critical` |
| Info/on leave | `text-status-info` | `--status-info` |

## Gradients

| Name | Value | Usage |
|:-----|:------|:------|
| Primary gradient | `linear-gradient(135deg, #7c3aed, #8b5cf6)` | Primary action buttons |
| Chart fill | `linear-gradient(180deg, #7c3aed20, transparent)` | Area chart fills |

## Related

- [[frontend/design-system/components/component-catalog|Component Catalog]] — component library
- [[frontend/design-system/foundations/typography|Typography]] — type scale
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — tenant color customization
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — page layouts
