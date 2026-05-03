# Backend Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fill the existing ONEVO.sln scaffold with working foundation code so `dotnet build ONEVO.sln` and `dotnet test ONEVO.sln` pass with zero errors.

**Architecture:** Clean Architecture — Domain (no deps) → Application (MediatR + FluentValidation) → Infrastructure (EF Core + Npgsql) → two ASP.NET Core host projects. All tests run without a real PostgreSQL instance.

**Tech Stack:** .NET 9, MediatR 12 (MediatR.Contracts for Domain), FluentValidation 11, EF Core 9 + Npgsql 9, Serilog, xUnit, WebApplicationFactory

**Working directory for all commands:** `C:\OneVo-HR\OneVo-backend`

---

## File Map

| Path | Responsibility |
|:-----|:--------------|
| `src/ONEVO.Domain/Common/BaseEntity.cs` | Tenant-scoped entity base |
| `src/ONEVO.Domain/Common/PlatformEntity.cs` | Platform-level entity base (no TenantId) |
| `src/ONEVO.Domain/Common/IDomainEvent.cs` | Marker interface |
| `src/ONEVO.Domain/Common/ValueObject.cs` | Structural equality base |
| `src/ONEVO.Domain/Errors/*.cs` | DomainException, NotFoundException, ForbiddenException |
| `src/ONEVO.Domain/Enums/*.cs` | 5 shared enums |
| `src/ONEVO.Domain/ValueObjects/*.cs` | Email, Money, PhoneNumber, Address |
| `src/ONEVO.Domain/Features/InfrastructureModule/Entities/*.cs` | Country, Tenant, User, FileRecord |
| `src/ONEVO.Application/Common/Models/Error.cs` | Error record |
| `src/ONEVO.Application/Common/Models/Result.cs` | Result + Result<T> |
| `src/ONEVO.Application/Common/Interfaces/*.cs` | IApplicationDbContext, ICurrentUserService, ITenantContext, IDateTimeProvider, IUnitOfWork |
| `src/ONEVO.Application/Common/Behaviors/*.cs` | 4 MediatR pipeline behaviors |
| `src/ONEVO.Application/DependencyInjection.cs` | AddApplication() |
| `src/ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs` | Single DbContext |
| `src/ONEVO.Infrastructure/Persistence/ApplicationDbContextFactory.cs` | IDesignTimeDbContextFactory |
| `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/*.cs` | 4 EF configs |
| `src/ONEVO.Infrastructure/Persistence/Interceptors/*.cs` | Audit, SoftDelete, DomainEvent interceptors |
| `src/ONEVO.Infrastructure/Services/CurrentUserService.cs` | ICurrentUserService + ITenantContext |
| `src/ONEVO.Infrastructure/Services/DateTimeProvider.cs` | IDateTimeProvider |
| `src/ONEVO.Infrastructure/DependencyInjection.cs` | AddInfrastructure() |
| `src/ONEVO.Api/Program.cs` | Rewrite (remove WeatherForecast) |
| `src/ONEVO.Api/Middleware/*.cs` | CorrelationId, ExceptionMapping, TenantResolution |
| `src/ONEVO.Admin.Api/Program.cs` | Rewrite (admin/v1 prefix) |
| `src/ONEVO.Admin.Api/Middleware/*.cs` | Same 3 middleware |
| `tests/ONEVO.Tests.Unit/Domain/ResultTests.cs` | Result<T> unit tests |
| `tests/ONEVO.Tests.Unit/Domain/BaseEntityTests.cs` | Domain event management tests |
| `tests/ONEVO.Tests.Integration/ApiBootTests.cs` | API health check boot test |
| `tests/ONEVO.Tests.Integration/AdminApiBootTests.cs` | Admin API health check boot test |
| `tests/ONEVO.Tests.Integration/DbContextBootTests.cs` | DbContext construction test |

---

## Task 1: Domain Packages + Shared Kernel

**Files:**
- Modify: `src/ONEVO.Domain/ONEVO.Domain.csproj`
- Create: `src/ONEVO.Domain/Common/IDomainEvent.cs`
- Create: `src/ONEVO.Domain/Common/BaseEntity.cs`
- Create: `src/ONEVO.Domain/Common/PlatformEntity.cs`
- Create: `src/ONEVO.Domain/Common/ValueObject.cs`
- Create: `src/ONEVO.Domain/Errors/DomainException.cs`
- Create: `src/ONEVO.Domain/Errors/NotFoundException.cs`
- Create: `src/ONEVO.Domain/Errors/ForbiddenException.cs`
- Create: `src/ONEVO.Domain/Enums/EmploymentType.cs`
- Create: `src/ONEVO.Domain/Enums/EmploymentStatus.cs`
- Create: `src/ONEVO.Domain/Enums/ApprovalStatus.cs`
- Create: `src/ONEVO.Domain/Enums/Severity.cs`
- Create: `src/ONEVO.Domain/Enums/WorkMode.cs`
- Create: `src/ONEVO.Domain/ValueObjects/Email.cs`
- Create: `src/ONEVO.Domain/ValueObjects/Money.cs`
- Create: `src/ONEVO.Domain/ValueObjects/PhoneNumber.cs`
- Create: `src/ONEVO.Domain/ValueObjects/Address.cs`
- Test: `tests/ONEVO.Tests.Unit/Domain/BaseEntityTests.cs`
- Test: `tests/ONEVO.Tests.Unit/Domain/ResultTests.cs` (stub — implemented in Task 2)

- [ ] **Step 1: Add MediatR.Contracts to Domain**

Edit `src/ONEVO.Domain/ONEVO.Domain.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="MediatR.Contracts" Version="2.0.1" />
  </ItemGroup>
</Project>
```

- [ ] **Step 2: Write the failing test for BaseEntity domain events**

Create `tests/ONEVO.Tests.Unit/Domain/BaseEntityTests.cs`:

```csharp
using ONEVO.Domain.Common;

namespace ONEVO.Tests.Unit.Domain;

public class BaseEntityTests
{
    private class TestEntity : BaseEntity
    {
        public static TestEntity Create(Guid tenantId) => new() { Id = Guid.NewGuid(), TenantId = tenantId };
    }

    private class TestEvent : IDomainEvent { }

    [Fact]
    public void AddDomainEvent_AppearsInDomainEvents()
    {
        var entity = TestEntity.Create(Guid.NewGuid());
        entity.PublishEvent(new TestEvent());
        Assert.Single(entity.DomainEvents);
    }

    [Fact]
    public void ClearDomainEvents_EmptiesList()
    {
        var entity = TestEntity.Create(Guid.NewGuid());
        entity.PublishEvent(new TestEvent());
        entity.ClearDomainEvents();
        Assert.Empty(entity.DomainEvents);
    }
}
```

