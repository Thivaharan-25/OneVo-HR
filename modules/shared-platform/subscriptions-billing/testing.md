# Subscriptions & Billing — Testing

**Module:** Shared Platform
**Feature:** Subscriptions & Billing
**Location:** `tests/ONEVO.Tests.Unit/Modules/SharedPlatform/SubscriptionServiceTests.cs`

---

## Unit Tests

```csharp
public class SubscriptionServiceTests
{
    private readonly Mock<ISubscriptionRepository> _repoMock = new();
    private readonly SubscriptionService _sut;

    [Fact]
    public async Task Upgrade_plan_calls_Stripe_API()
    {
        // Arrange
        // ... setup mocks for upgrade plan calls stripe api

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Subscription updated
    }

    [Fact]
    public async Task Get_current_returns_active_plan()
    {
        // Arrange
        // ... setup mocks for get current returns active plan

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Plan details returned
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Upgrade plan calls Stripe API | Unit | Subscription updated |
| Get current returns active plan | Unit | Plan details returned |

## Related

- [[subscriptions-billing|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
