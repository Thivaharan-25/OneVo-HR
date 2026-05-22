# API Documentation: ONEVO

## API Design Standards

### Base URL

```
https://api.onevo.com/api/v{version}/{resource}
```

### Versioning

- URL-based: `/api/v1/`, `/api/v2/`
- Header: `Api-Version: 1` (optional override)
- Deprecation: `Sunset` header with date when endpoint will be removed


### Authentication

Customer browser calls to `/api/v1/*` use the ONEVO BFF-style HttpOnly cookie session. The frontend sends requests with `credentials: "include"` and does not attach tenant JWTs in an `Authorization` header.

Non-browser clients may use Bearer tokens only where explicitly documented, such as platform-admin server internals, IDE extension flows, desktop agent device APIs, and service integrations.

#### Internal Module Authentication

HR Management, Workforce Intelligence, and Work Management all live in the same backend and PostgreSQL database. The Angular frontend apps, IDE extension, and desktop agent call first-party ONEVO endpoints only.

- Customer web clients use HttpOnly cookie sessions backed by server-side auth state for the normal user audience (`onevo-api`).
- IDE clients use the normal user JWT audience (`onevo-api`) through IDE-specific secure storage.
- Desktop agents use device JWTs on `/api/v1/agent/*`; device JWTs cannot access HR or Work Management user APIs.
- Cross-pillar data flow uses direct foreign keys, application services, and in-process domain events.


### Authorization (Hybrid Permission Control)

Every endpoint must specify required permission. Permissions are checked against the user's **effective permissions** (role + individual overrides, filtered by feature grants). Data is automatically scoped to the user's **org hierarchy** (they only see employees below them).

```csharp
[HttpGet]
[RequirePermission("employees:read")]
public async Task<IResult> GetEmployees([AsParameters] PagedRequest request, CancellationToken ct)
{
    // IHierarchyScope is injected — queries are auto-scoped to subordinates
    // Super Admin bypasses hierarchy scoping
}
```

**Never hardcode role names.** Roles are custom — always check permissions or module grants:

```csharp
// WRONG
if (currentUser.RoleName == "HR Manager") { ... }

// RIGHT
if (currentUser.HasPermission("employees:write")) { ... }
```

### Request/Response Format

**Content-Type:** `application/json`
**Character Encoding:** UTF-8

### Standard Response Envelope

```json
// Success (single item)
{
  "data": { "id": "uuid", "firstName": "John", ... },
  "meta": { "timestamp": "2026-04-05T10:00:00Z", "correlationId": "abc-123" }
}

// Success (list with pagination)
{
  "data": [ { ... }, { ... } ],
  "pagination": {
    "pageNumber": 1,
    "pageSize": 20,
    "totalCount": 150,
    "totalPages": 8,
    "hasNext": true,
    "hasPrevious": false
  },
  "meta": { "timestamp": "...", "correlationId": "..." }
}

// Error (RFC 7807 Problem Details)
{
  "type": "https://onevo.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "One or more validation errors occurred.",
  "instance": "/api/v1/employees",
  "errors": {
    "firstName": ["First name is required."],
    "email": ["Invalid email format."]
  },
  "correlationId": "abc-123"
}
```

### HTTP Status Codes

| Code | Usage |
|:-----|:------|
| 200 | Success (GET, PUT, PATCH) |
| 201 | Created (POST) — include `Location` header |
| 204 | No Content (DELETE) |
| 400 | Bad Request (malformed JSON, invalid parameters) |
| 401 | Unauthorized (missing or invalid JWT) |
| 403 | Forbidden (valid JWT but insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate, concurrency) |
| 422 | Unprocessable Entity (validation errors) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

### Pagination

Cursor-based for high-volume endpoints, offset-based for admin endpoints:

```
GET /api/v1/employees?pageNumber=1&pageSize=20&sortBy=lastName&sortDirection=asc
GET /api/v1/audit-logs?cursor=eyJ0...&pageSize=50
```

**Max page size:** 100

### Filtering & Sorting

```
GET /api/v1/employees?departmentId=uuid&status=active&sortBy=hireDate&sortDirection=desc
GET /api/v1/leave-requests?status=pending&startDateFrom=2026-04-01&startDateTo=2026-04-30
```

