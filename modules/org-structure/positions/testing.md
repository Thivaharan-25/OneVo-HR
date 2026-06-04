# Positions — Testing

**Module:** Org Structure  
**Feature:** Positions  
**Location:** `tests/ONEVO.Tests.Unit/Modules/OrgStructure/PositionServiceTests.cs`

---

## Unit Tests

```csharp
public class PositionServiceTests
{
    private readonly Mock<IPositionRepository> _repoMock = new();
    private readonly Mock<ILegalEntityRepository> _legalEntityRepoMock = new();
    private readonly Mock<IDepartmentRepository> _deptRepoMock = new();
    private readonly Mock<IJobTitleRepository> _jobTitleRepoMock = new();
    private readonly Mock<IEventPublisher> _eventPublisherMock = new();
    private readonly PositionService _sut;

    public PositionServiceTests()
    {
        _sut = new PositionService(
            _repoMock.Object,
            _legalEntityRepoMock.Object,
            _deptRepoMock.Object,
            _jobTitleRepoMock.Object,
            _eventPublisherMock.Object);
    }

    // --- Create ---

    [Fact]
    public async Task CreateAsync_ValidUnique_ReturnsSuccess()

    [Fact]
    public async Task CreateAsync_ValidPooled_ReturnsSuccess()

    [Fact]
    public async Task CreateAsync_LegalEntityNotFound_ReturnsFailure()

    [Fact]
    public async Task CreateAsync_DepartmentNotInLegalEntity_ReturnsFailure()

    [Fact]
    public async Task CreateAsync_JobTitleNotFound_ReturnsFailure()

    [Fact]
    public async Task CreateAsync_DuplicateNameInLegalEntity_ReturnsFailure()

    [Fact]
    public async Task CreateAsync_ReportsToInDifferentLegalEntity_ReturnsFailure()

    [Fact]
    public async Task CreateAsync_ReportsToPooledPosition_ReturnsFailure()

    [Fact]
    public async Task CreateAsync_RootPosition_NoReportsTo_Succeeds()

    [Fact]
    public async Task CreateAsync_DirectCycle_AReportsToA_ReturnsFailure()

    [Fact]
    public async Task CreateAsync_IndirectCycle_AReportsToBReportsToCReportsToA_ReturnsFailure()

    [Fact]
    public async Task CreateAsync_PublishesDomainEvent_OnSuccess()

    // --- Bulk Create ---

    [Fact]
    public async Task BulkCreateAsync_AllValid_ReturnsAllSucceeded()

    [Fact]
    public async Task BulkCreateAsync_SomeInvalid_ReturnsPartialSuccess()

    [Fact]
    public async Task BulkCreateAsync_AllInvalid_ReturnsAllFailed()

    // --- Update ---

    [Fact]
    public async Task UpdateAsync_CapacityIncrease_Succeeds()

    [Fact]
    public async Task UpdateAsync_CapacityBelowCurrentOccupancy_ReturnsFailure()

    [Fact]
    public async Task UpdateAsync_LegalEntityChangeAttempted_ReturnsFailure()

    [Fact]
    public async Task UpdateAsync_DepartmentChangedToSameLegalEntity_Succeeds()

    [Fact]
    public async Task UpdateAsync_DepartmentChangedToDifferentLegalEntity_ReturnsFailure()

    [Fact]
    public async Task UpdateAsync_ReportsToChanged_WritesHistoryRow()

    [Fact]
    public async Task UpdateAsync_ReportsToChangedCreatesNewCycle_ReturnsFailure()

    [Fact]
    public async Task UpdateAsync_ReportsToRemovedBecomesRoot_Succeeds()

    // --- Deactivate ---

    [Fact]
    public async Task DeactivateAsync_NoOccupants_NoDependents_Succeeds()

    [Fact]
    public async Task DeactivateAsync_HasActiveOccupant_ReturnsFailure()

    [Fact]
    public async Task DeactivateAsync_OtherPositionsReportToIt_ReturnsFailure()

    [Fact]
    public async Task DeactivateAsync_ClosesOpenHistoryRow()
}
```

---

## Integration Tests

