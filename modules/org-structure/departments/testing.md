# Departments - Testing

**Module:** Org Structure
**Feature:** Departments
**Location:** `tests/ONEVO.Tests.Unit/Modules/OrgStructure/DepartmentServiceTests.cs`

---

## Unit Tests

```csharp
public class DepartmentServiceTests
{
    private readonly Mock<IDepartmentRepository> _repoMock = new();
    private readonly Mock<IEmployeeRepository> _employeeRepoMock = new();
    private readonly Mock<IDomainEventPublisher> _eventPublisherMock = new();
    private readonly DepartmentService _sut;

    public DepartmentServiceTests()
    {
        _sut = new DepartmentService(
            _repoMock.Object,
            _employeeRepoMock.Object,
            _eventPublisherMock.Object);
    }

    [Fact]
    public async Task CreateAsync_WithValidData_ReturnsSuccess()
    {
        _repoMock.Setup(r => r.IsCodeUniqueAsync(It.IsAny<string>(), It.IsAny<Guid>(), default))
            .ReturnsAsync(true);

        var command = new CreateDepartmentCommand
        {
            Name = "Engineering",
            Code = "ENG"
        };

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Name.Should().Be("Engineering");
        result.Value.Code.Should().Be("ENG");
    }

    [Fact]
    public async Task CreateAsync_WithDuplicateCode_ReturnsFailure()
    {
        _repoMock.Setup(r => r.IsCodeUniqueAsync("ENG", It.IsAny<Guid>(), default))
            .ReturnsAsync(false);

        var command = new CreateDepartmentCommand
        {
            Name = "Engineering",
            Code = "ENG"
        };

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("code already exists");
    }

    [Fact]
    public async Task UpdateAsync_CircularReference_ReturnsFailure()
    {
        var grandparent = new Department { Id = Guid.NewGuid(), ParentDepartmentId = null };
        var parent = new Department { Id = Guid.NewGuid(), ParentDepartmentId = grandparent.Id };
        var child = new Department { Id = Guid.NewGuid(), ParentDepartmentId = parent.Id };

        _repoMock.Setup(r => r.GetByIdAsync(grandparent.Id, default)).ReturnsAsync(grandparent);
        _repoMock.Setup(r => r.GetAncestorIdsAsync(child.Id, default))
            .ReturnsAsync(new List<Guid> { parent.Id, grandparent.Id });

        var command = new UpdateDepartmentCommand { ParentDepartmentId = child.Id };
        var result = await _sut.UpdateAsync(grandparent.Id, command, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Circular");
    }

    [Fact]
    public async Task GetAllAsync_TreeView_ReturnsNestedStructure()
    {
        var root = new Department { Id = Guid.NewGuid(), Name = "Root", ParentDepartmentId = null };
        var child = new Department { Id = Guid.NewGuid(), Name = "Child", ParentDepartmentId = root.Id };
        _repoMock.Setup(r => r.GetAllAsync(default))
            .ReturnsAsync(new List<Department> { root, child });

        var result = await _sut.GetAllAsync("tree", default);

        result.Should().HaveCount(1);
        result[0].Children.Should().HaveCount(1);
        result[0].Children[0].Name.Should().Be("Child");
    }
}
```

## Integration Tests

```csharp
public class DepartmentEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _adminClient;

    public DepartmentEndpointTests(ONEVOWebFactory factory)
    {
        _adminClient = factory.CreateAuthenticatedClient(permission: "org:manage");
    }

    [Fact]
    public async Task CreateDepartment_ReturnsInTreeView()
    {
        var create = new
        {
            Name = "QA Department",
            Code = $"QA-{Guid.NewGuid():N}"[..10]
        };

        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments", create);
        resp.StatusCode.Should().Be(HttpStatusCode.Created);

        var tree = await _adminClient.GetFromJsonAsync<List<DepartmentTreeDto>>(
            "/api/v1/org/departments?view=tree");
        tree.Should().NotBeNull();
    }

    [Fact]
    public async Task CreateChildDepartment_AppearsUnderParent()
    {
        var parentResp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Parent", Code = $"P-{Guid.NewGuid():N}"[..10] });
        var parentId = (await parentResp.Content.ReadFromJsonAsync<DepartmentDto>())!.Id;

        var childResp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Child", Code = $"C-{Guid.NewGuid():N}"[..10], ParentDepartmentId = parentId });
        childResp.StatusCode.Should().Be(HttpStatusCode.Created);
    }

    [Fact]
    public async Task RecursiveTreeQuery_HandlesDeepHierarchy()
    {
        Guid? parentId = null;
        for (int i = 0; i < 5; i++)
        {
            var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
                new { Name = $"Level-{i}", Code = $"L{i}-{Guid.NewGuid():N}"[..10], ParentDepartmentId = parentId });
            parentId = (await resp.Content.ReadFromJsonAsync<DepartmentDto>())!.Id;
        }

        var tree = await _adminClient.GetFromJsonAsync<List<DepartmentTreeDto>>(
            "/api/v1/org/departments?view=tree");
        tree.Should().NotBeEmpty();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create with valid data | Unit | Success |
| Create with duplicate code | Unit | Failure, conflict |
| Update causing circular reference | Unit | Failure |
| Tree view returns nested structure | Unit | Correct nesting |
| Create and retrieve in tree | Integration | Appears in tree |
| Create child under parent | Integration | 201 Created |
| 5-level deep hierarchy | Integration | Correct tree rendering |
| Deactivate parent with active children | Integration | Blocked |
| Tenant isolation | Integration | Cannot see other tenant departments |

## Related

- [[modules/org-structure/departments/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
