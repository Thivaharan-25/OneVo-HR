# Monitoring Data Flow (Frontend)

## How Monitoring Data Reaches the UI

```
Desktop Agent ? Agent Gateway ? Activity Monitoring ? Daily Summary
                                                          ¦
                                                          ?
SignalR push <- Notifications <- Phase 1 lightweight alert detection <- snapshots + presence
     ¦
     ?
Frontend Dashboard ?-- TanStack Query ?-- REST API (aggregated data)
```

## Data Sources by Page

| Page | API Endpoint | Data Source | Refresh |
|:-----|:-------------|:-----------|:--------|
| Live Dashboard | `GET /monitoring/presence/live` | TimeAttendance | SignalR `monitoring-live` |
| Employee Activity | `GET /activity/summary/{id}` | ActivityMonitoring | 30s polling |
| Activity Snapshots | `GET /activity/snapshots/{id}` | ActivityMonitoring | 30s polling |
| App Usage | `GET /activity/apps/{id}` | ActivityMonitoring | On page load |
| Monitoring Alerts | `GET /monitoring/alerts` | Monitoring Alerts | Notifications `notifications-{userId}` |
| Daily Report | `GET /analytics/daily/{id}` | ProductivityAnalytics | On page load |
| Monitoring Snapshot | `GET /analytics/monitoring` | ProductivityAnalytics | On page load |
| Monitoring Settings | `GET /settings/monitoring` | Configuration | On page load |

## Key Data Types (TypeScript)

```typescript
interface MonitoringStatus {
  totalEmployees: number;
  activeCount: number;
  idleCount: number;
  onTimeOffCount: number;
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
  productiveAppMinutes: number;
  personalAppMinutes: number;
  unknownAppMinutes: number;
  focusMinutes: number;
  activityScore: number;
  dataCoveragePercentage: number;
  topApps: AppUsage[];
  intensityAvg: number;
}

interface DailyEmployeeReport {
  employeeId: string;
  date: string;
  activePercentage: number;
  productiveAppHours: number;
  focusHours: number;
  activityScore: number;
  workOutputScore?: number;
  productivityScore?: number;
  productivityScoreBasis: 'composite' | 'activity_only' | 'worksync_only' | 'insufficient_data';
  dataCoveragePercentage: number;
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

## Phase 1 Monitoring Alerts

Phase 1 monitoring alerts do not use configurable Exception Engine rules or Workflow Engine routing.

Phase 1 alert producers are:
- **Identity Verification** — photo/biometric verification failures and expirations
- **Activity Monitoring** — non-allowed app usage violations, idle threshold breaches
- **Discrepancy Engine** — unaccounted time gaps after day close
- **Work Location Evidence** — work location mismatch beyond grace period

They create lightweight alert/notification records and route them through Notifications/Inbox. **Monitoring Policy** controls recipient resolution:

**When `monitoring_alert_recipient_resolver` = `management_coverage_availability_chain` (default):**
1. Load active date-effective management coverage assignments for the employee
2. Order eligible responsible people by configured coverage priority / responsibility weight
3. Filter to users with the required alert permission (e.g., `monitoring:alerts:read`, `monitoring:alerts:resolve`, `verification:review`)
4. Check availability: scheduled to work, clocked in / present, not on approved leave, not marked unavailable
5. If a responsible person is scheduled but has not reached scheduled start time + `monitoring_alert_wait_for_scheduled_recipient_grace_minutes` (default: 15), wait before skipping
6. If no eligible available person exists, follow `monitoring_alert_unresolved_routing_action` (default: `create_routing_issue`)

**When `monitoring_alert_recipient_resolver` = `reporting_manager`:**
1. Resolve reporting manager from position hierarchy
2. Check required alert permission and availability (same rules as above)
3. If unavailable and `monitoring_alert_fallback_to_management_coverage_chain` is enabled, fall back to management coverage availability chain
4. If still unresolved, follow `monitoring_alert_unresolved_routing_action`

Phase 2 may move alert evaluation into configurable Exception Engine rules and Workflow/Automation routing.

---

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring]] — activity monitoring module
- [[modules/agent-gateway/overview|Agent Gateway]] — agent data ingestion
- [[modules/agent-gateway/data-ingestion/overview|Data Ingestion]] — ingestion feature
- [[modules/activity-monitoring/raw-data-processing/overview|Raw Data Processing]] — raw buffer processing
- [[modules/activity-monitoring/daily-aggregation/overview|Daily Aggregation]] — daily summary aggregation
- [[modules/exception-engine/overview|Exception Engine]] — Phase 2 configurable exception detection from data
