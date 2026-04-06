# WEEK3: Activity Monitoring Module

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 3
**Sprint:** Week 3 (Apr 21-25)
**Module:** ActivityMonitoring

## Description

Implement the activity data pipeline: raw buffer ingestion, snapshot processing, app usage tracking, meeting detection, screenshot management, daily summary aggregation, and application categorization.

## Acceptance Criteria

### Data Pipeline
- [ ] `activity_raw_buffer` table — partitioned daily via `pg_partman`, batch INSERT via `COPY`/`unnest()`
- [ ] `ProcessRawBufferJob` Hangfire job (every 2 min) — parse raw → snapshots + app usage + meetings
- [ ] `activity_snapshots` table — partitioned monthly, 90-day retention
- [ ] Intensity score calculation: `(keyboard + mouse) / max_expected * 100`, capped at 100
- [ ] `application_usage` table — time per app per day
- [ ] Window title hashing (SHA-256) — never store raw titles
- [ ] `meeting_sessions` table — Phase 1: process name matching (Teams.exe, zoom.exe)
- [ ] Camera/mic detection via process inspection
- [ ] `device_tracking` table — laptop active minutes, estimated mobile
- [ ] `activity_daily_summary` table — INSERT or UPDATE on conflict `(tenant_id, employee_id, date)`

### Screenshots
- [ ] `screenshots` table — metadata only, files in blob storage via `IFileService`
- [ ] Screenshot trigger types: `scheduled`, `random`, `manual`
- [ ] `PurgeExpiredScreenshotsJob` (daily 4 AM) — per tenant retention policy
- [ ] Screenshot classified as RESTRICTED data

### Application Categories
- [ ] `application_categories` table — tenant-configurable
- [ ] Glob pattern matching (e.g., `*chrome*`)
- [ ] `is_productive` flag (nullable — uncategorized apps)

### Aggregation & Retention
- [ ] `AggregateDailySummaryJob` (every 30 min + EOD)
- [ ] `PurgeRawBufferJob` (daily 3 AM) — drop partitions > 48h
- [ ] `PurgeExpiredSnapshotsJob` (monthly) — drop partitions > 90 days
- [ ] `IActivityMonitoringService` public interface implementation

### Security
- [ ] Feature toggle check before processing — `IConfigurationService`
- [ ] Never log window titles or app names — only counts
- [ ] Domain events: `ActivitySnapshotReceived`, `DailySummaryAggregated`
- [ ] Unit tests ≥80% coverage

## Related Files

- [[activity-monitoring]] — module architecture, data pipeline diagram
- [[agent-gateway]] — data source
- [[configuration]] — feature toggles
- [[exception-engine]] — consumes snapshots
- [[data-classification]] — screenshots are RESTRICTED