- [ ] **Step 3: Run the test — verify it FAILS (types don't exist yet)**

```powershell
dotnet test tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj
```

Expected: build error — `ONEVO.Domain.Common` namespace not found.

- [ ] **Step 4: Create IDomainEvent.cs**

Create `src/ONEVO.Domain/Common/IDomainEvent.cs`:

```csharp
using MediatR;

namespace ONEVO.Domain.Common;

public interface IDomainEvent : INotification { }
```

- [ ] **Step 5: Create BaseEntity.cs**

Create `src/ONEVO.Domain/Common/BaseEntity.cs`:

```csharp
namespace ONEVO.Domain.Common;

public abstract class BaseEntity
{
    public Guid Id { get; set; }
    public Guid TenantId { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset? UpdatedAt { get; set; }
    public Guid CreatedById { get; set; }
    public bool IsDeleted { get; set; }

    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyList<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    public void PublishEvent(IDomainEvent domainEvent) => _domainEvents.Add(domainEvent);
    public void ClearDomainEvents() => _domainEvents.Clear();
}
```

Note: method named `PublishEvent` (not `AddDomainEvent`) to avoid confusion with MediatR's `Publish`. Adjust test to match.

- [ ] **Step 6: Create PlatformEntity.cs**

Create `src/ONEVO.Domain/Common/PlatformEntity.cs`:

```csharp
namespace ONEVO.Domain.Common;

public abstract class PlatformEntity
{
    public Guid Id { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset? UpdatedAt { get; set; }
    public bool IsDeleted { get; set; }

    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyList<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    public void PublishEvent(IDomainEvent domainEvent) => _domainEvents.Add(domainEvent);
    public void ClearDomainEvents() => _domainEvents.Clear();
}
```

- [ ] **Step 7: Create ValueObject.cs**

Create `src/ONEVO.Domain/Common/ValueObject.cs`:

```csharp
namespace ONEVO.Domain.Common;

public abstract class ValueObject
{
    protected abstract IEnumerable<object> GetEqualityComponents();

    public override bool Equals(object? obj)
    {
        if (obj is null || obj.GetType() != GetType()) return false;
        return GetEqualityComponents().SequenceEqual(((ValueObject)obj).GetEqualityComponents());
    }

    public override int GetHashCode()
        => GetEqualityComponents().Aggregate(0, HashCode.Combine);

    public static bool operator ==(ValueObject? left, ValueObject? right)
        => left?.Equals(right) ?? right is null;

    public static bool operator !=(ValueObject? left, ValueObject? right)
        => !(left == right);
}
```

- [ ] **Step 8: Create Errors**

Create `src/ONEVO.Domain/Errors/DomainException.cs`:

```csharp
namespace ONEVO.Domain.Errors;

public class DomainException : Exception
{
    public DomainException(string message) : base(message) { }
}
```

Create `src/ONEVO.Domain/Errors/NotFoundException.cs`:

```csharp
namespace ONEVO.Domain.Errors;

public class NotFoundException : Exception
{
    public NotFoundException(string entityName, object key)
        : base($"{entityName} with key '{key}' was not found.") { }

    public NotFoundException(string message) : base(message) { }
}
```

Create `src/ONEVO.Domain/Errors/ForbiddenException.cs`:

```csharp
namespace ONEVO.Domain.Errors;

public class ForbiddenException : Exception
{
    public ForbiddenException(string message = "Access denied.") : base(message) { }
}
```

- [ ] **Step 9: Create Enums**

Create `src/ONEVO.Domain/Enums/EmploymentType.cs`:

```csharp
namespace ONEVO.Domain.Enums;

public enum EmploymentType { FullTime, PartTime, Contract, Intern }
```

Create `src/ONEVO.Domain/Enums/EmploymentStatus.cs`:

```csharp
namespace ONEVO.Domain.Enums;

public enum EmploymentStatus { Active, OnLeave, Suspended, Terminated }
```

Create `src/ONEVO.Domain/Enums/ApprovalStatus.cs`:

```csharp
namespace ONEVO.Domain.Enums;

public enum ApprovalStatus { Pending, Approved, Rejected, Cancelled }
```

Create `src/ONEVO.Domain/Enums/Severity.cs`:

```csharp
namespace ONEVO.Domain.Enums;

public enum Severity { Low, Medium, High, Critical }
```

Create `src/ONEVO.Domain/Enums/WorkMode.cs`:

```csharp
namespace ONEVO.Domain.Enums;

public enum WorkMode { OnSite, Remote, Hybrid }
```

- [ ] **Step 10: Create ValueObjects**

Create `src/ONEVO.Domain/ValueObjects/Email.cs`:

```csharp
using ONEVO.Domain.Common;
using ONEVO.Domain.Errors;

namespace ONEVO.Domain.ValueObjects;

public sealed class Email : ValueObject
{
    public string Value { get; }

    private Email(string value) => Value = value;

    public static Email Create(string email)
    {
        if (string.IsNullOrWhiteSpace(email))
            throw new DomainException("Email cannot be empty.");
        email = email.Trim().ToLowerInvariant();
        if (!email.Contains('@') || email.Length > 254)
            throw new DomainException($"'{email}' is not a valid email address.");
        return new Email(email);
    }

    protected override IEnumerable<object> GetEqualityComponents() { yield return Value; }
    public override string ToString() => Value;
}
```

Create `src/ONEVO.Domain/ValueObjects/Money.cs`:

```csharp
using ONEVO.Domain.Common;
using ONEVO.Domain.Errors;

namespace ONEVO.Domain.ValueObjects;

public sealed class Money : ValueObject
{
    public decimal Amount { get; }
    public string CurrencyCode { get; }

    private Money(decimal amount, string currencyCode) { Amount = amount; CurrencyCode = currencyCode; }

    public static Money Create(decimal amount, string currencyCode)
    {
        if (amount < 0) throw new DomainException("Amount cannot be negative.");
        if (string.IsNullOrWhiteSpace(currencyCode) || currencyCode.Length != 3)
            throw new DomainException("Currency code must be a 3-letter ISO 4217 code.");
        return new Money(amount, currencyCode.ToUpperInvariant());
    }

    protected override IEnumerable<object> GetEqualityComponents() { yield return Amount; yield return CurrencyCode; }
    public override string ToString() => $"{Amount} {CurrencyCode}";
}
```

Create `src/ONEVO.Domain/ValueObjects/PhoneNumber.cs`:

```csharp
using System.Text.RegularExpressions;
using ONEVO.Domain.Common;
using ONEVO.Domain.Errors;

namespace ONEVO.Domain.ValueObjects;

public sealed class PhoneNumber : ValueObject
{
    private static readonly Regex E164 = new(@"^\+[1-9]\d{1,14}$", RegexOptions.Compiled);

    public string Value { get; }

    private PhoneNumber(string value) => Value = value;

    public static PhoneNumber Create(string number)
    {
        if (string.IsNullOrWhiteSpace(number)) throw new DomainException("Phone number cannot be empty.");
        if (!E164.IsMatch(number)) throw new DomainException($"'{number}' is not a valid E.164 phone number.");
        return new PhoneNumber(number);
    }

    protected override IEnumerable<object> GetEqualityComponents() { yield return Value; }
    public override string ToString() => Value;
}
```

Create `src/ONEVO.Domain/ValueObjects/Address.cs`:

```csharp
using ONEVO.Domain.Common;

namespace ONEVO.Domain.ValueObjects;

public sealed class Address : ValueObject
{
    public string Street { get; }
    public string City { get; }
    public string Country { get; }
    public string PostalCode { get; }

    public Address(string street, string city, string country, string postalCode)
    {
        Street = street; City = city; Country = country; PostalCode = postalCode;
    }

    protected override IEnumerable<object> GetEqualityComponents()
    {
        yield return Street; yield return City; yield return Country; yield return PostalCode;
    }
}
```

- [ ] **Step 11: Add Domain reference to Tests.Unit csproj**

Edit `tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj` — add Domain reference:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="coverlet.collector" Version="6.0.2" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.12.0" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
  </ItemGroup>
  <ItemGroup>
    <Using Include="Xunit" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\..\src\ONEVO.Domain\ONEVO.Domain.csproj" />
    <ProjectReference Include="..\..\src\ONEVO.Application\ONEVO.Application.csproj" />
  </ItemGroup>
</Project>
```

- [ ] **Step 12: Run the test — verify it PASSES**

```powershell
dotnet test tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj --filter "BaseEntityTests"
```

Expected: `Passed! - 2 tests`

- [ ] **Step 13: Commit**

```powershell
git add src/ONEVO.Domain tests/ONEVO.Tests.Unit
git commit -m "feat(domain): add shared kernel — BaseEntity, ValueObject, Errors, Enums, ValueObjects"
```

---

## Task 2: Application Common Foundation

**Files:**
- Modify: `src/ONEVO.Application/ONEVO.Application.csproj`
- Create: `src/ONEVO.Application/Common/Models/Error.cs`
- Create: `src/ONEVO.Application/Common/Models/Result.cs`
- Create: `src/ONEVO.Application/Common/Interfaces/IApplicationDbContext.cs`
- Create: `src/ONEVO.Application/Common/Interfaces/ICurrentUserService.cs`
- Create: `src/ONEVO.Application/Common/Interfaces/ITenantContext.cs`
- Create: `src/ONEVO.Application/Common/Interfaces/IDateTimeProvider.cs`
- Create: `src/ONEVO.Application/Common/Interfaces/IUnitOfWork.cs`
- Create: `src/ONEVO.Application/Common/Behaviors/ValidationBehavior.cs`
- Create: `src/ONEVO.Application/Common/Behaviors/LoggingBehavior.cs`
- Create: `src/ONEVO.Application/Common/Behaviors/PerformanceBehavior.cs`
- Create: `src/ONEVO.Application/Common/Behaviors/UnhandledExceptionBehavior.cs`
- Create: `src/ONEVO.Application/DependencyInjection.cs`
- Test: `tests/ONEVO.Tests.Unit/Domain/ResultTests.cs`

- [ ] **Step 1: Write failing Result<T> tests**

Create `tests/ONEVO.Tests.Unit/Domain/ResultTests.cs`:

```csharp
using ONEVO.Application.Common.Models;

namespace ONEVO.Tests.Unit.Domain;

public class ResultTests
{
    [Fact]
    public void Success_IsSuccess_True()
    {
        var result = Result<string>.Success("hello");
        Assert.True(result.IsSuccess);
        Assert.Equal("hello", result.Value);
    }

    [Fact]
    public void Failure_IsSuccess_False()
    {
        var error = new Error("Test.Error", "Something failed");
        var result = Result<string>.Failure(error);
        Assert.False(result.IsSuccess);
        Assert.Equal(error, result.Error);
    }

    [Fact]
    public void NonGeneric_Success_IsSuccess_True()
    {
        var result = Result.Success();
        Assert.True(result.IsSuccess);
    }

    [Fact]
    public void NonGeneric_Failure_IsSuccess_False()
    {
        var error = new Error("Test.Error", "Something failed");
        var result = Result.Failure(error);
        Assert.False(result.IsSuccess);
    }
}
```

- [ ] **Step 2: Run — verify FAILS (types missing)**

```powershell
dotnet test tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj --filter "ResultTests"
```

Expected: build error.

- [ ] **Step 3: Update Application.csproj packages**

Edit `src/ONEVO.Application/ONEVO.Application.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="MediatR" Version="12.4.1" />
    <PackageReference Include="FluentValidation.DependencyInjectionExtensions" Version="11.11.0" />
    <PackageReference Include="Microsoft.Extensions.Logging.Abstractions" Version="9.0.4" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\ONEVO.Domain\ONEVO.Domain.csproj" />
  </ItemGroup>
</Project>
```

- [ ] **Step 4: Create Error.cs**

Create `src/ONEVO.Application/Common/Models/Error.cs`:

```csharp
namespace ONEVO.Application.Common.Models;

public sealed record Error(string Code, string Message)
{
    public static readonly Error None = new(string.Empty, string.Empty);
    public static readonly Error NullValue = new("Error.NullValue", "A null value was provided.");
}
```

- [ ] **Step 5: Create Result.cs**

Create `src/ONEVO.Application/Common/Models/Result.cs`:

```csharp
namespace ONEVO.Application.Common.Models;

public class Result
{
    public bool IsSuccess { get; }
    public bool IsFailure => !IsSuccess;
    public Error Error { get; }

    protected Result(bool isSuccess, Error error)
    {
        if (isSuccess && error != Error.None) throw new InvalidOperationException("Success result cannot carry an error.");
        if (!isSuccess && error == Error.None) throw new InvalidOperationException("Failure result must carry an error.");
        IsSuccess = isSuccess;
        Error = error;
    }

    public static Result Success() => new(true, Error.None);
    public static Result Failure(Error error) => new(false, error);
}

public sealed class Result<T> : Result
{
    public T? Value { get; }

    private Result(T value, bool isSuccess, Error error) : base(isSuccess, error) => Value = value;

    public static Result<T> Success(T value) => new(value, true, Error.None);
    public new static Result<T> Failure(Error error) => new(default!, false, error);

    public static implicit operator Result<T>(T value) => Success(value);
}
```

- [ ] **Step 6: Run Result tests — verify PASS**

```powershell
dotnet test tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj --filter "ResultTests"
```

Expected: `Passed! - 4 tests`

- [ ] **Step 7: Create Interfaces**

Create `src/ONEVO.Application/Common/Interfaces/ICurrentUserService.cs`:

```csharp
namespace ONEVO.Application.Common.Interfaces;

public interface ICurrentUserService
{
    Guid? UserId { get; }
    Guid? TenantId { get; }
    bool IsAuthenticated { get; }
}
```

Create `src/ONEVO.Application/Common/Interfaces/ITenantContext.cs`:

```csharp
namespace ONEVO.Application.Common.Interfaces;

public interface ITenantContext
{
    Guid? TenantId { get; }
    bool HasTenant { get; }
}
```

Create `src/ONEVO.Application/Common/Interfaces/IDateTimeProvider.cs`:

```csharp
namespace ONEVO.Application.Common.Interfaces;

public interface IDateTimeProvider
{
    DateTimeOffset UtcNow { get; }
    DateOnly Today { get; }
}
```

Create `src/ONEVO.Application/Common/Interfaces/IUnitOfWork.cs`:

```csharp
namespace ONEVO.Application.Common.Interfaces;

public interface IUnitOfWork
{
    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
}
```

Create `src/ONEVO.Application/Common/Interfaces/IApplicationDbContext.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using ONEVO.Domain.Features.InfrastructureModule.Entities;

namespace ONEVO.Application.Common.Interfaces;

public interface IApplicationDbContext
{
    DbSet<Country> Countries { get; }
    DbSet<Tenant> Tenants { get; }
    DbSet<User> Users { get; }
    DbSet<FileRecord> FileRecords { get; }
}
```

- [ ] **Step 8: Create Pipeline Behaviors**

Create `src/ONEVO.Application/Common/Behaviors/UnhandledExceptionBehavior.cs`:

```csharp
using MediatR;
using Microsoft.Extensions.Logging;

namespace ONEVO.Application.Common.Behaviors;

public class UnhandledExceptionBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : notnull
{
    private readonly ILogger<UnhandledExceptionBehavior<TRequest, TResponse>> _logger;

    public UnhandledExceptionBehavior(ILogger<UnhandledExceptionBehavior<TRequest, TResponse>> logger)
        => _logger = logger;

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        try
        {
            return await next();
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            _logger.LogError(ex, "Unhandled exception for request {RequestType}", typeof(TRequest).Name);
            throw;
        }
    }
}
```

Create `src/ONEVO.Application/Common/Behaviors/ValidationBehavior.cs`:

```csharp
using FluentValidation;
using MediatR;