```csharp
public class PositionEndpointTests : IClassFixture<OnevoWebFactory>
{
    private readonly HttpClient _adminClient;

    // --- POST /api/v1/org/positions ---

    [Fact]
    public async Task Post_ValidPosition_Returns201()
    {
        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/positions", new
        {
            legalEntityId = _legalEntityId,
            departmentId = _deptId,
            jobTitleId = _jobTitleId,
            name = "Senior Engineer",
            positionType = "unique",
            capacity = 30
        });
        resp.StatusCode.Should().Be(HttpStatusCode.Created);
        var dto = await resp.Content.ReadFromJsonAsync<PositionDto>();
        dto!.Name.Should().Be("Senior Engineer");
        dto.CurrentOccupancy.Should().Be(0);
    }

    [Fact]
    public async Task Post_DuplicateNameInLegalEntity_Returns409()

    [Fact]
    public async Task Post_DepartmentFromDifferentLegalEntity_Returns422()

    [Fact]
    public async Task Post_ReportsToPooled_Returns422()

    [Fact]
    public async Task Post_CyclicReporting_Returns422()

    // --- POST /api/v1/org/positions/bulk ---

    [Fact]
    public async Task BulkPost_PartialFailure_Returns200WithMixedResults()
    {
        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/positions/bulk", new
        {
            items = new[]
            {
                new { name = "Engineering Manager", positionType = "unique", capacity = 1, /* ... */ },
                new { name = "Engineering Manager", positionType = "unique", capacity = 1, /* duplicate */ }
            }
        });
        resp.StatusCode.Should().Be(HttpStatusCode.OK);
        var result = await resp.Content.ReadFromJsonAsync<BulkPositionResultDto>();
        result!.Succeeded.Should().HaveCount(1);
        result.Failed.Should().HaveCount(1);
        result.Failed[0].Errors.Should().Contain(e => e.Contains("already exists"));
    }

    // --- GET /api/v1/org/positions ---

    [Fact]
    public async Task Get_ByLegalEntity_ReturnsOnlyThatEntityPositions()

    [Fact]
    public async Task Get_IncludesCurrentOccupancyCount()

    // --- GET /api/v1/org/positions/tree ---

    [Fact]
    public async Task GetTree_ReturnsNestedHierarchy()

    [Fact]
    public async Task GetTree_VacantPositions_FlaggedIsVacantTrue()

    // --- PUT /api/v1/org/positions/{id} ---

    [Fact]
    public async Task Put_CapacityIncrease_Returns200()

    [Fact]
    public async Task Put_CapacityBelowOccupancy_Returns422()

    [Fact]
    public async Task Put_LegalEntityChange_Returns422()

    [Fact]
    public async Task Put_ReportsToUpdate_WritesHistoryAndRebuildsClosureTable()

    // --- DELETE /api/v1/org/positions/{id} ---

    [Fact]
    public async Task Delete_EmptyPosition_Returns204()

    [Fact]
    public async Task Delete_OccupiedPosition_Returns422()

    [Fact]
    public async Task Delete_PositionWithDependentReportsTo_Returns422()

    // --- Cross-tenant isolation ---

    [Fact]
    public async Task Get_CannotSeeOtherTenantPositions()

    [Fact]
    public async Task Post_CannotCreatePositionInOtherTenantLegalEntity()
}
```

---

## Scenario Table

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create unique position with reporting line | Integration | 201; history row written |
| Create pooled position, no reports-to | Integration | 201 |
| Create with reports-to pointing to pooled position | Integration | 422 |
| Create duplicate name in same legal entity | Integration | 409 |
| Create duplicate name in different legal entity | Integration | 201 (allowed) |
| Cycle: A reports to B reports to A | Unit | Failure |
| Multi-hop cycle: A→B→C→A | Unit | Failure |
| Root position (no reports-to) | Unit | Success |
| Capacity set to 0 | Unit | Failure (validation) |
| Capacity reduction below occupancy | Integration | 422 |
| Update reports-to: history closed and new row opened | Unit | Success; history count +1 |
| Deactivate occupied position | Integration | 422 |
| Deactivate position others report to | Integration | 422 |
| Deactivate empty leaf position | Integration | 204 |
| Cross-tenant position access | Integration | 404 / 0 results |
| Bulk create all valid | Integration | 200; all succeeded |
| Bulk create partial failure | Integration | 200; mixed result |
| legal_entity_id change on update | Integration | 422 |

---

## Related

- [[modules/org-structure/positions/overview|Overview]]
- [[modules/org-structure/positions/end-to-end-logic|End-to-End Logic]]
- [[modules/org-structure/departments/testing|Departments Testing]]
- [[code-standards/testing-strategy|Testing Strategy]]
