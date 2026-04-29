# Data Flow: ONEVO Platform

**Last Updated:** 2026-04-28

Three scenarios: reading data to the frontend, writing data from a button click, and combining two features in one request.

---

## Flow 1: Database → Frontend (Query / Read)

User opens a page or a list loads.

```
Browser (Next.js)
  │
  │  GET /api/v1/leave/requests?employeeId=xxx
  ▼
ONEVO.Api
  │
  ├─ TenantResolutionMiddleware
  │     reads JWT → extracts TenantId, UserId → populates ICurrentUser
  │
  ├─ PermissionMiddleware
  │     checks [RequirePermission("leave:read")] — rejects with 403 if missing
  │
  ├─ LeaveController.GetRequests(employeeId, ct)
  │     maps route/query params → creates query object
  │     calls: _mediator.Send(new GetLeaveRequestsQuery(employeeId))
  │
  ├─ MediatR Pipeline (runs before handler)
  │     [1] ValidationBehavior     — validates query fields (FluentValidation)
  │     [2] LoggingBehavior        — logs query name, UserId, TenantId
  │     [3] PerformanceBehavior    — starts timer, warns if > 500ms
  │     [4] UnhandledExceptionBehavior — safety net
  │
  ├─ GetLeaveRequestsQueryHandler.Handle(query, ct)
  │     injects: IApplicationDbContext
  │
  │     var results = await _db.LeaveRequests
  │         .Where(r => r.EmployeeId == query.EmployeeId)  ← your filter
  │         .Select(r => new LeaveRequestDto { ... })
  │         .ToListAsync(ct);
  │
  │     (ApplicationDbContext ALSO auto-applies global filters invisibly:)
  │         AND TenantId == currentUser.TenantId           ← tenant isolation
  │         AND IsDeleted == false                         ← soft delete filter
  │
  ├─ EF Core → SQL → PostgreSQL
  │     executes: SELECT ... FROM leave_requests
  │               WHERE employee_id = @p1
  │               AND tenant_id = @p2
  │               AND is_deleted = false
  │
  ├─ Handler returns: Result<List<LeaveRequestDto>>.Success(results)
  │
  ├─ Controller maps result → HTTP 200 OK + JSON body
  │
  ▼
Browser receives JSON → React renders the list
```

**Key rule:** Handler never returns a Domain entity to the controller — always a DTO.

---

## Flow 2: Frontend Button Click → Database (Command / Write)

User clicks "Approve Leave Request" button.

```
Browser (Next.js)
  │
  │  POST /api/v1/leave/requests/{id}/approve
  │  Body: { "approverId": "uuid" }
  ▼
ONEVO.Api
  │
  ├─ TenantResolutionMiddleware  — sets ICurrentUser from JWT
  ├─ PermissionMiddleware        — checks [RequirePermission("leave:approve")]
  │
  ├─ LeaveController.Approve(id, dto, ct)
  │     _mediator.Send(new ApproveLeaveRequestCommand(id, dto.ApproverId))
  │
  ├─ MediatR Pipeline
  │     [1] ValidationBehavior
  │           RuleFor(x => x.LeaveRequestId).NotEmpty()
  │           RuleFor(x => x.ApproverId).NotEmpty()
  │           → returns 422 immediately if invalid (handler never runs)
  │     [2] LoggingBehavior
  │     [3] PerformanceBehavior
  │     [4] UnhandledExceptionBehavior
  │
  ├─ ApproveLeaveRequestHandler.Handle(cmd, ct)
  │     injects: IApplicationDbContext, IUnitOfWork
  │
  │     // 1. Load entity
  │     var request = await _db.LeaveRequests
  │         .FirstOrDefaultAsync(r => r.Id == cmd.LeaveRequestId, ct);
  │     if (request is null)
  │         return Result.Failure("Leave request not found");
  │
  │     // 2. Call entity method — business logic lives HERE, not in handler
  │     request.Approve();
  │         // inside Approve():
  │         //   validates Status == Pending (throws DomainException if not)
  │         //   sets Status = Approved
  │         //   calls AddDomainEvent(new LeaveApprovedEvent(Id, EmployeeId))
  │         //   ↑ event is STORED on the entity, not dispatched yet
  │
  │     // 3. Persist
  │     await _uow.SaveChangesAsync(ct);
  │         │
  │         ├─ AuditableEntityInterceptor
  │         │     sets UpdatedAt = UtcNow, CreatedById (if new)
  │         │
  │         ├─ SoftDeleteInterceptor
  │         │     converts any Delete → IsDeleted = true (no hard deletes)
  │         │
  │         ├─ SQL written to PostgreSQL ✓
  │         │
  │         └─ DomainEventDispatchInterceptor  ← runs AFTER SQL succeeds
  │               collects entity.DomainEvents
  │               entity.ClearDomainEvents()
  │               IPublisher.Publish(LeaveApprovedEvent) → MediatR in-process
  │                   │
  │                   ├─ WorkforcePresence EventHandler reacts → marks shift absent
  │                   ├─ Payroll EventHandler reacts         → creates deduction
  │                   └─ Notifications EventHandler reacts   → sends email/push
  │
  │     return Result<LeaveRequestDto>.Success(dto);
  │
  ├─ Controller → HTTP 200 OK + updated DTO
  │
  ▼
Browser receives response → UI updates (button becomes "Approved")
```

