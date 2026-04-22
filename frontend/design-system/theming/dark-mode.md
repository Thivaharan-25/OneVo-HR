# Dark Mode

## Strategy

- **Default:** System preference (`prefers-color-scheme`) — resolved on first load
- **User override:** Theme toggle button in Topbar (Sun / Moon / Monitor icon). Cycles: system → light → dark
- **Persistence:** `localStorage` key `theme` — values: `"system"` | `"light"` | `"dark"`
- **Attribute:** `data-theme="dark"` or `data-theme="light"` on `<html>` element
- **Dark is the hero mode:** The design is dark-first. Light mode is fully supported.

## Implementation

### Root Layout
```tsx
// src/components/ui/ThemeProvider.tsx
// Reads localStorage on mount, applies data-theme to <html>,
// tracks prefers-color-scheme when in "system" mode.
// Exposes useTheme() → { theme: 'dark' | 'light' | 'system', setTheme }

// src/main.tsx
<ThemeProvider>
  <App />
</ThemeProvider>
```

### Theme Toggle
```tsx
function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const order = ['system', 'light', 'dark'] as const
  const cycle = () => setTheme(order[(order.indexOf(theme) + 1) % order.length])

  return (
    <button onClick={cycle} title={`Theme: ${theme}`}>
      {theme === 'dark' ? <Moon size={14} /> : theme === 'light' ? <Sun size={14} /> : <Monitor size={14} />}
    </button>
  )
}
```

## Color Token Mapping

All colors use CSS custom properties that switch between light and dark:

```css
/* CSS custom properties — applied via data-theme attribute on <html> */

[data-theme="dark"] {
  --bg-base:       #0a0a0a;
  --bg-surface:    #111111;
  --bg-elevated:   #1a1a1a;
  --bg-overlay:    #222222;
  --bg-hover:      #2a2a2a;
  --border:        #2a2a2a;
  --border-soft:   #1f1f1f;
  --fg-1:          #f5f5f5;   /* primary text */
  --fg-2:          #a3a3a3;   /* secondary text */
  --fg-3:          #666666;   /* muted text */
  --fg-4:          #3d3d3d;   /* disabled / separator */
  --accent-subtle: #1e1e1e;   /* active item background */
  --accent-border: #333333;   /* active item border */
  --success:       #22c55e;
  --warning:       #f59e0b;
  --danger:        #ef4444;
  --info:          #3b82f6;
}

[data-theme="light"] {
  --bg-base:       #f5f5f5;
  --bg-surface:    #ffffff;
  --bg-elevated:   #fafafa;
  --bg-overlay:    #f0f0f0;
  --bg-hover:      #ebebeb;
  --border:        #e5e5e5;
  --border-soft:   #efefef;
  --fg-1:          #0a0a0a;
  --fg-2:          #525252;
  --fg-3:          #a3a3a3;
  --fg-4:          #d4d4d4;
  --accent-subtle: #f0f0f0;
  --accent-border: #d4d4d4;
  --success:       #16a34a;
  --warning:       #d97706;
  --danger:        #dc2626;
  --info:          #2563eb;
}
```

## Dark Mode Rules

### Status Colors Stay Fixed
Status colors (active/green, idle/yellow, offline/red) do NOT change between modes — they reduce saturation slightly for eye comfort:

```css
:root {
  --status-active: 142 76% 36%;
}
.dark {
  --status-active: 142 60% 45%;     /* Slightly brighter, less saturated */
}
```

### Charts in Dark Mode
- Background: transparent (inherits card background)
- Grid lines: `stroke-muted` (auto-adjusts)
- Text: `fill-muted-foreground` (auto-adjusts)
- Data colors: same hues, +10% lightness in dark mode

### Images and Avatars
- Employee avatars: no change
- Brand logos: provide dark variant or use `filter: brightness(0) invert(1)` for monochrome logos
- Illustrations/empty states: provide dark variant or use muted-foreground color

### Glass Surfaces in Light Mode

Glass surfaces use different opacity values in light mode:
- Dark: `rgba(10, 10, 15, 0.85)` — frosted dark glass
- Light: `rgba(255, 255, 255, 0.7)` — frosted white glass
- `backdrop-filter: blur(16px)` remains the same
- Violet glow effects use lower opacity in light mode (`0.1` vs `0.25`)

### Shadows in Dark Mode
Shadows are invisible on dark backgrounds. Compensate with brighter borders:

```css
.dark {
  /* Floating elements get visible borders instead of relying on shadow */
  --popover-border: hsl(217 33% 20%);
}
```

## Testing Dark Mode

- Toggle in Storybook via `next-themes` decorator
- Playwright: set `colorScheme: 'dark'` in config for dark mode E2E screenshots
- Visual regression: capture both modes

## Related

- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — tenant color customization
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — full color system
- [[frontend/design-system/foundations/elevation|Elevation]] — shadow behavior in dark mode
