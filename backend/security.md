# Security Implementation: ONEVO

**Last Updated:** 2026-04-27

---

## Password Hashing

**Library:** `BCrypt.Net-Next`
**WorkFactor:** 12 (non-negotiable — never lower in production)
**Interface:** `IPasswordHasher` in `ONEVO.Application/Common/Interfaces/`
**Implementation:** `ONEVO.Infrastructure/Identity/PasswordHasher.cs`

Rule: never store plain text. Never use MD5 or SHA1. All comparisons go through `IPasswordHasher.Verify()`.

```csharp
public interface IPasswordHasher
{
    string Hash(string plainText);
    bool Verify(string plainText, string hash);
}
```

---

## JWT Authentication

**Interface:** `ITokenService` in `ONEVO.Application/Common/Interfaces/`
**Implementation:** `ONEVO.Infrastructure/Identity/JwtTokenService.cs`

### Mandatory validation settings (non-negotiable)

```csharp
tokenValidationParameters = new TokenValidationParameters
{
    ValidateIssuer = true,
    ValidateAudience = true,
    ValidateLifetime = true,          // ← must be true
    ValidateIssuerSigningKey = true,
    ClockSkew = TimeSpan.Zero,        // ← no grace window
    IssuerSigningKey = new SymmetricSecurityKey(
        Encoding.UTF8.GetBytes(Environment.GetEnvironmentVariable("JWT_SECRET_KEY")!))
};
```

### Secret key rule

**Never store `JWT_SECRET_KEY` in `appsettings.json`.**
- Development: environment variable
- Production: Azure Key Vault via `IConfiguration` binding

### Three token types (isolated issuers)

| Token type | Issuer | Valid at |
|---|---|---|
| Customer | `onevo-customer` | `ONEVO.Api` only |
| Platform admin | `onevo-platform-admin` | `ONEVO.Admin.Api` only |
| Agent machine | `onevo-agent` | `AgentGateway` endpoints only |

Tokens from one issuer are **rejected** at endpoints requiring another.

---

## PII Encryption

**Algorithm:** AES-256-GCM
**Interface:** `IEncryptionService` in `ONEVO.Application/Common/Interfaces/`
**Implementation:** `ONEVO.Infrastructure/Security/AesEncryptionService.cs`

```csharp
public interface IEncryptionService
{
    string Encrypt(string plainText);
    string Decrypt(string cipherText);
}
```

**Fields that must be encrypted:**
- `Employee`: NIC number, passport number, bank account number
- `SalaryHistory`: salary amount
- `VerificationRequest`: biometric hash
- `SmtpConfig`: SMTP password

Applied via EF Core **value converters** in `IEntityTypeConfiguration<T>` — encryption is transparent to handlers.

**Encryption key:** Azure Key Vault in production (`ENCRYPTION_KEY` env var in dev).

---

## Multi-Tenancy

`TenantResolutionMiddleware` reads `tenant_id` claim from JWT and populates `ICurrentUser`.

`ApplicationDbContext` applies global query filters:

```csharp
// Applied to every DbSet<T> where T : BaseEntity
modelBuilder.Entity<T>().HasQueryFilter(
    x => x.TenantId == _currentUser.TenantId && !x.IsDeleted);
```

**DevPlatform exception:** `DevPlatformAccount` and related entities have no `TenantId` and are excluded from this filter.

---

## RBAC

```csharp
// Controller endpoint
[RequirePermission("leave:approve")]
public async Task<IActionResult> ApproveLeave(...)

// Middleware reads JWT claims
// Permission format: "{resource}:{action}"
// Examples: "leave:approve", "employee:create", "payroll:run"
```

Missing permission → `ForbiddenException` → `ExceptionHandlerMiddleware` → HTTP 403 RFC 7807.

---

## Global Exception Handling

`ONEVO.Api/Middleware/ExceptionHandlerMiddleware.cs` catches all unhandled exceptions and returns RFC 7807 Problem Details:

```json
{
  "type": "https://tools.ietf.org/html/rfc7807",
  "title": "Validation Error",
  "status": 422,
  "detail": "Leave request dates are invalid.",
  "instance": "/api/v1/leave/requests",
  "errors": { "StartDate": ["Must be in the future"] }
}
```

| Exception | HTTP Status |
|---|---|
| `NotFoundException` | 404 |
| `ForbiddenException` | 403 |
| `ValidationException` (FluentValidation) | 422 |
| `DomainException` | 422 |
| `System.Exception` (unhandled) | 500 (logs stack trace, returns safe message) |
