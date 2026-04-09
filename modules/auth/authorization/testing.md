# Authorization — Testing

**Module:** Auth
**Feature:** Authorization (Hybrid Permission Control)
**Location:** `tests/ONEVO.Tests.Unit/Modules/Auth/`

---

## Unit Tests

### PermissionResolverTests

```csharp
public class PermissionResolverTests
{
    private readonly Mock<IRoleRepository> _roleRepoMock = new();
    private readonly Mock<IUserPermissionOverrideRepository> _overrideRepoMock = new();
    private readonly Mock<IFeatureAccessRepository> _featureAccessRepoMock = new();
    private readonly PermissionResolver _sut;

    [Fact]
    public async Task Resolve_MergesRolePermissionsAndGrantOverrides()
    {
        // Role gives: employees:read
        // Override grants: leave:approve
        // Expected: [employees:read, leave:approve]
    }

    [Fact]
    public async Task Resolve_RevokeOverrideRemovesRolePermission()
    {
        // Role gives: employees:read, employees:update
        // Override revokes: employees:update
        // Expected: [employees:read]
    }

    [Fact]
    public async Task Resolve_FiltersOutPermissionsForUngrantedModules()
    {
        // Role gives: leave:approve, payroll:read
        // Feature grants: only 'leave' module
        // Expected: [leave:approve] (payroll:read filtered out)
    }

    [Fact]
    public async Task Resolve_SuperAdmin_GetsWildcard()
    {
        // Super Admin role -> returns ["*"]
        // No feature filtering applied
    }
}
```

### RoleServiceTests

```csharp
public class RoleServiceTests
{
    private readonly Mock<IRoleRepository> _roleRepoMock = new();
    private readonly Mock<IPermissionRepository> _permRepoMock = new();
    private readonly RoleService _sut;

    [Fact]
    public async Task CreateRoleAsync_ValidInput_CreatesRoleWithPermissions()
    {
        _roleRepoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<string>(), default)).ReturnsAsync(false);
        _permRepoMock.Setup(r => r.AllExistAsync(It.IsAny<List<Guid>>(), default)).ReturnsAsync(true);

        var result = await _sut.CreateRoleAsync(new CreateRoleCommand
        {
            Name = "Custom Manager",
            PermissionIds = new List<Guid> { Guid.NewGuid() }
        }, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.IsSystem.Should().BeFalse();
    }

    [Fact]
    public async Task CreateRoleAsync_DuplicateName_ReturnsConflict()
    {
        _roleRepoMock.Setup(r => r.ExistsByNameAsync("Admin", default)).ReturnsAsync(true);

        var result = await _sut.CreateRoleAsync(new CreateRoleCommand { Name = "Admin" }, default);

        result.IsSuccess.Should().BeFalse();
    }

    [Fact]
    public async Task AssignRoleAsync_AlreadyAssigned_ReturnsFailure()
    {
        _roleRepoMock.Setup(r => r.IsAssignedAsync(It.IsAny<Guid>(), It.IsAny<Guid>(), default)).ReturnsAsync(true);

        var result = await _sut.AssignRoleAsync(Guid.NewGuid(), Guid.NewGuid(), default);

        result.IsSuccess.Should().BeFalse();
    }
}
```

### HierarchyScopeServiceTests

```csharp
public class HierarchyScopeServiceTests
{
    [Fact]
    public async Task GetSubordinateIds_ReturnsDirectAndIndirectReports()
    {
        // Manager -> TeamLead -> Employee
        // Manager should see both TeamLead and Employee
    }

    [Fact]
    public async Task GetSubordinateIds_SuperAdmin_ReturnsAllEmployees()
    {
        // Super Admin bypasses hierarchy
    }

    [Fact]
    public async Task GetSubordinateIds_NoReports_ReturnsEmptySet()
    {
        // Regular employee with no reports -> empty set
    }

    [Fact]
    public async Task GetSubordinateIds_CachesResult()
    {
        // Second call hits Redis, not DB
    }
}
```

### FeatureAccessServiceTests

```csharp
public class FeatureAccessServiceTests
{
    [Fact]
    public async Task Grant_RoleLevel_AllUsersWithRoleGetAccess()
    {
        // Grant 'leave' module to a role -> all users with that role can access leave
    }

    [Fact]
    public async Task Grant_EmployeeLevel_OnlyThatEmployeeGetsAccess()
    {
        // Grant 'payroll' module to employee X -> only X can access payroll
    }

    [Fact]
    public async Task Revoke_InvalidatesCacheForAffectedUsers()
    {
        // Revoking feature access invalidates permission cache
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Resolve permissions: role only | Unit | Role permissions returned |
| Resolve permissions: role + grant override | Unit | Union of both |
| Resolve permissions: role + revoke override | Unit | Role minus revoked |
| Resolve permissions: ungranted module filtered | Unit | Module permissions excluded |
| Super Admin: wildcard permissions | Unit | `*` returned, no filtering |
| Create role with permissions | Unit | Role created |
| Duplicate role name | Unit | Conflict |
| Assign role to user | Unit | Success, cache invalidated |
| Role already assigned | Unit | Failure |
| Cannot delete system role | Unit | Failure |
| Hierarchy: direct reports only | Unit | Returns subordinate IDs |
| Hierarchy: recursive reports | Unit | Returns full subtree |
| Hierarchy: Super Admin bypasses | Unit | Returns all |
| Feature grant to role | Integration | All role users gain access |
| Feature grant to employee | Integration | Only that employee gains access |
| Permission override grant | Integration | Employee gains extra permission |
| Permission override revoke | Integration | Employee loses specific permission |
| Cache invalidation on role change | Integration | Affected users refreshed |
| Cache invalidation on hierarchy change | Integration | Subtree recalculated |

## Related

- [[frontend/cross-cutting/authorization|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
