# Data Visualization

## Chart Library Choice

| Library | Use For |
|:--------|:--------|
| **Recharts** | Standard charts (line, bar, pie, area, composed) |
| **Tremor** | Dashboard blocks (KPI cards, sparklines, progress bars, donut) |

## Chart Types by Page

### Live Workforce Dashboard

| Visual | Type | Library | Data |
|:-------|:-----|:--------|:-----|
| Active vs Idle vs Leave | Donut chart | Tremor | WorkforceStatus |
| Department breakdown | Horizontal bar | Recharts | departmentBreakdown[] |
| Activity heatmap | Custom grid | Custom (Tailwind) | Hourly intensity per department |
| Active exceptions | List with severity badges | shadcn Table | ExceptionAlert[] |

### Employee Activity Detail

| Visual | Type | Library | Data |
|:-------|:-----|:--------|:-----|
| Day timeline | Custom horizontal bar | Custom (div-based) | Active/idle/break/meeting segments |
| Intensity over time | Area chart | Recharts | Hourly intensity scores |
| App usage breakdown | Horizontal bar | Recharts | ApplicationUsage[] |
| Meeting timeline | Event list | Custom | MeetingSession[] |
| Device split | Pie chart | Tremor | laptop% vs mobile% |

### Reports Page

| Visual | Type | Library | Data |
|:-------|:-----|:--------|:-----|
| Trend line (active%) | Line chart | Recharts | Daily/weekly active_percentage |
| Week-over-week | Grouped bar | Recharts | This week vs last week |
| Department comparison | Bar chart | Recharts | Department averages |
| Exception trend | Area chart | Recharts | Daily exception counts |

## Custom Components

### Timeline Bar

Full-day horizontal bar showing activity segments:

```
8:00  9:00  10:00  11:00  12:00  1:00  2:00  3:00  4:00  5:00
[████ active ████][idle][███ meeting ███][break][████ active ████]
```

Colors:
- Active: `bg-green-500`
- Idle: `bg-yellow-300`
- Meeting: `bg-blue-500`
- Break: `bg-gray-300`
- Offline: `bg-gray-100`

### Activity Heatmap

Grid showing hourly intensity (0-100) with color intensity mapping:

```
         8am  9am  10am  11am  12pm  1pm  2pm  3pm  4pm  5pm
Eng.     ██   ███  ████  ███   █    ██   ████  ███  ██   █
Sales    ██   ██   ███   ████  ██   ██   ███   ██   ██   █
Support  ███  ████ ████  ███   █    ███  ████  ████ ███  ██
```

Color scale: `bg-green-50` (0) → `bg-green-200` (25) → `bg-green-400` (50) → `bg-green-600` (75) → `bg-green-800` (100)

## Recharts Standard Config

```tsx
// Consistent chart styling
const chartConfig = {
  colors: {
    primary: 'hsl(var(--primary))',
    active: '#22c55e',    // green-500
    idle: '#eab308',      // yellow-500
    meeting: '#3b82f6',   // blue-500
    exception: '#ef4444', // red-500
  },
  style: {
    fontSize: 12,
    fontFamily: 'var(--font-sans)',
  },
};

// Standard responsive container
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={data}>
    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
    <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
    <YAxis tick={{ fontSize: 12 }} />
    <Tooltip />
    <Line type="monotone" dataKey="intensity" stroke={chartConfig.colors.primary} />
  </LineChart>
</ResponsiveContainer>
```

## KPI Cards (Tremor)

```tsx
// Standard KPI card pattern
<Card>
  <Text>Active Employees</Text>
  <Metric>{status.activeCount}</Metric>
  <Flex className="mt-2">
    <Text className="text-muted-foreground">
      {((status.activeCount / status.totalEmployees) * 100).toFixed(0)}% of total
    </Text>
    <BadgeDelta deltaType="increase" size="xs">+5.2%</BadgeDelta>
  </Flex>
  <SparkAreaChart data={sparkData} categories={['value']} index="time" className="mt-4 h-10" />
</Card>
```

## Related

- [[component-catalog]] — component library
- [[daily-reports]] — productivity reports
- [[workforce-snapshots]] — workforce analytics
- [[productivity-analytics]] — analytics module
- [[color-tokens]] — color system