namespace ONEVO.Application.Common.Behaviors;

public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : notnull
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators) => _validators = validators;

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        if (!_validators.Any()) return await next();

        var context = new ValidationContext<TRequest>(request);
        var failures = _validators
            .Select(v => v.Validate(context))
            .SelectMany(r => r.Errors)
            .Where(f => f != null)
            .ToList();

        if (failures.Count > 0) throw new ValidationException(failures);

        return await next();
    }
}
```

Create `src/ONEVO.Application/Common/Behaviors/LoggingBehavior.cs`:

```csharp
using MediatR;
using Microsoft.Extensions.Logging;

namespace ONEVO.Application.Common.Behaviors;

public class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : notnull
{
    private readonly ILogger<LoggingBehavior<TRequest, TResponse>> _logger;

    public LoggingBehavior(ILogger<LoggingBehavior<TRequest, TResponse>> logger) => _logger = logger;

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        _logger.LogInformation("Handling {RequestType}", typeof(TRequest).Name);
        var response = await next();
        _logger.LogInformation("Handled {RequestType}", typeof(TRequest).Name);
        return response;
    }
}
```

Create `src/ONEVO.Application/Common/Behaviors/PerformanceBehavior.cs`:

```csharp
using System.Diagnostics;
using MediatR;
using Microsoft.Extensions.Logging;

namespace ONEVO.Application.Common.Behaviors;

public class PerformanceBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : notnull
{
    private const int SlowRequestThresholdMs = 500;
    private readonly ILogger<PerformanceBehavior<TRequest, TResponse>> _logger;

    public PerformanceBehavior(ILogger<PerformanceBehavior<TRequest, TResponse>> logger) => _logger = logger;

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        var sw = Stopwatch.StartNew();
        var response = await next();
        sw.Stop();

        if (sw.ElapsedMilliseconds > SlowRequestThresholdMs)
            _logger.LogWarning("Slow request: {RequestType} took {ElapsedMs}ms", typeof(TRequest).Name, sw.ElapsedMilliseconds);

        return response;
    }
}
```

- [ ] **Step 9: Create DependencyInjection.cs**

Create `src/ONEVO.Application/DependencyInjection.cs`:

```csharp
using FluentValidation;
using MediatR;
using Microsoft.Extensions.DependencyInjection;
using ONEVO.Application.Common.Behaviors;

namespace ONEVO.Application;

public static class DependencyInjection
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        var assembly = typeof(DependencyInjection).Assembly;

        services.AddMediatR(cfg =>
        {
            cfg.RegisterServicesFromAssembly(assembly);
            cfg.AddBehavior(typeof(IPipelineBehavior<,>), typeof(UnhandledExceptionBehavior<,>));
            cfg.AddBehavior(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
            cfg.AddBehavior(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
            cfg.AddBehavior(typeof(IPipelineBehavior<,>), typeof(PerformanceBehavior<,>));
        });

        services.AddValidatorsFromAssembly(assembly);

        return services;
    }
}
```

- [ ] **Step 10: Build Application project**

```powershell
dotnet build src/ONEVO.Application/ONEVO.Application.csproj
```

Expected: `Build succeeded.`

- [ ] **Step 11: Commit**

```powershell
git add src/ONEVO.Application tests/ONEVO.Tests.Unit
git commit -m "feat(application): add Result<T>, interfaces, MediatR behaviors, DI registration"
```

---

## Task 3: Foundation Entities (Domain)

**Files:**
- Create: `src/ONEVO.Domain/Features/InfrastructureModule/Entities/Country.cs`
- Create: `src/ONEVO.Domain/Features/InfrastructureModule/Entities/Tenant.cs`
- Create: `src/ONEVO.Domain/Features/InfrastructureModule/Entities/User.cs`
- Create: `src/ONEVO.Domain/Features/InfrastructureModule/Entities/FileRecord.cs`

- [ ] **Step 1: Create Country entity**

Create `src/ONEVO.Domain/Features/InfrastructureModule/Entities/Country.cs`:

```csharp
using ONEVO.Domain.Common;