### Standard Headers

| Header | Direction | Purpose |
|:-------|:----------|:--------|
| `Cookie` | Request | Customer web session cookie, sent automatically by browser |
| `X-CSRF-Token` | Request | Required for cookie-authenticated state-changing requests |
| `Authorization` | Request | Bearer token only for non-browser clients where explicitly documented |
| `X-Correlation-Id` | Both | Request tracing (auto-generated if missing) |
| `X-Tenant-Id` | Request | Explicit tenant (for service-to-service calls) |
| `X-Rate-Limit-Remaining` | Response | Remaining rate limit quota |
| `Retry-After` | Response | Seconds until rate limit resets (on 429) |

## Core API Endpoints

### Infrastructure

```
POST   /admin/v1/tenants                  # Create tenant (operator-controlled Developer Console only)
GET    /admin/v1/tenants/{id}             # Get tenant (operator-controlled Developer Console only)
PATCH  /admin/v1/tenants/{id}/subscription # Assign subscription/commercial terms
PUT    /admin/v1/tenants/{id}/modules      # Assign module entitlements and sales states
PATCH  /admin/v1/tenants/{id}/settings     # Assign required tenant settings
GET    /admin/v1/tenants/{id}/permissions/catalog # Module-filtered permission catalog
POST   /admin/v1/tenants/{id}/role-templates/{templateId}/apply # Apply starter roles
POST   /admin/v1/tenants/{id}/invite-admin # Send tenant-owner set-password invite
PATCH  /admin/v1/tenants/{id}/provision/confirm # Activate completed provisioning draft
POST   /api/v1/users                      # Create user
GET    /api/v1/users/{id}                 # Get user
POST   /api/v1/files/upload               # Upload file
GET    /api/v1/files/{id}                 # Get file metadata
GET    /api/v1/countries                   # List countries
```

Tenant provisioning config is intentionally split across specific Developer Platform admin endpoints: `/subscription`, `/modules`, `/settings`, `/permissions/catalog`, `/role-templates`, `/invite-admin`, and `/provision/confirm`. Do not model full tenant provisioning as one generic tenant update endpoint; each owning module validates and persists its part of the draft.


### Auth

```
POST   /api/v1/auth/login                 # Login (sets HttpOnly session cookie)
POST   /api/v1/auth/refresh               # Refresh/rotate cookie-backed session
POST   /api/v1/auth/logout                # Logout (revoke session)
GET    /api/v1/auth/me                    # Current user profile
GET    /api/v1/roles                       # List roles
POST   /api/v1/roles                       # Create custom role
GET    /api/v1/permissions                 # List all permissions
POST   /api/v1/users/{id}/roles           # Assign role to user
```

### Org Structure

```
CRUD   /api/v1/legal-entities
CRUD   /api/v1/office-locations
CRUD   /api/v1/departments                # Supports hierarchical queries
CRUD   /api/v1/job-families
CRUD   /api/v1/job-family-levels
CRUD   /api/v1/job-titles
CRUD   /api/v1/teams
POST   /api/v1/teams/{id}/members         # Add team member
DELETE /api/v1/teams/{id}/members/{empId}  # Remove team member
```

### Core HR

```
CRUD   /api/v1/employees
GET    /api/v1/employees/{id}/profile      # Full profile (dependents, addresses, qualifications, work history)
CRUD   /api/v1/employees/{id}/dependents
CRUD   /api/v1/employees/{id}/addresses
CRUD   /api/v1/employees/{id}/qualifications
CRUD   /api/v1/employees/{id}/work-history
CRUD   /api/v1/employees/{id}/emergency-contacts
GET    /api/v1/employees/{id}/salary-history
POST   /api/v1/employees/{id}/salary       # Record salary change
GET    /api/v1/employees/{id}/lifecycle     # Lifecycle events
POST   /api/v1/employees/{id}/onboarding   # Create onboarding steps
POST   /api/v1/employees/{id}/offboarding  # Initiate offboarding
```

### Workforce Presence

