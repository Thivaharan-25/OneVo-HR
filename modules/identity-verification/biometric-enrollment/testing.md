# Biometric Enrollment — Testing

**Module:** Identity Verification
**Feature:** Biometric Enrollment
**Location:** `tests/ONEVO.Tests.Unit/Modules/IdentityVerification/BiometricEnrollmentServiceTests.cs`

---

## Unit Tests

```csharp
public class BiometricEnrollmentServiceTests
{
    private readonly Mock<IBiometricEnrollmentRepository> _repoMock = new();
    private readonly BiometricEnrollmentService _sut;

    [Fact]
    public async Task Enroll_with_consent_succeeds()
    {
        // Arrange
        // ... setup mocks for enroll with consent succeeds

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Enrollment created
    }

    [Fact]
    public async Task Enroll_without_consent_fails()
    {
        // Arrange
        // ... setup mocks for enroll without consent fails

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // GDPR consent required
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Enroll with consent succeeds | Unit | Enrollment created |
| Enroll without consent fails | Unit | GDPR consent required |

## Related

- [[identity-verification|Identity Verification Module]]
- [[biometric-enrollment/end-to-end-logic|Biometric Enrollment — End-to-End Logic]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
- [[WEEK3-identity-verification]]
