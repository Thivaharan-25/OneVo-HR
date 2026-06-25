# ONEVO Backend Architecture Rulebook

> Source repo: `C:\onevoNew\Onevo_Backend`
>
> NFR source: `C:\onevoNew\NFS-ASP.NET(Backend).docx`
>
>
> Purpose: this document defines how the ONEVO backend must be structured and extended so new work follows the intended architecture without creating dependency, tenant-isolation, security, or maintainability flaws.

## 1. Non-Negotiable Architecture

ONEVO backend uses Clean Architecture with CQRS through MediatR.

```text
Client / Browser / Admin Console
        |
        v
ONEVO.Api
HTTP host, controllers, middleware, auth, CORS, Swagger, health endpoints
        |
        v
ONEVO.Application
Use cases, commands, queries, handlers, validators, DTOs, mappers, interfaces
        |
        v
ONEVO.Infrastructure
EF Core, PostgreSQL, repositories, identity, security, external service adapters
        |
        v
ONEVO.Domain
Entities, domain contracts, shared domain primitives
```

Dependency direction:

```text
ONEVO.Api
  -> ONEVO.Application
  -> ONEVO.Domain

ONEVO.Infrastructure
  -> ONEVO.Application
  -> ONEVO.Domain
```

Rules:

- `Domain` must not reference `Application`, `Infrastructure`, or `Api`.
- `Application` must not reference Infrastructure implementations.
- `Application` owns interfaces for repositories and external services.
- `Infrastructure` implements Application interfaces.
- `Api` must call business use cases through MediatR.
- Controllers must not use `ApplicationDbContext`.
- Controllers must not contain business workflows.
- Handlers must not depend on ASP.NET controllers, middleware, or `HttpContext`.
- Infrastructure must not contain endpoint routing or controller logic.

If a proposed change breaks these rules, do not implement it until the architecture decision is reviewed.

## 2. Project Responsibilities

### 2.1 `ONEVO.Api`

`ONEVO.Api` is the HTTP boundary.

It is responsible for:

- App startup and dependency registration.
- Middleware pipeline ordering.
- HTTP routing and versioned endpoints.
- Request/response translation.
- Authentication and authorization.
- Tenant/admin/system route enforcement.
- CSRF protection.
- Rate limiting.
- Swagger/OpenAPI.
- Health check endpoints.

It is not responsible for:

- Business workflow decisions.
- Database access.
- Entity persistence.
- Cross-feature orchestration outside HTTP concerns.

Canonical folder structure:

```text
src/ONEVO.Api/
  Auth/
  Configuration/
  Controllers/
    Admin/
    {Feature}/
      {SubFeature}/
  Extensions/
  Filters/
  Middleware/
  Properties/
  Program.cs
```

Controller rules:

- Use `[ApiController]`.
- Use versioned routes such as `/api/v1/...` or `/admin/v1/...`.
- Accept request DTOs or simple route/query parameters.
- Create a Command or Query.
- Call `await _mediator.Send(...)`.
- Convert `Result` into the correct HTTP response.
- Keep endpoint permission requirements visible through policy attributes or permission filters.
- Customer controllers should live under `Controllers/{Feature}/{SubFeature}/` unless an architecture decision approves a different route grouping.
- Admin controllers may live under `Controllers/Admin/` when they are platform-console endpoints.

### 2.2 `ONEVO.Application`

`ONEVO.Application` is the use-case layer. Most business behavior belongs here.

It is responsible for:

- Commands and command handlers.
- Queries and query handlers.
- FluentValidation validators.
- DTOs.
- Mappers.
- Helpers for pure application logic.
- Repository interfaces.
- Service interfaces.
- MediatR pipeline behaviors.
- Application-level security rules.

It is not responsible for:

- EF Core implementations.
- HTTP middleware.
- Concrete email/payment/storage providers.
- Database migrations.
- ASP.NET-specific request handling.

Canonical folder structure:

```text
src/ONEVO.Application/
  Common/
    Behaviors/
    Configuration/
    Exceptions/
    Models/
      Auth/
    RepositoryInterfaces/
    Security/
    ServiceInterfaces/
  Features/
    {Feature}/
      {SubFeature}/
        Commands/
          {UseCase}/
            {UseCase}Command.cs
            {UseCase}CommandHandler.cs
            {UseCase}CommandValidator.cs
        Queries/
          {UseCase}/
            {UseCase}Query.cs
            {UseCase}QueryHandler.cs
        DTOs/
          Requests/
            {UseCase}RequestDto.cs
          Responses/
            {UseCase}ResponseDto.cs
        Mappers/
          {EntityOrUseCase}Mapper.cs
        Helpers/
          {Purpose}Helper.cs
        RepositoryInterfaces/
          I{EntityOrCapability}Repository.cs
        ServiceInterfaces/
          I{Capability}Service.cs
  DependencyInjection.cs
```