```
CRUD   /api/v1/shifts
CRUD   /api/v1/work-schedules
CRUD   /api/v1/schedule-templates
POST   /api/v1/employees/{id}/shift-assignment
GET    /api/v1/workforce/presence?date=2026-04-05&departmentId=uuid
POST   /api/v1/workforce/clock-in          # Policy-gated clock-in
POST   /api/v1/workforce/clock-out         # Policy-gated clock-out
POST   /api/v1/workforce/breaks/start      # Start break and pause monitoring
POST   /api/v1/workforce/breaks/end        # End break and resume monitoring
POST   /api/v1/workforce/biometric/webhook # Biometric device webhook
CRUD   /api/v1/workforce/overtime-requests
CRUD   /api/v1/workforce/attendance-corrections
CRUD   /api/v1/holidays
```

Clock-in source validation is server-side. Office employees normally clock in through biometric terminals only. Remote employees may clock in through approved web/tray flows with identity and work-location evidence. Hybrid employees use biometric onsite and web/tray remotely. Onsite web/tray clock-in is allowed only during a time-limited biometric outage override for the affected legal entity/location/device. IDE extension and Work Management time logging must never create Workforce Presence clock-in/out records.

### Leave

```
CRUD   /api/v1/leave-types
CRUD   /api/v1/leave-policies
GET    /api/v1/employees/{id}/leave-entitlements
POST   /api/v1/leave-requests
GET    /api/v1/leave-requests?status=pending
POST   /api/v1/leave-requests/{id}/approve
POST   /api/v1/leave-requests/{id}/reject
```

### Performance

```
CRUD   /api/v1/review-cycles
GET    /api/v1/review-cycles/{id}/participants
POST   /api/v1/review-participants/{id}/self-rating
POST   /api/v1/review-participants/{id}/manager-rating
POST   /api/v1/peer-feedbacks
CRUD   /api/v1/goals
CRUD   /api/v1/recognitions
CRUD   /api/v1/succession-plans
```

### Skills & Learning

```
CRUD   /api/v1/skill-categories
CRUD   /api/v1/skills
GET    /api/v1/employees/{id}/skills
POST   /api/v1/skill-assessments           # Submit assessment responses
CRUD   /api/v1/courses
POST   /api/v1/course-assignments
CRUD   /api/v1/development-plans
CRUD   /api/v1/certifications
POST   /api/v1/skill-validations            # Request skill validation
```

### Payroll (Week 4)

```
GET    /api/v1/payroll-providers
CRUD   /api/v1/payroll-connections
CRUD   /api/v1/tax-engines
CRUD   /api/v1/allowance-types
CRUD   /api/v1/pension-plans
POST   /api/v1/payroll-runs                 # Initiate payroll run
GET    /api/v1/payroll-runs/{id}            # Run status + line items
GET    /api/v1/payroll-runs/{id}/line-items # Detailed line items
```

### Work Management

```
CRUD   /api/v1/workspaces
CRUD   /api/v1/projects
CRUD   /api/v1/tasks
CRUD   /api/v1/sprints
CRUD   /api/v1/boards
CRUD   /api/v1/okr/objectives
CRUD   /api/v1/time-logs
CRUD   /api/v1/channels
CRUD   /api/v1/documents
CRUD   /api/v1/repositories
```

Work Management is an internal ONEVO pillar. In the customer web app it uses the same cookie-backed user session and the same tenant/module entitlement checks as HR.

## Rate Limiting

3-layer rate limiting:

| Layer | Scope | Limit | Enforcement |
|:------|:------|:------|:-----------|
| Cloudflare | IP | 1000 req/min | WAF rule |
| .NET Middleware | Organization | Plan-based (Redis token bucket) | Per-tenant quota |
| .NET Middleware | User | Sub-quota of org limit | Per-user within org |

## Related

- [[security/auth-architecture|Auth Architecture]] — JWT authentication and RBAC authorization
- [[code-standards/backend-standards|Backend Standards]] — Minimal API endpoint conventions
- [[backend/module-catalog|Module Catalog]] — module-specific API endpoints
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant scoping for all API requests
- [[backend/external-integrations|External Integrations]] - third-party integrations only
