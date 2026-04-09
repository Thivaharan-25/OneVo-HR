# Motion & Animation

## Principles

1. **Functional, not decorative** — animations serve a purpose (state change, spatial orientation, feedback). No gratuitous motion.
2. **Fast** — dashboard users interact rapidly. Animations should feel instant, not theatrical.
3. **Respect preferences** — honor `prefers-reduced-motion`. All motion must degrade gracefully.

## Duration Scale

| Token | Duration | Usage |
|:------|:---------|:------|
| `instant` | 0ms | State toggles with no visual transition |
| `fast` | 100ms | Hover states, focus rings, button press |
| `normal` | 150ms | Dropdown open/close, tab switch, tooltip |
| `moderate` | 200ms | Sidebar expand/collapse, card expand |
| `slow` | 300ms | Dialog enter/exit, sheet slide, page transition |
| `deliberate` | 500ms | Skeleton shimmer cycle, progress bar fill |

## Easing Curves

| Name | CSS | Usage |
|:-----|:----|:------|
| `ease-out` | `cubic-bezier(0.16, 1, 0.3, 1)` | Enter animations (appearing elements) |
| `ease-in` | `cubic-bezier(0.7, 0, 0.84, 0)` | Exit animations (disappearing elements) |
| `ease-in-out` | `cubic-bezier(0.45, 0, 0.55, 1)` | Continuous motion (sidebar slide, reorder) |
| `spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Playful feedback (success checkmark, badge count bump) |

## Tailwind Config

```ts
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      transitionDuration: {
        'fast': '100ms',
        'normal': '150ms',
        'moderate': '200ms',
        'slow': '300ms',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-out': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'slide-in-bottom': {
          '0%': { transform: 'translateY(8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'pulse-dot': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        'count-bump': {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.2)' },
          '100%': { transform: 'scale(1)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 150ms ease-out',
        'fade-out': 'fade-out 100ms ease-in',
        'slide-in-right': 'slide-in-right 300ms ease-out',
        'slide-in-bottom': 'slide-in-bottom 150ms ease-out',
        'scale-in': 'scale-in 150ms ease-out',
        'shimmer': 'shimmer 2s linear infinite',
        'pulse-dot': 'pulse-dot 2s ease-in-out infinite',
        'count-bump': 'count-bump 300ms ease-out',
      },
    },
  },
};
```

## Animation Patterns

### Dialog Enter/Exit
```tsx
<DialogContent className="animate-scale-in data-[state=closed]:animate-fade-out">
```

### Sheet Slide
```tsx
<SheetContent className="animate-slide-in-right data-[state=closed]:animate-fade-out">
```

### Dropdown / Popover
```tsx
<DropdownMenuContent className="animate-slide-in-bottom">
```

### Live Status Dot
```tsx
// Pulsing green dot for "active" status
<span className="relative flex h-2 w-2">
  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
  <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
</span>
```

### Notification Badge Count
```tsx
// Bumps when count changes
<Badge className={cn("tabular-nums", countChanged && "animate-count-bump")}>
  {count}
</Badge>
```

### Skeleton Loading
```tsx
<div className="h-4 w-32 rounded bg-muted animate-shimmer bg-[length:200%_100%] bg-gradient-to-r from-muted via-muted-foreground/5 to-muted" />
```

### Sidebar Collapse

See the Sidebar Panel Expand/Collapse pattern below for the expansion panel approach used alongside the sidebar width transition:

```tsx
<aside className={cn(
  "transition-[width] duration-moderate ease-in-out",
  isOpen ? "w-[220px]" : "w-16"
)}>
```

### KPI Card Hover

```css
@keyframes card-lift {
  to { transform: translateY(-2px); }
}

.kpi-card:hover {
  animation: card-lift 150ms ease-out forwards;
  box-shadow: 0 0 20px rgba(124, 58, 237, 0.2);
  border-color: rgba(124, 58, 237, 0.3);
}
```

### Violet Shimmer (Branded Skeleton Loading)

```css
@keyframes violet-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton-violet {
  background: linear-gradient(
    90deg,
    var(--bg-raised) 25%,
    rgba(139, 92, 246, 0.08) 50%,
    var(--bg-raised) 75%
  );
  background-size: 200% 100%;
  animation: violet-shimmer 1.5s ease-in-out infinite;
}
```

### KPI Number Count-Up

```tsx
// Animated number transition on first load
<motion.span
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.4 }}
>
  {animatedValue}
</motion.span>
```

### Chart Progressive Draw

```tsx
// Line charts trace left-to-right on mount
<Area
  animationBegin={0}
  animationDuration={800}
  animationEasing="ease-out"
/>
```

### Alert Badge Pulse

```css
@keyframes alert-breathe {
  0%, 100% { box-shadow: 0 0 8px rgba(124, 58, 237, 0.2); }
  50% { box-shadow: 0 0 16px rgba(124, 58, 237, 0.4); }
}

.alert-badge {
  animation: alert-breathe 2s ease-in-out infinite;
}
```

### Page Content Enter

```css
@keyframes page-enter {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-content {
  animation: page-enter 150ms ease-out;
}
```

### Sidebar Panel Expand/Collapse

```css
.expansion-panel {
  transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1);
}

.expansion-panel[data-state="closed"] {
  transform: translateX(-100%);
}

.expansion-panel[data-state="open"] {
  transform: translateX(0);
}
```

## Reduced Motion

All animations must respect the user's OS preference:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Related

- [[frontend/design-system/foundations/elevation|Elevation]] — shadow transitions
- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]] — sidebar animation
- [[modules/performance/feedback/overview|Feedback]] — toast/loading animations