Terms:

- `{Feature}` is the broad module or bounded area, such as `Auth`, `DevPlatform`, or `OrgStructure`.
- `{SubFeature}` is the owned capability inside the feature, such as `Login`, `Invite`, `Permission`, `Tenancy`, or `Subscription`.
- `{UseCase}` is the specific command/query action, such as `CreateTenant`, `UpdateRole`, `GetSubscriptionPlan`, or `ListSubscriptionPlans`.
- `{EntityOrUseCase}` is the entity, aggregate, DTO mapping target, or use-case name that the mapper owns.
- `{Purpose}` is the narrow helper purpose, such as pricing, module selection, or permission composition.
- `{EntityOrCapability}` is the entity, aggregate, read model, or capability the repository contract owns.
- `{Capability}` is the external/system capability the service contract owns.

The template is not an instruction to create every listed folder. Do not create empty folders just to match the template. Add a folder only when the use case needs it.

Valid examples:

```text
Features/Auth/Login/Commands/Login/
Features/Auth/Invite/RepositoryInterfaces/
Features/Auth/Permission/ServiceInterfaces/
Features/DevPlatform/Tenancy/Queries/GetProvisioningSummary/
Features/DevPlatform/Subscription/Commands/CreateSubscriptionPlan/
```

These examples are not an allowlist. A new feature/subfeature path is valid when it follows `{Feature}/{SubFeature}` and the name matches the owning business capability.

Application folder rules:

| Folder | Rule |
|---|---|
| `Commands/` | Mutating use cases: create, update, delete, archive, login, logout, assign, confirm. |
| `Queries/` | Read-only use cases. Queries must not mutate state or call `SaveChangesAsync`. |
| `DTOs/Requests/` | Request contracts used by controllers or application use cases. Use `*RequestDto.cs` when the DTO represents an external/API request body. |
| `DTOs/Responses/` | Response contracts returned by handlers. Use `*ResponseDto.cs` when the DTO represents an external/API response body. |
| `Mappers/` | Entity-to-DTO mapping and response composition. Must be deterministic and side-effect free. Keep repeated or non-trivial mapping here instead of hiding it in handlers. |
| `Helpers/` | Pure application calculations or reusable logic. No EF, HTTP, external provider code, or workflow orchestration. |
| `RepositoryInterfaces/` | Data access contracts owned by Application and implemented in Infrastructure. |
| `ServiceInterfaces/` | External/system service contracts owned by Application and implemented in Infrastructure. |
| `Validators` | Keep close to the command/query they validate. |

New Application file placement rules:

- Common repository contracts go in `ONEVO.Application/Common/RepositoryInterfaces/`.
- Feature-specific repository contracts go in `ONEVO.Application/Features/{Feature}/{SubFeature}/RepositoryInterfaces/`.
- Common service contracts go in `ONEVO.Application/Common/ServiceInterfaces/`.
- Feature-specific service contracts go in `ONEVO.Application/Features/{Feature}/{SubFeature}/ServiceInterfaces/`.
- Do not use `Interfaces/`, `Repositories/`, or `Services/` as folder names for Application interfaces.

A new Application folder or file is a violation when:

- It uses `Features/{Feature}/Commands/`, `Features/{Feature}/Queries/`, `Features/{Feature}/DTOs/`, `Features/{Feature}/RepositoryInterfaces/`, or `Features/{Feature}/ServiceInterfaces/` without a `{SubFeature}` level, unless an architecture decision explicitly approves the exception.
- It places feature-specific repository interfaces outside `Features/{Feature}/{SubFeature}/RepositoryInterfaces/`.
- It places shared repository interfaces outside `Common/RepositoryInterfaces/`.
- It creates an optional folder with no required files or use case.
- It introduces a new top-level `{Feature}` name when the work belongs under an existing feature/subfeature.
- It copies placeholder names such as `Thing`, `Item`, or `Sample` into real code.

Command rules:

