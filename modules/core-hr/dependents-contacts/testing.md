# Dependents & Contacts — Testing

**Module:** Core HR
**Feature:** Dependents & Contacts
**Location:** `tests/ONEVO.Tests.Unit/Modules/CoreHR/DependentServiceTests.cs`

---

## Unit Tests

```csharp
public class DependentServiceTests
{
    private readonly Mock<IDependentRepository> _repoMock = new();
    private readonly DependentService _sut;

    [Fact]
    public async Task Add_dependent_creates_record()
    {
        // Arrange
        // ... setup mocks for add dependent creates record

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Dependent inserted
    }

    [Fact]
    public async Task Emergency_contact_primary_flag_toggled()
    {
        // Arrange
        // ... setup mocks for emergency contact primary flag toggled

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Previous primary unset
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Add dependent creates record | Unit | Dependent inserted |
| Emergency contact primary flag toggled | Unit | Previous primary unset |

## Related

- [[modules/core-hr/dependents-contacts/overview|Dependents & Contacts Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