namespace ONEVO.Domain.Features.InfrastructureModule.Entities;

public class Country : PlatformEntity
{
    public string Code { get; private set; } = string.Empty;        // ISO 3166-1 alpha-2
    public string Name { get; private set; } = string.Empty;
    public string? PhoneCode { get; private set; }
    public string? CurrencyCode { get; private set; }
    public string? FlagEmoji { get; private set; }

    private Country() { }

    public static Country Create(string code, string name, string? phoneCode = null, string? currencyCode = null, string? flagEmoji = null)
        => new() { Id = Guid.NewGuid(), Code = code.ToUpperInvariant(), Name = name, PhoneCode = phoneCode, CurrencyCode = currencyCode, FlagEmoji = flagEmoji, CreatedAt = DateTimeOffset.UtcNow };
}
```

- [ ] **Step 2: Create Tenant entity**

Create `src/ONEVO.Domain/Features/InfrastructureModule/Entities/Tenant.cs`:

```csharp
using ONEVO.Domain.Common;

namespace ONEVO.Domain.Features.InfrastructureModule.Entities;

public class Tenant : PlatformEntity
{
    public string Name { get; private set; } = string.Empty;
    public string Slug { get; private set; } = string.Empty;
    public string Status { get; private set; } = "provisioning";
    public Guid? SubscriptionPlanId { get; private set; }   // FK wired when SharedPlatform lands
    public string? PrimaryDomain { get; private set; }
    public bool IsActive { get; private set; }
    public DateTimeOffset? SuspendedAt { get; private set; }
    public DateTimeOffset? ActivatedAt { get; private set; }

    private Tenant() { }

    public static Tenant Create(string name, string slug)
        => new() { Id = Guid.NewGuid(), Name = name, Slug = slug.ToLowerInvariant(), Status = "provisioning", IsActive = false, CreatedAt = DateTimeOffset.UtcNow };
}
```

- [ ] **Step 3: Create User entity**

Create `src/ONEVO.Domain/Features/InfrastructureModule/Entities/User.cs`:

```csharp
using ONEVO.Domain.Common;

namespace ONEVO.Domain.Features.InfrastructureModule.Entities;

public class User : BaseEntity
{
    public string Email { get; private set; } = string.Empty;
    public string PasswordHash { get; private set; } = string.Empty;
    public string FirstName { get; private set; } = string.Empty;
    public string LastName { get; private set; } = string.Empty;
    public bool IsActive { get; private set; }
    public bool MustChangePassword { get; private set; }
    public bool PasswordSetByAdmin { get; private set; }
    public DateTimeOffset? TemporaryPasswordExpiresAt { get; private set; }

    private User() { }

    public static User Create(string email, string passwordHash, string firstName, string lastName, Guid tenantId, Guid createdById)
        => new()
        {
            Id = Guid.NewGuid(), TenantId = tenantId, CreatedById = createdById, CreatedAt = DateTimeOffset.UtcNow,
            Email = email.Trim().ToLowerInvariant(), PasswordHash = passwordHash,
            FirstName = firstName, LastName = lastName, IsActive = true
        };
}
```

- [ ] **Step 4: Create FileRecord entity**

Create `src/ONEVO.Domain/Features/InfrastructureModule/Entities/FileRecord.cs`:

```csharp
using ONEVO.Domain.Common;

namespace ONEVO.Domain.Features.InfrastructureModule.Entities;

public class FileRecord : BaseEntity
{
    public string OriginalName { get; private set; } = string.Empty;
    public string ContentType { get; private set; } = string.Empty;
    public long SizeBytes { get; private set; }
    public string StoragePath { get; private set; } = string.Empty;

    private FileRecord() { }

    public static FileRecord Create(string originalName, string contentType, long sizeBytes, string storagePath, Guid tenantId, Guid createdById)
        => new()
        {
            Id = Guid.NewGuid(), TenantId = tenantId, CreatedById = createdById, CreatedAt = DateTimeOffset.UtcNow,
            OriginalName = originalName, ContentType = contentType, SizeBytes = sizeBytes, StoragePath = storagePath
        };
}
```

- [ ] **Step 5: Build and commit**

```powershell
dotnet build src/ONEVO.Domain/ONEVO.Domain.csproj
git add src/ONEVO.Domain
git commit -m "feat(domain): add foundation entities — Country, Tenant, User, FileRecord"
```

---

## Task 4: Infrastructure Persistence Foundation

**Files:**
- Modify: `src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj`
- Create: `src/ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/ApplicationDbContextFactory.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/CountryConfiguration.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/TenantConfiguration.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/UserConfiguration.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/FileRecordConfiguration.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Interceptors/AuditableEntityInterceptor.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Interceptors/SoftDeleteInterceptor.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Interceptors/DomainEventDispatchInterceptor.cs`
- Create: `src/ONEVO.Infrastructure/Services/CurrentUserService.cs`
- Create: `src/ONEVO.Infrastructure/Services/DateTimeProvider.cs`
- Create: `src/ONEVO.Infrastructure/DependencyInjection.cs`
- Test: `tests/ONEVO.Tests.Integration/DbContextBootTests.cs`

- [ ] **Step 1: Write failing DbContext boot test**

Create `tests/ONEVO.Tests.Integration/DbContextBootTests.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using ONEVO.Infrastructure.Persistence;

namespace ONEVO.Tests.Integration;

public class DbContextBootTests
{
    [Fact]
    public void ApplicationDbContext_CanBeConstructed_WithInMemoryDatabase()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;

        using var context = new ApplicationDbContext(options, null);

        Assert.NotNull(context);
        Assert.NotNull(context.Countries);
        Assert.NotNull(context.Tenants);
        Assert.NotNull(context.Users);
        Assert.NotNull(context.FileRecords);
    }
}
```

- [ ] **Step 2: Run — verify FAILS (types missing)**

```powershell
dotnet test tests/ONEVO.Tests.Integration/ONEVO.Tests.Integration.csproj --filter "DbContextBootTests"
```

Expected: build error.

- [ ] **Step 3: Update Infrastructure.csproj**

Edit `src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="MediatR" Version="12.4.1" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="9.0.4">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
    <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="9.0.4" />
    <PackageReference Include="Microsoft.AspNetCore.Http.Abstractions" Version="2.3.0" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\ONEVO.Application\ONEVO.Application.csproj" />
  </ItemGroup>
</Project>
```

- [ ] **Step 4: Update Tests.Integration.csproj to add InMemory + reference Infrastructure**

The existing csproj already references Infrastructure. Add InMemory package:

Edit `tests/ONEVO.Tests.Integration/ONEVO.Tests.Integration.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="coverlet.collector" Version="6.0.2" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.12.0" />
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="9.0.4" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.InMemory" Version="9.0.4" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
  </ItemGroup>
  <ItemGroup>
    <Using Include="Xunit" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\..\src\ONEVO.Infrastructure\ONEVO.Infrastructure.csproj" />
    <ProjectReference Include="..\..\src\ONEVO.Api\ONEVO.Api.csproj" />
    <ProjectReference Include="..\..\src\ONEVO.Admin.Api\ONEVO.Admin.Api.csproj" />
  </ItemGroup>
</Project>
```

- [ ] **Step 5: Create Interceptors**

Create `src/ONEVO.Infrastructure/Persistence/Interceptors/AuditableEntityInterceptor.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;
using ONEVO.Application.Common.Interfaces;
using ONEVO.Domain.Common;

namespace ONEVO.Infrastructure.Persistence.Interceptors;

public class AuditableEntityInterceptor : SaveChangesInterceptor
{
    private readonly ICurrentUserService? _currentUserService;
    private readonly IDateTimeProvider? _dateTimeProvider;

