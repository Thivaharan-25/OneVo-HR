# Event Catalog: ONEVO

All domain events published and consumed across modules. Phase 1 uses in-process MediatR `INotification` (see [[exchange-topology]]); future phases migrate to RabbitMQ for scale. See [[error-handling]] for retry and idempotency patterns.

## Event Format

```csharp
public abstract record DomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
    public DateTimeOffset OccurredAt { get; init; } = DateTimeOffset.UtcNow;
    public Guid TenantId { get; init; }
}
```

## Infrastructure Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `TenantCreated` | Infrastructure | TenantId, Name, Plan | OrgStructure (seed default dept), Configuration (seed settings) |
| `TenantActivated` | Infrastructure | TenantId | SharedPlatform (create subscription) |
| `TenantDeactivated` | Infrastructure | TenantId, Reason | All modules (restrict access) |
| `UserCreated` | Infrastructure | UserId, TenantId, Email | Auth (assign default role), CoreHR (link employee) |
| `UserStatusChanged` | Infrastructure | UserId, OldStatus, NewStatus | Auth (revoke sessions if deactivated) |
| `FileUploaded` | Infrastructure | FileRecordId, Context, UploadedById | Module-specific (link file to entity) |

## Auth Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `UserLoggedIn` | Auth | UserId, TenantId, DeviceType, IpAddress | SharedPlatform (update presence) |
| `UserLoggedOut` | Auth | UserId, SessionId | SharedPlatform (clear presence) |
| `RoleAssigned` | Auth | UserId, RoleId, AssignedById | Audit (log), Notifications (notify user) |
| `PermissionChanged` | Auth | RoleId, PermissionId, Action | Cache (invalidate permission cache) |

## Core HR Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `EmployeeHired` | CoreHR | EmployeeId, TenantId, DepartmentId, JobFamilyId | WorkforcePresence (assign default schedule), Leave (calculate entitlements), Skills (assess gaps), Documents (assign onboarding docs), Calendar (add start date), Notifications (welcome) |
| `EmployeePromoted` | CoreHR | EmployeeId, OldLevel, NewLevel, OldDeptId, NewDeptId | Performance (update succession), Leave (recalculate entitlements), Skills (new required skills), Notifications |
| `EmployeeTransferred` | CoreHR | EmployeeId, FromDeptId, ToDeptId | Attendance (reassign schedule), Notifications |
| `SalaryChanged` | CoreHR | EmployeeId, OldSalary, NewSalary, Currency, EffectiveDate | Payroll (update calculations), Notifications |
| `EmployeeOffboarded` | CoreHR | EmployeeId, LastWorkingDay, Reason | All modules (cleanup), AgentGateway (revoke agent), Notifications |
| `OnboardingStepCompleted` | CoreHR | EmployeeId, StepName | Notifications |

## Workforce Presence Events (replaces Attendance)

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `PresenceSessionStarted` | WorkforcePresence | EmployeeId, Date, Source | Notifications (team online status) |
| `PresenceSessionEnded` | WorkforcePresence | EmployeeId, Date, TotalMinutes | ActivityMonitoring (close day tracking) |
| `BreakExceeded` | WorkforcePresence | EmployeeId, BreakId, Duration | ExceptionEngine (flag long break) |
| `OvertimeRequested` | WorkforcePresence | EmployeeId, RequestId, Hours | Notifications, SharedPlatform (approval) |
| `OvertimeApproved` | WorkforcePresence | EmployeeId, RequestId, Hours | Payroll (overtime pay), Notifications |
| `AttendanceCorrected` | WorkforcePresence | EmployeeId, Date, CorrectedBy | Audit (log correction) |

## Agent Gateway Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `AgentRegistered` | AgentGateway | AgentId, DeviceId, TenantId | Configuration (push initial policy) |
| `AgentHeartbeatLost` | AgentGateway | AgentId, DeviceId, LastHeartbeat | ExceptionEngine (flag offline agent) |
| `AgentRevoked` | AgentGateway | AgentId, RevokedBy | Agent receives 401 on next request |

## Activity Monitoring Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `ActivitySnapshotReceived` | ActivityMonitoring | EmployeeId, SnapshotId, IntensityScore | ExceptionEngine (evaluate rules) |
| `DailySummaryAggregated` | ActivityMonitoring | EmployeeId, Date, Summary | ProductivityAnalytics (build reports) |
| `ScreenshotCaptured` | ActivityMonitoring | EmployeeId, ScreenshotId | Audit trail |

## Identity Verification Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `VerificationCompleted` | IdentityVerification | EmployeeId, Method, Confidence | WorkforcePresence (confirm identity) |
| `VerificationFailed` | IdentityVerification | EmployeeId, Method, FailureReason | ExceptionEngine (alert), Notifications (notify manager) |
| `BiometricDeviceOffline` | IdentityVerification | DeviceId, LastHeartbeat | Notifications (alert admin) |

