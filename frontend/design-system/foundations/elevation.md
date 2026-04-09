# Elevation & Shadow System

## Shadow Scale

ONEVO uses a restrained elevation system — flat by default, shadows only for floating elements. The UI should feel grounded, not stacked.

| Level | Tailwind | CSS | Usage |
|:------|:---------|:----|:------|
| 0 (flat) | — | `none` | Cards, table rows, sidebar items (default) |
| 1 (subtle) | `shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Hover state on cards, dropdown triggers |
| 2 (raised) | `shadow` | `0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)` | Popovers, dropdown menus, date pickers |
| 3 (floating) | `shadow-md` | `0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)` | Dialogs, command palette, notification panel |
| 4 (overlay) | `shadow-lg` | `0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)` | Sheets, full modals |

## Glass Surfaces (Selective Drama)

Glassmorphism is reserved for **hero elements only** — sidebar, topbar, KPI stat cards, modals, quick search.

### Glass Variants

| Variant | Background | Blur | Border | Usage |
|:--------|:-----------|:-----|:-------|:------|
| `glass` | `rgba(10,10,15,0.85)` | `blur(16px)` | `rgba(255,255,255,0.06)` | Sidebar, topbar |
| `glass-light` | `rgba(20,20,28,0.9)` | `blur(16px)` | `rgba(255,255,255,0.06)` | Expansion panel |
| `glass-glow` | Same as `glass` | `blur(16px)` | `rgba(124,58,237,0.3)` + `box-shadow: 0 0 16px rgba(124,58,237,0.15)` | Active/important glass elements |

### Light Theme Glass

```css
.light .glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 0, 0, 0.06);
}
```

### High Contrast Fallback

```css
@media (prefers-contrast: more) {
  .glass {
    background: var(--bg-raised);
    backdrop-filter: none;
    border: 1px solid var(--border-default);
  }
}
```

### What Does NOT Get Glass

- DataTables and list pages → flat bordered cards
- Form fields and detail page sections → flat bordered cards
- Activity feeds and timelines → flat bordered cards
- Charts containers on non-dashboard pages → flat bordered cards

These use the standard flat surface:

```css
.flat {
  background: var(--bg-raised);
  border: 1px solid var(--border-default);
  border-radius: 8px;
}
```

## Elevation Rules

### Cards — Selective
- **Glass cards:** KPI stat cards on dashboard, sidebar panels, modals
- **Flat cards:** Data tables, form sections, detail page sections, activity feeds
- Flat cards use borders (`border`) not shadows. Shadows only for floating UI
- Glass cards on dashboard get violet glow when they represent actionable items (pending approvals, alerts)

### Interactive Elevation
Cards and rows gain subtle elevation on hover to indicate interactivity:

```tsx
// Clickable card (KPI, employee card)
<Card className="border bg-card transition-shadow hover:shadow-sm cursor-pointer">

// Table row with click handler
<TableRow className="transition-colors hover:bg-muted/50 cursor-pointer">
```

### Floating UI — Consistent Shadow

All floating UI (popovers, dropdowns, command palette, tooltips) use the same shadow level for visual consistency:

```tsx
// Popover content
<PopoverContent className="shadow-md border bg-popover">

// Dropdown menu
<DropdownMenuContent className="shadow-md border bg-popover">

// Command palette
<CommandDialog className="shadow-lg border bg-popover">

// Tooltip
<TooltipContent className="shadow-sm border bg-popover">
```

### Dialog / Sheet Overlay

Modals and sheets use a backdrop overlay + shadow:

```tsx
// Dialog
<DialogOverlay className="bg-black/50 backdrop-blur-sm" />
<DialogContent className="shadow-lg border bg-background">

// Sheet (slide-over)
<SheetOverlay className="bg-black/30" />
<SheetContent className="shadow-lg border-l bg-background">
```

## Z-Index Scale

Controlled z-index to prevent stacking conflicts:

| Layer | Z-Index | Elements |
|:------|:--------|:---------|
| Base | `z-0` | Page content |
| Sticky | `z-10` | Sticky table headers, filter bars |
| Sidebar | `z-20` | Sidebar navigation |
| Topbar | `z-30` | Top navigation bar |
| Dropdown | `z-40` | Popovers, dropdown menus, tooltips |
| Modal | `z-50` | Dialogs, sheets, command palette |
| Toast | `z-[100]` | Toast notifications (always on top) |
| Network Banner | `z-[110]` | Offline/reconnecting banner |

## Dark Mode Elevation

In dark mode, shadows are less visible. Compensate with subtle border brightness:

```css
.dark {
  /* Floating elements get slightly brighter borders in dark mode */
  --popover-border: hsl(217 33% 17%);  /* Slightly lighter than background */
}
```

## Related

- [[frontend/design-system/foundations/spacing|Spacing]] — spacing scale
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — surface colors
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — page structure
