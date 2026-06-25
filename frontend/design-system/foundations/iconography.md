# Iconography

## Icon Library

**Material Symbols** (Google) - the icon set used alongside Angular Material. Variable font-based, single HTTP request for the full library, MIT licensed.

Add to `index.html`:

```html
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
```

Use in Angular templates via Angular Material's `<mat-icon>`:

```html
<mat-icon>people</mat-icon>
<mat-icon fontVariation="FILL 1">favorite</mat-icon>
```

Or as a standalone component from `@angular/material/icon`:

```typescript
import { MatIconModule } from '@angular/material/icon';
```

## Size Scale

Use Tailwind size classes on the `<mat-icon>` element, or Angular Material's built-in `[inline]` variant:

| Size | Tailwind class | Pixels | Usage |
|:-----|:--------------|:-------|:------|
| `xs` | `text-[12px]` | 12px | Inline with caption text, badge icons |
| `sm` | `text-[16px]` | 16px | **Default** - buttons, menu items, table actions, form labels |
| `md` | `text-[20px]` | 20px | Stat card icons, page feature icons |
| `lg` | `text-[24px]` | 24px | Page header icons, empty state illustrations |
| `xl` | `text-[32px]` | 32px | Feature cards, onboarding steps |
| `2xl` | `text-[48px]` | 48px | Empty state hero, error page |

**Default size is `sm` (16px).** Use this unless there's a specific reason for larger.

## Icon Map by Domain

### Navigation - Rail Pillar Icons

Exact Material Symbol names for the rail pillars, in display order:

| Pillar | Material Symbol | Has Panel |
|:-------|:----------------|:----------|
| Home | `home` | No |
| Inbox | `inbox` | No |
| People | `group` | Yes |
| Time Off | `event_available` | Yes |
| Time & Attendance | `schedule` | Yes |
| Work | `work` | Yes |
| Calendar | `calendar_month` | Yes |
| Monitoring | `monitoring` | Yes |
| Settings | `settings` | Yes |

Rail icon size: **16px**, `font-variation-settings: 'FILL' 0, 'wght' 300`.

### Status Icons

| Icon | Material Symbol | Context |
|:-----|:----------------|:--------|
| Success | `check_circle` | Approved, completed, active |
| Error | `cancel` | Rejected, failed, critical |
| Warning | `warning` | Needs attention |
| Info | `info` | Informational state |
| Pending | `schedule` | Awaiting action |
| Loading | `progress_activity` | Spinner (add CSS rotate animation) |

### Action Icons

| Icon | Material Symbol | Context |
|:-----|:----------------|:--------|
| Create | `add` | Add new item |
| Edit | `edit` | Modify existing |
| Delete | `delete` | Remove item |
| Export | `download` | Download file/report |
| Import | `upload` | Upload file |
| Search | `search` | Search input |
| Filter | `filter_list` | Filter controls |
| More | `more_horiz` | Row action menu |
| Expand | `expand_more` | Dropdown/accordion |
| External link | `open_in_new` | Links to external resource |
| Copy | `content_copy` | Copy to clipboard |
| View | `visibility` | View/preview |
| Hide | `visibility_off` | Hide/mask data |
| Refresh | `refresh` | Retry/refresh |

## Usage Patterns

### Button with Icon

```html
<!-- Icon before label (default) -->
<button mat-raised-button color="primary">
  <mat-icon>add</mat-icon>
  Add Employee
</button>

<!-- Icon-only button - must have aria-label -->
<button mat-icon-button aria-label="Edit employee" (click)="edit()">
  <mat-icon>edit</mat-icon>
</button>

<!-- Icon-only with MatTooltip -->
<button mat-icon-button matTooltip="Edit" (click)="edit()">
  <mat-icon>edit</mat-icon>
</button>
```

### Nav Rail Item

```html
<!-- Rail icon - size and stroke controlled via CSS custom properties -->
<button class="rail-item" [class.active]="isActive()" (click)="navigate()">
  <mat-icon class="rail-icon">group</mat-icon>
  <span class="rail-label">People</span>
</button>
```

```scss
.rail-icon {
  font-size: 16px;
  width: 16px;
  height: 16px;
  font-variation-settings: 'FILL' 0, 'wght' 300;
}

.rail-item.active .rail-icon {
  font-variation-settings: 'FILL' 1, 'wght' 400;
}
```

### Status with Icon

```html
<div class="flex items-center gap-1.5">
  <mat-icon class="text-[16px] text-green-600">check_circle</mat-icon>
  <span class="text-sm">Approved</span>
</div>
```

### Empty State

```html
<div class="flex flex-col items-center py-12">
  <mat-icon class="text-[48px] text-gray-300 mb-4">calendar_month</mat-icon>
  <p class="text-sm font-medium">No Time Off requests</p>
  <p class="text-xs text-gray-500 mt-1">Time off requests will appear here once submitted</p>
</div>
```

## Accessibility

- Icon-only buttons **must** have `aria-label` or `matTooltip`
- Decorative icons (next to text that says the same thing) get `aria-hidden="true"`
- Status icons that convey meaning should have `aria-label`

```html
<!-- Decorative - label already says "Approved" -->
<mat-icon aria-hidden="true">check_circle</mat-icon>
<span>Approved</span>

<!-- Meaningful - no text label -->
<mat-icon aria-label="Warning" role="img">warning</mat-icon>
```

## Related

- [[frontend/design-system/components/component-catalog|Component Catalog]] - button icon placement
- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]] - rail icon spec
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] - status icon colours
