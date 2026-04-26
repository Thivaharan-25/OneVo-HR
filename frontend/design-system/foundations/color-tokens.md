# Color Tokens

## CSS Custom Properties

All colors defined as CSS custom properties for light/dark mode support.

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

## Semantic Color Usage

| Purpose | Token |
|:--------|:------|
| Page background | `bg-[var(--bg-base)]` |
| Card / panel surface | `bg-[var(--bg-surface)]` |
| Elevated surface | `bg-[var(--bg-elevated)]` |
| Hover state | `bg-[var(--bg-hover)]` |
| Primary text | `text-[var(--fg-1)]` |
| Secondary text | `text-[var(--fg-2)]` |
| Muted / label text | `text-[var(--fg-3)]` |
| Separator / disabled | `text-[var(--fg-4)]` |
| Border | `border-[var(--border)]` |
| Soft border | `border-[var(--border-soft)]` |
| Active item bg | `bg-[var(--accent-subtle)]` |
| Active item border | `border-[var(--accent-border)]` |
| Online / success | `text-[var(--success)]` |
| Warning | `text-[var(--warning)]` |
| Error / critical | `text-[var(--danger)]` |
| Info | `text-[var(--info)]` |

## Gradients

| Name | Value | Usage |
|:-----|:------|:------|
| Chart fill | `linear-gradient(180deg, #7c3aed20, transparent)` | Area chart fills |

## Brand & Shell Tokens

These tokens are used directly in the shell navigation components (rail, panel, topbar). They are NOT part of the semantic `[data-theme]` system — they are hardcoded constants because the shell has a fixed visual identity that does not vary by theme.

### Accent (OneVo Purple)

| Token | Value | Usage |
|:------|:------|:------|
| `--accent-600` | `#5B4FE8` | Active panel item text, primary buttons, focus rings |
| `--accent-400` | `#8C86F2` | Active panel item text in dark mode |
| `--accent-100` | `#ECEAFD` | Active panel item background in light mode |
| accent dark bg | `rgba(91,79,232,0.20)` | Active panel item background in dark mode |

```css
/* Tailwind usage */
text-[#5B4FE8]           /* active panel item, light */
text-[#8C86F2]           /* active panel item, dark */
bg-[#ECEAFD]             /* active panel item bg, light */
bg-[rgba(91,79,232,0.20)] /* active panel item bg, dark */
```

### Neutral Scale (Shell UI)

| Token | Value | Usage |
|:------|:------|:------|
| `--neutral-800` | `#1E2140` | Panel title, topbar entity name (light) |
| `--neutral-700` | `#353A5E` | — |
| `--neutral-600` | `#4C5278` | Panel head button hover (light) |
| `--neutral-500` | `#6B7194` | Panel item default text (light) |
| `--neutral-400` | `#9499B0` | Panel head button default, topbar icons (light) |
| `--neutral-300` | `#C8CADC` | Topbar breadcrumb separator, search kbd (light) |
| `--neutral-200` | `#E2E3EA` | Topbar border, topbar divider (light) |
| `--neutral-100` | `#EDEEF2` | Shell body background (light) |
| `--neutral-50` | `#F4F5F8` | Topbar search background, hover backgrounds (light) |

### Shell Component Surfaces

| Name | Value | Usage |
|:-----|:------|:------|
| Rail background | `#17181F` | Icon rail — same in light AND dark mode |
| Panel background (light) | `#FAF9F6` | Expansion panel in light mode — warm off-white |
| Panel background (dark) | `#000000` | Expansion panel in dark mode — pure black |
| Panel border (light) | `#E8E8EC` | Expansion panel border in light mode |
| Panel head border (light) | `#EEEDE9` | Separator between panel head and body |
| Panel hover (light) | `#EEECEA` | Panel item and head button hover background |
| Topbar bg (light) | `#FFFFFF` | Topbar surface in light mode |
| Topbar bg (dark) | `#17181F` | Topbar surface in dark mode (same as rail) |
| Content bg (dark) | `#111118` | Main content area in dark mode |
| Shell body (dark) | `#0A0A0D` | Page base background in dark mode |

### Gradients

| Name | Value | Usage |
|:-----|:------|:------|
| User avatar (rail) | `linear-gradient(135deg, #C9A96E, #E8C98A)` | Bottom avatar in the icon rail |
| User avatar (topbar) | `linear-gradient(135deg, #5B4FE8, #8C86F2)` | Avatar chip in topbar right |

## Related

- [[frontend/design-system/components/component-catalog|Component Catalog]] — component library
- [[frontend/design-system/foundations/typography|Typography]] — type scale
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — tenant color customization
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — page layouts
