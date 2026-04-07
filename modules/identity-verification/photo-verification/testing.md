# Photo Verification — Testing

**Module:** Identity Verification
**Feature:** Photo Verification
**Location:** `tests/ONEVO.Tests.Unit/Modules/IdentityVerification/VerificationServiceTests.cs`

---

## Unit Tests

```csharp
public class VerificationServiceTests
{
    private readonly Mock<IVerificationRepository> _repoMock = new();
    private readonly VerificationService _sut;

    [Fact]
    public async Task Photo_above_threshold_returns_verified()
    {
        // Arrange
        // ... setup mocks for photo above threshold returns verified

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = verified
    }

    [Fact]
    public async Task Photo_below_threshold_returns_failed_and_publishes_event()
    {
        // Arrange
        // ... setup mocks for photo below threshold returns failed and publishes event

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // VerificationFailed event
    }

    [Fact]
    public async Task Verification_disabled_skips_check()
    {
        // Arrange
        // ... setup mocks for verification disabled skips check

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // No verification performed
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Photo above threshold returns verified | Unit | Status = verified |
| Photo below threshold returns failed and publishes event | Unit | VerificationFailed event |
| Verification disabled skips check | Unit | No verification performed |

## Related

- [[identity-verification|Identity Verification Module]]
- [[photo-verification/end-to-end-logic|Photo Verification — End-to-End Logic]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
- [[WEEK3-identity-verification]]