- Commands change state.
- Commands may call repositories and `IUnitOfWork.SaveChangesAsync`.
- Commands should validate input before creating or mutating entities.
- Commands should return `Result<T>` or the project-standard result type.
- Mutating handlers should commit once at the end where practical.

Query rules:

- Queries read state.
- Queries must not call `SaveChangesAsync`.
- Queries must not create audit records or side effects unless explicitly designed and reviewed.
- Queries should return DTOs, not EF entities.

Mapper rules:

- Put repeated or non-trivial mapping in `Mappers/`.
- Do not inject services into mappers unless there is a strong reason.
- Do not perform database calls inside mappers.

Helper rules:

- Use `Helpers/` for pure calculations such as pricing or module selection.
- Do not hide business workflows inside helpers.
- If helper logic grows into a use case, move it into a handler/service.

### 2.3 `ONEVO.Domain`

`ONEVO.Domain` is the business model.

It is responsible for:

- Entities.
- Domain exceptions/errors.
- Domain interfaces that are truly domain-level.
- Base entity types.
- Tenant-owned entity markers.
- Domain events.

It is not responsible for:

- EF Core configuration.
- Repository implementation.
- HTTP concerns.
- External providers.
- Application DTOs.

Canonical folder structure:

```text
src/ONEVO.Domain/
  Common/
  Errors/
  Features/
    {Feature}/
      {SubFeature}/
        Entities/
        ValueObjects/
        Events/
  Lookups/
```

Domain rules:

- Keep entities persistence-friendly but not persistence-dependent.
- Do not put `DbContext`, migrations, controller attributes, or service adapters here.
- Tenant-scoped entities must be reviewed for `ITenantOwnedEntity`.
- Domain exceptions should represent business rule violations, not infrastructure failures.
- Do not add Domain files directly under `Features/{Feature}/` when the model belongs to a specific subfeature, unless an architecture decision explicitly approves the exception.

### 2.4 `ONEVO.Infrastructure`

`ONEVO.Infrastructure` implements persistence and external integrations.

It is responsible for:

- `ApplicationDbContext`.
- EF Core configurations.
- EF Core migrations.
- Repository implementations.
- Unit of Work implementation.
- Identity/token/session implementations.
- Email/payment/storage/external service implementations.
- Security implementations.
- Cache implementation.
- Seeders.
- Health check dependency registrations where appropriate.
- Polly policies for external dependencies.

It is not responsible for:

- API endpoint definitions.
- Business use-case orchestration.
- Application DTO contracts unless implementing an Application interface requires them.

Canonical folder structure:

```text
src/ONEVO.Infrastructure/
  Caching/
  Configuration/
  ExternalServices/
    Email/
    Messaging/
  Identity/
  Migrations/
  Persistence/
    Configurations/
      {Feature}/
        {SubFeature}/
    Interceptors/
    Repositories/
      {Feature}/
        {SubFeature}/
    Seeders/
  Security/
  Services/
    {Feature}/
      {SubFeature}/
  DependencyInjection.cs
```

Infrastructure rules:

- Repository implementations go under `Persistence/Repositories/{Feature}/{SubFeature}`.
- Entity mappings go under `Persistence/Configurations/{Feature}/{SubFeature}` when the entity belongs to a feature/subfeature.
- Non-EF service implementations go under `Services/{Feature}/{SubFeature}` when they implement an Application service interface.
- External provider adapters go under `ExternalServices/{ProviderArea}` when they wrap a third-party provider such as email, storage, payment, calendar, or messaging.
- Database schema changes require migrations.
- Do not bypass tenant isolation accidentally with raw SQL.
- Any raw SQL touching tenant-owned data must be reviewed for tenant filtering/RLS behavior.

A new Infrastructure folder or file is a violation when:

- A repository implementation is not under `Persistence/Repositories/{Feature}/{SubFeature}`.
- An EF configuration for a feature entity is not under `Persistence/Configurations/{Feature}/{SubFeature}`.
- A service implementation for an Application-owned feature service interface is not under `Services/{Feature}/{SubFeature}`.
- Infrastructure code introduces endpoint routing, controller behavior, or use-case orchestration.

## 3. Request Flow

Current HTTP request flow:

