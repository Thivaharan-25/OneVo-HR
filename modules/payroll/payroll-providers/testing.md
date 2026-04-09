# Payroll Providers — Testing

**Module:** Payroll
**Feature:** Payroll Providers
**Location:** `tests/ONEVO.Tests.Unit/Modules/Payroll/PayrollProviderServiceTests.cs`

---

## Unit Tests

```csharp
public class PayrollProviderServiceTests
{
    private readonly Mock<IPayrollProviderRepository> _repoMock = new();
    private readonly PayrollProviderService _sut;

    [Fact]
    public async Task Create_provider_encrypts_credentials()
    {
        // Arrange
        // ... setup mocks for create provider encrypts credentials

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Encrypted at rest
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create provider encrypts credentials | Unit | Encrypted at rest |

## Related

- [[frontend/architecture/overview|Payroll Providers Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
