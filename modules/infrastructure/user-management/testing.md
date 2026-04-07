# User Management — Testing

**Module:** Infrastructure
**Feature:** User Management
**Location:** `tests/ONEVO.Tests.Unit/Modules/Infrastructure/UserServiceTests.cs`

---

## Unit Tests

```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _repoMock = new();
    private readonly UserService _sut;

    [Fact]
    public async Task Create_user_hashes_password()
    {
        // Arrange
        // ... setup mocks for create user hashes password

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // bcrypt hash stored
    }

    [Fact]
    public async Task Duplicate_email_returns_conflict()
    {
        // Arrange
        // ... setup mocks for duplicate email returns conflict

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 409 Conflict
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create user hashes password | Unit | bcrypt hash stored |
| Duplicate email returns conflict | Unit | 409 Conflict |

## Related

- [[user-management|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
