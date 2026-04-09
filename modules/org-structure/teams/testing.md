# Teams — Testing

**Module:** Org Structure
**Feature:** Teams
**Location:** `tests/ONEVO.Tests.Unit/Modules/OrgStructure/TeamServiceTests.cs`

---

## Unit Tests

```csharp
public class TeamServiceTests
{
    private readonly Mock<ITeamRepository> _repoMock = new();
    private readonly TeamService _sut;

    [Fact]
    public async Task Create_team_validates_department()
    {
        // Arrange
        // ... setup mocks for create team validates department

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Team created
    }

    [Fact]
    public async Task Add_member_validates_employee()
    {
        // Arrange
        // ... setup mocks for add member validates employee

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Member added
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create team validates department | Unit | Team created |
| Add member validates employee | Unit | Member added |

## Related

- [[modules/org-structure/teams/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
