# Dark Mode

## Strategy

- **Default:** System preference (`prefers-color-scheme`)
- **User override:** Toggle in sidebar bottom + user dropdown. Overrides system when set.
- **Persistence:** `localStorage` key `theme` — values: `system` | `light` | `dark`
- **Tenant default:** Tenant branding can set a default theme. User override still takes precedence.
- **Dark is the hero mode:** The "Selective Drama" glass aesthetic is designed dark-first. Light mode is fully supported but the brand showcase is dark.

## Implementation

### Root Layout
```tsx
// app/layout.tsx
import { ThemeProvider } from 'next-themes';

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        style={{
          fontFamily: 'var(--font-body)',
        }}
      >
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

CSS variable font setup:

```css
:root {
  --font-display: 'Outfit', sans-serif;   /* headings, KPI numbers */
  --font-body: 'Geist', sans-serif;       /* body text, UI labels */
  --font-mono: 'Geist Mono', monospace;   /* code, IDs, timestamps */
}
```

### Theme Toggle
```tsx
function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme('light')}>Light</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('dark')}>Dark</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('system')}>System</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

## Color Token Mapping

All colors use CSS custom properties that switch between light and dark:

```css
:root {
  --background: 0 0% 100%;          /* White */
  --foreground: 222.2 84% 4.9%;     /* Near-black */
  --card: 0 0% 100%;
  --muted: 210 40% 96.1%;
  --border: 214.3 31.8% 91.4%;
  --sidebar-background: 0 0% 98%;
}

.dark {
  --background: 222.2 84% 4.9%;     /* Near-black */
  --foreground: 210 40% 98%;        /* Near-white */
  --card: 222.2 84% 6%;             /* Slightly lighter than bg */
  --muted: 217.2 32.6% 12%;
  --border: 217.2 32.6% 17.5%;
  --sidebar-background: 222.2 84% 3.5%;
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
