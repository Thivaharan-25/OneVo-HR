# Tenant Management — Testing

**Module:** Infrastructure
**Feature:** Tenant Management
**Location:** `tests/ONEVO.Tests.Unit/Modules/Infrastructure/TenantServiceTests.cs`

---

## Unit Tests

```csharp
public class TenantServiceTests
{
    private readonly Mock<ITenantRepository> _repoMock = new();
    private readonly TenantService _sut;

    [Fact]
    public async Task Provision_tenant_seeds_default_data()
    {
        // Arrange
        // ... setup mocks for provision tenant seeds default data

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Roles and toggles created
    }

    [Fact]
    public async Task Duplicate_slug_returns_conflict()
    {
        // Arrange
        // ... setup mocks for duplicate slug returns conflict

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 409 Conflict
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Provision tenant seeds default data | Unit | Roles and toggles created |
| Duplicate slug returns conflict | Unit | 409 Conflict |

## Related

- [[tenant-management|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
