# Module Event Matrix

Single-glance reference showing which events each module publishes and consumes. All cross-module events are delivered via **RabbitMQ via MassTransit**. For routing key details see [[backend/messaging/exchange-topology|Exchange Topology]]. For event payloads see [[backend/messaging/event-catalog|Event Catalog]].

| Module | Publishes | Consumes |
|:-------|:---------|:---------|
| activity-monitoring | `ExceptionDetected`, `DiscrepancyDetected`, `ActivitySnapshotReceived`, `DailySummaryAggregated` | `PresenceSessionStarted` |
| agent-gateway | `AgentRegistered`, `AgentHeartbeatLost`, `AgentRevoked` | `EmployeeOffboarded` |
| auth | `UserLoggedIn`, `UserLoggedOut`, `RoleAssigned`, `PermissionChanged` | `UserStatusChanged` |
| calendar | _(none)_ | `LeaveApproved`, `ReviewCycleStarted`, `EmployeeHired` |
| configuration | _(none)_ | `TenantCreated` |
| core-hr | `EmployeeHired`, `EmployeePromoted`, `EmployeeTransferred`, `SalaryChanged`, `EmployeeOffboarded`, `OnboardingStepCompleted` | _(none)_ |
| discrepancy-engine | `DiscrepancyCriticalDetected` | `DailySummaryAggregated` |
| documents | `DocumentPublished`, `AcknowledgementReceived` | `EmployeeHired`, `EmployeeOffboarded` |
| exception-engine | `ExceptionAlertCreated`, `AlertEscalated`, `AlertAcknowledged` | `ActivitySnapshotReceived`, `BreakExceeded`, `AgentHeartbeatLost` |
| expense | `ExpenseClaimSubmitted`, `ExpenseClaimApproved`, `ExpenseClaimPaid` | _(none)_ |
| grievance | `GrievanceFiled`, `DisciplinaryActionIssued`, `GrievanceResolved` | _(none)_ |
| identity-verification | `VerificationCompleted`, `VerificationFailed`, `BiometricDeviceOffline` | `ActivitySnapshotReceived` |
| infrastructure | `TenantCreated`, `TenantActivated`, `TenantDeactivated`, `UserCreated`, `UserStatusChanged` | _(none)_ |
| leave | `LeaveRequested`, `LeaveApproved`, `LeaveRejected`, `LeaveCancelled`, `EntitlementAdjusted` | `EmployeeHired` |
| notifications | _(none)_ | `LeaveRequested`, `LeaveApproved`, `EmployeeHired`, `PayrollRunCompleted`, `ReviewCompleted`, `ExceptionAlertCreated` _(+ others)_ |
| org-structure | `DepartmentChanged` | `TenantCreated` |
| payroll | `PayrollRunStarted`, `PayrollRunCompleted`, `PayrollRunFailed` | `LeaveApproved`, `SalaryChanged`, `OvertimeApproved`, `ExpenseClaimApproved` |
| performance | `ReviewCycleStarted`, `ReviewCompleted`, `GoalCreated`, `RecognitionGiven` | `EmployeeHired` |
| productivity-analytics | `DailyReportReady`, `WeeklyReportReady`, `MonthlyReportReady` | `ActivitySnapshotReceived`, `ExceptionAlertCreated` |
| reporting-engine | _(none)_ | _(none — reads via query service interfaces)_ |
| shared-platform | `WorkflowStepCompleted`, `WorkflowCompleted`, `SubscriptionChanged`, `FeatureFlagToggled` | `UserLoggedIn`, `TenantActivated` |
| skills | `SkillValidated`, `CourseCompleted`, `CertificationEarned`, `CertificationExpiring` | `EmployeeHired`, `ReviewCompleted` |
| workforce-presence | `PresenceSessionStarted`, `PresenceSessionEnded`, `BreakExceeded`, `OvertimeRequested`, `OvertimeApproved`, `AttendanceCorrected` | `EmployeeHired`, `LeaveApproved` |

## Related

- [[backend/messaging/exchange-topology|Exchange Topology]] — routing key patterns per module
- [[backend/messaging/event-catalog|Event Catalog]] — full event payloads and consumers
- [[backend/module-boundaries|Module Boundaries]] — module dependency graph
