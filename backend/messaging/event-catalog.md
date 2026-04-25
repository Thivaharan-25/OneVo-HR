# Event Catalog: ONEVO

All events published and consumed across modules. Phase 1 uses **RabbitMQ via MassTransit** for cross-module integration events and **MediatR `INotification`** for intra-module domain events only (see [[backend/messaging/exchange-topology|Exchange Topology]]). See [[backend/messaging/error-handling|Error Handling]] for retry and idempotency patterns.

## Event Types

### Domain Event (intra-module — MediatR only)

Published and handled within the same module. Never crosses a module boundary.

```csharp
public abstract record DomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
    public DateTimeOffset OccurredAt { get; init; } = DateTimeOffset.UtcNow;
    public Guid TenantId { get; init; }
}
```

### Integration Event (cross-module — RabbitMQ via IEventBus)

Published via `IEventBus.PublishAsync()` → written to module outbox → delivered by RabbitMQ. Consumers use `IConsumer<T>` with inbox-state idempotency.

```csharp
public abstract record IntegrationEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
    public DateTimeOffset OccurredAt { get; init; } = DateTimeOffset.UtcNow;
    public abstract Guid TenantId { get; init; }
    public string EventType => GetType().Name;
}
```

## Infrastructure Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `TenantCreated` | `infrastructure.tenant.created` | Infrastructure | TenantId, Name, Plan | OrgStructure (seed default dept), Configuration (seed settings) |
| `TenantActivated` | `infrastructure.tenant.activated` | Infrastructure | TenantId | SharedPlatform (create subscription) |
| `TenantDeactivated` | `infrastructure.tenant.deactivated` | Infrastructure | TenantId, Reason | All modules (restrict access) |
| `UserCreated` | `infrastructure.user.created` | Infrastructure | UserId, TenantId, Email | Auth (assign default role), CoreHR (link employee) |
| `UserStatusChanged` | `infrastructure.user.status` | Infrastructure | UserId, OldStatus, NewStatus | Auth (revoke sessions if deactivated) |
| `FileUploaded` | `infrastructure.file.uploaded` | Infrastructure | FileRecordId, Context, UploadedById | Module-specific (link file to entity) |

## Auth Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `UserLoggedIn` | `auth.login` | Auth | UserId, TenantId, DeviceType, IpAddress | SharedPlatform (update presence) |
| `UserLoggedOut` | `auth.logout` | Auth | UserId, SessionId | SharedPlatform (clear presence) |
| `RoleAssigned` | `auth.role` | Auth | UserId, RoleId, AssignedById | Audit (log), Notifications (notify user) |
| `PermissionChanged` | `auth.permission` | Auth | RoleId, PermissionId, Action | Cache (invalidate permission cache) |

## Core HR Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `EmployeeHired` | `core-hr.employee.hired` | CoreHR | EmployeeId, TenantId, DepartmentId, JobFamilyId | WorkforcePresence (assign default schedule), Leave (calculate entitlements), Skills (assess gaps), Documents (assign onboarding docs), Calendar (add start date), Notifications (welcome), **WMS People Sync** (auto-provision WMS account if tenant has WMS linked) |
| `EmployeePromoted` | `core-hr.employee.promoted` | CoreHR | EmployeeId, OldLevel, NewLevel, OldDeptId, NewDeptId | Performance (update succession), Leave (recalculate entitlements), Skills (new required skills), Notifications, **WMS People Sync** (update WMS permission level via `wms_role_mappings`) |
| `EmployeeTransferred` | `core-hr.employee.transferred` | CoreHR | EmployeeId, FromDeptId, ToDeptId | Attendance (reassign schedule), Notifications, **WMS People Sync** (re-map task scope to new team/department) |
| `SalaryChanged` | `core-hr.employee.salary_changed` | CoreHR | EmployeeId, OldSalary, NewSalary, Currency, EffectiveDate | Payroll (update calculations), Notifications |
| `EmployeeOffboarded` | `core-hr.employee.offboarded` | CoreHR | EmployeeId, LastWorkingDay, Reason | All modules (cleanup), AgentGateway (revoke agent), Notifications, **WMS People Sync** (deactivate WMS access + trigger task reassignment alert to Team Lead) |
| `OnboardingStepCompleted` | `core-hr.employee.onboarding` | CoreHR | EmployeeId, StepName | Notifications |

## Workforce Presence Events (replaces Attendance)

