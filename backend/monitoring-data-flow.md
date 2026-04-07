# Monitoring Data Flow (Frontend)

## How Workforce Intelligence Data Reaches the UI

```
Desktop Agent → Agent Gateway → Activity Monitoring → Daily Summary
                                                          │
                                                          ▼
SignalR push ←── Exception Engine ←── Evaluates snapshots + presence
     │
     ▼
Frontend Dashboard ←── TanStack Query ←── REST API (aggregated data)
```

## Data Sources by Page

| Page | API Endpoint | Data Source | Refresh |
|:-----|:-------------|:-----------|:--------|
| Live Dashboard | `GET /workforce/presence/live` | WorkforcePresence | SignalR `workforce-live` |
| Employee Activity | `GET /activity/summary/{id}` | ActivityMonitoring | 30s polling |
| Activity Snapshots | `GET /activity/snapshots/{id}` | ActivityMonitoring | 30s polling |
| App Usage | `GET /activity/apps/{id}` | ActivityMonitoring | On page load |
| Exceptions | `GET /exceptions/alerts` | ExceptionEngine | SignalR `exception-alerts` |
| Daily Report | `GET /analytics/daily/{id}` | ProductivityAnalytics | On page load |
| Workforce Snapshot | `GET /analytics/workforce` | ProductivityAnalytics | On page load |
| Monitoring Settings | `GET /settings/monitoring` | Configuration | On page load |

## Key Data Types (TypeScript)

```typescript
interface WorkforceStatus {
  totalEmployees: number;
  activeCount: number;
  idleCount: number;
  onLeaveCount: number;
  absentCount: number;
  departmentBreakdown: DepartmentStatus[];
}

interface ActivityDailySummary {
  employeeId: string;
  date: string;
  totalActiveMinutes: number;
  totalIdleMinutes: number;
  totalMeetingMinutes: number;
  activePercentage: number;
  topApps: AppUsage[];
  intensityAvg: number;
}

interface ExceptionAlert {
  id: string;
  employeeId: string;
  employeeName: string;
  ruleName: string;
  severity: 'info' | 'warning' | 'critical';
  summary: string;
  triggeredAt: string;
  status: 'new' | 'acknowledged' | 'dismissed' | 'escalated';
}

interface MonitoringToggles {
  activityMonitoring: boolean;
  applicationTracking: boolean;
  screenshotCapture: boolean;
  meetingDetection: boolean;
  deviceTracking: boolean;
  identityVerification: boolean;
  biometric: boolean;
}
```

## Empty States

When monitoring is disabled (tenant or employee level), show appropriate empty states:

```tsx
function ActivitySection({ employeeId }: { employeeId: string }) {
  const { data, isLoading } = useActivitySummary(employeeId, today);
  
  if (isLoading) return <Skeleton />;
  
  if (!data) {
    return (
      <EmptyState
        icon={<MonitorOff />}
        title="Activity monitoring not enabled"
        description="Activity tracking is not enabled for this employee."
      />
    );
  }
  
  return <ActivityDashboard data={data} />;
}
```

## Related

- [[activity-monitoring]] — activity monitoring module
- [[agent-gateway]] — agent data ingestion
- [[data-ingestion]] — ingestion feature
- [[raw-data-processing]] — raw buffer processing
- [[daily-aggregation]] — daily summary aggregation
- [[exception-engine]] — exception detection from data
