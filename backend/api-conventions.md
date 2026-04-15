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

All endpoints require JWT Bearer token (except `/api/v1/auth/login`, `/api/v1/auth/register`, `/api/v1/auth/refresh`):

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

#### Bridge API Authentication (service-to-service)

`/api/v1/bridges/*` endpoints use a **separate bridge JWT** — user tokens are rejected.

1. Obtain a bridge JWT via `POST /api/v1/auth/bridge/token` (OAuth 2.0 Client Credentials)
2. Include it as `Authorization: Bearer <bridge_jwt>` on all bridge endpoint calls

Bridge JWT audience is `"onevo-bridge"` (user JWT audience is `"onevo-api"`). The bridge JWT carries a `bridges` claim listing which bridge endpoints the client may call. Middleware validates audience, claim, and bridge scope — user JWTs on bridge endpoints return `403`. See [[backend/bridge-api-contracts|Bridge API Contracts]] for the full auth flow.

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
if (currentUser.HasPermission("employees:update")) { ... }
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
| `Authorization` | Request | JWT Bearer token |
| `X-Correlation-Id` | Both | Request tracing (auto-generated if missing) |
| `X-Tenant-Id` | Request | Explicit tenant (for service-to-service calls) |
| `X-Rate-Limit-Remaining` | Response | Remaining rate limit quota |
| `Retry-After` | Response | Seconds until rate limit resets (on 429) |

## Core API Endpoints

### Infrastructure

```
POST   /api/v1/tenants                    # Create tenant
GET    /api/v1/tenants/{id}               # Get tenant
PUT    /api/v1/tenants/{id}               # Update tenant
POST   /api/v1/users                      # Create user
GET    /api/v1/users/{id}                 # Get user
POST   /api/v1/files/upload               # Upload file
GET    /api/v1/files/{id}                 # Get file metadata
GET    /api/v1/countries                   # List countries
```

### Auth

```
POST   /api/v1/auth/login                 # Login (returns JWT + refresh token)
POST   /api/v1/auth/refresh               # Refresh token
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

### Attendance

```
CRUD   /api/v1/shifts
CRUD   /api/v1/work-schedules
CRUD   /api/v1/schedule-templates
POST   /api/v1/employees/{id}/shift-assignment
GET    /api/v1/attendance?date=2026-04-05&departmentId=uuid
POST   /api/v1/attendance/clock-in         # Manual clock-in
POST   /api/v1/attendance/clock-out        # Manual clock-out
POST   /api/v1/biometric/webhook           # Biometric device webhook
CRUD   /api/v1/overtime-requests
CRUD   /api/v1/attendance-corrections
CRUD   /api/v1/holidays
```

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

### WorkManage Pro Bridges

```
GET    /api/v1/bridges/people-sync/employees    # Employee data for WorkManage
GET    /api/v1/bridges/availability/{empId}      # Leave + attendance for scheduling
POST   /api/v1/bridges/performance/metrics       # Accept work metrics from WorkManage
GET    /api/v1/bridges/skills/{empId}            # Skill data for task matching
POST   /api/v1/bridges/skills/{empId}            # Update skills from WorkManage
```

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
- [[backend/external-integrations|External Integrations]] — WorkManage Pro bridge API contracts