```text
1. Client sends request
2. ONEVO.Api receives request
3. ExceptionHandlerMiddleware
4. CorrelationIdMiddleware
5. Swagger in Development
6. Serilog request logging
7. HTTPS redirection outside Development
8. CORS
9. Forwarded headers
10. HostTenantResolutionMiddleware
11. AuthRateLimitingMiddleware
12. Authentication
13. CsrfProtectionMiddleware
14. TenantEnforcementMiddleware
15. PermissionVersionMiddleware
16. Authorization
17. Controller action
18. IMediator.Send(...)
19. MediatR behaviors
20. Command/Query handler
21. Application interface
22. Infrastructure implementation
23. EF Core / PostgreSQL / external service
24. Result/DTO returned
25. HTTP response returned
```

Final mental model:

```text
HTTP Request
  -> API Middleware
  -> Tenant/Auth/Security Checks
  -> Controller
  -> MediatR Command or Query
  -> Validation / Logging / Performance Behaviors
  -> Application Handler
  -> Application Interface
  -> Infrastructure Implementation
  -> Database / External Dependency
  -> Result / DTO
  -> HTTP Response
```

MediatR pipeline:

```text
Controller
  -> IMediator.Send(command/query)
    -> UnhandledExceptionBehavior
    -> ValidationBehavior
    -> LoggingBehavior
    -> PerformanceBehavior
    -> Handler
```

Pipeline behavior rules:

| Behavior | Required purpose |
|---|---|
| `UnhandledExceptionBehavior` | Log unexpected use-case errors and let API error middleware shape the response. |
| `ValidationBehavior` | Run FluentValidation before handlers. |
| `LoggingBehavior` | Log request execution with useful user/tenant context. |
| `PerformanceBehavior` | Warn on slow application requests. |

## 4. Tenant Isolation Rules

Tenant isolation is layered. Do not rely on only one layer.

```text
Host / Subdomain
  -> HostTenantResolutionMiddleware
  -> TenantContextAccessor
  -> TenantEnforcementMiddleware
  -> Session/Auth tenant claim check
  -> Application handlers use current tenant
  -> EF Core query filter on ITenantOwnedEntity
  -> TenantRlsInterceptor sets DB session variables
  -> PostgreSQL RLS policy enforces tenant_id boundary
```

Tenant context modes:

| Mode | Meaning |
|---|---|
| `tenant` | Tenant API request. Tenant data must be scoped. |
| `admin` | Platform/admin context. Admin routes are allowed. |
| `system` | Root/system host context. |

RLS runtime variables:

```text
app.current_tenant_id
app.tenant_context_mode
```

Rules:

- Tenant APIs must run under tenant context.
- Admin APIs must run under admin context.
- Tenant host must not access admin routes.
- Admin host must not access tenant API routes.
- Tenant authenticated requests must match the resolved host tenant.
- Tenant-owned entities must implement `ITenantOwnedEntity`.
- Admin/system bypass must be intentional and reviewed.
- Raw SQL must preserve tenant boundaries.

Middleware boundary rules:

- Middleware may enforce request-boundary rules such as host-to-tenant resolution, admin-vs-tenant route separation, authentication freshness, CSRF, correlation IDs, and exception shaping.
- Middleware must not own complex business workflows, persistence orchestration, or feature use cases.
- Simple tenant access gating in middleware is allowed when it protects request boundaries. If tenant status or entitlement rules grow beyond simple allow/deny checks, move the policy behind an Application-owned interface and review the design.

## 5. Authentication and Authorization Rules

### 5.1 Tenant User Auth

Tenant auth uses secure cookies.

```text
Login request
  -> tenant resolved from host
  -> email/password validated
  -> optional MFA challenge
  -> session created
  -> refresh token created
  -> onevo_session cookie set
  -> onevo_refresh cookie set
  -> onevo_csrf cookie set
```

Rules:

- `onevo_session` must be HttpOnly, Secure, SameSite Strict.
- `onevo_refresh` must be HttpOnly, Secure, SameSite Strict.
- `onevo_csrf` is readable by frontend and must be matched with `X-CSRF-Token`.
- Refresh tokens must be stored hashed, not raw.
- Passwords must be hashed with BCrypt or a reviewed stronger replacement.
- MFA state must come from MFA records, not from a loose user profile flag.

### 5.2 Admin Auth

Admin auth uses JWT Bearer.

```text
Admin request
  -> AdminScheme JWT validation
  -> platform_role claim checked
  -> AdminPolicy / AdminWritePolicy / AdminSuperPolicy
```

Policy rules:

