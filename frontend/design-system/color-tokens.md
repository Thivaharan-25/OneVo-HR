# Color Tokens

## CSS Custom Properties

All colors defined as CSS custom properties for light/dark mode support.

```css
/* globals.css */
:root {
  /* Brand */
  --primary: 222.2 84% 51%;        /* Brand blue */
  --primary-foreground: 210 40% 98%;
  
  /* Backgrounds */
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  
  /* Borders */
  --border: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 51%;
  
  /* Status (fixed, not theme-dependent) */
  --status-active: 142 76% 36%;     /* Green */
  --status-idle: 48 96% 53%;        /* Yellow */
  --status-offline: 0 84% 60%;      /* Red */
  --status-leave: 217 91% 60%;      /* Blue */
  --status-partial: 25 95% 53%;     /* Orange */
  
  /* Severity */
  --severity-info: 217 91% 60%;     /* Blue */
  --severity-warning: 48 96% 53%;   /* Yellow */
  --severity-critical: 0 84% 60%;   /* Red */
  
  /* Sidebar */
  --sidebar-background: 0 0% 98%;
  --sidebar-foreground: 240 5.3% 26.1%;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... dark mode overrides */
}
```

## Semantic Color Usage

| Purpose | Token | CSS Variable |
|:--------|:------|:-------------|
| Primary actions | `text-primary`, `bg-primary` | `--primary` |
| Page background | `bg-background` | `--background` |
| Card surface | `bg-card` | `--card` |
| Subtle background | `bg-muted` | `--muted` |
| Secondary text | `text-muted-foreground` | `--muted-foreground` |
| Borders | `border` | `--border` |
| Active/online | `text-green-600` | Direct Tailwind |
| Idle | `text-yellow-600` | Direct Tailwind |
| Offline/error | `text-red-600` | Direct Tailwind |
| On leave | `text-blue-600` | Direct Tailwind |

## Related

- [[component-catalog]] — component library
- [[typography]] — type scale
- [[tenant-branding]] — tenant color customization
- [[layout-patterns]] — page layouts
