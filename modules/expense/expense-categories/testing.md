# Expense Categories — Testing Strategy

**Module:** Expense
**Feature:** Expense Categories

---

## Unit Tests

### ExpenseCategoryServiceTests

```csharp
public class ExpenseCategoryServiceTests
{
    private readonly Mock<IExpenseCategoryRepository> _repoMock;
    private readonly Mock<ITenantContext> _tenantMock;
    private readonly ExpenseCategoryService _sut;

    public ExpenseCategoryServiceTests()
    {
        _repoMock = new Mock<IExpenseCategoryRepository>();
        _tenantMock = new Mock<ITenantContext>();
        _tenantMock.Setup(t => t.TenantId).Returns(Guid.NewGuid());
        _sut = new ExpenseCategoryService(_repoMock.Object, _tenantMock.Object);
    }

    [Fact]
    public async Task CreateAsync_ValidCategory_ReturnsCreatedDto()
    {
        // Arrange
        var request = new CreateExpenseCategoryRequest
        {
            Name = "Travel",
            MaxAmount = 5000m,
            RequiresReceipt = true
        };
        _repoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<Guid>(), "Travel"))
            .ReturnsAsync(false);
        _repoMock.Setup(r => r.AddAsync(It.IsAny<ExpenseCategory>()))
            .ReturnsAsync((ExpenseCategory c) => c);

        // Act
        var result = await _sut.CreateAsync(request);

        // Assert
        result.Name.Should().Be("Travel");
        result.MaxAmount.Should().Be(5000m);
        result.RequiresReceipt.Should().BeTrue();
        result.IsActive.Should().BeTrue();
        _repoMock.Verify(r => r.AddAsync(It.IsAny<ExpenseCategory>()), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_DuplicateName_ThrowsConflictException()
    {
        // Arrange
        var request = new CreateExpenseCategoryRequest { Name = "Travel" };
        _repoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<Guid>(), "Travel"))
            .ReturnsAsync(true);

        // Act
        var act = () => _sut.CreateAsync(request);

        // Assert
        await act.Should().ThrowAsync<ConflictException>()
            .WithMessage("*already exists*");
    }

    [Fact]
    public async Task DeactivateAsync_CategoryHasOpenClaims_ThrowsBusinessRuleException()
    {
        // Arrange
        var categoryId = Guid.NewGuid();
        var category = new ExpenseCategory { Id = categoryId, IsActive = true };
        _repoMock.Setup(r => r.GetByIdAsync(categoryId, It.IsAny<Guid>()))
            .ReturnsAsync(category);
        _repoMock.Setup(r => r.HasOpenClaimsAsync(categoryId))
            .ReturnsAsync(true);

        // Act
        var act = () => _sut.DeactivateAsync(categoryId);

        // Assert
        await act.Should().ThrowAsync<BusinessRuleException>()
            .WithMessage("*open claims*");
    }

    [Fact]
    public async Task UpdateAsync_CategoryNotFound_ThrowsNotFoundException()
    {
        // Arrange
        var categoryId = Guid.NewGuid();
        _repoMock.Setup(r => r.GetByIdAsync(categoryId, It.IsAny<Guid>()))
            .ReturnsAsync((ExpenseCategory?)null);

        // Act
        var act = () => _sut.UpdateAsync(categoryId, new UpdateExpenseCategoryRequest());

        // Assert
        await act.Should().ThrowAsync<NotFoundException>();
    }

    [Theory]
    [InlineData(null)]
    [InlineData(0)]
    public async Task CreateAsync_NullOrZeroMaxAmount_SetsUnlimited(decimal? maxAmount)
    {
        // Arrange
        var request = new CreateExpenseCategoryRequest
        {
            Name = "Miscellaneous",
            MaxAmount = maxAmount,
            RequiresReceipt = false
        };
        _repoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<Guid>(), It.IsAny<string>()))
            .ReturnsAsync(false);
        _repoMock.Setup(r => r.AddAsync(It.IsAny<ExpenseCategory>()))
            .ReturnsAsync((ExpenseCategory c) => c);

        // Act
        var result = await _sut.CreateAsync(request);

        // Assert
        result.MaxAmount.Should().BeNull();
    }
}
```

### CreateExpenseCategoryRequestValidatorTests

