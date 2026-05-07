# Data Flow: ONEVO Platform

**Last Updated:** 2026-05-06

This file describes the canonical backend request flow for reads, writes, and cross-feature work.

---

## Persistence Boundary

Handlers do not query EF Core or `ApplicationDbContext` directly. Persistence access always goes through repository/service interfaces owned by the Application layer and implemented in Infrastructure.

For reads, query handlers call reader/repository interfaces that return DTOs or read models. For writes, command handlers call repositories to load aggregates, invoke domain methods, and commit through `IUnitOfWork`. Cross-feature reads compose multiple reader interfaces; cross-feature write side effects use domain events.

`ApplicationDbContext` is reserved for Infrastructure persistence implementations, repositories, unit of work, migrations, and reviewed low-level persistence utilities. Application does not expose an `IApplicationDbContext`/`DbSet<T>` abstraction.

---

## Flow 1: Query / Read

User opens a page or a list loads.

```text
Browser
  -> GET /api/v1/leave/requests?employeeId=...
  -> ONEVO.Api
  -> TenantResolutionMiddleware sets current tenant/user
  -> PermissionMiddleware checks [RequirePermission("leave:read")]
  -> LeaveController maps route/query params to GetLeaveRequestsQuery
  -> MediatR pipeline
  -> GetLeaveRequestsQueryHandler
       injects: ILeaveRequestReader
       calls: _leaveRequests.ListForEmployeeAsync(employeeId, ct)
       receives: List<LeaveRequestDto>
  -> Controller returns HTTP 200 + JSON
```

The reader implementation lives in Infrastructure and applies tenant isolation, soft-delete filtering, cancellation, and projection rules. The handler never returns a Domain entity to the controller.

---

## Flow 2: Command / Write

User clicks "Approve Leave Request".

```text
Browser
  -> POST /api/v1/leave/requests/{id}/approve
  -> ONEVO.Api
  -> TenantResolutionMiddleware
  -> PermissionMiddleware checks [RequirePermission("leave:approve")]
  -> LeaveController maps body/route to ApproveLeaveRequestCommand
  -> MediatR pipeline
  -> ApproveLeaveRequestHandler
       injects: ILeaveRequestRepository, IUnitOfWork
       loads aggregate: _leaveRequests.GetByIdAsync(id, ct)
       calls domain method: request.Approve()
       commits: _uow.SaveChangesAsync(ct)
  -> EF interceptors run in Infrastructure
  -> Domain events dispatch after save succeeds
  -> Controller returns updated response DTO
```

If `SaveChangesAsync` fails, domain events are not dispatched and side effects do not run.

---

## Flow 3: Cross-Feature Read

Example: an Employee Leave Summary card needs CoreHR employee data and Leave entitlement/request data.

```text
GetEmployeeLeaveSummaryQueryHandler
  injects:
    IEmployeeReader
    ILeaveEntitlementReader
    ILeaveRequestReader

  employee = _employees.GetSummaryAsync(employeeId, ct)
  entitlement = _leaveEntitlements.GetForEmployeeYearAsync(employeeId, year, ct)
  pendingCount = _leaveRequests.CountPendingForEmployeeAsync(employeeId, ct)

  combines those results into EmployeeLeaveSummaryDto
```

The handler composes public reader interfaces from the owning features. It does not query another feature's DbSet directly.

---

## Flow 4: Cross-Feature Write Side Effect

If a write in Feature A needs Feature B to react:

```text
Feature A entity raises domain event
  -> SaveChangesAsync succeeds
  -> DomainEventDispatchInterceptor publishes event
  -> Feature B EventHandler handles it
  -> Feature B uses its own repository/service interfaces
  -> Feature B commits through IUnitOfWork when it changes state
```

This keeps Feature A from directly calling Feature B's internals.

---

## Summary Table

| Scenario | Entry point | Data access | Response |
|---|---|---|---|
| Read | GET endpoint | Repository/reader interface returns DTO/read model | DTO to JSON |
| Write | POST/PUT/DELETE endpoint | Repository loads aggregate, domain method changes state, unit of work commits | Response DTO to JSON |
| Cross-feature read | GET endpoint | Handler composes feature-owned reader interfaces | Combined DTO |
| Cross-feature write side effect | Domain event after save | Event handler uses its feature's repositories/services | No direct HTTP response |

---

## Related

- [[backend/cqrs-patterns|CQRS Patterns]]
- [[backend/domain-events|Domain Events]]
- [[backend/clean-architecture-overview|Clean Architecture Overview]]
- [[backend/module-boundaries|Layer Boundary Rules]]