**Key rule:** If `SaveChangesAsync` throws, the interceptor never runs — no domain events fire, no side effects happen. The DB write and event dispatch are atomic.

---

## Flow 3: Request That Needs Data From Two Features

Example: Load an "Employee Leave Summary" card that needs **CoreHR** employee profile data AND **Leave** entitlement/request data.

There is no message broker or inter-service call. Because everything is in one `ApplicationDbContext`, the handler simply queries both DbSets directly.

```
Browser
  │
  │  GET /api/v1/leave/summary?employeeId=xxx
  ▼
ONEVO.Api → MediatR Pipeline → GetEmployeeLeaveSummaryQueryHandler
  │
  ├─ Handler injects: IApplicationDbContext
  │
  │  // Query Feature 1: CoreHR
  │  var employee = await _db.Employees
  │      .Where(e => e.Id == query.EmployeeId)
  │      .Select(e => new { e.FullName, e.Department, e.EmploymentType })
  │      .FirstOrDefaultAsync(ct);
  │
  │  // Query Feature 2: Leave
  │  var entitlement = await _db.LeaveEntitlements
  │      .Where(e => e.EmployeeId == query.EmployeeId && e.Year == currentYear)
  │      .FirstOrDefaultAsync(ct);
  │
  │  var pendingCount = await _db.LeaveRequests
  │      .CountAsync(r => r.EmployeeId == query.EmployeeId
  │                    && r.Status == ApprovalStatus.Pending, ct);
  │
  │  // Both DbSets silently get:
  │  //   AND tenant_id = currentUser.TenantId
  │  //   AND is_deleted = false
  │
  │  // Combine into one response DTO
  │  var summary = new EmployeeLeaveSummaryDto
  │  {
  │      EmployeeName  = employee.FullName,
  │      Department    = employee.Department,
  │      TotalDays     = entitlement?.TotalDays ?? 0,
  │      UsedDays      = entitlement?.UsedDays ?? 0,
  │      PendingCount  = pendingCount
  │  };
  │
  │  return Result<EmployeeLeaveSummaryDto>.Success(summary);
  │
  ▼
Browser receives one combined JSON response
```

**Alternative: cross-feature via domain events (for writes)**

If a write in Feature A needs to trigger a write in Feature B:

```
Feature A entity raises domain event
    ↓ (after SaveChangesAsync)
DomainEventDispatchInterceptor dispatches event
    ↓
Feature B EventHandler (INotificationHandler<TEvent>)
    reads/writes Feature B's DbSets
    calls _uow.SaveChangesAsync(ct)
```

This keeps Feature A's handler clean — it doesn't import or call Feature B directly.

---

## Summary Table

| Scenario | Entry point | Data access | Response |
|---|---|---|---|
| Read (Query) | GET endpoint | IApplicationDbContext — single or joined DbSet queries | DTO → JSON |
| Write (Command) | POST/PUT/DELETE endpoint | Load entity → call method → SaveChangesAsync → domain events fire | Updated DTO → JSON |
| Cross-feature read | GET endpoint | Same handler queries multiple DbSets — all in one ApplicationDbContext | Combined DTO → JSON |
| Cross-feature write side-effect | Domain event after SaveChangesAsync | Feature B's EventHandler handles it independently | No direct response — happens in-process |

---

## Related

- [[backend/cqrs-patterns|CQRS Patterns]] — command and query code examples
- [[backend/domain-events|Domain Events]] — how cross-feature side effects work
- [[backend/clean-architecture-overview|Clean Architecture Overview]] — full request lifecycle
- [[backend/module-boundaries|Layer Boundary Rules]] — what each layer may reference