| Event                    | Routing Key                 | Publisher         | Payload                        | Consumers                                |
| :----------------------- | :-------------------------- | :---------------- | :----------------------------- | :--------------------------------------- |
| `PresenceSessionStarted` | `workforce.presence.started` | WorkforcePresence | EmployeeId, Date, Source       | Notifications (team online status)       |
| `PresenceSessionEnded`   | `workforce.presence.ended`   | WorkforcePresence | EmployeeId, Date, TotalMinutes | ActivityMonitoring (close day tracking)  |
| `BreakExceeded`          | `workforce.presence.break`   | WorkforcePresence | EmployeeId, BreakId, Duration  | ExceptionEngine (flag long break)        |
| `OvertimeRequested`      | `workforce.presence.overtime_req` | WorkforcePresence | EmployeeId, RequestId, Hours   | Notifications, SharedPlatform (approval) |
| `OvertimeApproved`       | `workforce.presence.overtime_approved` | WorkforcePresence | EmployeeId, RequestId, Hours   | Payroll (overtime pay), Notifications    |
| `AttendanceCorrected`    | `workforce.presence.corrected` | WorkforcePresence | EmployeeId, Date, CorrectedBy  | Audit (log correction)                   |

## Agent Gateway Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `AgentRegistered` | `agent.gateway.registered` | AgentGateway | AgentId, DeviceId, TenantId | Configuration (push initial policy) |
| `AgentHeartbeatLost` | `agent.gateway.heartbeat_lost` | AgentGateway | AgentId, DeviceId, LastHeartbeat | ExceptionEngine (flag offline agent) |
| `AgentRevoked` | `agent.gateway.revoked` | AgentGateway | AgentId, RevokedBy | Agent receives 401 on next request |

## Activity Monitoring Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `ActivitySnapshotReceived` | `activity.snapshot` | ActivityMonitoring | EmployeeId, SnapshotId, IntensityScore | ExceptionEngine (evaluate rules) |
| `DailySummaryAggregated` | `activity.summary` | ActivityMonitoring | EmployeeId, Date, Summary | ProductivityAnalytics (build reports) |
| `ScreenshotCaptured` | `activity.screenshot` | ActivityMonitoring | EmployeeId, ScreenshotId | Audit trail |

## Identity Verification Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `VerificationCompleted` | `identity.verified` | IdentityVerification | EmployeeId, Method, Confidence | WorkforcePresence (confirm identity) |
| `VerificationFailed` | `identity.failed` | IdentityVerification | EmployeeId, Method, FailureReason | ExceptionEngine (alert), Notifications (notify manager) |
| `BiometricDeviceOffline` | `identity.device_offline` | IdentityVerification | DeviceId, LastHeartbeat | Notifications (alert admin) |

## Exception Engine Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `ExceptionAlertCreated` | `exception.alert` | ExceptionEngine | AlertId, EmployeeId, RuleId, Severity, Summary | Notifications (send via escalation chain), SignalR push |
| `AlertEscalated` | `exception.escalated` | ExceptionEngine | AlertId, EscalationStep, NotifyRole | Notifications (notify next in chain) |
| `AlertAcknowledged` | `exception.acknowledged` | ExceptionEngine | AlertId, AcknowledgedBy, Action | Audit trail |

## Productivity Analytics Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `DailyReportReady` | `analytics.daily` | ProductivityAnalytics | TenantId, Date, EmployeeCount | Notifications (send summary to managers) |
| `WeeklyReportReady` | `analytics.weekly` | ProductivityAnalytics | TenantId, WeekStart | Notifications (send weekly digest) |
| `MonthlyReportReady` | `analytics.monthly` | ProductivityAnalytics | TenantId, Year, Month | Notifications |

## Leave Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `LeaveRequested` | `leave.request.requested` | Leave | LeaveRequestId, EmployeeId, LeaveTypeId, StartDate, EndDate, ConflictCount | SharedPlatform (create workflow instance), Notifications (notify manager — includes conflict count if > 0) |
| `LeaveApproved` | `leave.request.approved` | Leave | LeaveRequestId, EmployeeId, StartDate, EndDate, TotalDays | WorkforcePresence (mark leave days), Calendar (create event), Payroll (leave adjustments), Notifications |
| `LeaveRejected` | `leave.request.rejected` | Leave | LeaveRequestId, EmployeeId, Reason | Notifications |
| `EntitlementAdjusted` | `leave.entitlement.adjusted` | Leave | EmployeeId, LeaveTypeId, Year, Adjustment | Audit (log) |