    public AuditableEntityInterceptor(ICurrentUserService? currentUserService = null, IDateTimeProvider? dateTimeProvider = null)
    {
        _currentUserService = currentUserService;
        _dateTimeProvider = dateTimeProvider;
    }

    public override InterceptionResult<int> SavingChanges(DbContextEventData eventData, InterceptionResult<int> result)
    {
        UpdateAuditFields(eventData.Context);
        return base.SavingChanges(eventData, result);
    }

    public override ValueTask<InterceptionResult<int>> SavingChangesAsync(DbContextEventData eventData, InterceptionResult<int> result, CancellationToken ct = default)
    {
        UpdateAuditFields(eventData.Context);
        return base.SavingChangesAsync(eventData, result, ct);
    }

    private void UpdateAuditFields(DbContext? context)
    {
        if (context is null) return;
        var now = _dateTimeProvider?.UtcNow ?? DateTimeOffset.UtcNow;
        var userId = _currentUserService?.UserId ?? Guid.Empty;

        foreach (var entry in context.ChangeTracker.Entries<BaseEntity>())
        {
            if (entry.State == EntityState.Added)
            {
                entry.Entity.CreatedAt = now;
                entry.Entity.CreatedById = userId;
            }
            if (entry.State is EntityState.Added or EntityState.Modified)
                entry.Entity.UpdatedAt = now;
        }

        foreach (var entry in context.ChangeTracker.Entries<PlatformEntity>())
        {
            if (entry.State == EntityState.Added) entry.Entity.CreatedAt = now;
            if (entry.State is EntityState.Added or EntityState.Modified) entry.Entity.UpdatedAt = now;
        }
    }
}
```

Create `src/ONEVO.Infrastructure/Persistence/Interceptors/SoftDeleteInterceptor.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;
using ONEVO.Domain.Common;

namespace ONEVO.Infrastructure.Persistence.Interceptors;

public class SoftDeleteInterceptor : SaveChangesInterceptor
{
    public override InterceptionResult<int> SavingChanges(DbContextEventData eventData, InterceptionResult<int> result)
    {
        SoftDelete(eventData.Context);
        return base.SavingChanges(eventData, result);
    }

    public override ValueTask<InterceptionResult<int>> SavingChangesAsync(DbContextEventData eventData, InterceptionResult<int> result, CancellationToken ct = default)
    {
        SoftDelete(eventData.Context);
        return base.SavingChangesAsync(eventData, result, ct);
    }

    private static void SoftDelete(DbContext? context)
    {
        if (context is null) return;
        foreach (var entry in context.ChangeTracker.Entries<BaseEntity>().Where(e => e.State == EntityState.Deleted))
        {
            entry.State = EntityState.Modified;
            entry.Entity.IsDeleted = true;
        }
    }
}
```

Create `src/ONEVO.Infrastructure/Persistence/Interceptors/DomainEventDispatchInterceptor.cs`:

```csharp
using MediatR;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;
using ONEVO.Domain.Common;

namespace ONEVO.Infrastructure.Persistence.Interceptors;

public class DomainEventDispatchInterceptor : SaveChangesInterceptor
{
    private readonly IPublisher? _publisher;

    public DomainEventDispatchInterceptor(IPublisher? publisher = null) => _publisher = publisher;

    public override async ValueTask<int> SavedChangesAsync(SaveChangesCompletedEventData eventData, int result, CancellationToken ct = default)
    {
        await DispatchAsync(eventData.Context, ct);
        return await base.SavedChangesAsync(eventData, result, ct);
    }

    public override int SavedChanges(SaveChangesCompletedEventData eventData, int result)
    {
        DispatchAsync(eventData.Context, CancellationToken.None).GetAwaiter().GetResult();
        return base.SavedChanges(eventData, result);
    }

    private async Task DispatchAsync(DbContext? context, CancellationToken ct)
    {
        if (context is null || _publisher is null) return;

        var entities = context.ChangeTracker.Entries<BaseEntity>()
            .Where(e => e.Entity.DomainEvents.Count > 0)
            .Select(e => e.Entity)
            .ToList();

        var events = entities.SelectMany(e => e.DomainEvents).ToList();
        entities.ForEach(e => e.ClearDomainEvents());

        foreach (var ev in events)
            await _publisher.Publish(ev, ct);
    }
}
```

- [ ] **Step 6: Create ApplicationDbContext.cs**

Create `src/ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using ONEVO.Application.Common.Interfaces;
using ONEVO.Domain.Common;
using ONEVO.Domain.Features.InfrastructureModule.Entities;
using ONEVO.Infrastructure.Persistence.Interceptors;

namespace ONEVO.Infrastructure.Persistence;

public class ApplicationDbContext : DbContext, IApplicationDbContext, IUnitOfWork
{
    private readonly ICurrentUserService? _currentUserService;

    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options, ICurrentUserService? currentUserService)
        : base(options)
    {
        _currentUserService = currentUserService;
    }

    public DbSet<Country> Countries => Set<Country>();
    public DbSet<Tenant> Tenants => Set<Tenant>();
    public DbSet<User> Users => Set<User>();
    public DbSet<FileRecord> FileRecords => Set<FileRecord>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(ApplicationDbContext).Assembly);

        var tenantId = _currentUserService?.TenantId ?? Guid.Empty;
        modelBuilder.Entity<User>().HasQueryFilter(u => !u.IsDeleted && u.TenantId == tenantId);
        modelBuilder.Entity<FileRecord>().HasQueryFilter(f => !f.IsDeleted && f.TenantId == tenantId);

        base.OnModelCreating(modelBuilder);
    }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.AddInterceptors(
            new AuditableEntityInterceptor(),
            new SoftDeleteInterceptor(),
            new DomainEventDispatchInterceptor());
    }
}
```

- [ ] **Step 7: Create ApplicationDbContextFactory.cs**

Create `src/ONEVO.Infrastructure/Persistence/ApplicationDbContextFactory.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace ONEVO.Infrastructure.Persistence;

public class ApplicationDbContextFactory : IDesignTimeDbContextFactory<ApplicationDbContext>
{
    public ApplicationDbContext CreateDbContext(string[] args)
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseNpgsql("Host=localhost;Port=5432;Database=onevo_design;Username=postgres;Password=postgres",
                o => o.MigrationsAssembly(typeof(ApplicationDbContext).Assembly.FullName))
            .Options;

        return new ApplicationDbContext(options, currentUserService: null);
    }
}
```

- [ ] **Step 8: Create EF Configurations**

Create `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/CountryConfiguration.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using ONEVO.Domain.Features.InfrastructureModule.Entities;

namespace ONEVO.Infrastructure.Persistence.Configurations.InfrastructureModule;

public class CountryConfiguration : IEntityTypeConfiguration<Country>
{
    public void Configure(EntityTypeBuilder<Country> builder)
    {
        builder.ToTable("countries");
        builder.HasKey(c => c.Id);
        builder.Property(c => c.Id).HasColumnName("id");
        builder.Property(c => c.Code).HasColumnName("code").HasMaxLength(2).IsRequired();
        builder.Property(c => c.Name).HasColumnName("name").HasMaxLength(100).IsRequired();
        builder.Property(c => c.PhoneCode).HasColumnName("phone_code").HasMaxLength(10);
        builder.Property(c => c.CurrencyCode).HasColumnName("currency_code").HasMaxLength(3);
        builder.Property(c => c.FlagEmoji).HasColumnName("flag_emoji").HasMaxLength(10);
        builder.Property(c => c.CreatedAt).HasColumnName("created_at");
        builder.Property(c => c.UpdatedAt).HasColumnName("updated_at");
        builder.Property(c => c.IsDeleted).HasColumnName("is_deleted").HasDefaultValue(false);
        builder.HasIndex(c => c.Code).IsUnique();
    }
}
```

Create `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/TenantConfiguration.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using ONEVO.Domain.Features.InfrastructureModule.Entities;

namespace ONEVO.Infrastructure.Persistence.Configurations.InfrastructureModule;

