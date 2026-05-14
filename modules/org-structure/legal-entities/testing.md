# Company Registration Profile - Testing

**Module:** Org Structure
**Feature:** Company Registration Profile
**Location:** `tests/ONEVO.Tests.Unit/Modules/OrgStructure/CompanyProfileServiceTests.cs`

---

## Unit Tests

```csharp
public class CompanyProfileServiceTests
{
    private readonly Mock<ICompanyProfileRepository> _repoMock = new();
    private readonly Mock<ICountryRepository> _countryRepoMock = new();
    private readonly Mock<IDomainEventPublisher> _eventPublisherMock = new();
    private readonly CompanyProfileService _sut;

    public CompanyProfileServiceTests()
    {
        _sut = new CompanyProfileService(
            _repoMock.Object,
            _countryRepoMock.Object,
            _eventPublisherMock.Object);
    }

    [Fact]
    public async Task UpdateAsync_WithValidData_ReturnsSuccess()
    {
        _countryRepoMock.Setup(r => r.ExistsAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(true);

        var command = new UpdateCompanyProfileCommand
        {
            Name = "ONEVO Ltd",
            RegistrationNumber = "UK-12345678",
            CountryId = Guid.NewGuid(),
            CurrencyCode = "GBP",
            AddressJson = """{"line1": "10 Downing St", "city": "London", "postcode": "SW1A 2AA"}"""
        };

        var result = await _sut.UpdateAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Name.Should().Be("ONEVO Ltd");
        _repoMock.Verify(r => r.UpsertForCurrentTenantAsync(It.IsAny<CompanyRegistrationProfile>(), default), Times.Once);
    }

    [Fact]
    public async Task UpdateAsync_WithInvalidCountry_ReturnsFailure()
    {
        _countryRepoMock.Setup(r => r.ExistsAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(false);

        var command = new UpdateCompanyProfileCommand
        {
            Name = "Bad Country Corp",
            RegistrationNumber = "XX-000",
            CountryId = Guid.NewGuid(),
            CurrencyCode = "USD"
        };

        var result = await _sut.UpdateAsync(command, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Country not found");
    }

    [Fact]
    public async Task UpdateAsync_WhenCountryChanges_PublishesCompanyProfileCountrySet()
    {
        var previousCountryId = Guid.NewGuid();
        var newCountryId = Guid.NewGuid();

        _repoMock.Setup(r => r.GetForCurrentTenantAsync(default))
            .ReturnsAsync(new CompanyRegistrationProfile { CountryId = previousCountryId });
        _countryRepoMock.Setup(r => r.ExistsAsync(newCountryId, default))
            .ReturnsAsync(true);

        var command = new UpdateCompanyProfileCommand
        {
            Name = "ONEVO Ltd",
            RegistrationNumber = "UK-12345678",
            CountryId = newCountryId,
            CurrencyCode = "GBP"
        };

        var result = await _sut.UpdateAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        _eventPublisherMock.Verify(p => p.PublishAsync(
            It.IsAny<CompanyProfileCountrySet>(), default), Times.Once);
    }
}
```

## Integration Tests

```csharp
public class CompanyProfileEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _adminClient;

    public CompanyProfileEndpointTests(ONEVOWebFactory factory)
    {
        _adminClient = factory.CreateAuthenticatedClient(permission: "org:manage");
    }

    [Fact]
    public async Task UpdateAndGet_ReturnsCurrentTenantProfile()
    {
        var update = new
        {
            Name = "Integration Test Ltd",
            RegistrationNumber = $"INT-{Guid.NewGuid():N}",
            CountryId = TestData.UkCountryId,
            CurrencyCode = "GBP",
            AddressJson = """{"line1":"1 Test St","city":"London"}"""
        };

        var updateResp = await _adminClient.PutAsJsonAsync("/api/v1/org/company-profile", update);
        updateResp.StatusCode.Should().Be(HttpStatusCode.OK);

        var profile = await _adminClient.GetFromJsonAsync<CompanyProfileDto>(
            "/api/v1/org/company-profile");
        profile!.RegistrationNumber.Should().Be(update.RegistrationNumber);
    }

    [Fact]
    public async Task Update_InvalidCountry_Returns422()
    {
        var update = new
        {
            Name = "Invalid Country Ltd",
            RegistrationNumber = "BAD-COUNTRY",
            CountryId = Guid.NewGuid(),
            CurrencyCode = "GBP"
        };

        var response = await _adminClient.PutAsJsonAsync("/api/v1/org/company-profile", update);

        response.StatusCode.Should().Be(HttpStatusCode.UnprocessableEntity);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Update with valid data | Unit | Success |
| Update with invalid country_id | Unit | Failure, validation error |
| Country change | Unit | Publishes `CompanyProfileCountrySet` |
| Update and get round-trip | Integration | Profile reflects latest update |
| Invalid country across API | Integration | 422 |
| Tenant isolation | Integration | Profile is scoped to current tenant |

## Related

- [[modules/org-structure/legal-entities/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