| Policy | Requirement |
|---|---|
| `AdminPolicy` | Authenticated admin with `platform_role`. |
| `AdminWritePolicy` | `platform_role` is `super_admin` or `admin`. |
| `AdminSuperPolicy` | `platform_role` is `super_admin`. |

Authorization rules:

- Do not authorize based on frontend state.
- Do not rely on profile fields for roles.
- Roles and permissions must be checked server-side.
- Tenant-facing permission checks should use permission claims/resolver patterns already in the backend.

## 6. Persistence Rules

Persistence flow:

```text
Application Handler
  -> Repository/Service Interface
  -> Infrastructure EF Repository/Service
  -> ApplicationDbContext
  -> EF Core Configuration
  -> Npgsql
  -> PostgreSQL
```

Rules:

- Application defines interfaces.
- Infrastructure implements interfaces.
- `ApplicationDbContext` stays in Infrastructure.
- Feature entity configuration belongs in `Persistence/Configurations/{Feature}/{SubFeature}`.
- Feature repository implementation belongs in `Persistence/Repositories/{Feature}/{SubFeature}`.
- Shared lookup configuration may use a clearly named shared subfeature such as `Persistence/Configurations/Lookups/Common`.
- Database changes require migrations.
- Mutating use cases should call `IUnitOfWork.SaveChangesAsync` once at the end where practical.
- Queries should return DTOs, not tracked EF entities.
- Tenant-owned tables must be covered by tenant query filters and PostgreSQL RLS where applicable.

## 7. NFR Implementation Requirements

The NFR document requires production-readiness beyond basic feature code. These requirements must be considered when building or reviewing backend work.

### 7.1 Performance

Targets:

| Metric | Target |
|---|---|
| p50 latency | <= 150 ms |
| p95 latency | <= 400 ms |
| p99 latency | <= 800 ms |
| Warm-cache end-to-end interaction | <= 1.5 s p95 |

Rules:

- Use async database and external service calls.
- Avoid N+1 database queries.
- Add indexes for new query patterns.
- Use pagination for list endpoints.
- Cache read-heavy stable data where appropriate.
- Do not cache tenant-sensitive data without tenant-aware cache keys.

### 7.2 Polly Retry and Circuit Breaker

Requirement: external dependency calls must use resilience policies.

What this solves:

- Temporary provider failures.
- Network timeouts.
- Intermittent 5xx responses.
- Dependency overload or throttling.

Where to implement:

- Infrastructure dependency registration.
- Typed `HttpClient` registrations.
- External service adapters such as email, payment, Google auth, object storage, and future third-party APIs.

Do not:

- Wrap all controller actions with retries.
- Retry non-idempotent operations blindly.
- Retry database writes without understanding transaction behavior.

Required target:

```text
Retry:
  attempt 1 -> 250 ms
  attempt 2 -> 500 ms
  attempt 3 -> 1 s

Circuit breaker:
  open after 5 consecutive failures
  half-open probe after 30 seconds
```

Expected pattern:

```text
ONEVO.Application
  Common/
    ServiceInterfaces/
      IEmailService.cs

ONEVO.Infrastructure
  ExternalServices/Email/
    ResendSmtpEmailService.cs
  DependencyInjection.cs
    register HttpClient + Polly retry/circuit breaker
```

### 7.3 Application Insights

Requirement: production telemetry must be available.

What this solves:

- Request latency tracking.
- Dependency latency tracking.
- Exception tracking.
- Availability dashboards.
- Alerting.
- Correlation across services.

Where to implement:

```text
src/ONEVO.Api/Program.cs
src/ONEVO.Api/appsettings.json
environment variables
```

Rules:

- Use environment variables for the Application Insights connection string.
- Do not commit secrets.
- Preserve correlation IDs in logs and telemetry.
- Track requests, dependencies, exceptions, and custom business-critical events.

Required dashboards:

- Availability.
- p50/p95/p99 latency.
- 5xx error rate.
- Cache hit ratio.
- Dependency latency.
- Active sessions.

Required alerts:

| Condition | Action |
|---|---|
| 5xx > 1% over 5 minutes | Page on-call |
| p95 latency > 1 second over 10 minutes | Warning |
| Availability < 99.5% over 1 hour | Page on-call |
| Dependency error rate > 5% over 5 minutes | Warning |

### 7.4 Broad Public API Rate Limiting

Current state: auth endpoint rate limiting exists. Broad public API rate limiting must also exist for production.

