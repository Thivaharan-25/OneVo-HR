# Legal Entities — Testing

**Module:** Org Structure  
**Feature:** Legal Entities  
**Location:** `tests/ONEVO.Tests.Unit/Modules/OrgStructure/LegalEntityServiceTests.cs`

---

## Unit Tests

```csharp
public class LegalEntityServiceTests
{
    private readonly Mock<ILegalEntityRepository> _repoMock = new();
    private readonly Mock<ICountryRepository> _countryRepoMock = new();
    private readonly Mock<IDomainEventPublisher> _eventPublisherMock = new();
    private readonly LegalEntityService _sut;

    public LegalEntityServiceTests()
    {
        _sut = new LegalEntityService(
            _repoMock.Object,
            _countryRepoMock.Object,
            _eventPublisherMock.Object);
    }

    [Fact]
    public async Task CreateAsync_WithValidData_ReturnsSuccess()
    {
        _countryRepoMock.Setup(r => r.ExistsAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(true);
        _repoMock.Setup(r => r.IsRegistrationNumberUniqueAsync(
                It.IsAny<string>(), It.IsAny<Guid>(), default))
            .ReturnsAsync(true);

        var command = new CreateLegalEntityCommand
        {
            Name = "ONEVO Ltd",
            RegistrationNumber = "UK-12345678",
            CountryId = Guid.NewGuid(),
            AddressJson = """{"line1": "10 Downing St", "city": "London", "postcode": "SW1A 2AA"}"""
        };

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Name.Should().Be("ONEVO Ltd");
        result.Value.IsActive.Should().BeTrue();
        _repoMock.Verify(r => r.AddAsync(It.IsAny<LegalEntity>(), default), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_WithDuplicateRegistrationNumber_ReturnsFailure()
    {
        _countryRepoMock.Setup(r => r.ExistsAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(true);
        _repoMock.Setup(r => r.IsRegistrationNumberUniqueAsync(
                It.IsAny<string>(), It.IsAny<Guid>(), default))
            .ReturnsAsync(false);

        var command = new CreateLegalEntityCommand
        {
            Name = "Duplicate Corp",
            RegistrationNumber = "UK-EXISTING",
            CountryId = Guid.NewGuid()
        };

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Registration number already exists");
    }

    [Fact]
    public async Task CreateAsync_WithInvalidCountry_ReturnsFailure()
    {
        _countryRepoMock.Setup(r => r.ExistsAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(false);

        var command = new CreateLegalEntityCommand
        {
            Name = "Bad Country Corp",
            RegistrationNumber = "XX-000",
            CountryId = Guid.NewGuid()
        };

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Country not found");
    }

    [Fact]
    public async Task DeactivateAsync_WithActiveDepartments_ReturnsFailure()
    {
        var entityId = Guid.NewGuid();
        _repoMock.Setup(r => r.GetByIdAsync(entityId, default))
            .ReturnsAsync(new LegalEntity { Id = entityId, IsActive = true });
        _repoMock.Setup(r => r.HasActiveDepartmentsAsync(entityId, default))
            .ReturnsAsync(true);

        var result = await _sut.DeactivateAsync(entityId, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("active departments exist");
    }

    [Fact]
    public async Task DeactivateAsync_WithNoDependencies_SetsInactive()
    {
        var entity = new LegalEntity { Id = Guid.NewGuid(), IsActive = true };
        _repoMock.Setup(r => r.GetByIdAsync(entity.Id, default)).ReturnsAsync(entity);
        _repoMock.Setup(r => r.HasActiveDepartmentsAsync(entity.Id, default)).ReturnsAsync(false);

        var result = await _sut.DeactivateAsync(entity.Id, default);

        result.IsSuccess.Should().BeTrue();
        entity.IsActive.Should().BeFalse();
    }
}
```

## Integration Tests

```csharp
public class LegalEntityEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _adminClient;

    public LegalEntityEndpointTests(ONEVOWebFactory factory)
    {
        _adminClient = factory.CreateAuthenticatedClient(role: "settings:admin");
    }

    [Fact]
    public async Task CreateAndList_ReturnsCreatedEntity()
    {
        var create = new
        {
            Name = "Integration Test Ltd",
            RegistrationNumber = $"INT-{Guid.NewGuid():N}",
            CountryId = TestData.UkCountryId,
            AddressJson = """{"line1":"1 Test St","city":"London"}"""
        };

        var createResp = await _adminClient.PostAsJsonAsync("/api/v1/legal-entities", create);
        createResp.StatusCode.Should().Be(HttpStatusCode.Created);

        var listResp = await _adminClient.GetFromJsonAsync<List<LegalEntityDto>>(
            "/api/v1/legal-entities");
        listResp.Should().Contain(e => e.RegistrationNumber == create.RegistrationNumber);
    }

    [Fact]
    public async Task Create_DuplicateRegistrationNumber_Returns409()
    {
        var regNumber = $"DUP-{Guid.NewGuid():N}";
        var body = new { Name = "First", RegistrationNumber = regNumber, CountryId = TestData.UkCountryId };

        await _adminClient.PostAsJsonAsync("/api/v1/legal-entities", body);
        var duplicate = await _adminClient.PostAsJsonAsync("/api/v1/legal-entities",
            new { Name = "Second", RegistrationNumber = regNumber, CountryId = TestData.UkCountryId });

        duplicate.StatusCode.Should().Be(HttpStatusCode.Conflict);
    }

    [Fact]
    public async Task TenantIsolation_CannotSeeOtherTenantEntities()
    {
        var otherTenantClient = _factory.CreateAuthenticatedClient(
            role: "settings:admin", tenantId: TestData.OtherTenantId);

        var entities = await otherTenantClient.GetFromJsonAsync<List<LegalEntityDto>>(
            "/api/v1/legal-entities");
        entities.Should().NotContain(e => e.TenantId == TestData.DefaultTenantId);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create with valid data | Unit | Success, is_active = true |
| Create with duplicate registration number | Unit | Failure, conflict |
| Create with invalid country_id | Unit | Failure, validation error |
| Deactivate with active departments | Unit | Failure, cannot deactivate |
| Deactivate with no dependencies | Unit | Success, is_active = false |
| Create and list round-trip | Integration | Entity appears in list |
| Duplicate registration number across API | Integration | 409 Conflict |
| Tenant isolation | Integration | Cannot see other tenant data |
| Update registration number to existing | Integration | 409 Conflict |

## Related

- [[legal-entities|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