## Exception Engine Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `ExceptionAlertCreated` | ExceptionEngine | AlertId, EmployeeId, RuleId, Severity, Summary | Notifications (send via escalation chain), SignalR push |
| `AlertEscalated` | ExceptionEngine | AlertId, EscalationStep, NotifyRole | Notifications (notify next in chain) |
| `AlertAcknowledged` | ExceptionEngine | AlertId, AcknowledgedBy, Action | Audit trail |

## Productivity Analytics Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `DailyReportReady` | ProductivityAnalytics | TenantId, Date, EmployeeCount | Notifications (send summary to managers) |
| `WeeklyReportReady` | ProductivityAnalytics | TenantId, WeekStart | Notifications (send weekly digest) |
| `MonthlyReportReady` | ProductivityAnalytics | TenantId, Year, Month | Notifications |

## Leave Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `LeaveRequested` | Leave | LeaveRequestId, EmployeeId, LeaveTypeId, StartDate, EndDate, ConflictCount | SharedPlatform (create workflow instance), Notifications (notify manager — includes conflict count if > 0) |
| `LeaveApproved` | Leave | LeaveRequestId, EmployeeId, StartDate, EndDate, TotalDays | WorkforcePresence (mark leave days), Calendar (create event), Payroll (leave adjustments), Notifications |
| `LeaveRejected` | Leave | LeaveRequestId, EmployeeId, Reason | Notifications |
| `EntitlementAdjusted` | Leave | EmployeeId, LeaveTypeId, Year, Adjustment | Audit (log) |

## Payroll Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `PayrollRunStarted` | Payroll | PayrollRunId, TenantId, PeriodStart, PeriodEnd | Notifications (notify admins) |
| `PayrollRunCompleted` | Payroll | PayrollRunId, TotalGross, TotalNet, EmployeeCount | Notifications, Reports |
| `PayrollRunFailed` | Payroll | PayrollRunId, ErrorMessage | Notifications (alert admins) |

## Performance Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `ReviewCycleStarted` | Performance | ReviewCycleId, PeriodStart, PeriodEnd | Notifications (notify all participants), Calendar (create event) |
| `ReviewCompleted` | Performance | ReviewParticipantId, EmployeeId, CalibratedRating | Skills (update development plans), Notifications |
| `GoalCreated` | Performance | GoalId, EmployeeId, Title | Notifications |
| `RecognitionGiven` | Performance | GiverId, ReceiverId, BadgeType, Points | Notifications |

## Skills & Learning Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `SkillValidated` | Skills | EmployeeId, SkillId, FromLevel, ToLevel | Performance (update reviews), Notifications |
| `CourseCompleted` | Skills | EmployeeId, CourseId, CompletionPercent | Performance (milestone tracking), Notifications |
| `CertificationEarned` | Skills | EmployeeId, CertificationName | Notifications |
| `CertificationExpiring` | Skills | EmployeeId, CertificationId, ExpiryDate | Notifications (30-day warning) |

## Document Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `DocumentPublished` | Documents | DocumentId, Title, RequiresAcknowledgement | Notifications (if ack required) |
| `AcknowledgementReceived` | Documents | DocumentVersionId, EmployeeId | Audit (log) |

## Grievance Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `GrievanceFiled` | Grievance | CaseId, EmployeeId, CaseType, Severity | Notifications (notify HR), SharedPlatform (escalation rules) |
| `DisciplinaryActionIssued` | Grievance | ActionId, EmployeeId, ActionType | Notifications |
| `GrievanceResolved` | Grievance | CaseId, Resolution | Notifications |

## Expense Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `ExpenseClaimSubmitted` | Expense | ClaimId, EmployeeId, TotalAmount | SharedPlatform (create workflow), Notifications |
| `ExpenseClaimApproved` | Expense | ClaimId, EmployeeId, TotalAmount | Payroll (reimbursement), Notifications |
| `ExpenseClaimPaid` | Expense | ClaimId, PaidAt | Notifications |

## Shared Platform Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `WorkflowStepCompleted` | SharedPlatform | InstanceId, StepOrder, Action, ActorId | Source module (via resource_type routing) |
| `WorkflowCompleted` | SharedPlatform | InstanceId, ResourceType, ResourceId, FinalStatus | Source module |
| `SubscriptionChanged` | SharedPlatform | TenantId, OldPlan, NewPlan | Feature flags (update limits) |
| `FeatureFlagToggled` | SharedPlatform | TenantId, FlagKey, IsEnabled | Cache (invalidate) |

## Related

- [[module-boundaries]]
- [[exchange-topology]]
- [[error-handling]]
- [[shared-kernel]]
- [[core-hr]]
- [[leave]]
- [[payroll]]
- [[attendance]]
- [[expense]]
- [[notifications]]
- [[workforce-presence]]
- [[activity-monitoring]]
- [[exception-engine]]