Goal:

- Protect public APIs from abusive traffic.
- Keep auth-specific limits stricter.
- Avoid accidental double blocking.

Required policy:

| Endpoint type | Limit |
|---|---|
| Public APIs | 100 requests/minute/IP |
| Auth APIs | 30 requests/minute/IP or stricter endpoint-specific rules |

Recommended implementation:

```text
src/ONEVO.Api/
  Extensions/
    RateLimitingExtensions.cs
  Program.cs
```

Rules:

- Prefer ASP.NET Core built-in rate limiting for broad API policies.
- Keep current auth rate limiting if it provides endpoint-specific protections.
- Exclude or specially handle auth paths so broad policy does not conflict with stricter auth policy.
- Consider tenant-aware or user-aware policies for authenticated tenant APIs.

### 7.5 Health Checks

Current state: basic API health check exists. Production readiness requires dependency checks.

Required endpoints:

| Endpoint | Purpose |
|---|---|
| `/health` | Liveness: process is running. Should be lightweight. |
| `/health/ready` | Readiness: app can safely receive traffic. Should check required dependencies. |

Required checks:

- API process liveness.
- PostgreSQL connectivity.
- Required external dependencies.
- Cache/distributed cache if introduced.
- Object/file storage if introduced.
- Payment/email dependencies if required for the deployed workload.

Rules:

- Liveness should not fail just because the database is briefly down.
- Readiness should fail when the app cannot safely serve traffic.
- Health check output must not expose secrets.

### 7.6 Idempotency for Booking/Renewal and Critical Mutations

Current state: booking endpoints were not found in the inspected backend. This requirement applies when booking, renewal, payment, or other critical mutating workflows are implemented.

Problem it solves:

- Client retries after timeout.
- Duplicate booking/renewal/payment requests.
- Double-submit from UI.
- Network failure after server completed the transaction.

Rule:

- Critical mutating endpoints must accept a client-generated idempotency key.
- Duplicate requests with the same key and same request body must return the original response.
- Duplicate requests with the same key but different body must be rejected.

Recommended header:

```text
Idempotency-Key: <client-generated-guid-or-random-key>
```

Recommended table:

```text
id
tenant_id
user_id
idempotency_key
endpoint
request_hash
status
response_status_code
response_body
created_at
expires_at
```

Recommended flow:

```text
Request arrives
  -> Validate idempotency key exists
  -> Hash normalized request body
  -> Check existing idempotency record by tenant/user/endpoint/key
  -> If existing completed record and hash matches, return stored response
  -> If existing record and hash differs, return 409 Conflict
  -> Create processing record
  -> Execute business transaction
  -> Persist final response/status
  -> Return response
```

Rules:

- Do not implement idempotency as naive middleware only.
- Business transaction must own correctness.
- Scope keys by tenant and user where applicable.
- Store enough response data to return the original result.
- Use expiration/cleanup for old idempotency records.

### 7.7 Security Headers and Transport

Rules:

- HTTPS only in production.
- TLS 1.2 or later.
- HSTS enabled in production.
- CORS must use allow-listed frontend domains.
- Add security headers such as:
  - `Content-Security-Policy`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- Do not log secrets, raw tokens, payment data, or excessive PII.
- Log access to sensitive audit/security logs.

### 7.8 Audit Trail

Required audit events:

- Authentication events.
- Authorization changes.
- Booking creation/modification/cancellation when booking exists.
- Administrative actions.
- Failed access attempts.
- Data export/deletion requests.

Required audit fields:

```text
timestamp_utc
user_id
tenant_id where applicable
action
resource
ip_address
correlation_id
```

Rules:

- Audit logs must be tamper-resistant.
- Audit retention target is minimum 7 years.
- Audit records must not contain secrets or raw tokens.

## 8. API Versioning Rules

Rules:

- Public APIs must be versioned.
- Prefer URL-based versioning:

```text
/api/v1/...
/api/v2/...
/admin/v1/...
```

- Breaking changes require a new API version.
- Existing API versions must have a defined support window.
- Minimum support window target is 12 months.
- Deprecation notice target is at least 90 days.
- API contracts must be documented through OpenAPI/Swagger.

## 9. Error Handling Rules

Rules:

- Use structured error responses.
- Include correlation ID.
- Do not leak stack traces to clients.
- Validation failures should return validation details.
- Business rule failures should return clear domain/application errors.
- Unexpected failures should return safe generic messages.