public class TenantConfiguration : IEntityTypeConfiguration<Tenant>
{
    public void Configure(EntityTypeBuilder<Tenant> builder)
    {
        builder.ToTable("tenants");
        builder.HasKey(t => t.Id);
        builder.Property(t => t.Id).HasColumnName("id");
        builder.Property(t => t.Name).HasColumnName("name").HasMaxLength(200).IsRequired();
        builder.Property(t => t.Slug).HasColumnName("slug").HasMaxLength(100).IsRequired();
        builder.Property(t => t.Status).HasColumnName("status").HasMaxLength(30).IsRequired();
        builder.Property(t => t.SubscriptionPlanId).HasColumnName("subscription_plan_id");
        builder.Property(t => t.PrimaryDomain).HasColumnName("primary_domain").HasMaxLength(253);
        builder.Property(t => t.IsActive).HasColumnName("is_active").HasDefaultValue(false);
        builder.Property(t => t.SuspendedAt).HasColumnName("suspended_at");
        builder.Property(t => t.ActivatedAt).HasColumnName("activated_at");
        builder.Property(t => t.CreatedAt).HasColumnName("created_at");
        builder.Property(t => t.UpdatedAt).HasColumnName("updated_at");
        builder.Property(t => t.IsDeleted).HasColumnName("is_deleted").HasDefaultValue(false);
        builder.HasIndex(t => t.Slug).IsUnique();
    }
}
```

Create `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/UserConfiguration.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using ONEVO.Domain.Features.InfrastructureModule.Entities;

namespace ONEVO.Infrastructure.Persistence.Configurations.InfrastructureModule;

public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.ToTable("users");
        builder.HasKey(u => u.Id);
        builder.Property(u => u.Id).HasColumnName("id");
        builder.Property(u => u.TenantId).HasColumnName("tenant_id");
        builder.Property(u => u.CreatedAt).HasColumnName("created_at");
        builder.Property(u => u.UpdatedAt).HasColumnName("updated_at");
        builder.Property(u => u.CreatedById).HasColumnName("created_by_id");
        builder.Property(u => u.IsDeleted).HasColumnName("is_deleted").HasDefaultValue(false);
        builder.Property(u => u.Email).HasColumnName("email").HasMaxLength(254).IsRequired();
        builder.Property(u => u.PasswordHash).HasColumnName("password_hash").IsRequired();
        builder.Property(u => u.FirstName).HasColumnName("first_name").HasMaxLength(100).IsRequired();
        builder.Property(u => u.LastName).HasColumnName("last_name").HasMaxLength(100).IsRequired();
        builder.Property(u => u.IsActive).HasColumnName("is_active").HasDefaultValue(true);
        builder.Property(u => u.MustChangePassword).HasColumnName("must_change_password").HasDefaultValue(false);
        builder.Property(u => u.PasswordSetByAdmin).HasColumnName("password_set_by_admin").HasDefaultValue(false);
        builder.Property(u => u.TemporaryPasswordExpiresAt).HasColumnName("temporary_password_expires_at");
        builder.HasIndex(u => new { u.TenantId, u.Email }).IsUnique();
    }
}
```

Create `src/ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/FileRecordConfiguration.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using ONEVO.Domain.Features.InfrastructureModule.Entities;

namespace ONEVO.Infrastructure.Persistence.Configurations.InfrastructureModule;

public class FileRecordConfiguration : IEntityTypeConfiguration<FileRecord>
{
    public void Configure(EntityTypeBuilder<FileRecord> builder)
    {
        builder.ToTable("file_records");
        builder.HasKey(f => f.Id);
        builder.Property(f => f.Id).HasColumnName("id");
        builder.Property(f => f.TenantId).HasColumnName("tenant_id");
        builder.Property(f => f.CreatedAt).HasColumnName("created_at");
        builder.Property(f => f.UpdatedAt).HasColumnName("updated_at");
        builder.Property(f => f.CreatedById).HasColumnName("created_by_id");
        builder.Property(f => f.IsDeleted).HasColumnName("is_deleted").HasDefaultValue(false);
        builder.Property(f => f.OriginalName).HasColumnName("original_name").HasMaxLength(500).IsRequired();
        builder.Property(f => f.ContentType).HasColumnName("content_type").HasMaxLength(100).IsRequired();
        builder.Property(f => f.SizeBytes).HasColumnName("size_bytes").IsRequired();
        builder.Property(f => f.StoragePath).HasColumnName("storage_path").HasMaxLength(1000).IsRequired();
    }
}
```

- [ ] **Step 9: Create Services**

Create `src/ONEVO.Infrastructure/Services/CurrentUserService.cs`:

```csharp
using Microsoft.AspNetCore.Http;
using ONEVO.Application.Common.Interfaces;

namespace ONEVO.Infrastructure.Services;

public class CurrentUserService : ICurrentUserService, ITenantContext
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public CurrentUserService(IHttpContextAccessor httpContextAccessor)
        => _httpContextAccessor = httpContextAccessor;

    public Guid? UserId => ParseGuidClaim("sub");
    public Guid? TenantId => ParseGuidClaim("tenant_id");
    public bool IsAuthenticated => _httpContextAccessor.HttpContext?.User.Identity?.IsAuthenticated ?? false;
    bool ITenantContext.HasTenant => TenantId.HasValue;

    private Guid? ParseGuidClaim(string claimType)
    {
        var value = _httpContextAccessor.HttpContext?.User.FindFirst(claimType)?.Value;
        return Guid.TryParse(value, out var id) ? id : null;
    }
}
```

Create `src/ONEVO.Infrastructure/Services/DateTimeProvider.cs`:

```csharp
using ONEVO.Application.Common.Interfaces;

namespace ONEVO.Infrastructure.Services;

public class DateTimeProvider : IDateTimeProvider
{
    public DateTimeOffset UtcNow => DateTimeOffset.UtcNow;
    public DateOnly Today => DateOnly.FromDateTime(DateTime.UtcNow);
}
```

- [ ] **Step 10: Create Infrastructure DependencyInjection.cs**

Create `src/ONEVO.Infrastructure/DependencyInjection.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using ONEVO.Application.Common.Interfaces;
using ONEVO.Infrastructure.Persistence;
using ONEVO.Infrastructure.Persistence.Interceptors;
using ONEVO.Infrastructure.Services;

namespace ONEVO.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddHttpContextAccessor();
        services.AddScoped<ICurrentUserService, CurrentUserService>();
        services.AddScoped<ITenantContext>(sp => (ITenantContext)sp.GetRequiredService<ICurrentUserService>());
        services.AddSingleton<IDateTimeProvider, DateTimeProvider>();

        services.AddScoped<AuditableEntityInterceptor>();
        services.AddScoped<SoftDeleteInterceptor>();
        services.AddScoped<DomainEventDispatchInterceptor>();

        services.AddDbContext<ApplicationDbContext>((sp, options) =>
        {
            options.UseNpgsql(
                configuration.GetConnectionString("DefaultConnection"),
                npgsql => npgsql.MigrationsAssembly(typeof(ApplicationDbContext).Assembly.FullName));

            options.AddInterceptors(
                sp.GetRequiredService<AuditableEntityInterceptor>(),
                sp.GetRequiredService<SoftDeleteInterceptor>(),
                sp.GetRequiredService<DomainEventDispatchInterceptor>());
        });

        services.AddScoped<IApplicationDbContext>(sp => sp.GetRequiredService<ApplicationDbContext>());
        services.AddScoped<IUnitOfWork>(sp => sp.GetRequiredService<ApplicationDbContext>());

        return services;
    }
}
```

- [ ] **Step 11: Run DbContext boot test — verify PASSES**

```powershell
dotnet test tests/ONEVO.Tests.Integration/ONEVO.Tests.Integration.csproj --filter "DbContextBootTests"
```

Expected: `Passed! - 1 test`

- [ ] **Step 12: Commit**

```powershell
git add src/ONEVO.Infrastructure tests/ONEVO.Tests.Integration
git commit -m "feat(infrastructure): add ApplicationDbContext, EF configs, interceptors, services, DI"
```

---

## Task 5: EF Migration — InitialFoundation

**Files:**
- Create: `src/ONEVO.Infrastructure/Persistence/Migrations/` (generated by dotnet-ef)

- [ ] **Step 1: Install dotnet-ef global tool if not already present**

```powershell
dotnet tool install --global dotnet-ef
```

If already installed: `dotnet tool update --global dotnet-ef`

- [ ] **Step 2: Create InitialFoundation migration**

```powershell
cd C:\OneVo-HR\OneVo-backend
dotnet ef migrations add InitialFoundation `
  --project src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj `
  --startup-project src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj `
  --output-dir Persistence/Migrations
```

Expected: Three files created under `src/ONEVO.Infrastructure/Persistence/Migrations/`:
- `*_InitialFoundation.cs`
- `*_InitialFoundation.Designer.cs`
- `ApplicationDbContextModelSnapshot.cs`

- [ ] **Step 3: Verify build still clean**

```powershell
dotnet build src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj
```

Expected: `Build succeeded.`

- [ ] **Step 4: Commit**

```powershell
git add src/ONEVO.Infrastructure/Persistence/Migrations
git commit -m "chore(db): add InitialFoundation EF migration for countries, tenants, users, file_records"
```

---

## Task 6: ONEVO.Api Host

