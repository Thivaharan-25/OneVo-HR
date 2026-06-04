# Job Hierarchy — Testing

**Module:** Org Structure
**Feature:** Job Hierarchy
**Location:** `tests/ONEVO.Tests.Unit/Modules/OrgStructure/JobHierarchyServiceTests.cs`

---

## Unit Tests

```csharp
public class JobHierarchyServiceTests
{
    private readonly Mock<IJobHierarchyRepository> _repoMock = new();
    private readonly Mock<IDomainEventPublisher> _eventPublisherMock = new();
    private readonly JobHierarchyService _sut;

    public JobHierarchyServiceTests()
    {
        _sut = new JobHierarchyService(_repoMock.Object, _eventPublisherMock.Object);
    }

    // --- Job Family ---

    [Fact]
    public async Task CreateFamilyAsync_ValidName_ReturnsSuccess()

    [Fact]
    public async Task CreateFamilyAsync_DuplicateName_ReturnsFailure()

    [Fact]
    public async Task CreateFamilyAsync_PublishesEvent()

    // --- Job Level ---

    [Fact]
    public async Task CreateLevelAsync_ValidFamilyAndRank_ReturnsSuccess()

    [Fact]
    public async Task CreateLevelAsync_FamilyNotFound_ReturnsFailure()

    [Fact]
    public async Task CreateLevelAsync_DuplicateRankInFamily_ReturnsFailure()

    [Fact]
    public async Task CreateLevelAsync_DuplicateRankInDifferentFamily_Succeeds()

    [Fact]
    public async Task CreateLevelAsync_WithSuggestedRole_StoresRoleId()

    // --- Job Title ---

    [Fact]
    public async Task CreateTitleAsync_NameOnly_NoFamilyOrLevel_Succeeds()

    [Fact]
    public async Task CreateTitleAsync_WithFamilyAndLevel_Succeeds()

    [Fact]
    public async Task CreateTitleAsync_WithFamilyOnly_NoLevel_Succeeds()

    [Fact]
    public async Task CreateTitleAsync_LevelWithoutFamily_ReturnsFailure()

    [Fact]
    public async Task CreateTitleAsync_LevelNotBelongingToFamily_ReturnsFailure()

    [Fact]
    public async Task CreateTitleAsync_DuplicateNameInTenant_ReturnsFailure()

    [Fact]
    public async Task CreateTitleAsync_SameNameInTenant_OnlyOneAllowed()
    // Unlike departments, title names are unique across the whole tenant

    [Fact]
    public async Task CreateTitleAsync_FamilyNotFound_ReturnsFailure()

    [Fact]
    public async Task CreateTitleAsync_LevelNotFound_ReturnsFailure()

    [Fact]
    public async Task CreateTitleAsync_PublishesEvent()

    // --- Update Job Title ---

    [Fact]
    public async Task UpdateTitleAsync_LinkFamilyToExistingTitle_Succeeds()

    [Fact]
    public async Task UpdateTitleAsync_RemoveFamilyAndLevel_Succeeds()

    [Fact]
    public async Task UpdateTitleAsync_ChangeLevelToOneBelongingToDifferentFamily_ReturnsFailure()

    [Fact]
    public async Task UpdateTitleAsync_DuplicateNameOnRename_ReturnsFailure()

    // --- Delete ---

    [Fact]
    public async Task DeleteFamily_WithLinkedTitles_ReturnsFailure()

    [Fact]
    public async Task DeleteFamily_NoLinkedTitles_Succeeds()

    [Fact]
    public async Task DeleteLevel_WithLinkedTitles_ReturnsFailure()

    [Fact]
    public async Task DeleteLevel_NoLinkedTitles_Succeeds()

    [Fact]
    public async Task DeleteTitle_InUseByPosition_ReturnsFailure()

    [Fact]
    public async Task DeleteTitle_InUseByEmployee_ReturnsFailure()

    [Fact]
    public async Task DeleteTitle_NotInUse_WithNoFamilyOrLevel_Succeeds()
}
```

---

## Integration Tests

