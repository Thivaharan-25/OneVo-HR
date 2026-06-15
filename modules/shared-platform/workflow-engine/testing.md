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
        // WorkflowApproved event
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create instance resolves first approver through resolver | Unit | Step instance created without role-name checks |
| Resolver returns users with selected permission | Unit | All eligible users are candidates |
| Resolver returns no candidate | Unit | Step is blocked and the automation owner or configured escalation resolver is notified |
| Only one approval is required | Unit | First approver completes the step; other assignees see completed state |
| All assigned approvers must approve | Unit | Step remains pending until every assignee approves |
| Approve in order | Unit | Next approver receives the request only after previous approval |
| Create case conversation | Integration | Private case conversation is linked to workflow item |
| Delivery router with Chat enabled | Integration | Action card appears in ONEVO Chat case conversation |
| Delivery router without Chat | Integration | Action card appears in Inbox detail panel |
| Teams mirror enabled | Integration | Discussion is mirrored, but official action remains a ONEVO link |
| Approve advances to next step | Unit | Next resolver is evaluated and next assignee notified |
| Final approval approves workflow | Unit | WorkflowApproved event |
| Unresolved delay escalates dynamically | Unit | Escalation resolver receives action card and audit entry is written |

## Related

- [[modules/shared-platform/workflow-engine/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
