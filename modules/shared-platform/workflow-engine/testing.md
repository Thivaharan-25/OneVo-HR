# Workflow Engine — Testing

**Module:** Shared Platform
**Feature:** Workflow Engine
**Location:** `tests/ONEVO.Tests.Unit/Modules/SharedPlatform/WorkflowServiceTests.cs`

---

## Unit Tests

```csharp
public class WorkflowServiceTests
{
    private readonly Mock<IWorkflowRepository> _repoMock = new();
    private readonly WorkflowService _sut;

    [Fact]
    public async Task Create_instance_resolves_first_approver()
    {
        // Arrange
        // ... setup mocks for create instance resolves first approver

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Step instance created
    }

    [Fact]
    public async Task Approve_advances_to_next_step()
    {
        // Arrange
        // ... setup mocks for approve advances to next step

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Next approver notified
    }

    [Fact]
    public async Task Final_approval_completes_workflow()
    {
        // Arrange
        // ... setup mocks for final approval completes workflow

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // WorkflowCompleted event
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create instance resolves first approver | Unit | Step instance created |
| Approve advances to next step | Unit | Next approver notified |
| Final approval completes workflow | Unit | WorkflowCompleted event |

## Related

- [[modules/shared-platform/workflow-engine/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
