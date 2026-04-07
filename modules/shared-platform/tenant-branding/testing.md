# Tenant Branding — Testing

**Module:** Shared Platform
**Feature:** Tenant Branding
**Location:** `tests/ONEVO.Tests.Unit/Modules/SharedPlatform/BrandingServiceTests.cs`

---

## Unit Tests

```csharp
public class BrandingServiceTests
{
    private readonly Mock<IBrandingRepository> _repoMock = new();
    private readonly BrandingService _sut;

    [Fact]
    public async Task Update_branding_uploads_logo()
    {
        // Arrange
        // ... setup mocks for update branding uploads logo

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // File uploaded
    }

    [Fact]
    public async Task Get_branding_returns_config()
    {
        // Arrange
        // ... setup mocks for get branding returns config

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Branding returned
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Update branding uploads logo | Unit | File uploaded |
| Get branding returns config | Unit | Branding returned |

## Related

- [[tenant-branding|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
