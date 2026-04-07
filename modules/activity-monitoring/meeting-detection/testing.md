# Meeting Detection — Testing

**Module:** Activity Monitoring
**Feature:** Meeting Detection
**Location:** `tests/ONEVO.Tests.Unit/Modules/ActivityMonitoring/MeetingDetectionServiceTests.cs`

---

## Unit Tests

```csharp
public class MeetingDetectionServiceTests
{
    private readonly Mock<IMeetingSessionRepository> _repoMock = new();
    private readonly MeetingDetectionService _sut;

    [Fact]
    public async Task DetectMeeting_TeamsProcess_CreatesMeetingSession()
    {
        var snapshot = new ActivitySnapshot { ForegroundApp = "Microsoft Teams", CapturedAt = DateTime.UtcNow };

        await _sut.ProcessSnapshotForMeetingsAsync(snapshot, default);

        _repoMock.Verify(r => r.InsertAsync(
            It.Is<MeetingSession>(m => m.Platform == "teams"), default), Times.Once);
    }

    [Fact]
    public async Task DetectMeeting_UnknownApp_NoSessionCreated()
    {
        var snapshot = new ActivitySnapshot { ForegroundApp = "Notepad", CapturedAt = DateTime.UtcNow };

        await _sut.ProcessSnapshotForMeetingsAsync(snapshot, default);

        _repoMock.Verify(r => r.InsertAsync(It.IsAny<MeetingSession>(), default), Times.Never);
    }

    [Fact]
    public async Task DetectMeeting_ExistingSession_UpdatesEndTime()
    {
        var existingSession = new MeetingSession { Platform = "teams", MeetingEnd = null };
        _repoMock.Setup(r => r.GetOpenSessionAsync(It.IsAny<Guid>(), "teams", default))
            .ReturnsAsync(existingSession);
        var snapshot = new ActivitySnapshot { ForegroundApp = "Microsoft Teams", CapturedAt = DateTime.UtcNow };

        await _sut.ProcessSnapshotForMeetingsAsync(snapshot, default);

        existingSession.MeetingEnd.Should().NotBeNull();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Teams.exe detected | Unit | Meeting session created |
| zoom.exe detected | Unit | Meeting session created |
| Unknown app | Unit | No session |
| Existing open session | Unit | End time updated |
| Short meeting (< 2 min) | Unit | Still recorded |

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[meeting-detection/end-to-end-logic|Meeting Detection — End-to-End Logic]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
- [[WEEK3-activity-monitoring]]