**Files:**
- Modify: `src/ONEVO.Api/ONEVO.Api.csproj`
- Modify: `src/ONEVO.Api/Program.cs`
- Modify: `src/ONEVO.Api/appsettings.json`
- Create: `src/ONEVO.Api/Middleware/CorrelationIdMiddleware.cs`
- Create: `src/ONEVO.Api/Middleware/ExceptionMappingMiddleware.cs`
- Create: `src/ONEVO.Api/Middleware/TenantResolutionMiddleware.cs`
- Test: `tests/ONEVO.Tests.Integration/ApiBootTests.cs`

- [ ] **Step 1: Write failing API boot test**

Create `tests/ONEVO.Tests.Integration/ApiBootTests.cs`:

```csharp
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using ONEVO.Infrastructure.Persistence;

namespace ONEVO.Tests.Integration;

public class ApiBootTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public ApiBootTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
            builder.ConfigureServices(services =>
            {
                var descriptor = services.SingleOrDefault(d => d.ServiceType == typeof(DbContextOptions<ApplicationDbContext>));
                if (descriptor is not null) services.Remove(descriptor);
                services.AddDbContext<ApplicationDbContext>((sp, opt) =>
                    opt.UseInMemoryDatabase("ApiBootTest"));
            }));
    }

    [Fact]
    public async Task HealthEndpoint_Returns200()
    {
        var client = _factory.CreateClient();
        var response = await client.GetAsync("/api/v1/health");
        Assert.Equal(System.Net.HttpStatusCode.OK, response.StatusCode);
    }
}
```

- [ ] **Step 2: Run — verify FAILS**

```powershell
dotnet test tests/ONEVO.Tests.Integration/ONEVO.Tests.Integration.csproj --filter "ApiBootTests"
```

Expected: build error — Program class not accessible.

- [ ] **Step 3: Update ONEVO.Api.csproj with Serilog**

Edit `src/ONEVO.Api/ONEVO.Api.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="9.0.4" />
    <PackageReference Include="Serilog.AspNetCore" Version="9.0.0" />
    <PackageReference Include="Serilog.Sinks.Console" Version="6.0.0" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\ONEVO.Infrastructure\ONEVO.Infrastructure.csproj" />
    <ProjectReference Include="..\ONEVO.Application\ONEVO.Application.csproj" />
  </ItemGroup>
</Project>
```

- [ ] **Step 4: Create Middleware**

Create `src/ONEVO.Api/Middleware/CorrelationIdMiddleware.cs`:

```csharp
namespace ONEVO.Api.Middleware;

public class CorrelationIdMiddleware
{
    private const string Header = "X-Correlation-Id";
    private readonly RequestDelegate _next;

    public CorrelationIdMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context)
    {
        var id = context.Request.Headers.TryGetValue(Header, out var existing)
            ? existing.ToString()
            : Guid.NewGuid().ToString();

        context.Response.Headers[Header] = id;
        context.Items["CorrelationId"] = id;

        await _next(context);
    }
}
```

Create `src/ONEVO.Api/Middleware/ExceptionMappingMiddleware.cs`:

```csharp
using FluentValidation;
using Microsoft.AspNetCore.Mvc;
using ONEVO.Domain.Errors;

namespace ONEVO.Api.Middleware;

public class ExceptionMappingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionMappingMiddleware> _logger;

    public ExceptionMappingMiddleware(RequestDelegate next, ILogger<ExceptionMappingMiddleware> logger)
    { _next = next; _logger = logger; }

    public async Task InvokeAsync(HttpContext context)
    {
        try { await _next(context); }
        catch (Exception ex) { await HandleAsync(context, ex); }
    }

    private async Task HandleAsync(HttpContext context, Exception ex)
    {
        var correlationId = context.Items["CorrelationId"]?.ToString() ?? "unknown";

        var (status, title) = ex switch
        {
            ValidationException   => (StatusCodes.Status422UnprocessableEntity, "Validation Error"),
            NotFoundException     => (StatusCodes.Status404NotFound, "Not Found"),
            ForbiddenException    => (StatusCodes.Status403Forbidden, "Forbidden"),
            DomainException       => (StatusCodes.Status422UnprocessableEntity, "Domain Error"),
            _                     => (StatusCodes.Status500InternalServerError, "Internal Server Error")
        };

        if (status == 500) _logger.LogError(ex, "Unhandled exception (correlation: {Id})", correlationId);

        var problem = new ProblemDetails
        {
            Title = title, Status = status, Detail = ex.Message,
            Instance = context.Request.Path,
            Extensions = { ["correlationId"] = correlationId }
        };

        context.Response.StatusCode = status;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problem);
    }
}
```

Create `src/ONEVO.Api/Middleware/TenantResolutionMiddleware.cs`:

```csharp
namespace ONEVO.Api.Middleware;

public class TenantResolutionMiddleware
{
    private readonly RequestDelegate _next;
    public TenantResolutionMiddleware(RequestDelegate next) => _next = next;

    // Tenant is resolved from JWT claims by CurrentUserService.
    // Custom domain → tenant lookup added in Phase 2.
    public Task InvokeAsync(HttpContext context) => _next(context);
}
```

- [ ] **Step 5: Rewrite Program.cs**

Overwrite `src/ONEVO.Api/Program.cs`:

```csharp
using ONEVO.Api.Middleware;
using ONEVO.Application;
using ONEVO.Infrastructure;
using Serilog;

Log.Logger = new LoggerConfiguration().WriteTo.Console().CreateBootstrapLogger();

try
{
    var builder = WebApplication.CreateBuilder(args);

    builder.Host.UseSerilog((ctx, lc) => lc
        .ReadFrom.Configuration(ctx.Configuration)
        .Enrich.FromLogContext()
        .Enrich.WithProperty("Application", "ONEVO.Api")
        .WriteTo.Console());

    builder.Services.AddOpenApi();
    builder.Services.AddHealthChecks();
    builder.Services.AddApplication();
    builder.Services.AddInfrastructure(builder.Configuration);

    var app = builder.Build();

    app.UseMiddleware<CorrelationIdMiddleware>();
    app.UseMiddleware<ExceptionMappingMiddleware>();
    app.UseMiddleware<TenantResolutionMiddleware>();

    if (app.Environment.IsDevelopment())
        app.MapOpenApi();

    app.UseHttpsRedirection();
    app.MapHealthChecks("/api/v1/health");

    app.Run();
}
catch (Exception ex) when (ex is not HostAbortedException)
{
    Log.Fatal(ex, "ONEVO.Api startup failed");
}
finally
{
    Log.CloseAndFlush();
}

public partial class Program { }
```

- [ ] **Step 6: Update appsettings.json**

Overwrite `src/ONEVO.Api/appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=onevo;Username=postgres;Password=postgres"
  },
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "Microsoft.EntityFrameworkCore": "Warning",
        "System": "Warning"
      }
    }
  },
  "AllowedHosts": "*"
}
```

- [ ] **Step 7: Run API boot test — verify PASSES**

```powershell
dotnet test tests/ONEVO.Tests.Integration/ONEVO.Tests.Integration.csproj --filter "ApiBootTests"
```

Expected: `Passed! - 1 test`

- [ ] **Step 8: Commit**

```powershell
git add src/ONEVO.Api tests/ONEVO.Tests.Integration
git commit -m "feat(api): rewrite Program.cs — health endpoint, correlation ID, exception mapping, Serilog, tenant resolution middleware"
```

---

## Task 7: ONEVO.Admin.Api Host

**Files:**
- Modify: `src/ONEVO.Admin.Api/ONEVO.Admin.Api.csproj`
- Modify: `src/ONEVO.Admin.Api/Program.cs`
- Modify: `src/ONEVO.Admin.Api/appsettings.json`
- Create: `src/ONEVO.Admin.Api/Middleware/CorrelationIdMiddleware.cs`
- Create: `src/ONEVO.Admin.Api/Middleware/ExceptionMappingMiddleware.cs`
- Test: `tests/ONEVO.Tests.Integration/AdminApiBootTests.cs`

- [ ] **Step 1: Write failing Admin API boot test**

Create `tests/ONEVO.Tests.Integration/AdminApiBootTests.cs`:

