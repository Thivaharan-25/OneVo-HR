# SSO Authentication — Testing

**Module:** Shared Platform
**Feature:** SSO Authentication
**Location:** `tests/ONEVO.Tests.Unit/Modules/SharedPlatform/SsoProviderServiceTests.cs`

---

## Unit Tests

```csharp
public class SsoProviderServiceTests
{
    private readonly Mock<ISsoProviderRepository> _repoMock = new();
    private readonly SsoProviderService _sut;

    [Fact]
    public async Task Create_SSO_provider_encrypts_credentials()
    {
        // Arrange
        // ... setup mocks for create sso provider encrypts credentials

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Encrypted at rest
    }

    [Fact]
    public async Task SSO_login_auto-provisions_user()
    {
        // Arrange
        // ... setup mocks for sso login auto-provisions user

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // User created on first login
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create SSO provider encrypts credentials | Unit | Encrypted at rest |
| SSO login auto-provisions user | Unit | User created on first login |

## Related

- [[sso-authentication|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
