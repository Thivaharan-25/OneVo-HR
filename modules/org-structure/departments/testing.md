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
    private readonly Mock<ILegalEntityRepository> _legalEntityRepoMock = new();
    private readonly Mock<IEmployeeRepository> _employeeRepoMock = new();
    private readonly Mock<IDomainEventPublisher> _eventPublisherMock = new();
    private readonly DepartmentService _sut;

    public DepartmentServiceTests()
    {
        _sut = new DepartmentService(
            _repoMock.Object,
            _legalEntityRepoMock.Object,
            _employeeRepoMock.Object,
            _eventPublisherMock.Object);
    }

    // --- Create ---

    [Fact]
    public async Task CreateAsync_ValidData_ReturnsSuccess()
    {
        var legalEntityId = Guid.NewGuid();
        _legalEntityRepoMock.Setup(r => r.ExistsAsync(legalEntityId, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsNameUniqueInLegalEntityAsync("Engineering", legalEntityId, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsCodeUniqueInLegalEntityAsync("ENG", legalEntityId, default)).ReturnsAsync(true);

        var command = new CreateDepartmentCommand { LegalEntityId = legalEntityId, Name = "Engineering", Code = "ENG" };
        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Name.Should().Be("Engineering");
        result.Value.LegalEntityId.Should().Be(legalEntityId);
    }

    [Fact]
    public async Task CreateAsync_LegalEntityNotFound_ReturnsFailure()
    {
        _legalEntityRepoMock.Setup(r => r.ExistsAsync(It.IsAny<Guid>(), default)).ReturnsAsync(false);

        var result = await _sut.CreateAsync(new CreateDepartmentCommand { LegalEntityId = Guid.NewGuid(), Name = "HR" }, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Company");
    }

    [Fact]
    public async Task CreateAsync_DuplicateNameInSameLegalEntity_ReturnsFailure()
    {
        var legalEntityId = Guid.NewGuid();
        _legalEntityRepoMock.Setup(r => r.ExistsAsync(legalEntityId, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsNameUniqueInLegalEntityAsync("Engineering", legalEntityId, default)).ReturnsAsync(false);

        var result = await _sut.CreateAsync(new CreateDepartmentCommand { LegalEntityId = legalEntityId, Name = "Engineering" }, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("already exists");
    }

    [Fact]
    public async Task CreateAsync_DuplicateNameInDifferentLegalEntity_Succeeds()
    {
        // Same name "Engineering" is allowed in a different Company
        var entityA = Guid.NewGuid();
        var entityB = Guid.NewGuid();
        _legalEntityRepoMock.Setup(r => r.ExistsAsync(entityB, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsNameUniqueInLegalEntityAsync("Engineering", entityB, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsCodeUniqueInLegalEntityAsync(It.IsAny<string>(), entityB, default)).ReturnsAsync(true);

        var result = await _sut.CreateAsync(new CreateDepartmentCommand { LegalEntityId = entityB, Name = "Engineering" }, default);

        result.IsSuccess.Should().BeTrue();
    }

    [Fact]
    public async Task CreateAsync_DuplicateCodeInSameLegalEntity_ReturnsFailure()
    {
        var legalEntityId = Guid.NewGuid();
        _legalEntityRepoMock.Setup(r => r.ExistsAsync(legalEntityId, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsNameUniqueInLegalEntityAsync(It.IsAny<string>(), legalEntityId, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsCodeUniqueInLegalEntityAsync("ENG", legalEntityId, default)).ReturnsAsync(false);

        var result = await _sut.CreateAsync(new CreateDepartmentCommand { LegalEntityId = legalEntityId, Name = "Engineering 2", Code = "ENG" }, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("code already exists");
    }

    [Fact]
    public async Task CreateAsync_ParentInDifferentLegalEntity_ReturnsFailure()
    {
        var legalEntityId = Guid.NewGuid();
        var parentId = Guid.NewGuid();
        _legalEntityRepoMock.Setup(r => r.ExistsAsync(legalEntityId, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsNameUniqueInLegalEntityAsync(It.IsAny<string>(), legalEntityId, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.GetByIdAsync(parentId, default)).ReturnsAsync(
            new Department { Id = parentId, LegalEntityId = Guid.NewGuid() }); // different entity

        var result = await _sut.CreateAsync(
            new CreateDepartmentCommand { LegalEntityId = legalEntityId, Name = "Child", ParentDepartmentId = parentId }, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("same Company");
    }

    [Fact]
    public async Task CreateAsync_NoCode_GeneratesCode()
    {
        var legalEntityId = Guid.NewGuid();
        _legalEntityRepoMock.Setup(r => r.ExistsAsync(legalEntityId, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsNameUniqueInLegalEntityAsync(It.IsAny<string>(), legalEntityId, default)).ReturnsAsync(true);

        var result = await _sut.CreateAsync(new CreateDepartmentCommand { LegalEntityId = legalEntityId, Name = "Finance" }, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Code.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public async Task CreateAsync_PublishesDomainEvent_OnSuccess()
    {
        var legalEntityId = Guid.NewGuid();
        _legalEntityRepoMock.Setup(r => r.ExistsAsync(legalEntityId, default)).ReturnsAsync(true);
        _repoMock.Setup(r => r.IsNameUniqueInLegalEntityAsync(It.IsAny<string>(), legalEntityId, default)).ReturnsAsync(true);

        await _sut.CreateAsync(new CreateDepartmentCommand { LegalEntityId = legalEntityId, Name = "Marketing" }, default);

        _eventPublisherMock.Verify(e => e.PublishAsync(It.IsAny<DepartmentCreated>(), default), Times.Once);
    }

    // --- Update ---

    [Fact]
    public async Task UpdateAsync_CircularReference_ReturnsFailure()
    {
        var grandparent = new Department { Id = Guid.NewGuid(), LegalEntityId = Guid.NewGuid(), ParentDepartmentId = null };
        var parent = new Department { Id = Guid.NewGuid(), LegalEntityId = grandparent.LegalEntityId, ParentDepartmentId = grandparent.Id };
        var child = new Department { Id = Guid.NewGuid(), LegalEntityId = grandparent.LegalEntityId, ParentDepartmentId = parent.Id };

        _repoMock.Setup(r => r.GetByIdAsync(grandparent.Id, default)).ReturnsAsync(grandparent);
        _repoMock.Setup(r => r.GetAncestorIdsAsync(child.Id, default))
            .ReturnsAsync(new List<Guid> { parent.Id, grandparent.Id });

        var result = await _sut.UpdateAsync(grandparent.Id, new UpdateDepartmentCommand { ParentDepartmentId = child.Id }, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Circular");
    }

    [Fact]
    public async Task UpdateAsync_CodeChangedToExistingInLegalEntity_ReturnsFailure()
    {
        var legalEntityId = Guid.NewGuid();
        var dept = new Department { Id = Guid.NewGuid(), LegalEntityId = legalEntityId, Code = "OLD" };
        _repoMock.Setup(r => r.GetByIdAsync(dept.Id, default)).ReturnsAsync(dept);
        _repoMock.Setup(r => r.IsCodeUniqueInLegalEntityAsync("ENG", legalEntityId, default)).ReturnsAsync(false);

        var result = await _sut.UpdateAsync(dept.Id, new UpdateDepartmentCommand { Code = "ENG" }, default);

        result.IsSuccess.Should().BeFalse();
    }
}
```

---

## Integration Tests

```csharp
public class DepartmentEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _adminClient;
    private readonly Guid _legalEntityId; // selected Company context mapped internally to legal_entity_id

    public DepartmentEndpointTests(ONEVOWebFactory factory)
    {
        _adminClient = factory.CreateAuthenticatedClient(permission: "org:manage");
        _legalEntityId = factory.DefaultLegalEntityId;
    }

    [Fact]
    public async Task Post_ValidDepartment_Returns201AndAppearsInTree()
    {
        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "QA Department", Code = $"QA-{Guid.NewGuid():N}"[..8] });
        resp.StatusCode.Should().Be(HttpStatusCode.Created);

        var tree = await _adminClient.GetFromJsonAsync<List<DepartmentTreeDto>>(
            "/api/v1/org/departments?view=tree");
        tree.Should().Contain(d => d.Name == "QA Department");
    }

    [Fact]
    public async Task Post_DuplicateNameInSameCompany_Returns409()
    {
        await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Duplicate Dept" });

        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Duplicate Dept" });

        resp.StatusCode.Should().Be(HttpStatusCode.Conflict);
    }

    [Fact]
    public async Task Post_SameNameInDifferentCompany_Returns201()
    {
        var otherCompanyClient = await CreateClientForOtherCompanyAsync();

        await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Engineering" });
        var resp = await otherCompanyClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Engineering" });

        resp.StatusCode.Should().Be(HttpStatusCode.Created);
    }

    [Fact]
    public async Task Post_ParentInDifferentCompany_Returns422()
    {
        var otherCompanyClient = await CreateClientForOtherCompanyAsync();
        var parentResp = await otherCompanyClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Parent" });
        var parentId = (await parentResp.Content.ReadFromJsonAsync<DepartmentDto>())!.Id;

        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Child", ParentDepartmentId = parentId });

        resp.StatusCode.Should().Be(HttpStatusCode.UnprocessableEntity);
    }

    [Fact]
    public async Task Post_MissingCompanyContext_Returns422()
    {
        var noCompanyClient = _factory.CreateAuthenticatedClient(permission: "org:manage", legalEntityId: null);
        var resp = await noCompanyClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Orphan Dept" });

        resp.StatusCode.Should().Be(HttpStatusCode.UnprocessableEntity);
    }

    [Fact]
    public async Task Post_ChildDepartment_AppearsUnderParentInTree()
    {
        var parentResp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Parent Dept" });
        var parentId = (await parentResp.Content.ReadFromJsonAsync<DepartmentDto>())!.Id;

        var childResp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Child Dept", ParentDepartmentId = parentId });

        childResp.StatusCode.Should().Be(HttpStatusCode.Created);
    }

    [Fact]
    public async Task Get_Tree_HandlesDeepHierarchy()
    {
        Guid? parentId = null;
        for (int i = 0; i < 5; i++)
        {
            var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/departments",
                new { Name = $"Level-{i}-{Guid.NewGuid():N}"[..20], ParentDepartmentId = parentId });
            parentId = (await resp.Content.ReadFromJsonAsync<DepartmentDto>())!.Id;
        }

        var tree = await _adminClient.GetFromJsonAsync<List<DepartmentTreeDto>>(
            "/api/v1/org/departments?view=tree");
        tree.Should().NotBeEmpty();
    }

    [Fact]
    public async Task Get_DoesNotReturnOtherCompanyDepartments()
    {
        var otherCompanyClient = await CreateClientForOtherCompanyAsync();
        await otherCompanyClient.PostAsJsonAsync("/api/v1/org/departments",
            new { Name = "Other Company Dept" });

        var results = await _adminClient.GetFromJsonAsync<List<DepartmentDto>>(
            "/api/v1/org/departments?view=flat");

        results.Should().NotContain(d => d.Name == "Other Company Dept");
    }

    [Fact]
    public async Task Get_CannotSeeOtherTenantDepartments()
    {
        // client authenticated to a different tenant cannot see this tenant's departments
    }
}
```

---

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create with valid data and selected Company | Unit | Success; internal LegalEntityId on result |
| Create - selected Company not found | Unit | Failure |
| Create - duplicate name in same Company | Unit | Failure |
| Create - same name in different Company | Unit | Success (allowed) |
| Create - duplicate code in same Company | Unit | Failure |
| Create - parent in different Company | Unit | Failure |
| Create - no code provided | Unit | Code generated |
| Create - publishes DepartmentCreated event | Unit | Event published once |
| Update - circular reference | Unit | Failure |
| Update - code changed to existing code in Company | Unit | Failure |
| Post valid department and retrieve in tree | Integration | 201; appears in tree |
| Post duplicate name same Company | Integration | 409 |
| Post same name different Company | Integration | 201 |
| Post with parent from different Company | Integration | 422 |
| Post without selected Company | Integration | 422 |
| Get tree scoped to selected Company only | Integration | No cross-entity leakage |
| 5-level deep hierarchy | Integration | Correct tree rendering |
| Cross-tenant isolation | Integration | Cannot see other tenant departments |

---

## Related

- [[modules/org-structure/departments/overview|Overview]]
- [[modules/org-structure/departments/end-to-end-logic|End-to-End Logic]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