Required shape:

```json
{
  "type": "https://onevo.com/errors/example",
  "title": "Error title",
  "status": 400,
  "detail": "Human-readable detail",
  "correlationId": "..."
}
```

## 10. Testing Rules

Test project structure:

```text
tests/
  ONEVO.Tests.Unit/
    Features/
      Api/
      {Feature}/
        {SubFeature}/

  ONEVO.Tests.Integration/
    {Feature}/
      {SubFeature}/

  ONEVO.Tests.Architecture/
    LayerDependencyTests.cs
```

Rules:

- Unit test handlers and business logic.
- Integration test API/database/auth/tenant behavior.
- Architecture tests must protect dependency direction.
- Add tests for tenant boundary behavior when touching tenant-owned data.
- Add tests for permission behavior when adding secured endpoints.
- Add tests for idempotency when adding critical mutating workflows.
- Target at least 70% test coverage on business logic.

## 11. New Feature Build Checklist

Use this checklist before adding a backend feature.

1. Identify `{Feature}` and `{SubFeature}`. Reuse an existing feature/subfeature when the capability already belongs there.
2. Confirm whether a Domain entity, value object, event, or lookup is needed.
3. Add Application command/query folders under `Features/{Feature}/{SubFeature}/`.
4. Add request/response DTOs.
5. Add FluentValidation validators for non-trivial input.
6. Add command/query handlers.
7. Add mappers for repeated or non-trivial entity-to-DTO mapping.
8. Add helpers only for pure reusable application logic.
9. Add repository/service interfaces in Application only when the use case needs persistence or external/system services.
10. Add Infrastructure implementations under the matching `{Feature}/{SubFeature}` path.
11. Add EF configurations and migrations if schema changes.
12. Add or update controller endpoints.
13. Add authorization policy or permission filter.
14. Check tenant context and tenant isolation.
15. Check error response behavior.
16. Check logging and correlation ID behavior.
17. Check rate limiting impact.
18. Check health/readiness impact if a new dependency is introduced.
19. Add Polly policy if a new external HTTP dependency is introduced.
20. Add telemetry for important dependency/business events.
21. Add idempotency if the endpoint is a critical mutation.
22. Add unit tests.
23. Add integration tests if API, DB, auth, tenant, or idempotency behavior is involved.
24. Update Swagger/OpenAPI contract if endpoint behavior changes.

## 12. Acceptable and Not Acceptable

Acceptable:

- Thin controllers.
- One command/query folder per use case.
- Application-owned interfaces.
- Infrastructure-owned implementations.
- DTO mapping in `Mappers`.
- Pure calculations in `Helpers`.
- One transaction/save boundary per mutating use case where practical.
- Explicit tenant context checks in sensitive handlers.
- Structured failure results.

Not acceptable:

- Controller directly using `ApplicationDbContext`.
- Handler directly using Infrastructure concrete classes.
- Query mutating state.
- Business workflow hidden in middleware.
- Raw SQL without tenant isolation review.
- Tenant-owned entity without tenant boundary review.
- Authorization based only on frontend/profile fields.
- Logging secrets or raw tokens.
- Returning raw exception details to clients.
- Retrying non-idempotent external operations blindly.
- Adding external dependency without health/telemetry/resilience consideration.

## 13. Current Known Gaps To Close

These are known gaps compared with the NFR document and should be closed as production readiness work.

| Gap | Required direction |
|---|---|
| Polly retry/circuit breaker not confirmed | Add policies around external dependency clients in Infrastructure. |
| Application Insights not confirmed | Add telemetry registration in API and configure through environment variables. |
| Broad public API rate limiting not confirmed | Add ASP.NET Core broad rate limiting while preserving stricter auth limits. |
| DB/dependency health checks not confirmed | Add readiness checks for PostgreSQL and required dependencies. |
| Booking/renewal idempotency not applicable yet | Implement when booking/renewal or similar critical mutating endpoints are added. |

## 14. Final Rule

Every backend change must preserve this flow:

```text
HTTP Request
  -> ONEVO.Api middleware
  -> Tenant/Auth/Security checks
  -> Controller
  -> MediatR Command or Query
  -> Application pipeline behaviors
  -> Application handler
  -> Application-owned interface
  -> Infrastructure implementation
  -> EF Core/PostgreSQL or external dependency
  -> Result/DTO
  -> HTTP response
```