```csharp
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using ONEVO.Infrastructure.Persistence;

namespace ONEVO.Tests.Integration;

public class AdminApiBootTests : IClassFixture<WebApplicationFactory<AdminProgram>>
{
    private readonly WebApplicationFactory<AdminProgram> _factory;

    public AdminApiBootTests(WebApplicationFactory<AdminProgram> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
            builder.ConfigureServices(services =>
            {
                var descriptor = services.SingleOrDefault(d => d.ServiceType == typeof(DbContextOptions<ApplicationDbContext>));
                if (descriptor is not null) services.Remove(descriptor);
                services.AddDbContext<ApplicationDbContext>((sp, opt) =>
                    opt.UseInMemoryDatabase("AdminApiBootTest"));
            }));
    }

    [Fact]
    public async Task AdminHealthEndpoint_Returns200()
    {
        var client = _factory.CreateClient();
        var response = await client.GetAsync("/admin/v1/health");
        Assert.Equal(System.Net.HttpStatusCode.OK, response.StatusCode);
    }
}
```

- [ ] **Step 2: Update Admin.Api.csproj**

Edit `src/ONEVO.Admin.Api/ONEVO.Admin.Api.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="9.0.4" />
    <PackageReference Include="Serilog.AspNetCore" Version="9.0.0" />
    <PackageReference Include="Serilog.Sinks.Console" Version="6.0.0" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\ONEVO.Infrastructure\ONEVO.Infrastructure.csproj" />
    <ProjectReference Include="..\ONEVO.Application\ONEVO.Application.csproj" />
  </ItemGroup>
</Project>
```

- [ ] **Step 3: Create Admin Middleware**

Create `src/ONEVO.Admin.Api/Middleware/CorrelationIdMiddleware.cs`:

```csharp
namespace ONEVO.Admin.Api.Middleware;

public class CorrelationIdMiddleware
{
    private const string Header = "X-Correlation-Id";
    private readonly RequestDelegate _next;
    public CorrelationIdMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context)
    {
        var id = context.Request.Headers.TryGetValue(Header, out var existing)
            ? existing.ToString() : Guid.NewGuid().ToString();
        context.Response.Headers[Header] = id;
        context.Items["CorrelationId"] = id;
        await _next(context);
    }
}
```

Create `src/ONEVO.Admin.Api/Middleware/ExceptionMappingMiddleware.cs`:

```csharp
using FluentValidation;
using Microsoft.AspNetCore.Mvc;
using ONEVO.Domain.Errors;

namespace ONEVO.Admin.Api.Middleware;

public class ExceptionMappingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionMappingMiddleware> _logger;

    public ExceptionMappingMiddleware(RequestDelegate next, ILogger<ExceptionMappingMiddleware> logger)
    { _next = next; _logger = logger; }

    public async Task InvokeAsync(HttpContext context)
    {
        try { await _next(context); }
        catch (Exception ex) { await HandleAsync(context, ex); }
    }

    private async Task HandleAsync(HttpContext context, Exception ex)
    {
        var correlationId = context.Items["CorrelationId"]?.ToString() ?? "unknown";
        var (status, title) = ex switch
        {
            ValidationException => (422, "Validation Error"),
            NotFoundException   => (404, "Not Found"),
            ForbiddenException  => (403, "Forbidden"),
            DomainException     => (422, "Domain Error"),
            _                   => (500, "Internal Server Error")
        };
        if (status == 500) _logger.LogError(ex, "Unhandled exception (correlation: {Id})", correlationId);
        var problem = new ProblemDetails
        {
            Title = title, Status = status, Detail = ex.Message,
            Instance = context.Request.Path,
            Extensions = { ["correlationId"] = correlationId }
        };
        context.Response.StatusCode = status;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problem);
    }
}
```

- [ ] **Step 4: Rewrite Admin Program.cs**

Overwrite `src/ONEVO.Admin.Api/Program.cs`:

```csharp
using ONEVO.Admin.Api.Middleware;
using ONEVO.Application;
using ONEVO.Infrastructure;
using Serilog;

Log.Logger = new LoggerConfiguration().WriteTo.Console().CreateBootstrapLogger();

try
{
    var builder = WebApplication.CreateBuilder(args);

    builder.Host.UseSerilog((ctx, lc) => lc
        .ReadFrom.Configuration(ctx.Configuration)
        .Enrich.FromLogContext()
        .Enrich.WithProperty("Application", "ONEVO.Admin.Api")
        .WriteTo.Console());

    builder.Services.AddOpenApi();
    builder.Services.AddHealthChecks();
    builder.Services.AddApplication();
    builder.Services.AddInfrastructure(builder.Configuration);

    var app = builder.Build();

    app.UseMiddleware<CorrelationIdMiddleware>();
    app.UseMiddleware<ExceptionMappingMiddleware>();

    if (app.Environment.IsDevelopment())
        app.MapOpenApi();

    app.UseHttpsRedirection();
    app.MapHealthChecks("/admin/v1/health");

    app.Run();
}
catch (Exception ex) when (ex is not HostAbortedException)
{
    Log.Fatal(ex, "ONEVO.Admin.Api startup failed");
}
finally
{
    Log.CloseAndFlush();
}

public partial class AdminProgram { }
```

- [ ] **Step 5: Update Admin appsettings.json**

Overwrite `src/ONEVO.Admin.Api/appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=onevo;Username=postgres;Password=postgres"
  },
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "Microsoft.EntityFrameworkCore": "Warning",
        "System": "Warning"
      }
    }
  },
  "AllowedHosts": "*"
}
```

- [ ] **Step 6: Run Admin boot test — verify PASSES**

```powershell
dotnet test tests/ONEVO.Tests.Integration/ONEVO.Tests.Integration.csproj --filter "AdminApiBootTests"
```

Expected: `Passed! - 1 test`

- [ ] **Step 7: Commit**

```powershell
git add src/ONEVO.Admin.Api tests/ONEVO.Tests.Integration
git commit -m "feat(admin-api): rewrite Program.cs — /admin/v1/health, correlation ID, exception mapping, Serilog"
```

---

## Task 8: Full Verification + DEV1.md Update

- [ ] **Step 1: Run full solution build**

```powershell
cd C:\OneVo-HR\OneVo-backend
dotnet build ONEVO.sln
```

Expected: `Build succeeded. 0 Warning(s) 0 Error(s)`

Fix any errors before proceeding.

- [ ] **Step 2: Run full test suite**

```powershell
dotnet test ONEVO.sln
```

Expected: All tests pass. Count should include:
- `BaseEntityTests` (2 tests)
- `ResultTests` (4 tests)
- `DbContextBootTests` (1 test)
- `ApiBootTests` (1 test)
- `AdminApiBootTests` (1 test)

- [ ] **Step 3: Delete placeholder UnitTest1.cs files**

```powershell
Remove-Item tests/ONEVO.Tests.Unit/UnitTest1.cs -ErrorAction SilentlyContinue
Remove-Item tests/ONEVO.Tests.Integration/UnitTest1.cs -ErrorAction SilentlyContinue
Remove-Item tests/ONEVO.Tests.Architecture/UnitTest1.cs -ErrorAction SilentlyContinue
```

- [ ] **Step 4: Re-run tests — confirm still passing**

```powershell
dotnet test ONEVO.sln
```

- [ ] **Step 5: Update DEV1.md Task 1 checkboxes**

In `C:\OneVo-HR\current-focus\DEV1.md`, mark completed acceptance criteria:

```markdown
- [x] Solution structure exists for API, application, domain, infrastructure, tests, and admin API host.
- [x] Shared kernel includes base entity, auditable entity, result type, domain event base, tenant context abstraction, and time provider abstraction.
- [x] API project exposes health checks and OpenAPI.
- [x] Database context is configured for PostgreSQL and snake_case naming.
- [x] Migrations can be created and applied locally.
- [x] Request pipeline includes correlation ID, exception mapping, tenant resolution, and structured logging.
- [x] Baseline test project validates API boot, admin API boot, and database context boot.
```

- [ ] **Step 6: Final commit**

```powershell
git add .
git commit -m "chore: complete DEV1 Task 1 — backend foundation implemented, all tests passing"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Solution structure — 9 projects, wired
- ✅ Shared kernel — BaseEntity, PlatformEntity, Result<T>, IDomainEvent, ITenantContext, IDateTimeProvider
- ✅ API health checks and OpenAPI — `/api/v1/health`, `/admin/v1/health`
- ✅ DbContext PostgreSQL + snake_case — all configurations use `HasColumnName("snake_case")`
- ✅ Migrations — `InitialFoundation` covering 4 foundation tables
- ✅ Pipeline — CorrelationId, ExceptionMapping, TenantResolution middleware; Serilog
- ✅ Tests — boot tests for both APIs + DbContext boot test

**Placeholder scan:** None found — all steps contain concrete code.

**Type consistency:** `AdminProgram` used in both `AdminApiBootTests` and `Admin Program.cs` partial. `Program` used in `ApiBootTests` and `ONEVO.Api/Program.cs` partial.