```csharp
public class JobHierarchyEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _adminClient;

    // --- Job Title: standalone (no family/level) ---

    [Fact]
    public async Task PostTitle_NameOnly_Returns201()
    {
        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/job-titles",
            new { Name = "Product Manager" });

        resp.StatusCode.Should().Be(HttpStatusCode.Created);
        var dto = await resp.Content.ReadFromJsonAsync<JobTitleDto>();
        dto!.JobFamilyId.Should().BeNull();
        dto.JobLevelId.Should().BeNull();
    }

    [Fact]
    public async Task PostTitle_WithFamilyAndLevel_Returns201()
    {
        var familyId = await CreateFamilyAsync("Engineering");
        var levelId = await CreateLevelAsync(familyId, "Senior", rank: 300);

        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/job-titles",
            new { Name = "Senior Engineer", JobFamilyId = familyId, JobLevelId = levelId });

        resp.StatusCode.Should().Be(HttpStatusCode.Created);
    }

    [Fact]
    public async Task PostTitle_LevelWithoutFamily_Returns422()
    {
        var familyId = await CreateFamilyAsync("Sales");
        var levelId = await CreateLevelAsync(familyId, "Junior", rank: 100);

        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/job-titles",
            new { Name = "Sales Rep", JobLevelId = levelId }); // no family

        resp.StatusCode.Should().Be(HttpStatusCode.UnprocessableEntity);
    }

    [Fact]
    public async Task PostTitle_LevelBelongingToDifferentFamily_Returns422()
    {
        var familyA = await CreateFamilyAsync("Engineering");
        var familyB = await CreateFamilyAsync("HR");
        var levelInB = await CreateLevelAsync(familyB, "Senior", rank: 300);

        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/job-titles",
            new { Name = "Mismatch Title", JobFamilyId = familyA, JobLevelId = levelInB });

        resp.StatusCode.Should().Be(HttpStatusCode.UnprocessableEntity);
    }

    [Fact]
    public async Task PostTitle_DuplicateName_Returns409()
    {
        await _adminClient.PostAsJsonAsync("/api/v1/org/job-titles", new { Name = "Analyst" });
        var resp = await _adminClient.PostAsJsonAsync("/api/v1/org/job-titles", new { Name = "Analyst" });

        resp.StatusCode.Should().Be(HttpStatusCode.Conflict);
    }

    // --- Update: link family/level to existing standalone title ---

    [Fact]
    public async Task PutTitle_LinkFamilyAndLevel_Returns200()
    {
        var titleResp = await _adminClient.PostAsJsonAsync("/api/v1/org/job-titles", new { Name = "Engineer" });
        var titleId = (await titleResp.Content.ReadFromJsonAsync<JobTitleDto>())!.Id;

        var familyId = await CreateFamilyAsync("Engineering");
        var levelId = await CreateLevelAsync(familyId, "Mid", rank: 200);

        var resp = await _adminClient.PutAsJsonAsync($"/api/v1/org/job-titles/{titleId}",
            new { Name = "Engineer", JobFamilyId = familyId, JobLevelId = levelId });

        resp.StatusCode.Should().Be(HttpStatusCode.OK);
        var dto = await resp.Content.ReadFromJsonAsync<JobTitleDto>();
        dto!.JobFamilyId.Should().Be(familyId);
        dto.JobLevelId.Should().Be(levelId);
    }

    // --- List ---

    [Fact]
    public async Task GetTitles_NoFilter_ReturnsAll()

    [Fact]
    public async Task GetTitles_FilterByFamily_ReturnsOnlyThatFamily()

    [Fact]
    public async Task GetTitles_StandaloneTitlesIncluded_WhenNoFilter()

    // --- Cross-tenant ---

    [Fact]
    public async Task GetTitles_CannotSeeOtherTenantTitles()
}
```

---

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create job title — name only, no family or level | Unit + Integration | Success; both FK fields null |
| Create job title — with family only | Unit | Success |
| Create job title — with family and matching level | Unit + Integration | Success |
| Create job title — level without family | Unit + Integration | Failure |
| Create job title — level belonging to different family | Unit + Integration | Failure |
| Create job title — duplicate name in tenant | Unit + Integration | Failure |
| Update title — link family and level to standalone title | Integration | 200; FKs populated |
| Update title — remove family and level | Unit | Success |
| Update title — level from wrong family | Unit | Failure |
| Create job family — duplicate name | Unit | Failure |
| Create job level — duplicate rank in same family | Unit | Failure |
| Create job level — duplicate rank in different family | Unit | Success (allowed) |
| Delete family with linked titles | Unit | Failure |
| Delete level with linked titles | Unit | Failure |
| Delete title in use by position | Unit | Failure |
| Delete title not in use | Unit | Success |
| Get titles — standalone titles included without filter | Integration | Included |
| Cross-tenant isolation | Integration | Cannot see other tenant titles |

---

## Related

- [[modules/org-structure/job-hierarchy/overview|Overview]]
- [[modules/org-structure/job-hierarchy/end-to-end-logic|End-to-End Logic]]
- [[modules/org-structure/positions/testing|Positions Testing]]
- [[code-standards/testing-strategy|Testing Standards]]