```csharp
public class CreateExpenseCategoryRequestValidatorTests
{
    private readonly CreateExpenseCategoryRequestValidator _validator = new();

    [Fact]
    public void Validate_EmptyName_ReturnsError()
    {
        var request = new CreateExpenseCategoryRequest { Name = "" };
        var result = _validator.Validate(request);

        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "Name");
    }

    [Fact]
    public void Validate_NegativeMaxAmount_ReturnsError()
    {
        var request = new CreateExpenseCategoryRequest { Name = "Food", MaxAmount = -100m };
        var result = _validator.Validate(request);

        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "MaxAmount");
    }

    [Fact]
    public void Validate_ValidRequest_Passes()
    {
        var request = new CreateExpenseCategoryRequest
        {
            Name = "Office Supplies",
            MaxAmount = 500m,
            RequiresReceipt = true
        };
        var result = _validator.Validate(request);

        result.IsValid.Should().BeTrue();
    }
}
```

---

## Integration Tests

```csharp
public class ExpenseCategoriesApiTests : IClassFixture<CustomWebApplicationFactory>
{
    private readonly HttpClient _client;

    public ExpenseCategoriesApiTests(CustomWebApplicationFactory factory)
    {
        _client = factory.CreateAuthenticatedClient(permission: "expense:manage");
    }

    [Fact]
    public async Task CreateAndList_Category_RoundTrips()
    {
        // Arrange
        var request = new { Name = "Hotel", MaxAmount = 300.00, RequiresReceipt = true };

        // Act — Create
        var createResponse = await _client.PostAsJsonAsync("/api/v1/expenses/categories", request);
        createResponse.StatusCode.Should().Be(HttpStatusCode.Created);
        var created = await createResponse.Content.ReadFromJsonAsync<ExpenseCategoryDto>();

        // Act — List
        var listResponse = await _client.GetAsync("/api/v1/expenses/categories");
        var categories = await listResponse.Content.ReadFromJsonAsync<List<ExpenseCategoryDto>>();

        // Assert
        categories.Should().Contain(c => c.Id == created!.Id && c.Name == "Hotel");
    }

    [Fact]
    public async Task CreateCategory_DuplicateName_Returns409()
    {
        // Arrange
        var request = new { Name = "Duplicate-Test", MaxAmount = 100.00, RequiresReceipt = false };
        await _client.PostAsJsonAsync("/api/v1/expenses/categories", request);

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/expenses/categories", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Conflict);
    }

    [Fact]
    public async Task UpdateCategory_ChangeName_Returns200()
    {
        // Arrange
        var create = new { Name = "OldName", RequiresReceipt = false };
        var createResp = await _client.PostAsJsonAsync("/api/v1/expenses/categories", create);
        var created = await createResp.Content.ReadFromJsonAsync<ExpenseCategoryDto>();

        // Act
        var update = new { Name = "NewName", RequiresReceipt = true, IsActive = true };
        var response = await _client.PutAsJsonAsync($"/api/v1/expenses/categories/{created!.Id}", update);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var updated = await response.Content.ReadFromJsonAsync<ExpenseCategoryDto>();
        updated!.Name.Should().Be("NewName");
    }
}
```

---

## Test Scenarios

| Scenario | Input | Expected Output | Type |
|:---------|:------|:----------------|:-----|
| Create valid category | Name="Travel", MaxAmount=5000 | 201 Created, category returned | Integration |
| Create duplicate name | Same name twice for same tenant | 409 Conflict | Integration |
| Create with null max_amount | Name="Misc", MaxAmount=null | Category with no limit | Unit |
| Create with negative max_amount | MaxAmount=-100 | 400 validation error | Unit |
| List active categories | isActive=true | Only active categories | Integration |
| Update category name | New unique name | 200 OK, name updated | Integration |
| Deactivate with open claims | Category used in draft claim | 422 BusinessRuleException | Unit |
| Delete non-existent category | Random GUID | 404 Not Found | Unit |
| Cross-tenant isolation | Tenant B queries | Tenant A categories not visible | Integration |

---

## Test Data

- **Seed categories**: "Travel", "Meals", "Office Supplies", "Equipment" with varying `max_amount` and `requires_receipt` values.
- **Tenant isolation**: Two tenants seeded; each has distinct categories.
- **Open claims fixture**: One category linked to a `draft` status expense claim for deactivation tests.

## Related

- [[expense-categories]] — feature overview
- [[testing/README|Testing Standards]] — project-wide testing conventions