## Payroll Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `PayrollRunStarted` | `payroll.run.started` | Payroll | PayrollRunId, TenantId, PeriodStart, PeriodEnd | Notifications (notify admins) |
| `PayrollRunCompleted` | `payroll.run.completed` | Payroll | PayrollRunId, TotalGross, TotalNet, EmployeeCount | Notifications, Reports |
| `PayrollRunFailed` | `payroll.run.failed` | Payroll | PayrollRunId, ErrorMessage | Notifications (alert admins) |

## Performance Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `ReviewCycleStarted` | `performance.review.started` | Performance | ReviewCycleId, PeriodStart, PeriodEnd | Notifications (notify all participants), Calendar (create event) |
| `ReviewCompleted` | `performance.review.completed` | Performance | ReviewParticipantId, EmployeeId, CalibratedRating | Skills (update development plans), Notifications |
| `GoalCreated` | `performance.goal.created` | Performance | GoalId, EmployeeId, Title | Notifications |
| `RecognitionGiven` | `performance.recognition` | Performance | GiverId, ReceiverId, BadgeType, Points | Notifications |

## Skills & Learning Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `SkillValidated` | `skills.validated` | Skills | EmployeeId, SkillId, FromLevel, ToLevel | Performance (update reviews), Notifications |
| `CourseCompleted` | `skills.course` | Skills | EmployeeId, CourseId, CompletionPercent | Performance (milestone tracking), Notifications |
| `CertificationEarned` | `skills.cert.earned` | Skills | EmployeeId, CertificationName | Notifications |
| `CertificationExpiring` | `skills.cert.expiring` | Skills | EmployeeId, CertificationId, ExpiryDate | Notifications (30-day warning) |

## Document Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `DocumentPublished` | `documents.published` | Documents | DocumentId, Title, RequiresAcknowledgement | Notifications (if ack required) |
| `AcknowledgementReceived` | `documents.acknowledged` | Documents | DocumentVersionId, EmployeeId | Audit (log) |

## Grievance Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `GrievanceFiled` | `grievance.filed` | Grievance | CaseId, EmployeeId, CaseType, Severity | Notifications (notify HR), SharedPlatform (escalation rules) |
| `DisciplinaryActionIssued` | `grievance.disciplinary` | Grievance | ActionId, EmployeeId, ActionType | Notifications |
| `GrievanceResolved` | `grievance.resolved` | Grievance | CaseId, Resolution | Notifications |

## Expense Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `ExpenseClaimSubmitted` | `expense.submitted` | Expense | ClaimId, EmployeeId, TotalAmount | SharedPlatform (create workflow), Notifications |
| `ExpenseClaimApproved` | `expense.approved` | Expense | ClaimId, EmployeeId, TotalAmount | Payroll (reimbursement), Notifications |
| `ExpenseClaimPaid` | `expense.paid` | Expense | ClaimId, PaidAt | Notifications |

## Shared Platform Events

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:----------|:---------|:--------|:----------|
| `WorkflowStepCompleted` | `platform.workflow.step` | SharedPlatform | InstanceId, StepOrder, Action, ActorId | Source module (via resource_type routing) |
| `WorkflowCompleted` | `platform.workflow.completed` | SharedPlatform | InstanceId, ResourceType, ResourceId, FinalStatus | Source module |
| `SubscriptionChanged` | `platform.subscription` | SharedPlatform | TenantId, OldPlan, NewPlan | Feature flags (update limits) |
| `FeatureFlagToggled` | `platform.flag` | SharedPlatform | TenantId, FlagKey, IsEnabled | Cache (invalidate) |

## Related

- [[backend/module-boundaries|Module Boundaries]]
- [[backend/messaging/exchange-topology|Exchange Topology]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/shared-kernel|Shared Kernel]]
- [[modules/core-hr/overview|Core Hr]]
- [[modules/leave/overview|Leave]]
- [[modules/payroll/overview|Payroll]]
- [[modules/workforce-presence/overview|Workforce Presence]]
- [[modules/expense/overview|Expense]]
- [[modules/notifications/overview|Notifications]]
- [[modules/workforce-presence/overview|Workforce Presence]]
- [[modules/activity-monitoring/overview|Activity Monitoring]]
- [[modules/exception-engine/overview|Exception Engine]]
