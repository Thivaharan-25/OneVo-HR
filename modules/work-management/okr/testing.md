# OKR & Goals — Testing

**Module:** WorkSync
**Feature:** OKR & Goals
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/OKR/`

---

## Unit Tests

```csharp
public class OKRServiceTests
{
    [Fact]
    public async Task AddCheckIn_UpdatesProgressCascade()
    {
        var kr = new KeyResult { StartValue = 0, TargetValue = 100, CurrentValue = 0, Progress = 0 };
        var objective = new Objective { Progress = 0 };
        SetupObjectiveWithOneKR(objective, kr);

        await _sut.AddCheckInAsync(kr.Id, newValue: 50, "On track", default);

        kr.CurrentValue.Should().Be(50);
        kr.Progress.Should().Be(50);
        objective.Progress.Should().Be(50);
    }

    [Fact]
    public async Task AddCheckIn_BooleanKR_InvalidValue_ReturnsFailure()
    {
        var kr = new KeyResult { ResultType = "boolean", TargetValue = 1 };
        var result = await _sut.AddCheckInAsync(kr.Id, newValue: 5, "", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("0 or 1");
    }

    [Fact]
    public async Task AddCheckIn_ProgressExceeds100_ClampedTo100()
    {
        var kr = new KeyResult { StartValue = 0, TargetValue = 10, CurrentValue = 9 };
        await _sut.AddCheckInAsync(kr.Id, newValue: 15, "", default);
        kr.Progress.Should().Be(100); // clamped
    }

    [Fact]
    public async Task ObjectiveStatus_SetOnTrack_WhenProgressAbove70()
    {
        var objective = new Objective();
        SetupObjectiveProgress(objective, 75);
        objective.RecalculateStatus();
        objective.Status.Should().Be("on_track");
    }

    [Fact]
    public async Task ObjectiveStatus_SetAtRisk_WhenProgressBetween40And69()
    {
        var objective = new Objective();
        SetupObjectiveProgress(objective, 55);
        objective.RecalculateStatus();
        objective.Status.Should().Be("at_risk");
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Check-in cascades to objective | Unit | KR and objective progress updated |
| Boolean KR with invalid value | Unit | Failure |
| Progress clamped at 100 | Unit | Progress = 100 |
| Status = on_track when ≥ 70% | Unit | Correct status |
| Status = at_risk when 40–69% | Unit | Correct status |
| Status = off_track when < 40% | Unit | Correct status |

## Related

- [[modules/work-management/okr/overview|OKR Overview]]
- [[modules/work-management/okr/end-to-end-logic|OKR Logic]]
