# Spacing System

## Base Scale

All spacing derives from a **4px base unit** via Tailwind's default scale. ONEVO favors compact, information-dense layouts — default to smaller spacing, open up only for breathing room between major sections.

| Token | Value | Tailwind | Usage |
|:------|:------|:---------|:------|
| `0.5` | 2px | `p-0.5`, `gap-0.5` | Icon padding, tight inline spacing |
| `1` | 4px | `p-1`, `gap-1` | Badge padding, compact list items |
| `1.5` | 6px | `p-1.5`, `gap-1.5` | Small button padding, tag gaps |
| `2` | 8px | `p-2`, `gap-2` | Default inline spacing, form field gaps |
| `3` | 12px | `p-3`, `gap-3` | Card padding (compact), table cell padding |
| `4` | 16px | `p-4`, `gap-4` | Standard card padding, section gaps |
| `5` | 20px | `p-5`, `gap-5` | Dialog padding |
| `6` | 24px | `p-6`, `gap-6` | Page content padding, card body |
| `8` | 32px | `p-8`, `gap-8` | Section separation within a page |
| `10` | 40px | `p-10` | Large empty state padding |
| `12` | 48px | `p-12` | Auth page centering |
| `16` | 64px | `py-16` | Hero spacing (rare) |

## Layout Spacing

| Context | Spacing | Class |
|:--------|:--------|:------|
| Page content padding | 24px | `p-6` |
| Between page header and content | 24px | `space-y-6` |
| Between KPI cards | 16px | `gap-4` |
| Between sections on a page | 32px | `space-y-8` |
| Between form fields | 16px | `space-y-4` |
| Between form field and label | 6px | `space-y-1.5` |
| Table cell horizontal padding | 16px | `px-4` |
| Table cell vertical padding | 12px | `py-3` |
| Sidebar item padding | `8px 12px` | `px-3 py-2` |
| Sidebar section gap | 16px | `space-y-4` |
| Topbar height | 56px | `h-14` |
| Sidebar rail width | 64px | `w-16` |
| Sidebar panel width | 220px | `w-[220px]` |
| Sidebar total (rail + panel) | 284px | — |
| Breadcrumb to content | 16px | `mb-4` |

## Component Internal Spacing

### Cards
```tsx
// Standard card
<Card className="p-6">              {/* 24px all sides */}
  <CardHeader className="pb-4">     {/* 16px bottom */}
    <CardTitle />
    <CardDescription />
  </CardHeader>
  <CardContent className="space-y-4"> {/* 16px between children */}
    ...
  </CardContent>
</Card>

// Compact card (KPI)
<Card className="p-4">              {/* 16px all sides */}
  <div className="space-y-1">       {/* 4px between metric and label */}
    <p className="text-xs text-muted-foreground">Active</p>
    <p className="text-2xl font-bold">342</p>
  </div>
</Card>
```

### Tables
```tsx
// Dense table (default for admin views)
<Table>
  <TableHeader>
    <TableRow>
      <TableHead className="px-4 py-3 text-xs">Name</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell className="px-4 py-2.5 text-sm">John Doe</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Forms
```tsx
// Standard form layout
<form className="space-y-4">         {/* 16px between fields */}
  <div className="space-y-1.5">     {/* 6px between label and input */}
    <Label>Employee Name</Label>
    <Input />
    <p className="text-xs text-muted-foreground">As shown on official documents</p>
  </div>

  <div className="grid grid-cols-2 gap-4"> {/* 16px gap for side-by-side fields */}
    <div className="space-y-1.5">
      <Label>Start Date</Label>
      <DatePicker />
    </div>
    <div className="space-y-1.5">
      <Label>Department</Label>
      <Select />
    </div>
  </div>
</form>
```

## Responsive Spacing

Content padding reduces on smaller screens:

```tsx
<main className="p-4 md:p-6">       {/* 16px mobile, 24px desktop */}
  <div className="space-y-4 md:space-y-6 lg:space-y-8">
    ...
  </div>
</main>
```

## Related

- [[frontend/design-system/foundations/typography|Typography]] — type scale
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — page layouts
- [[frontend/design-system/components/component-catalog|Composed Components]] — component spacing
