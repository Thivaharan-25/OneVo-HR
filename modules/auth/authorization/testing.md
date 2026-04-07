# Authorization — Testing

**Module:** Auth
**Feature:** Authorization (RBAC)
**Location:** `tests/ONEVO.Tests.Unit/Modules/Auth/RoleServiceTests.cs`

---

## Unit Tests

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

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create role with permissions | Unit | Role created |
| Duplicate role name | Unit | Conflict |
| Assign role to user | Unit | Success |
| Role already assigned | Unit | Failure |
| Cannot delete system role | Unit | Failure |

## Related

- [[authorization|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
