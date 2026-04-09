# Biometric Devices — Testing

**Module:** Identity Verification
**Feature:** Biometric Devices
**Location:** `tests/ONEVO.Tests.Unit/Modules/IdentityVerification/BiometricDeviceServiceTests.cs`

---

## Unit Tests

```csharp
public class BiometricDeviceServiceTests
{
    private readonly Mock<IBiometricDeviceRepository> _repoMock = new();
    private readonly BiometricDeviceService _sut;

    [Fact]
    public async Task Register_device_encrypts_API_key()
    {
        // Arrange
        // ... setup mocks for register device encrypts api key

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Key encrypted at rest
    }

    [Fact]
    public async Task Webhook_validates_HMAC_signature()
    {
        // Arrange
        // ... setup mocks for webhook validates hmac signature

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Invalid signature rejected
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Register device encrypts API key | Unit | Key encrypted at rest |
| Webhook validates HMAC signature | Unit | Invalid signature rejected |

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[modules/identity-verification/biometric-devices/end-to-end-logic|Biometric Devices — End-to-End Logic]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
