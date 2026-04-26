# Iconography

## Icon Library

**Lucide React** — the icon set used by shadcn/ui. Consistent stroke weight, MIT licensed, tree-shakeable.

```tsx
import { Users, Calendar, BarChart3, AlertTriangle } from 'lucide-react';
```

## Size Scale

| Size | Class | Pixels | Usage |
|:-----|:------|:-------|:------|
| `xs` | `h-3 w-3` | 12px | Inline with caption text, badge icons |
| `sm` | `h-4 w-4` | 16px | Default — buttons, menu items, table actions, form labels |
| `md` | `h-5 w-5` | 20px | Stat card icons, page feature icons |
| `lg` | `h-6 w-6` | 24px | Page header icons, empty state illustrations |
| `xl` | `h-8 w-8` | 32px | Feature cards, onboarding steps |
| `2xl` | `h-12 w-12` | 48px | Empty state hero, error page |

**Default size is `sm` (`h-4 w-4`)**. Use this unless there's a specific reason for larger.

## Icon Map by Domain

### Navigation — Rail Pillar Icons

Exact Lucide icon names for the 9 rail pillars, in display order:

| Pillar | Lucide Import | Has Panel |
|:-------|:-------------|:----------|
| Home | `House` | No |
| Inbox | `Inbox` | No |
| People | `Users` | Yes |
| Workforce | `LayoutDashboard` | Yes |
| Org | `Network` | Yes |
| Calendar | `Calendar` | Yes |
| Chat | `MessageCircle` | No |
| Admin | `Shield` | Yes |
| Settings | `Settings` | Yes |

Rail icon size: **16×16px**, stroke-width: **1.6** (fixed — does not change on active state).

### Navigation — Panel Sub-Item Icons

See [[frontend/design-system/components/expansion-panel|Expansion Panel]] for the complete per-pillar icon map. Panel icons are **13×13px**, stroke-width **1.6**.

### Status
| Icon | Name | Context |
|:-----|:-----|:--------|
| `CheckCircle2` | Success | Approved, completed, active |
| `XCircle` | Error | Rejected, failed, critical |
| `AlertCircle` | Warning | Needs attention, approaching limit |
| `Info` | Information | Informational state |
| `Clock` | Pending | Awaiting action |
| `Loader2` | Loading | Spinner (add `animate-spin`) |
| `Circle` | Neutral | Status dot (filled with status color) |

### Actions
| Icon | Name | Context |
|:-----|:-----|:--------|
| `Plus` | Create | Add new item |
| `Pencil` | Edit | Modify existing |
| `Trash2` | Delete | Remove item |
| `Download` | Export | Download file/report |
| `Upload` | Import | Upload file |
| `Search` | Search | Search input |
| `Filter` | Filter | Filter controls |
| `MoreHorizontal` | More | Row action menu |
| `ChevronDown` | Expand | Dropdown/accordion |
| `ExternalLink` | External | Links to external resource |
| `Copy` | Copy | Copy to clipboard |
| `Eye` | View | View/preview |
| `EyeOff` | Hide | Hide/mask data |
| `RefreshCw` | Refresh | Retry/refresh |

## Usage Patterns

### Button with Icon
```tsx
// Icon before label (default)
<Button>
  <Plus className="h-4 w-4 mr-2" />
  Add Employee
</Button>

// Icon-only button (use tooltip)
<Tooltip>
  <TooltipTrigger asChild>
    <Button variant="ghost" size="icon">
      <Pencil className="h-4 w-4" />
    </Button>
  </TooltipTrigger>
  <TooltipContent>Edit</TooltipContent>
</Tooltip>
```

### Shell Navigation Icon Sizes by Zone

| Zone | Icon size | Stroke-width | Notes |
|:-----|:----------|:-------------|:------|
| Rail pillar icon | **16×16px** | **1.6** | Never changes on active — no stroke-width toggle |
| Rail item label | — | — | 9px text below icon, not an icon |
| Expansion panel item | **13×13px** | **1.6** | Same in all states |
| Panel head buttons (close/+) | 12px / 14px | 1.75 / 2 | Close is 12px, Plus is 14px |
| Panel create dropdown items | **13×13px** | 1.75 | |
| Topbar buttons (bell, help, theme) | **14×14px** | **1.75** | Right-side icon buttons |
| Topbar entity chevron | 11×11px | 2 | |
| Topbar search icon | 13×13px | 1.75 | |

### Rail Item (Correct Implementation)
```tsx
// Rail icon — strokeWidth is ALWAYS 1.6, does not change on active
<button className={cn(
  'w-[42px] flex flex-col items-center justify-center gap-1 py-[7px] pb-[6px] rounded-[8px]',
  'transition-[background,color] duration-[120ms]',
  isActive
    ? 'bg-white/10 text-white/95'
    : 'text-white/[0.28] hover:bg-white/[0.07] hover:text-white/[0.72]'
)}>
  <Users size={16} strokeWidth={1.6} aria-hidden="true" />
  <span className="text-[9px] font-medium leading-none">{label}</span>
</button>
```

### Status with Icon
```tsx
<div className="flex items-center gap-1.5">
  <CheckCircle2 className="h-4 w-4 text-green-600" />
  <span className="text-sm">Approved</span>
</div>
```

### Empty State
```tsx
<div className="flex flex-col items-center py-12">
  <CalendarDays className="h-12 w-12 text-muted-foreground/50 mb-4" />
  <p className="text-sm font-medium">No leave requests</p>
  <p className="text-xs text-muted-foreground mt-1">Leave requests will appear here once submitted</p>
</div>
```

## Accessibility

- Icon-only buttons **must** have `aria-label` or a `<Tooltip>`
- Decorative icons (next to text that says the same thing) get `aria-hidden="true"`
- Status icons that convey meaning should have `role="img"` and `aria-label`

```tsx
// Decorative (label already says "Approved")
<CheckCircle2 className="h-4 w-4" aria-hidden="true" />
<span>Approved</span>

// Meaningful (no text label)
<AlertTriangle className="h-4 w-4 text-yellow-600" role="img" aria-label="Warning" />
```

## Related

- [[frontend/design-system/components/component-catalog|Primitive Components]] — button icon placement
- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]] — sidebar icons
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — status icon colors
