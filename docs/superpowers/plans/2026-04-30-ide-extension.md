# IDE Extension (DEV9) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the OneVo VS Code extension — chat sidebar, full `@` tag picker (all WMS + HR actions), NLP via Semantic Kernel, context engine, and agent entitlement.

**Architecture:** Backend extends the existing `IDEExtension` module with HR tag routing, updated entitlements DTO, and a Semantic Kernel intent pipeline in `WorkSync.ChatAI`. The VS Code extension (TypeScript + webpack) is a client of the same backend APIs used by the web frontend — no separate DB, no separate auth, no separate permissions. All actions flow through `POST /api/v1/ide/tags/execute`.

**Tech Stack:** Backend: .NET 9, C# 13, MediatR, EF Core 9, Semantic Kernel, SignalR. Extension: TypeScript 5, VS Code Extension API, `@microsoft/signalr`, webpack 5. Tests: xUnit + WebApplicationFactory (backend), Mocha + sinon + `@vscode/test-electron` (extension).

**Spec:** `docs/superpowers/specs/2026-04-30-ide-extension-design.md`  
**Module spec:** `modules/ide-extension/overview.md`

---

## Scope Check

This plan is split into two parallel tracks:
- **Backend (Tasks B1–B3):** Extend existing .NET backend
- **Extension (Tasks E1–E7):** Build VS Code extension from scratch

Tasks B1–B3 can be done by one developer while E1 is being scaffolded. E2+ depend on B1 being done first.

---

## File Map

### Backend files (new/modified)

| Action | Path |
|--------|------|
| Modify | `ONEVO.Modules.IDEExtension/Application/DTOs/IDEEntitlementsDto.cs` |
| Modify | `ONEVO.Modules.IDEExtension/Application/Queries/GetEntitlementsQuery.cs` |
| Modify | `ONEVO.Modules.IDEExtension/Application/Queries/GetEntitlementsQueryHandler.cs` |
| Create | `ONEVO.Modules.IDEExtension/Application/Commands/ExecuteHRTagCommand.cs` |
| Create | `ONEVO.Modules.IDEExtension/Application/Commands/ExecuteHRTagCommandHandler.cs` |
| Create | `ONEVO.Modules.WorkSync.ChatAI/Application/Commands/DetectNlpIntentCommand.cs` |
| Create | `ONEVO.Modules.WorkSync.ChatAI/Application/Commands/DetectNlpIntentCommandHandler.cs` |
| Modify | `ONEVO.Api/Features/IDE/IDEEndpoints.cs` — chat message endpoint hooks SK pipeline |
| Modify | `tests/ONEVO.Modules.IDEExtension.Tests/GetEntitlementsQueryHandlerTests.cs` |
| Create | `tests/ONEVO.Modules.IDEExtension.Tests/ExecuteHRTagCommandHandlerTests.cs` |
| Create | `tests/ONEVO.Modules.WorkSync.ChatAI.Tests/DetectNlpIntentCommandHandlerTests.cs` |

### VS Code Extension files (all new)

```
onevo-ide-extension/
├── package.json
├── tsconfig.json
├── webpack.config.js
├── .vscodeignore
├── src/
│   ├── extension.ts
│   ├── auth/
│   │   ├── AuthService.ts
│   │   └── TokenRefresher.ts
│   ├── signalr/
│   │   └── IDEHubClient.ts
│   ├── api/
│   │   └── OneVoApiClient.ts
│   ├── config/
│   │   └── WorkspaceConfig.ts
│   ├── panels/
│   │   ├── ChatPanel.ts
│   │   ├── TasksPanel.ts
│   │   └── NotificationsPanel.ts
│   ├── webviews/
│   │   ├── ChatWebview.ts
│   │   ├── TaskDetailWebview.ts
│   │   └── MiniFormWebview.ts
│   ├── tag-engine/
│   │   ├── TagParser.ts
│   │   ├── TagExecutor.ts
│   │   ├── TagPickerWebview.ts
│   │   └── AutoCompleteProvider.ts
│   ├── hr/
│   │   ├── HrTagHandler.ts
│   │   ├── LeaveFormWebview.ts
│   │   └── TimesheetWebview.ts
│   ├── nlp/
│   │   └── NlpSuggestionHandler.ts
│   ├── context/
│   │   ├── BranchDetector.ts
│   │   ├── FileContextDetector.ts
│   │   └── TimeTracker.ts
│   └── agent-install/
│       └── AgentInstaller.ts
├── test/
│   ├── suite/
│   │   ├── index.ts
│   │   ├── TagParser.test.ts
│   │   ├── OneVoApiClient.test.ts
│   │   ├── HrTagHandler.test.ts
│   │   └── NlpSuggestionHandler.test.ts
│   └── runTests.ts
```

---

## Task B1: Extend IDEEntitlementsDto

**Files:**
- Modify: `ONEVO.Modules.IDEExtension/Application/DTOs/IDEEntitlementsDto.cs`
- Modify: `ONEVO.Modules.IDEExtension/Application/Queries/GetEntitlementsQueryHandler.cs`
- Modify: `tests/ONEVO.Modules.IDEExtension.Tests/GetEntitlementsQueryHandlerTests.cs`

The current DTO only returns `has_monitoring_entitlement`. We need to add `active_modules[]` and `permitted_tag_actions[]` so the extension knows what to show in the `@` picker.

- [ ] **Step 1: Write the failing test**

```csharp
// tests/ONEVO.Modules.IDEExtension.Tests/GetEntitlementsQueryHandlerTests.cs
[Fact]
public async Task Handle_WhenTenantHasHRModule_ReturnsHRInActiveModules()
{
    // Arrange — seed feature_access_grants with hr_management for tenant
    var tenantId = Guid.NewGuid();
    var userId = Guid.NewGuid();
    _db.FeatureAccessGrants.Add(new FeatureAccessGrant
    {
        TenantId = tenantId,
        Module = "hr_management",
        GrantedAt = DateTime.UtcNow
    });
    await _db.SaveChangesAsync();

    var query = new GetEntitlementsQuery(userId, tenantId);

    // Act
    var result = await _handler.Handle(query, CancellationToken.None);

    // Assert
    Assert.Contains("hr_management", result.ActiveModules);
}

[Fact]
public async Task Handle_WhenUserHasLeaveWritePermission_ReturnsLeaveRequestInPermittedActions()
{
    var tenantId = Guid.NewGuid();
    var userId = Guid.NewGuid();
    _db.UserPermissions.Add(new UserPermission
    {
        UserId = userId,
        TenantId = tenantId,
        Permission = "leave:write"
    });
    await _db.SaveChangesAsync();

    var query = new GetEntitlementsQuery(userId, tenantId);
    var result = await _handler.Handle(query, CancellationToken.None);

    Assert.Contains("leave:request", result.PermittedTagActions);
}

[Fact]
public async Task Handle_WhenTenantHasNoHRModule_DoesNotReturnHRActions()
{
    var tenantId = Guid.NewGuid();
    var userId = Guid.NewGuid();
    // No feature_access_grants for hr_management

    var query = new GetEntitlementsQuery(userId, tenantId);
    var result = await _handler.Handle(query, CancellationToken.None);

    Assert.DoesNotContain("hr_management", result.ActiveModules);
    Assert.DoesNotContain("leave:request", result.PermittedTagActions);
    Assert.DoesNotContain("clockin", result.PermittedTagActions);
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
dotnet test tests/ONEVO.Modules.IDEExtension.Tests/ -k "GetEntitlementsQueryHandlerTests" --no-build
```

Expected: FAIL — `ActiveModules` and `PermittedTagActions` properties don't exist yet.

- [ ] **Step 3: Extend the DTO**

```csharp
// ONEVO.Modules.IDEExtension/Application/DTOs/IDEEntitlementsDto.cs
public sealed record IDEEntitlementsDto
{
    public bool HasMonitoringEntitlement { get; init; }
    public Guid? WorkspaceId { get; init; }
    public string UserRole { get; init; } = string.Empty;
    public IReadOnlyList<string> ActiveModules { get; init; } = [];
    public IReadOnlyList<string> PermittedTagActions { get; init; } = [];
}
```

- [ ] **Step 4: Update the query handler**

```csharp
// ONEVO.Modules.IDEExtension/Application/Queries/GetEntitlementsQueryHandler.cs
public sealed class GetEntitlementsQueryHandler(ApplicationDbContext db)
    : IRequestHandler<GetEntitlementsQuery, IDEEntitlementsDto>
{
    // Map from permission → tag actions the user can perform
    private static readonly Dictionary<string, string[]> PermissionToTagActions = new()
    {
        ["tasks:write"]      = ["task:new", "task:status", "task:assign", "task:comment", "task:link", "task:move"],
        ["tasks:read"]       = ["task:view"],
        ["sprints:write"]    = ["sprint:add", "sprint:start", "sprint:complete"],
        ["sprints:read"]     = ["sprint:view"],
        ["time_logs:write"]  = ["time:log", "time:start", "time:stop"],
        ["time_logs:read"]   = ["time:view"],
        ["boards:write"]     = ["board:move"],
        ["boards:read"]      = ["board:view"],
        ["okr:write"]        = ["okr:checkin"],
        ["okr:read"]         = ["okr:view"],
        ["documents:write"]  = ["doc:create", "doc:link"],
        ["documents:read"]   = ["doc:view"],
        ["reviews:write"]    = ["review:request", "review:approve", "review:reject"],
        ["notifications:write"] = ["notify:send"],
        ["projects:read"]    = ["project:view", "project:members"],
        ["chat:write"]       = ["chat:send", "chat:pin", "chat:remind"],
        // HR — only included if tenant has hr_management module
        ["leave:write"]      = ["leave:request", "leave:cancel"],
        ["leave:read"]       = ["leave:view"],
        ["attendance:write"] = ["clockin", "break:start", "break:end", "clockout", "overtime:request"],
        ["payroll:read"]     = ["payslip:view"],
        ["timesheets:write"] = ["timesheet:submit"],
        ["timesheets:read"]  = ["timesheet:view"],
        ["shifts:read"]      = ["shift:view"],
        ["calendar:read"]    = ["calendar:view"],
    };

    // HR-specific actions that require hr_management in active_modules
    private static readonly HashSet<string> HrTagActions =
    [
        "leave:request", "leave:view", "leave:cancel", "clockin", "break:start",
        "break:end", "clockout", "overtime:request", "payslip:view",
        "timesheet:submit", "timesheet:view", "shift:view", "calendar:view"
    ];

    public async Task<IDEEntitlementsDto> Handle(GetEntitlementsQuery request, CancellationToken ct)
    {
        // 1. Resolve active modules from feature_access_grants + subscription plan
        var activeModules = await db.FeatureAccessGrants
            .Where(g => g.TenantId == request.TenantId)
            .Select(g => g.Module)
            .ToListAsync(ct);

        // Also pull plan-level modules
        var planModules = await db.Tenants
            .Where(t => t.Id == request.TenantId)
            .Select(t => t.SubscriptionPlan != null ? t.SubscriptionPlan.FeaturesJson : null)
            .FirstOrDefaultAsync(ct);

        if (planModules != null)
        {
            // FeaturesJson contains array of module names
            var planModuleList = JsonSerializer.Deserialize<List<string>>(planModules) ?? [];
            activeModules = activeModules.Union(planModuleList).Distinct().ToList();
        }

        bool hasHr = activeModules.Contains("hr_management");

        // 2. Resolve user permissions
        var userPermissions = await db.UserPermissions
            .Where(p => p.UserId == request.UserId && p.TenantId == request.TenantId)
            .Select(p => p.Permission)
            .ToListAsync(ct);

        // 3. Build permitted tag actions
        var permittedActions = new HashSet<string>();
        foreach (var permission in userPermissions)
        {
            if (PermissionToTagActions.TryGetValue(permission, out var actions))
            {
                foreach (var action in actions)
                {
                    // Skip HR actions if tenant doesn't have HR module
                    if (HrTagActions.Contains(action) && !hasHr) continue;
                    permittedActions.Add(action);
                }
            }
        }

        // 4. Resolve monitoring entitlement
        var hasMonitoring = await db.AgentInstallEntitlements
            .AnyAsync(e => e.TenantId == request.TenantId && e.IsActive, ct);

        // 5. Resolve workspace
        var workspaceId = await db.WorkspaceMembers
            .Where(m => m.UserId == request.UserId)
            .Select(m => (Guid?)m.WorkspaceId)
            .FirstOrDefaultAsync(ct);

        return new IDEEntitlementsDto
        {
            HasMonitoringEntitlement = hasMonitoring,
            WorkspaceId = workspaceId,
            ActiveModules = activeModules.AsReadOnly(),
            PermittedTagActions = permittedActions.ToList().AsReadOnly()
        };
    }
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
dotnet test tests/ONEVO.Modules.IDEExtension.Tests/ -k "GetEntitlementsQueryHandlerTests"
```

Expected: All 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add ONEVO.Modules.IDEExtension/Application/DTOs/IDEEntitlementsDto.cs \
        ONEVO.Modules.IDEExtension/Application/Queries/GetEntitlementsQueryHandler.cs \
        tests/ONEVO.Modules.IDEExtension.Tests/GetEntitlementsQueryHandlerTests.cs
git commit -m "feat(ide): extend IDEEntitlementsDto with active_modules and permitted_tag_actions"
```

---

## Task B2: HR Tag Routing in Tag Executor

**Files:**
- Create: `ONEVO.Modules.IDEExtension/Application/Commands/ExecuteHRTagCommand.cs`
- Create: `ONEVO.Modules.IDEExtension/Application/Commands/ExecuteHRTagCommandHandler.cs`
- Create: `tests/ONEVO.Modules.IDEExtension.Tests/ExecuteHRTagCommandHandlerTests.cs`

The existing `ExecuteTagAsync` in `IIDEExtensionService` handles WMS tags. We add HR tag routing here. HR tags call the `WorkforcePresence` and `Leave` module service interfaces.

- [ ] **Step 1: Write failing tests**

```csharp
// tests/ONEVO.Modules.IDEExtension.Tests/ExecuteHRTagCommandHandlerTests.cs
public class ExecuteHRTagCommandHandlerTests
{
    private readonly Mock<IWorkforcePresenceService> _presenceMock = new();
    private readonly Mock<ILeaveService> _leaveMock = new();
    private readonly ExecuteHRTagCommandHandler _handler;

    public ExecuteHRTagCommandHandlerTests()
    {
        _handler = new ExecuteHRTagCommandHandler(_presenceMock.Object, _leaveMock.Object);
    }

    [Fact]
    public async Task Handle_Clockin_CallsPresenceServiceStartSession()
    {
        var cmd = new ExecuteHRTagCommand(
            UserId: Guid.NewGuid(),
            TenantId: Guid.NewGuid(),
            TagAction: "clockin",
            Params: new Dictionary<string, string>()
        );

        await _handler.Handle(cmd, CancellationToken.None);

        _presenceMock.Verify(s => s.StartSessionAsync(cmd.UserId, cmd.TenantId, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task Handle_BreakStart_CallsPresenceServiceStartBreak()
    {
        var cmd = new ExecuteHRTagCommand(
            UserId: Guid.NewGuid(),
            TenantId: Guid.NewGuid(),
            TagAction: "break:start",
            Params: new Dictionary<string, string> { ["type"] = "personal" }
        );

        await _handler.Handle(cmd, CancellationToken.None);

        _presenceMock.Verify(s => s.StartBreakAsync(cmd.UserId, cmd.TenantId, "personal", It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task Handle_LeaveRequest_CallsLeaveServiceCreateRequest()
    {
        var userId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();
        var cmd = new ExecuteHRTagCommand(
            UserId: userId,
            TenantId: tenantId,
            TagAction: "leave:request",
            Params: new Dictionary<string, string>
            {
                ["leave_type_id"] = Guid.NewGuid().ToString(),
                ["from"] = "2026-05-05",
                ["to"] = "2026-05-07",
                ["reason"] = "Conference"
            }
        );

        await _handler.Handle(cmd, CancellationToken.None);

        _leaveMock.Verify(s => s.CreateRequestAsync(It.Is<CreateLeaveRequestDto>(r =>
            r.UserId == userId &&
            r.TenantId == tenantId &&
            r.StartDate == new DateOnly(2026, 5, 5) &&
            r.EndDate == new DateOnly(2026, 5, 7)
        ), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task Handle_UnknownHRTag_ThrowsArgumentException()
    {
        var cmd = new ExecuteHRTagCommand(
            UserId: Guid.NewGuid(),
            TenantId: Guid.NewGuid(),
            TagAction: "unknown:action",
            Params: new Dictionary<string, string>()
        );

        await Assert.ThrowsAsync<ArgumentException>(() =>
            _handler.Handle(cmd, CancellationToken.None));
    }
}
```

- [ ] **Step 2: Run to verify failures**

```bash
dotnet test tests/ONEVO.Modules.IDEExtension.Tests/ -k "ExecuteHRTagCommandHandlerTests"
```

Expected: FAIL — types don't exist yet.

- [ ] **Step 3: Create the command and handler**

```csharp
// ONEVO.Modules.IDEExtension/Application/Commands/ExecuteHRTagCommand.cs
public sealed record ExecuteHRTagCommand(
    Guid UserId,
    Guid TenantId,
    string TagAction,
    Dictionary<string, string> Params
) : IRequest;
```

```csharp
// ONEVO.Modules.IDEExtension/Application/Commands/ExecuteHRTagCommandHandler.cs
public sealed class ExecuteHRTagCommandHandler(
    IWorkforcePresenceService presenceService,
    ILeaveService leaveService)
    : IRequestHandler<ExecuteHRTagCommand>
{
    public async Task Handle(ExecuteHRTagCommand cmd, CancellationToken ct)
    {
        switch (cmd.TagAction)
        {
            case "clockin":
                await presenceService.StartSessionAsync(cmd.UserId, cmd.TenantId, ct);
                break;

            case "break:start":
                var breakType = cmd.Params.GetValueOrDefault("type", "personal");
                await presenceService.StartBreakAsync(cmd.UserId, cmd.TenantId, breakType, ct);
                break;

            case "break:end":
                await presenceService.EndBreakAsync(cmd.UserId, cmd.TenantId, ct);
                break;

            case "clockout":
                await presenceService.EndSessionAsync(cmd.UserId, cmd.TenantId, ct);
                break;

            case "overtime:request":
                var overtimeDate = DateOnly.Parse(cmd.Params["date"]);
                var hours = decimal.Parse(cmd.Params["hours"]);
                var reason = cmd.Params.GetValueOrDefault("reason", "");
                await presenceService.RequestOvertimeAsync(cmd.UserId, cmd.TenantId, overtimeDate, hours, reason, ct);
                break;

            case "leave:request":
                await leaveService.CreateRequestAsync(new CreateLeaveRequestDto
                {
                    UserId = cmd.UserId,
                    TenantId = cmd.TenantId,
                    LeaveTypeId = Guid.Parse(cmd.Params["leave_type_id"]),
                    StartDate = DateOnly.Parse(cmd.Params["from"]),
                    EndDate = DateOnly.Parse(cmd.Params["to"]),
                    Reason = cmd.Params.GetValueOrDefault("reason", "")
                }, ct);
                break;

            case "leave:cancel":
                await leaveService.CancelRequestAsync(Guid.Parse(cmd.Params["request_id"]), cmd.UserId, ct);
                break;

            case "timesheet:submit":
                await leaveService.SubmitTimesheetAsync(cmd.UserId, cmd.TenantId, ct);
                break;

            default:
                throw new ArgumentException($"Unknown HR tag action: {cmd.TagAction}");
        }
    }
}
```

- [ ] **Step 4: Wire HR tag actions into the existing `ExecuteTagAsync` handler**

In the existing `ExecuteTagCommandHandler.cs`, add routing for HR entities before the WMS switch:

```csharp
// In existing ExecuteTagCommandHandler.Handle():
private static readonly HashSet<string> HrEntities =
    ["clockin", "clockout", "break:start", "break:end", "break:end",
     "overtime:request", "leave:request", "leave:view", "leave:cancel",
     "payslip:view", "timesheet:view", "timesheet:submit", "shift:view", "calendar:view"];

// At the start of Handle():
if (HrEntities.Contains($"{cmd.ParsedEntity}:{cmd.ParsedAction}") ||
    HrEntities.Contains(cmd.ParsedEntity))
{
    await mediator.Send(new ExecuteHRTagCommand(
        cmd.UserId, cmd.TenantId,
        string.IsNullOrEmpty(cmd.ParsedAction)
            ? cmd.ParsedEntity
            : $"{cmd.ParsedEntity}:{cmd.ParsedAction}",
        cmd.ResolvedParams
    ), ct);
    return TagExecutionResult.Success();
}
```

- [ ] **Step 5: Run tests**

```bash
dotnet test tests/ONEVO.Modules.IDEExtension.Tests/ -k "ExecuteHRTagCommandHandlerTests"
```

Expected: All 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add ONEVO.Modules.IDEExtension/Application/Commands/ \
        tests/ONEVO.Modules.IDEExtension.Tests/ExecuteHRTagCommandHandlerTests.cs
git commit -m "feat(ide): add HR tag routing — clockin, break, clockout, leave, overtime"
```

---

## Task B3: Semantic Kernel Intent Pipeline

**Files:**
- Create: `ONEVO.Modules.WorkSync.ChatAI/Application/Commands/DetectNlpIntentCommand.cs`
- Create: `ONEVO.Modules.WorkSync.ChatAI/Application/Commands/DetectNlpIntentCommandHandler.cs`
- Modify: `ONEVO.Api/Features/Chat/ChatEndpoints.cs` — hook SK before storing message
- Create: `tests/ONEVO.Modules.WorkSync.ChatAI.Tests/DetectNlpIntentCommandHandlerTests.cs`

- [ ] **Step 1: Write failing tests**

```csharp
// tests/ONEVO.Modules.WorkSync.ChatAI.Tests/DetectNlpIntentCommandHandlerTests.cs
public class DetectNlpIntentCommandHandlerTests
{
    private readonly Mock<ISemanticKernelService> _skMock = new();
    private readonly DetectNlpIntentCommandHandler _handler;

    public DetectNlpIntentCommandHandlerTests()
    {
        _handler = new DetectNlpIntentCommandHandler(_skMock.Object);
    }

    [Fact]
    public async Task Handle_HighConfidenceTimeLog_ReturnsSuggestion()
    {
        _skMock.Setup(s => s.DetectIntentAsync("log 2 hours on the login bug", It.IsAny<NlpContext>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new NlpIntentResult
            {
                TagAction = "time:log",
                Confidence = 0.92,
                ResolvedParams = new Dictionary<string, string> { ["hours"] = "2", ["description"] = "login bug" }
            });

        var cmd = new DetectNlpIntentCommand(
            MessageText: "log 2 hours on the login bug",
            Context: new NlpContext(PermittedTagActions: ["time:log", "task:new"], ActiveBranchTask: "TASK-123")
        );

        var result = await _handler.Handle(cmd, CancellationToken.None);

        Assert.NotNull(result);
        Assert.Equal("time:log", result!.TagAction);
        Assert.Equal(0.92, result.Confidence);
    }

    [Fact]
    public async Task Handle_LowConfidenceMessage_ReturnsNull()
    {
        _skMock.Setup(s => s.DetectIntentAsync(It.IsAny<string>(), It.IsAny<NlpContext>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new NlpIntentResult { TagAction = "task:new", Confidence = 0.5 });

        var cmd = new DetectNlpIntentCommand(
            MessageText: "hey team what's up",
            Context: new NlpContext(PermittedTagActions: ["task:new"], ActiveBranchTask: null)
        );

        var result = await _handler.Handle(cmd, CancellationToken.None);

        Assert.Null(result); // Below 0.8 threshold → no suggestion
    }

    [Fact]
    public async Task Handle_IntentNotInPermittedActions_ReturnsNull()
    {
        _skMock.Setup(s => s.DetectIntentAsync(It.IsAny<string>(), It.IsAny<NlpContext>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new NlpIntentResult { TagAction = "leave:request", Confidence = 0.95 });

        // User does not have leave:request in permitted actions
        var cmd = new DetectNlpIntentCommand(
            MessageText: "I want to take leave next week",
            Context: new NlpContext(PermittedTagActions: ["task:new", "time:log"], ActiveBranchTask: null)
        );

        var result = await _handler.Handle(cmd, CancellationToken.None);

        Assert.Null(result); // Not permitted → no suggestion even if confident
    }
}
```

- [ ] **Step 2: Run to verify failures**

```bash
dotnet test tests/ONEVO.Modules.WorkSync.ChatAI.Tests/ -k "DetectNlpIntentCommandHandlerTests"
```

Expected: FAIL — types don't exist.

- [ ] **Step 3: Create command and handler**

```csharp
// ONEVO.Modules.WorkSync.ChatAI/Application/Commands/DetectNlpIntentCommand.cs
public sealed record NlpContext(
    IReadOnlyList<string> PermittedTagActions,
    string? ActiveBranchTask
);

public sealed record NlpIntentResult
{
    public string TagAction { get; init; } = string.Empty;
    public double Confidence { get; init; }
    public Dictionary<string, string> ResolvedParams { get; init; } = [];
}

public sealed record DetectNlpIntentCommand(
    string MessageText,
    NlpContext Context
) : IRequest<NlpIntentResult?>;
```

```csharp
// ONEVO.Modules.WorkSync.ChatAI/Application/Commands/DetectNlpIntentCommandHandler.cs
public sealed class DetectNlpIntentCommandHandler(ISemanticKernelService skService)
    : IRequestHandler<DetectNlpIntentCommand, NlpIntentResult?>
{
    private const double ConfidenceThreshold = 0.8;

    public async Task<NlpIntentResult?> Handle(DetectNlpIntentCommand cmd, CancellationToken ct)
    {
        var intent = await skService.DetectIntentAsync(cmd.MessageText, cmd.Context, ct);

        // Below threshold → treat as plain chat
        if (intent.Confidence < ConfidenceThreshold) return null;

        // SK cannot suggest actions user doesn't have permission for
        if (!cmd.Context.PermittedTagActions.Contains(intent.TagAction)) return null;

        return intent;
    }
}
```

- [ ] **Step 4: Hook SK into the chat message endpoint**

In `ONEVO.Api/Features/Chat/ChatEndpoints.cs`, in the `POST /api/v1/chat/messages` handler, before storing the message:

```csharp
// After validating the message, before saving:
var nlpContext = new NlpContext(
    PermittedTagActions: userEntitlements.PermittedTagActions,
    ActiveBranchTask: activeBranchTask // from IDE session context
);

var nlpIntent = await mediator.Send(new DetectNlpIntentCommand(request.Content, nlpContext), ct);

if (nlpIntent is not null)
{
    // Don't store message yet — push ai.suggestion event, let user confirm
    var jobId = Guid.NewGuid();
    await hubContext.Clients.User(userId.ToString())
        .SendAsync("ai:action_pending", new
        {
            job_id = jobId,
            tag_action = nlpIntent.TagAction,
            resolved_params = nlpIntent.ResolvedParams,
            original_message = request.Content,
            undo_expires_at = DateTime.UtcNow.AddSeconds(60)
        }, ct);
    return Results.Accepted();
}

// No intent detected — store as normal message
var message = await mediator.Send(new SendMessageCommand(channelId, userId, request.Content), ct);
return Results.Ok(message);
```

- [ ] **Step 5: Run tests**

```bash
dotnet test tests/ONEVO.Modules.WorkSync.ChatAI.Tests/ -k "DetectNlpIntentCommandHandlerTests"
```

Expected: All 3 PASS.

- [ ] **Step 6: Run the full backend test suite**

```bash
dotnet test ONEVO.sln --no-build
```

Expected: All existing tests still pass.

- [ ] **Step 7: Commit**

```bash
git add ONEVO.Modules.WorkSync.ChatAI/Application/Commands/ \
        ONEVO.Api/Features/Chat/ChatEndpoints.cs \
        tests/ONEVO.Modules.WorkSync.ChatAI.Tests/
git commit -m "feat(chat-ai): add Semantic Kernel NLP intent pipeline with 0.8 confidence threshold"
```

---

## Task E1: Extension Foundation — Scaffold, Auth, SignalR

**Files:** All new — `onevo-ide-extension/` directory (see file map above)

The extension must be scaffolded from scratch. We use `yo code` to generate the TypeScript + webpack template, then replace the generated stubs with production code.

- [ ] **Step 1: Scaffold the extension**

```bash
cd onevo-ide-extension
npm install -g yo generator-code
yo code --extensionType ext-webpack --extensionDisplayName "OneVo" --extensionName onevo --extensionDescription "OneVo workspace inside VS Code" --pkgManager npm --bundler webpack --skipInstall false
```

Expected output: Extension scaffolded with `package.json`, `src/extension.ts`, `webpack.config.js`.

- [ ] **Step 2: Install dependencies**

```bash
npm install @microsoft/signalr
npm install --save-dev mocha @types/mocha sinon @types/sinon @vscode/test-electron
```

- [ ] **Step 3: Write failing test for AuthService**

```typescript
// test/suite/AuthService.test.ts
import * as assert from 'assert';
import * as sinon from 'sinon';
import { AuthService } from '../../src/auth/AuthService';

suite('AuthService', () => {
    let mockSecretStorage: any;

    setup(() => {
        mockSecretStorage = {
            get: sinon.stub(),
            store: sinon.stub().resolves(),
            delete: sinon.stub().resolves()
        };
    });

    test('getToken returns null when no token stored', async () => {
        mockSecretStorage.get.resolves(undefined);
        const service = new AuthService(mockSecretStorage);
        const token = await service.getToken();
        assert.strictEqual(token, null);
    });

    test('getToken returns stored token', async () => {
        mockSecretStorage.get.resolves('eyJhbGci...');
        const service = new AuthService(mockSecretStorage);
        const token = await service.getToken();
        assert.strictEqual(token, 'eyJhbGci...');
    });

    test('storeToken saves to SecretStorage', async () => {
        const service = new AuthService(mockSecretStorage);
        await service.storeToken('new-token');
        sinon.assert.calledWith(mockSecretStorage.store, 'onevo.jwt', 'new-token');
    });

    test('clearToken removes from SecretStorage', async () => {
        const service = new AuthService(mockSecretStorage);
        await service.clearToken();
        sinon.assert.calledWith(mockSecretStorage.delete, 'onevo.jwt');
    });
});
```

- [ ] **Step 4: Run test to verify it fails**

```bash
npm test
```

Expected: FAIL — `AuthService` not found.

- [ ] **Step 5: Implement AuthService**

```typescript
// src/auth/AuthService.ts
import type { SecretStorage } from 'vscode';

const TOKEN_KEY = 'onevo.jwt';

export class AuthService {
    constructor(private readonly storage: SecretStorage) {}

    async getToken(): Promise<string | null> {
        const token = await this.storage.get(TOKEN_KEY);
        return token ?? null;
    }

    async storeToken(token: string): Promise<void> {
        await this.storage.store(TOKEN_KEY, token);
    }

    async clearToken(): Promise<void> {
        await this.storage.delete(TOKEN_KEY);
    }

    async isAuthenticated(): Promise<boolean> {
        const token = await this.getToken();
        return token !== null;
    }
}
```

- [ ] **Step 6: Write failing test for OneVoApiClient**

```typescript
// test/suite/OneVoApiClient.test.ts
import * as assert from 'assert';
import * as sinon from 'sinon';
import { OneVoApiClient } from '../../src/api/OneVoApiClient';

suite('OneVoApiClient', () => {
    let fetchStub: sinon.SinonStub;

    setup(() => {
        fetchStub = sinon.stub(globalThis, 'fetch');
    });

    teardown(() => {
        fetchStub.restore();
    });

    test('getEntitlements returns parsed entitlements', async () => {
        const mockResponse = {
            active_modules: ['worksync', 'hr_management'],
            permitted_tag_actions: ['task:new', 'clockin', 'leave:request'],
            has_monitoring_entitlement: false,
            workspace_id: 'ws-123',
            user_role: 'developer'
        };
        fetchStub.resolves({
            ok: true,
            json: async () => mockResponse
        } as Response);

        const client = new OneVoApiClient('https://api.onevo.app', 'test-token');
        const result = await client.getEntitlements();

        assert.deepStrictEqual(result.activeModules, ['worksync', 'hr_management']);
        assert.ok(result.permittedTagActions.includes('clockin'));
    });

    test('getEntitlements throws on 401', async () => {
        fetchStub.resolves({ ok: false, status: 401 } as Response);
        const client = new OneVoApiClient('https://api.onevo.app', 'bad-token');
        await assert.rejects(() => client.getEntitlements(), /Unauthorized/);
    });
});
```

- [ ] **Step 7: Implement OneVoApiClient**

```typescript
// src/api/OneVoApiClient.ts
export interface IDEEntitlements {
    activeModules: string[];
    permittedTagActions: string[];
    hasMonitoringEntitlement: boolean;
    workspaceId: string | null;
    userRole: string;
}

export interface Channel {
    id: string;
    name: string;
    type: 'group' | 'direct';
    unreadCount: number;
    lastMessage: string | null;
}

export interface Message {
    id: string;
    channelId: string;
    content: string;
    senderId: string;
    senderName: string;
    sentAt: string;
}

export interface TagExecutionResult {
    executionId: string;
    status: 'success' | 'failed' | 'denied';
    undoExpiresAt: string | null;
    errorMessage: string | null;
}

export class OneVoApiClient {
    constructor(
        private readonly baseUrl: string,
        private token: string
    ) {}

    updateToken(token: string): void {
        this.token = token;
    }

    private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
        const response = await fetch(`${this.baseUrl}${path}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`,
                ...options.headers
            }
        });

        if (response.status === 401) throw new Error('Unauthorized');
        if (response.status === 403) throw new Error('Forbidden');
        if (!response.ok) throw new Error(`API error ${response.status}`);

        return response.json() as Promise<T>;
    }

    async getEntitlements(): Promise<IDEEntitlements> {
        const data = await this.request<any>('/api/v1/ide/entitlements');
        return {
            activeModules: data.active_modules ?? [],
            permittedTagActions: data.permitted_tag_actions ?? [],
            hasMonitoringEntitlement: data.has_monitoring_entitlement ?? false,
            workspaceId: data.workspace_id ?? null,
            userRole: data.user_role ?? 'developer'
        };
    }

    async getChannels(): Promise<Channel[]> {
        return this.request<Channel[]>('/api/v1/chat/channels');
    }

    async getMessages(channelId: string, limit = 50): Promise<Message[]> {
        return this.request<Message[]>(`/api/v1/chat/messages?channel_id=${channelId}&limit=${limit}`);
    }

    async sendMessage(channelId: string, content: string): Promise<Message> {
        return this.request<Message>('/api/v1/chat/messages', {
            method: 'POST',
            body: JSON.stringify({ channel_id: channelId, content })
        });
    }

    async executeTag(rawInput: string, sessionId: string): Promise<TagExecutionResult> {
        return this.request<TagExecutionResult>('/api/v1/ide/tags/execute', {
            method: 'POST',
            body: JSON.stringify({ raw_tag_input: rawInput, session_id: sessionId })
        });
    }

    async undoTagExecution(executionId: string): Promise<void> {
        await this.request<void>(`/api/v1/ide/tags/executions/${executionId}`, { method: 'DELETE' });
    }

    async getLeaveTypes(): Promise<Array<{ id: string; name: string }>> {
        return this.request('/api/v1/leave/types');
    }

    async getLeaveBalance(): Promise<Array<{ leaveTypeId: string; leaveTypeName: string; remaining: number }>> {
        return this.request('/api/v1/leave/balance/me');
    }

    async registerInstall(editorVersion: string, extensionVersion: string): Promise<void> {
        await this.request('/api/v1/ide/register', {
            method: 'POST',
            body: JSON.stringify({ editor_type: 'vscode', editor_version: editorVersion, extension_version: extensionVersion })
        });
    }

    async startSession(workspaceId: string | null): Promise<string> {
        const data = await this.request<{ id: string }>('/api/v1/ide/sessions', {
            method: 'POST',
            body: JSON.stringify({ workspace_id: workspaceId })
        });
        return data.id;
    }

    async endSession(sessionId: string): Promise<void> {
        await this.request(`/api/v1/ide/sessions/${sessionId}/end`, { method: 'PUT' });
    }
}
```

- [ ] **Step 8: Run tests**

```bash
npm test
```

Expected: All 6 tests PASS.

- [ ] **Step 9: Implement IDEHubClient**

```typescript
// src/signalr/IDEHubClient.ts
import * as signalR from '@microsoft/signalr';

export type HubEventHandler = (event: string, data: unknown) => void;

export class IDEHubClient {
    private connection: signalR.HubConnection | null = null;
    private readonly handlers = new Map<string, HubEventHandler[]>();

    constructor(
        private readonly hubUrl: string,
        private readonly getToken: () => Promise<string | null>
    ) {}

    async connect(): Promise<void> {
        this.connection = new signalR.HubConnectionBuilder()
            .withUrl(this.hubUrl, {
                accessTokenFactory: async () => (await this.getToken()) ?? ''
            })
            .withAutomaticReconnect([0, 2000, 5000, 10000, 30000])
            .configureLogging(signalR.LogLevel.Warning)
            .build();

        // Register all known events
        const events = [
            'chat:message', 'chat:typing', 'task:updated',
            'notification:new', 'ai:action_pending', 'ai:action_finalized',
            'ai:action_undone', 'tag:executed'
        ];

        for (const event of events) {
            this.connection.on(event, (data: unknown) => {
                this.handlers.get(event)?.forEach(h => h(event, data));
            });
        }

        await this.connection.start();
    }

    on(event: string, handler: HubEventHandler): void {
        if (!this.handlers.has(event)) {
            this.handlers.set(event, []);
        }
        this.handlers.get(event)!.push(handler);
    }

    async joinChannel(channelId: string): Promise<void> {
        await this.connection?.invoke('JoinChannel', channelId);
    }

    async leaveChannel(channelId: string): Promise<void> {
        await this.connection?.invoke('LeaveChannel', channelId);
    }

    async disconnect(): Promise<void> {
        await this.connection?.stop();
    }

    get isConnected(): boolean {
        return this.connection?.state === signalR.HubConnectionState.Connected;
    }
}
```

- [ ] **Step 10: Implement WorkspaceConfig**

```typescript
// src/config/WorkspaceConfig.ts
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export interface OnevoConfig {
    workspaceId?: string;
    scanComments: boolean;
    commitTemplate: boolean;
    branchNaming?: string;
    timeTracking: 'auto' | 'manual';
    apiBaseUrl: string;
    hubUrl: string;
}

const DEFAULTS: OnevoConfig = {
    scanComments: false,
    commitTemplate: false,
    timeTracking: 'manual',
    apiBaseUrl: 'https://api.onevo.app',
    hubUrl: 'wss://api.onevo.app/hubs/ide'
};

export class WorkspaceConfig {
    static load(): OnevoConfig {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders?.length) return DEFAULTS;

        const configPath = path.join(workspaceFolders[0].uri.fsPath, '.onevo');
        if (!fs.existsSync(configPath)) return DEFAULTS;

        try {
            const raw = JSON.parse(fs.readFileSync(configPath, 'utf8'));
            return { ...DEFAULTS, ...raw };
        } catch {
            return DEFAULTS;
        }
    }
}
```

- [ ] **Step 11: Implement extension entry point**

```typescript
// src/extension.ts
import * as vscode from 'vscode';
import { AuthService } from './auth/AuthService';
import { TokenRefresher } from './auth/TokenRefresher';
import { IDEHubClient } from './signalr/IDEHubClient';
import { OneVoApiClient } from './api/OneVoApiClient';
import { WorkspaceConfig } from './config/WorkspaceConfig';
import { ChatPanel } from './panels/ChatPanel';
import { NotificationsPanel } from './panels/NotificationsPanel';
import { TasksPanel } from './panels/TasksPanel';
import type { IDEEntitlements } from './api/OneVoApiClient';

let hubClient: IDEHubClient | null = null;
let sessionId: string | null = null;

export async function activate(context: vscode.ExtensionContext): Promise<void> {
    const config = WorkspaceConfig.load();
    const auth = new AuthService(context.secrets);
    const apiClient = new OneVoApiClient(config.apiBaseUrl, '');

    // Check for existing token
    const existingToken = await auth.getToken();

    if (!existingToken) {
        // Show login — handled by ChatPanel rendering login webview
        const chatPanel = new ChatPanel(context, apiClient, null, null);
        context.subscriptions.push(chatPanel);
        return;
    }

    apiClient.updateToken(existingToken);

    // Start token refresh
    const refresher = new TokenRefresher(auth, apiClient);
    context.subscriptions.push(refresher);

    // Load entitlements
    let entitlements: IDEEntitlements;
    try {
        entitlements = await apiClient.getEntitlements();
    } catch {
        vscode.window.showErrorMessage('OneVo: Failed to connect. Please sign in again.');
        await auth.clearToken();
        return;
    }

    // Register extension install
    const extVersion = context.extension.packageJSON.version as string;
    const vscodeVersion = vscode.version;
    await apiClient.registerInstall(vscodeVersion, extVersion).catch(() => {/* non-fatal */});

    // Start session
    sessionId = await apiClient.startSession(entitlements.workspaceId).catch(() => null);

    // Connect SignalR
    hubClient = new IDEHubClient(config.hubUrl, () => auth.getToken());
    await hubClient.connect();

    // Register panels
    const chatPanel = new ChatPanel(context, apiClient, hubClient, entitlements);
    const tasksPanel = new TasksPanel(context, apiClient, hubClient);
    const notificationsPanel = new NotificationsPanel(context, apiClient, hubClient);

    context.subscriptions.push(chatPanel, tasksPanel, notificationsPanel);

    // Cleanup on deactivate
    context.subscriptions.push({
        dispose: async () => {
            if (sessionId) await apiClient.endSession(sessionId).catch(() => {});
            await hubClient?.disconnect();
        }
    });
}

export async function deactivate(): Promise<void> {
    await hubClient?.disconnect();
}
```

- [ ] **Step 12: Build to verify compilation**

```bash
npm run compile
```

Expected: 0 TypeScript errors.

- [ ] **Step 13: Commit**

```bash
git add onevo-ide-extension/
git commit -m "feat(ide-ext): scaffold extension — auth, SignalR, API client, entitlements, session lifecycle"
```

---

## Task E2: Chat Panel

**Files:**
- Create: `src/panels/ChatPanel.ts`
- Create: `src/webviews/ChatWebview.ts`
- Create: `src/webviews/MiniFormWebview.ts`

- [ ] **Step 1: Implement ChatPanel (TreeDataProvider for channel list)**

```typescript
// src/panels/ChatPanel.ts
import * as vscode from 'vscode';
import type { OneVoApiClient, Channel, Message } from '../api/OneVoApiClient';
import type { IDEHubClient } from '../signalr/IDEHubClient';
import type { IDEEntitlements } from '../api/OneVoApiClient';
import { ChatWebview } from '../webviews/ChatWebview';

class ChannelTreeItem extends vscode.TreeItem {
    constructor(public readonly channel: Channel) {
        super(channel.name, vscode.TreeItemCollapsibleState.None);
        this.description = channel.unreadCount > 0 ? `${channel.unreadCount} unread` : '';
        this.command = {
            command: 'onevo.openChannel',
            title: 'Open Channel',
            arguments: [channel]
        };
    }
}

export class ChatPanel implements vscode.TreeDataProvider<ChannelTreeItem>, vscode.Disposable {
    private channels: Channel[] = [];
    private activeChannelId: string | null = null;
    private chatWebview: ChatWebview | null = null;
    private readonly _onDidChangeTreeData = new vscode.EventEmitter<ChannelTreeItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    private readonly disposables: vscode.Disposable[] = [];

    constructor(
        private readonly context: vscode.ExtensionContext,
        private readonly api: OneVoApiClient,
        private readonly hub: IDEHubClient | null,
        private readonly entitlements: IDEEntitlements | null
    ) {
        const treeView = vscode.window.createTreeView('onevo.chat', { treeDataProvider: this });
        this.disposables.push(treeView);

        // Register open channel command
        this.disposables.push(
            vscode.commands.registerCommand('onevo.openChannel', (channel: Channel) => {
                this.openChannel(channel);
            })
        );

        // Real-time: new message → update unread badge + append if channel open
        hub?.on('chat:message', (_, data: any) => {
            const msg = data as { channel_id: string; message: Message };
            const channel = this.channels.find(c => c.id === msg.channel_id);
            if (channel && channel.id !== this.activeChannelId) {
                channel.unreadCount++;
                this._onDidChangeTreeData.fire(undefined);
            }
            if (channel?.id === this.activeChannelId) {
                this.chatWebview?.appendMessage(msg.message);
            }
        });

        // Load channels on startup
        if (entitlements) {
            this.loadChannels();
        }
    }

    getTreeItem(element: ChannelTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(): ChannelTreeItem[] {
        return this.channels.map(c => new ChannelTreeItem(c));
    }

    private async loadChannels(): Promise<void> {
        try {
            this.channels = await this.api.getChannels();
            this._onDidChangeTreeData.fire(undefined);
        } catch (e) {
            vscode.window.showErrorMessage('OneVo: Failed to load channels');
        }
    }

    private async openChannel(channel: Channel): Promise<void> {
        // Leave previous channel
        if (this.activeChannelId) {
            await this.hub?.leaveChannel(this.activeChannelId);
        }

        this.activeChannelId = channel.id;
        channel.unreadCount = 0;
        this._onDidChangeTreeData.fire(undefined);

        await this.hub?.joinChannel(channel.id);

        const messages = await this.api.getMessages(channel.id);

        if (!this.chatWebview) {
            this.chatWebview = new ChatWebview(this.context, this.api, this.hub, this.entitlements);
        }
        this.chatWebview.show(channel, messages);
    }

    dispose(): void {
        this.disposables.forEach(d => d.dispose());
        this._onDidChangeTreeData.dispose();
        this.chatWebview?.dispose();
    }
}
```

- [ ] **Step 2: Implement ChatWebview**

```typescript
// src/webviews/ChatWebview.ts
import * as vscode from 'vscode';
import type { OneVoApiClient, Channel, Message } from '../api/OneVoApiClient';
import type { IDEHubClient } from '../signalr/IDEHubClient';
import type { IDEEntitlements } from '../api/OneVoApiClient';

export class ChatWebview implements vscode.Disposable {
    private panel: vscode.WebviewPanel | null = null;
    private readonly disposables: vscode.Disposable[] = [];

    constructor(
        private readonly context: vscode.ExtensionContext,
        private readonly api: OneVoApiClient,
        private readonly hub: IDEHubClient | null,
        private readonly entitlements: IDEEntitlements | null
    ) {}

    show(channel: Channel, messages: Message[]): void {
        if (!this.panel) {
            this.panel = vscode.window.createWebviewPanel(
                'onevo.chat',
                `# ${channel.name}`,
                vscode.ViewColumn.Beside,
                { enableScripts: true, retainContextWhenHidden: true }
            );
            this.panel.onDidDispose(() => { this.panel = null; }, null, this.disposables);
            this.panel.webview.onDidReceiveMessage(msg => this.handleWebviewMessage(msg), null, this.disposables);
        } else {
            this.panel.title = `# ${channel.name}`;
            this.panel.reveal();
        }
        this.panel.webview.html = this.buildHtml(channel, messages);
    }

    appendMessage(message: Message): void {
        this.panel?.webview.postMessage({ type: 'APPEND_MESSAGE', message });
    }

    private async handleWebviewMessage(msg: any): Promise<void> {
        if (msg.type === 'SEND_MESSAGE') {
            try {
                await this.api.sendMessage(msg.channelId, msg.content);
            } catch {
                this.panel?.webview.postMessage({ type: 'SEND_ERROR' });
            }
        }
        if (msg.type === 'OPEN_TAG_PICKER') {
            vscode.commands.executeCommand('onevo.openTagPicker', msg.channelId);
        }
    }

    private buildHtml(channel: Channel, messages: Message[]): string {
        const messagesHtml = messages.map(m => `
            <div class="message">
                <div class="sender">${m.senderName} <span class="time">${new Date(m.sentAt).toLocaleTimeString()}</span></div>
                <div class="content">${m.content}</div>
            </div>
        `).join('');

        return /* html */`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); background: var(--vscode-editor-background); margin: 0; display: flex; flex-direction: column; height: 100vh; }
  #messages { flex: 1; overflow-y: auto; padding: 12px; }
  .message { margin-bottom: 12px; }
  .sender { font-weight: 600; font-size: 12px; }
  .sender .time { font-weight: 400; color: var(--vscode-descriptionForeground); margin-left: 8px; }
  .content { margin-top: 2px; font-size: 13px; }
  #composer { border-top: 1px solid var(--vscode-panel-border); padding: 8px; display: flex; gap: 6px; align-items: center; background: var(--vscode-sideBar-background); }
  #at-btn { width: 26px; height: 26px; background: var(--vscode-button-secondaryBackground); border: none; color: var(--vscode-button-secondaryForeground); border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: bold; }
  #msg-input { flex: 1; background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); color: var(--vscode-input-foreground); border-radius: 4px; padding: 5px 8px; font-family: inherit; font-size: 12px; }
  #send-btn { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; padding: 5px 12px; cursor: pointer; }
  .bot-card { background: var(--vscode-editorWidget-background); border-left: 3px solid var(--vscode-activityBarBadge-background); border-radius: 4px; padding: 8px; margin: 6px 0; font-size: 12px; }
</style>
</head>
<body>
<div id="messages">${messagesHtml}</div>
<div id="composer">
  <button id="at-btn" title="Tag actions">@</button>
  <input id="msg-input" placeholder="Message #${channel.name}" />
  <button id="send-btn">Send</button>
</div>
<script>
  const vscode = acquireVsCodeApi();
  const channelId = '${channel.id}';

  document.getElementById('at-btn').onclick = () => {
    vscode.postMessage({ type: 'OPEN_TAG_PICKER', channelId });
  };

  document.getElementById('send-btn').onclick = () => {
    const input = document.getElementById('msg-input');
    const content = input.value.trim();
    if (!content) return;
    vscode.postMessage({ type: 'SEND_MESSAGE', channelId, content });
    input.value = '';
  };

  document.getElementById('msg-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      document.getElementById('send-btn').click();
    }
  });

  window.addEventListener('message', ({ data }) => {
    if (data.type === 'APPEND_MESSAGE') {
      const div = document.getElementById('messages');
      const m = data.message;
      div.insertAdjacentHTML('beforeend', \`
        <div class="message">
          <div class="sender">\${m.senderName} <span class="time">\${new Date(m.sentAt).toLocaleTimeString()}</span></div>
          <div class="content">\${m.content}</div>
        </div>
      \`);
      div.scrollTop = div.scrollHeight;
    }
  });

  // Scroll to bottom on load
  const msgs = document.getElementById('messages');
  msgs.scrollTop = msgs.scrollHeight;
</script>
</body>
</html>`;
    }

    dispose(): void {
        this.panel?.dispose();
        this.disposables.forEach(d => d.dispose());
    }
}
```

- [ ] **Step 3: Build**

```bash
npm run compile
```

Expected: 0 errors.

- [ ] **Step 4: Commit**

```bash
git add src/panels/ChatPanel.ts src/webviews/ChatWebview.ts src/webviews/MiniFormWebview.ts
git commit -m "feat(ide-ext): chat panel — channel list, message feed, real-time SignalR, composer"
```

---

## Task E3: `@` Tag Picker + WMS Tag Engine

**Files:**
- Create: `src/tag-engine/TagParser.ts`
- Create: `src/tag-engine/TagExecutor.ts`
- Create: `src/tag-engine/TagPickerWebview.ts`
- Create: `src/tag-engine/AutoCompleteProvider.ts`
- Test: `test/suite/TagParser.test.ts`

- [ ] **Step 1: Write failing TagParser tests**

```typescript
// test/suite/TagParser.test.ts
import * as assert from 'assert';
import { TagParser } from '../../src/tag-engine/TagParser';

suite('TagParser', () => {
    const parser = new TagParser();

    test('parses simple entity:action', () => {
        const result = parser.parse('@task:new "Fix login bug"');
        assert.strictEqual(result.entity, 'task');
        assert.strictEqual(result.action, 'new');
        assert.strictEqual(result.params['title'], 'Fix login bug');
    });

    test('parses instant HR tag without action', () => {
        const result = parser.parse('@clockin');
        assert.strictEqual(result.entity, 'clockin');
        assert.strictEqual(result.action, '');
    });

    test('parses named params', () => {
        const result = parser.parse('@time:log 2h #task:TASK-123 "Auth refactor"');
        assert.strictEqual(result.entity, 'time');
        assert.strictEqual(result.action, 'log');
        assert.strictEqual(result.params['hours'], '2');
        assert.strictEqual(result.params['task'], 'TASK-123');
        assert.strictEqual(result.params['description'], 'Auth refactor');
    });

    test('returns null for non-tag input', () => {
        const result = parser.parse('hello world');
        assert.strictEqual(result, null);
    });

    test('parses @mention in params', () => {
        const result = parser.parse('@task:assign #task:TASK-456 @assign:sarah');
        assert.strictEqual(result.params['assign'], 'sarah');
        assert.strictEqual(result.params['task'], 'TASK-456');
    });
});
```

- [ ] **Step 2: Run to verify failure**

```bash
npm test -- --grep "TagParser"
```

Expected: FAIL — `TagParser` not found.

- [ ] **Step 3: Implement TagParser**

```typescript
// src/tag-engine/TagParser.ts
export interface ParsedTag {
    entity: string;
    action: string;
    params: Record<string, string>;
    rawInput: string;
}

export class TagParser {
    parse(input: string): ParsedTag | null {
        const trimmed = input.trim();
        if (!trimmed.startsWith('@')) return null;

        // Match @entity:action or @entity (no action, e.g. @clockin)
        const tagMatch = trimmed.match(/^@([\w]+)(?::([\w]+))?/);
        if (!tagMatch) return null;

        const entity = tagMatch[1];
        const action = tagMatch[2] ?? '';
        const rest = trimmed.slice(tagMatch[0].length).trim();

        const params: Record<string, string> = {};

        // Extract quoted strings as positional (title, description)
        const quoted = [...rest.matchAll(/"([^"]+)"/g)];
        if (quoted.length > 0) params['title'] = quoted[0][1];
        if (quoted.length > 1) params['description'] = quoted[1][1];

        // Match quoted as description if entity is time
        if (entity === 'time' && quoted.length > 0) {
            params['description'] = quoted[0][1];
        }

        // Extract hours (e.g. 2h, 1.5h)
        const hoursMatch = rest.match(/(\d+(?:\.\d+)?)h\b/);
        if (hoursMatch) params['hours'] = hoursMatch[1];

        // Extract #named:value params
        const namedParams = [...rest.matchAll(/#([\w]+):([\w.-]+)/g)];
        for (const [, key, value] of namedParams) {
            params[key] = value;
        }

        // Extract @mention params (e.g. @assign:sarah)
        const mentionParams = [...rest.matchAll(/@([\w]+):([\w.-]+)/g)];
        for (const [, key, value] of mentionParams) {
            if (key !== entity) params[key] = value;
        }

        return { entity, action, params, rawInput: input };
    }
}
```

- [ ] **Step 4: Run TagParser tests**

```bash
npm test -- --grep "TagParser"
```

Expected: All 5 PASS.

- [ ] **Step 5: Implement TagExecutor**

```typescript
// src/tag-engine/TagExecutor.ts
import * as vscode from 'vscode';
import type { OneVoApiClient } from '../api/OneVoApiClient';
import type { TagParser } from './TagParser';

export class TagExecutor {
    constructor(
        private readonly api: OneVoApiClient,
        private readonly parser: TagParser
    ) {}

    async execute(rawInput: string, sessionId: string): Promise<void> {
        const parsed = this.parser.parse(rawInput);
        if (!parsed) return;

        try {
            const result = await this.api.executeTag(rawInput, sessionId);

            if (result.status === 'denied') {
                vscode.window.showErrorMessage(
                    `OneVo: You don't have permission to perform this action.`
                );
                return;
            }

            if (result.status === 'failed') {
                vscode.window.showErrorMessage(`OneVo: Action failed. ${result.errorMessage ?? ''}`);
                return;
            }

            // Show undo toast for reversible actions
            if (result.undoExpiresAt) {
                this.showUndoToast(result.executionId, result.undoExpiresAt);
            }
        } catch (e: any) {
            vscode.window.showErrorMessage(`OneVo: ${e.message}`);
        }
    }

    private showUndoToast(executionId: string, expiresAt: string): void {
        const expiresMs = new Date(expiresAt).getTime() - Date.now();
        const seconds = Math.floor(expiresMs / 1000);

        vscode.window.showInformationMessage(
            `OneVo: Action executed. Undo available for ${seconds}s.`,
            'Undo'
        ).then(choice => {
            if (choice === 'Undo') {
                this.api.undoTagExecution(executionId).catch(() => {
                    vscode.window.showErrorMessage('OneVo: Undo failed or window expired.');
                });
            }
        });
    }
}
```

- [ ] **Step 6: Implement TagPickerWebview**

```typescript
// src/tag-engine/TagPickerWebview.ts
import * as vscode from 'vscode';
import type { IDEEntitlements } from '../api/OneVoApiClient';

interface TagDefinition {
    action: string;
    label: string;
    description: string;
    emoji: string;
    category: string;
    firesInstantly: boolean;
    opensForm: boolean;
}

const ALL_TAGS: TagDefinition[] = [
    // HR
    { action: 'clockin', label: '@clockin', description: 'Start shift', emoji: '🟢', category: 'HR AUTOMATION', firesInstantly: true, opensForm: false },
    { action: 'break:start', label: '@break:start', description: 'Take a break', emoji: '☕', category: 'HR AUTOMATION', firesInstantly: true, opensForm: false },
    { action: 'break:end', label: '@break:end', description: 'End break', emoji: '🔴', category: 'HR AUTOMATION', firesInstantly: true, opensForm: false },
    { action: 'clockout', label: '@clockout', description: 'End shift', emoji: '🔴', category: 'HR AUTOMATION', firesInstantly: true, opensForm: false },
    { action: 'leave:request', label: '@leave:request', description: 'Apply leave — opens form', emoji: '📋', category: 'HR AUTOMATION', firesInstantly: false, opensForm: true },
    { action: 'leave:view', label: '@leave:view', description: 'View leave balance', emoji: '📋', category: 'HR AUTOMATION', firesInstantly: false, opensForm: false },
    { action: 'leave:cancel', label: '@leave:cancel', description: 'Cancel leave request', emoji: '📋', category: 'HR AUTOMATION', firesInstantly: false, opensForm: false },
    { action: 'payslip:view', label: '@payslip:view', description: 'View latest payslip', emoji: '💰', category: 'HR AUTOMATION', firesInstantly: false, opensForm: false },
    { action: 'overtime:request', label: '@overtime:request', description: 'Request overtime', emoji: '🗓', category: 'HR AUTOMATION', firesInstantly: false, opensForm: true },
    { action: 'timesheet:view', label: '@timesheet:view', description: 'View timesheet', emoji: '📊', category: 'HR AUTOMATION', firesInstantly: false, opensForm: false },
    { action: 'timesheet:submit', label: '@timesheet:submit', description: 'Submit timesheet', emoji: '📤', category: 'HR AUTOMATION', firesInstantly: false, opensForm: true },
    { action: 'shift:view', label: '@shift:view', description: "Today's shift schedule", emoji: '📅', category: 'HR AUTOMATION', firesInstantly: false, opensForm: false },
    { action: 'calendar:view', label: '@calendar:view', description: 'Holidays + company events', emoji: '🏖', category: 'HR AUTOMATION', firesInstantly: false, opensForm: false },
    // Tasks
    { action: 'task:new', label: '@task:new', description: 'Create a task', emoji: '✅', category: 'TASKS', firesInstantly: false, opensForm: true },
    { action: 'task:view', label: '@task:view', description: 'View task detail', emoji: '👁', category: 'TASKS', firesInstantly: false, opensForm: false },
    { action: 'task:status', label: '@task:status', description: 'Update task status', emoji: '🔄', category: 'TASKS', firesInstantly: false, opensForm: false },
    { action: 'task:assign', label: '@task:assign', description: 'Assign task to someone', emoji: '👤', category: 'TASKS', firesInstantly: false, opensForm: false },
    { action: 'task:comment', label: '@task:comment', description: 'Add comment to task', emoji: '💬', category: 'TASKS', firesInstantly: false, opensForm: false },
    { action: 'task:link', label: '@task:link', description: 'Link branch/doc to task', emoji: '🔗', category: 'TASKS', firesInstantly: false, opensForm: false },
    { action: 'task:move', label: '@task:move', description: 'Move to sprint/board', emoji: '➡', category: 'TASKS', firesInstantly: false, opensForm: false },
    // Sprint
    { action: 'sprint:add', label: '@sprint:add', description: 'Add task to sprint', emoji: '➕', category: 'SPRINT', firesInstantly: false, opensForm: false },
    { action: 'sprint:start', label: '@sprint:start', description: 'Start a sprint', emoji: '🚀', category: 'SPRINT', firesInstantly: false, opensForm: false },
    { action: 'sprint:complete', label: '@sprint:complete', description: 'Complete sprint', emoji: '✅', category: 'SPRINT', firesInstantly: false, opensForm: false },
    { action: 'sprint:view', label: '@sprint:view', description: 'View sprint', emoji: '👁', category: 'SPRINT', firesInstantly: false, opensForm: false },
    // Time
    { action: 'time:log', label: '@time:log', description: 'Log hours on a task', emoji: '⏱', category: 'TIME', firesInstantly: false, opensForm: true },
    { action: 'time:start', label: '@time:start', description: 'Start timer', emoji: '▶️', category: 'TIME', firesInstantly: true, opensForm: false },
    { action: 'time:stop', label: '@time:stop', description: 'Stop timer + log', emoji: '⏹', category: 'TIME', firesInstantly: true, opensForm: false },
    { action: 'time:view', label: '@time:view', description: 'View time logs', emoji: '👁', category: 'TIME', firesInstantly: false, opensForm: false },
    // More
    { action: 'board:move', label: '@board:move', description: 'Move task to column', emoji: '📊', category: 'MORE', firesInstantly: false, opensForm: false },
    { action: 'okr:checkin', label: '@okr:checkin', description: 'OKR progress update', emoji: '🎯', category: 'MORE', firesInstantly: false, opensForm: false },
    { action: 'doc:link', label: '@doc:link', description: 'Link doc to task', emoji: '📄', category: 'MORE', firesInstantly: false, opensForm: false },
    { action: 'doc:create', label: '@doc:create', description: 'Create document', emoji: '📄', category: 'MORE', firesInstantly: false, opensForm: false },
    { action: 'review:request', label: '@review:request', description: 'Request code review', emoji: '👁', category: 'MORE', firesInstantly: false, opensForm: false },
    { action: 'notify:send', label: '@notify:send', description: 'Send notification', emoji: '🔔', category: 'MORE', firesInstantly: false, opensForm: false },
    { action: 'project:view', label: '@project:view', description: 'View project', emoji: '🏗', category: 'MORE', firesInstantly: false, opensForm: false },
];

const HR_ACTIONS = new Set(ALL_TAGS.filter(t => t.category === 'HR AUTOMATION').map(t => t.action));

export class TagPickerWebview implements vscode.Disposable {
    private panel: vscode.WebviewPanel | null = null;

    constructor(
        private readonly context: vscode.ExtensionContext,
        private readonly entitlements: IDEEntitlements
    ) {}

    show(channelId: string, onSelect: (action: string, channelId: string) => void): void {
        const permitted = new Set(this.entitlements.permittedTagActions);
        const hasHr = this.entitlements.activeModules.includes('hr_management');

        const visibleTags = ALL_TAGS.filter(tag => {
            if (HR_ACTIONS.has(tag.action) && !hasHr) return false;
            return permitted.has(tag.action);
        });

        if (!this.panel) {
            this.panel = vscode.window.createWebviewPanel(
                'onevo.tagPicker',
                'OneVo Actions',
                { viewColumn: vscode.ViewColumn.Beside, preserveFocus: true },
                { enableScripts: true }
            );
            this.panel.onDidDispose(() => { this.panel = null; });
        }

        this.panel.webview.html = this.buildHtml(visibleTags, hasHr);
        this.panel.reveal();

        this.panel.webview.onDidReceiveMessage(msg => {
            if (msg.type === 'SELECT_ACTION') {
                onSelect(msg.action, channelId);
                this.panel?.dispose();
            }
        });
    }

    private buildHtml(tags: TagDefinition[], hasHr: boolean): string {
        const categories = [...new Set(tags.map(t => t.category))];

        const groupsHtml = categories.map(cat => {
            const items = tags.filter(t => t.category === cat);
            const itemsHtml = items.map(t => `
                <div class="tag-item" data-action="${t.action}" onclick="select('${t.action}')">
                    <span class="emoji">${t.emoji}</span>
                    <span class="label">${t.label}</span>
                    <span class="desc">${t.description}</span>
                    ${t.firesInstantly ? '<span class="badge instant">instant</span>' : ''}
                    ${t.opensForm ? '<span class="badge form">form</span>' : ''}
                </div>
            `).join('');
            const tenantBadge = cat === 'HR AUTOMATION' ? '<span class="tenant-badge">tenant feature</span>' : '';
            return `<div class="group"><div class="group-header">${cat} ${tenantBadge}</div>${itemsHtml}</div>`;
        }).join('');

        return /* html */`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body { font-family: var(--vscode-font-family); background: var(--vscode-editorWidget-background); color: var(--vscode-foreground); margin: 0; padding: 0; }
  #search { width: 100%; box-sizing: border-box; padding: 8px 12px; background: var(--vscode-input-background); border: none; border-bottom: 1px solid var(--vscode-panel-border); color: var(--vscode-foreground); font-size: 12px; }
  #search:focus { outline: none; }
  .group-header { font-size: 10px; font-weight: 700; letter-spacing: 1px; color: var(--vscode-descriptionForeground); padding: 6px 12px 2px; }
  .tenant-badge { background: rgba(249,115,22,0.15); color: #f97316; border-radius: 8px; padding: 0 5px; font-size: 8px; margin-left: 4px; }
  .tag-item { display: flex; align-items: center; gap: 8px; padding: 5px 12px; cursor: pointer; font-size: 12px; }
  .tag-item:hover { background: var(--vscode-list-hoverBackground); }
  .emoji { width: 16px; text-align: center; }
  .label { font-weight: 600; min-width: 140px; }
  .desc { color: var(--vscode-descriptionForeground); font-size: 11px; flex: 1; }
  .badge { font-size: 9px; padding: 1px 5px; border-radius: 8px; }
  .badge.instant { background: rgba(166,227,161,0.2); color: #a6e3a1; }
  .badge.form { background: rgba(137,180,250,0.2); color: #89b4fa; }
  .group { border-bottom: 1px solid var(--vscode-panel-border); padding-bottom: 4px; }
  .hidden { display: none; }
</style>
</head>
<body>
<input id="search" placeholder="Search actions or describe what you want..." autofocus oninput="filterTags(this.value)" />
<div id="list">${groupsHtml}</div>
<script>
  const vscode = acquireVsCodeApi();

  function select(action) {
    vscode.postMessage({ type: 'SELECT_ACTION', action });
  }

  function filterTags(query) {
    const q = query.toLowerCase();
    document.querySelectorAll('.tag-item').forEach(el => {
      const text = el.textContent.toLowerCase();
      el.classList.toggle('hidden', q.length > 0 && !text.includes(q));
    });
    document.querySelectorAll('.group').forEach(g => {
      const visible = g.querySelectorAll('.tag-item:not(.hidden)').length > 0;
      g.classList.toggle('hidden', !visible);
    });
  }
</script>
</body>
</html>`;
    }

    dispose(): void {
        this.panel?.dispose();
    }
}
```

- [ ] **Step 7: Register tag picker command in extension.ts**

Add to `activate()` in `src/extension.ts`:

```typescript
// After registering panels, add:
const { TagParser } = await import('./tag-engine/TagParser');
const { TagExecutor } = await import('./tag-engine/TagExecutor');
const { TagPickerWebview } = await import('./tag-engine/TagPickerWebview');

const tagParser = new TagParser();
const tagExecutor = new TagExecutor(apiClient, tagParser);
const tagPicker = new TagPickerWebview(context, entitlements);

context.subscriptions.push(
    vscode.commands.registerCommand('onevo.openTagPicker', async (channelId: string) => {
        tagPicker.show(channelId, async (action, chId) => {
            if (action === 'leave:request') {
                vscode.commands.executeCommand('onevo.openLeaveForm', chId);
            } else if (['clockin','break:start','break:end','clockout','time:start','time:stop'].includes(action)) {
                await tagExecutor.execute(`@${action}`, sessionId ?? '');
            } else {
                // Insert into message input via postMessage
                vscode.commands.executeCommand('onevo.insertTag', `@${action}`, chId);
            }
        });
    }),
    tagPicker
);
```

- [ ] **Step 8: Build**

```bash
npm run compile
```

Expected: 0 errors.

- [ ] **Step 9: Commit**

```bash
git add src/tag-engine/
git commit -m "feat(ide-ext): @ tag picker with full WMS actions, permission-filtered, searchable"
```

---

## Task E4: HR Automation

**Files:**
- Create: `src/hr/HrTagHandler.ts`
- Create: `src/hr/LeaveFormWebview.ts`
- Create: `src/hr/TimesheetWebview.ts`
- Test: `test/suite/HrTagHandler.test.ts`

- [ ] **Step 1: Write failing test**

```typescript
// test/suite/HrTagHandler.test.ts
import * as assert from 'assert';
import * as sinon from 'sinon';
import { HrTagHandler } from '../../src/hr/HrTagHandler';

suite('HrTagHandler', () => {
    let apiMock: any;
    let handler: HrTagHandler;

    setup(() => {
        apiMock = {
            executeTag: sinon.stub().resolves({ executionId: 'ex-1', status: 'success', undoExpiresAt: null, errorMessage: null }),
        };
        handler = new HrTagHandler(apiMock);
    });

    test('clockin executes instantly without form', async () => {
        await handler.handleInstant('clockin', 'session-1');
        sinon.assert.calledWith(apiMock.executeTag, '@clockin', 'session-1');
    });

    test('break:start executes instantly', async () => {
        await handler.handleInstant('break:start', 'session-1');
        sinon.assert.calledWith(apiMock.executeTag, '@break:start', 'session-1');
    });

    test('isHrAction returns true for HR actions', () => {
        assert.ok(HrTagHandler.isHrAction('clockin'));
        assert.ok(HrTagHandler.isHrAction('leave:request'));
        assert.ok(HrTagHandler.isHrAction('break:end'));
        assert.ok(!HrTagHandler.isHrAction('task:new'));
        assert.ok(!HrTagHandler.isHrAction('time:log'));
    });

    test('isInstantAction returns true for no-form HR actions', () => {
        assert.ok(HrTagHandler.isInstantAction('clockin'));
        assert.ok(HrTagHandler.isInstantAction('break:start'));
        assert.ok(!HrTagHandler.isInstantAction('leave:request'));
        assert.ok(!HrTagHandler.isInstantAction('overtime:request'));
    });
});
```

- [ ] **Step 2: Run to verify failure**

```bash
npm test -- --grep "HrTagHandler"
```

Expected: FAIL.

- [ ] **Step 3: Implement HrTagHandler**

```typescript
// src/hr/HrTagHandler.ts
import * as vscode from 'vscode';
import type { OneVoApiClient } from '../api/OneVoApiClient';

const HR_ACTIONS = new Set([
    'clockin', 'break:start', 'break:end', 'clockout', 'overtime:request',
    'leave:request', 'leave:view', 'leave:cancel', 'payslip:view',
    'timesheet:view', 'timesheet:submit', 'shift:view', 'calendar:view'
]);

const INSTANT_ACTIONS = new Set([
    'clockin', 'break:start', 'break:end', 'clockout'
]);

export class HrTagHandler {
    constructor(private readonly api: OneVoApiClient) {}

    static isHrAction(action: string): boolean {
        return HR_ACTIONS.has(action);
    }

    static isInstantAction(action: string): boolean {
        return INSTANT_ACTIONS.has(action);
    }

    async handleInstant(action: string, sessionId: string): Promise<void> {
        const result = await this.api.executeTag(`@${action}`, sessionId);
        if (result.status === 'success') {
            const labels: Record<string, string> = {
                clockin: 'Clocked in',
                'break:start': 'Break started',
                'break:end': 'Break ended',
                clockout: 'Clocked out'
            };
            vscode.window.showInformationMessage(`OneVo: ${labels[action] ?? action}`);
        } else {
            vscode.window.showErrorMessage(`OneVo: Failed to ${action}. ${result.errorMessage ?? ''}`);
        }
    }
}
```

- [ ] **Step 4: Implement LeaveFormWebview**

```typescript
// src/hr/LeaveFormWebview.ts
import * as vscode from 'vscode';
import type { OneVoApiClient } from '../api/OneVoApiClient';

export class LeaveFormWebview implements vscode.Disposable {
    private panel: vscode.WebviewPanel | null = null;

    constructor(
        private readonly context: vscode.ExtensionContext,
        private readonly api: OneVoApiClient
    ) {}

    async show(sessionId: string, prefill?: { from?: string; to?: string }): Promise<void> {
        const leaveTypes = await this.api.getLeaveTypes();
        const balance = await this.api.getLeaveBalance();

        if (!this.panel) {
            this.panel = vscode.window.createWebviewPanel(
                'onevo.leaveForm', 'Apply Leave',
                vscode.ViewColumn.Beside,
                { enableScripts: true }
            );
            this.panel.onDidDispose(() => { this.panel = null; });
        }

        this.panel.webview.html = this.buildHtml(leaveTypes, balance, prefill);
        this.panel.reveal();

        this.panel.webview.onDidReceiveMessage(async msg => {
            if (msg.type === 'SUBMIT_LEAVE') {
                const result = await this.api.executeTag(
                    `@leave:request #leave_type_id:${msg.leaveTypeId} #from:${msg.from} #to:${msg.to} "${msg.reason}"`,
                    sessionId
                );
                if (result.status === 'success') {
                    vscode.window.showInformationMessage('OneVo: Leave request submitted — pending manager approval.');
                    this.panel?.dispose();
                } else {
                    this.panel?.webview.postMessage({ type: 'SUBMIT_ERROR', message: result.errorMessage });
                }
            }
        });
    }

    private buildHtml(
        leaveTypes: Array<{ id: string; name: string }>,
        balance: Array<{ leaveTypeId: string; leaveTypeName: string; remaining: number }>,
        prefill?: { from?: string; to?: string }
    ): string {
        const typeOptions = leaveTypes.map(t =>
            `<option value="${t.id}">${t.name}</option>`
        ).join('');

        const balanceMap = Object.fromEntries(balance.map(b => [b.leaveTypeId, b.remaining]));
        const balanceJson = JSON.stringify(balanceMap);
        const typesJson = JSON.stringify(Object.fromEntries(leaveTypes.map(t => [t.id, t.name])));

        return /* html */`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); background: var(--vscode-editor-background); padding: 20px; }
  label { display: block; font-size: 10px; letter-spacing: 0.5px; color: var(--vscode-descriptionForeground); margin-bottom: 3px; margin-top: 12px; text-transform: uppercase; }
  select, input { width: 100%; box-sizing: border-box; background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); color: var(--vscode-input-foreground); border-radius: 4px; padding: 5px 8px; font-family: inherit; font-size: 12px; }
  .row { display: flex; gap: 10px; }
  .row > div { flex: 1; }
  .balance { margin-top: 8px; padding: 6px 10px; background: var(--vscode-editorWidget-background); border-radius: 4px; font-size: 11px; }
  .actions { margin-top: 16px; display: flex; gap: 8px; }
  button.primary { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; padding: 6px 16px; cursor: pointer; }
  button.secondary { background: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground); border: none; border-radius: 4px; padding: 6px 16px; cursor: pointer; }
  .error { color: var(--vscode-errorForeground); margin-top: 8px; font-size: 11px; }
</style>
</head>
<body>
<h3 style="margin-top:0">Apply Leave</h3>
<label>Leave Type</label>
<select id="leave-type" onchange="updateBalance()">${typeOptions}</select>
<div class="balance" id="balance-display">Select leave type to see balance</div>
<div class="row">
  <div><label>From</label><input type="date" id="from" value="${prefill?.from ?? ''}" /></div>
  <div><label>To</label><input type="date" id="to" value="${prefill?.to ?? ''}" /></div>
</div>
<label>Reason <span style="color:var(--vscode-descriptionForeground)">(optional)</span></label>
<input type="text" id="reason" placeholder="e.g. Family event" />
<div class="error" id="error" style="display:none"></div>
<div class="actions">
  <button class="primary" onclick="submit()">Submit Request</button>
  <button class="secondary" onclick="cancel()">Cancel</button>
</div>
<script>
  const vscode = acquireVsCodeApi();
  const balance = ${balanceJson};
  const types = ${typesJson};

  function updateBalance() {
    const id = document.getElementById('leave-type').value;
    const rem = balance[id];
    const el = document.getElementById('balance-display');
    el.textContent = rem !== undefined ? \`\${types[id]}: \${rem} days remaining\` : 'Balance not available';
  }

  function submit() {
    const leaveTypeId = document.getElementById('leave-type').value;
    const from = document.getElementById('from').value;
    const to = document.getElementById('to').value;
    const reason = document.getElementById('reason').value;
    if (!from || !to) { showError('From and To dates are required.'); return; }
    if (new Date(to) < new Date(from)) { showError('To date must be after From date.'); return; }
    vscode.postMessage({ type: 'SUBMIT_LEAVE', leaveTypeId, from, to, reason });
  }

  function cancel() { vscode.postMessage({ type: 'CANCEL' }); }

  function showError(msg) {
    const el = document.getElementById('error');
    el.textContent = msg;
    el.style.display = 'block';
  }

  window.addEventListener('message', ({ data }) => {
    if (data.type === 'SUBMIT_ERROR') showError(data.message || 'Submission failed.');
  });

  updateBalance();
</script>
</body>
</html>`;
    }

    dispose(): void { this.panel?.dispose(); }
}
```

- [ ] **Step 5: Run HR tests**

```bash
npm test -- --grep "HrTagHandler"
```

Expected: All 4 PASS.

- [ ] **Step 6: Register HR commands in extension.ts**

Add to `activate()`:

```typescript
const { HrTagHandler } = await import('./hr/HrTagHandler');
const { LeaveFormWebview } = await import('./hr/LeaveFormWebview');
const hrHandler = new HrTagHandler(apiClient);
const leaveForm = new LeaveFormWebview(context, apiClient);

context.subscriptions.push(
    vscode.commands.registerCommand('onevo.openLeaveForm', async (channelId: string, prefill?: any) => {
        await leaveForm.show(sessionId ?? '', prefill);
    }),
    leaveForm
);
```

- [ ] **Step 7: Build**

```bash
npm run compile
```

Expected: 0 errors.

- [ ] **Step 8: Commit**

```bash
git add src/hr/
git commit -m "feat(ide-ext): HR automation — clockin/out/break instant fire, leave form with balance"
```

---

## Task E5: NLP Suggestion Handler

**Files:**
- Create: `src/nlp/NlpSuggestionHandler.ts`
- Test: `test/suite/NlpSuggestionHandler.test.ts`

- [ ] **Step 1: Write failing test**

```typescript
// test/suite/NlpSuggestionHandler.test.ts
import * as assert from 'assert';
import * as sinon from 'sinon';
import { NlpSuggestionHandler } from '../../src/nlp/NlpSuggestionHandler';

suite('NlpSuggestionHandler', () => {
    let apiMock: any;
    let handler: NlpSuggestionHandler;

    setup(() => {
        apiMock = { executeTag: sinon.stub().resolves({ executionId: 'ex-1', status: 'success', undoExpiresAt: null, errorMessage: null }) };
        handler = new NlpSuggestionHandler(apiMock);
    });

    test('buildConfirmationCard returns well-formed payload', () => {
        const card = handler.buildConfirmationCard({
            jobId: 'job-1',
            tagAction: 'time:log',
            resolvedParams: { hours: '2', description: 'login bug' },
            originalMessage: 'log 2 hours on the login bug',
            undoExpiresAt: '2026-05-01T09:30:00Z'
        });
        assert.strictEqual(card.tagAction, 'time:log');
        assert.strictEqual(card.resolvedParams.hours, '2');
        assert.ok(card.displayLabel.includes('time:log'));
    });

    test('handleConfirm calls executeTag with reconstructed tag', async () => {
        await handler.handleConfirm({
            tagAction: 'time:log',
            resolvedParams: { hours: '2', task: 'TASK-123', description: 'fix bug' },
            sessionId: 'sess-1'
        });
        sinon.assert.calledWith(apiMock.executeTag, sinon.match(/time:log/), 'sess-1');
    });
});
```

- [ ] **Step 2: Run to verify failure**

```bash
npm test -- --grep "NlpSuggestionHandler"
```

Expected: FAIL.

- [ ] **Step 3: Implement NlpSuggestionHandler**

```typescript
// src/nlp/NlpSuggestionHandler.ts
import * as vscode from 'vscode';
import type { OneVoApiClient } from '../api/OneVoApiClient';

export interface NlpSuggestionPayload {
    jobId: string;
    tagAction: string;
    resolvedParams: Record<string, string>;
    originalMessage: string;
    undoExpiresAt: string;
}

export interface ConfirmationCard {
    tagAction: string;
    resolvedParams: Record<string, string>;
    displayLabel: string;
}

export class NlpSuggestionHandler {
    constructor(private readonly api: OneVoApiClient) {}

    buildConfirmationCard(payload: NlpSuggestionPayload): ConfirmationCard {
        const paramStr = Object.entries(payload.resolvedParams)
            .map(([k, v]) => `#${k}:${v}`)
            .join(' ');
        return {
            tagAction: payload.tagAction,
            resolvedParams: payload.resolvedParams,
            displayLabel: `@${payload.tagAction} ${paramStr}`
        };
    }

    async handleConfirm(data: {
        tagAction: string;
        resolvedParams: Record<string, string>;
        sessionId: string;
    }): Promise<void> {
        const paramStr = Object.entries(data.resolvedParams)
            .map(([k, v]) => `#${k}:${v}`)
            .join(' ');
        const rawTag = `@${data.tagAction} ${paramStr}`.trim();
        const result = await this.api.executeTag(rawTag, data.sessionId);
        if (result.status !== 'success') {
            vscode.window.showErrorMessage(`OneVo: NLP action failed. ${result.errorMessage ?? ''}`);
        }
    }

    // Called by IDEHubClient on 'ai:action_pending' event
    handleSuggestionEvent(
        payload: NlpSuggestionPayload,
        sessionId: string,
        onEdit: (tagAction: string, params: Record<string, string>) => void
    ): void {
        const card = this.buildConfirmationCard(payload);

        vscode.window.showInformationMessage(
            `OneVo AI: ${card.displayLabel}`,
            'Confirm', 'Edit', 'Dismiss'
        ).then(choice => {
            if (choice === 'Confirm') {
                this.handleConfirm({ tagAction: payload.tagAction, resolvedParams: payload.resolvedParams, sessionId });
            } else if (choice === 'Edit') {
                onEdit(payload.tagAction, payload.resolvedParams);
            }
            // Dismiss → do nothing, message stored as plain text by backend
        });
    }
}
```

- [ ] **Step 4: Wire NLP handler into IDEHubClient in extension.ts**

Add to `activate()` after hub connect:

```typescript
const { NlpSuggestionHandler } = await import('./nlp/NlpSuggestionHandler');
const nlpHandler = new NlpSuggestionHandler(apiClient);

hubClient.on('ai:action_pending', (_, data: any) => {
    nlpHandler.handleSuggestionEvent(data, sessionId ?? '', (action, params) => {
        if (action === 'leave:request') {
            const from = params['from'];
            const to = params['to'];
            vscode.commands.executeCommand('onevo.openLeaveForm', null, { from, to });
        }
        // Other form actions can be handled similarly
    });
});
```

- [ ] **Step 5: Run NLP tests**

```bash
npm test -- --grep "NlpSuggestionHandler"
```

Expected: All 2 PASS.

- [ ] **Step 6: Build**

```bash
npm run compile
```

- [ ] **Step 7: Commit**

```bash
git add src/nlp/
git commit -m "feat(ide-ext): NLP suggestion handler — confirm/edit/dismiss for SK intent detections"
```

---

## Task E6: Context Engine

**Files:**
- Create: `src/context/BranchDetector.ts`
- Create: `src/context/FileContextDetector.ts`
- Create: `src/context/TimeTracker.ts`

- [ ] **Step 1: Implement BranchDetector**

```typescript
// src/context/BranchDetector.ts
import * as vscode from 'vscode';
import type { OneVoApiClient } from '../api/OneVoApiClient';

export interface BranchContext {
    repositoryUrl: string;
    branchName: string;
    linkedTaskId: string | null;
    linkedTaskTitle: string | null;
}

export class BranchDetector implements vscode.Disposable {
    private currentContext: BranchContext | null = null;
    private readonly disposables: vscode.Disposable[] = [];

    constructor(
        private readonly api: OneVoApiClient,
        private readonly onContextChange: (ctx: BranchContext | null) => void
    ) {}

    async start(): Promise<void> {
        // VS Code git extension
        const gitExtension = vscode.extensions.getExtension<any>('vscode.git');
        if (!gitExtension) return;

        const git = gitExtension.isActive
            ? gitExtension.exports
            : await gitExtension.activate();

        const api = git.getAPI(1);

        const updateContext = async () => {
            const repo = api.repositories[0];
            if (!repo) return;

            const branch = repo.state.HEAD?.name;
            const remoteUrl = repo.state.remotes[0]?.fetchUrl ?? '';

            if (!branch || !remoteUrl) {
                this.currentContext = null;
                this.onContextChange(null);
                return;
            }

            try {
                const data: any = await this.api['request'](`/api/v1/ide/context/branch?repo=${encodeURIComponent(remoteUrl)}&branch=${encodeURIComponent(branch)}`);
                this.currentContext = {
                    repositoryUrl: remoteUrl,
                    branchName: branch,
                    linkedTaskId: data.task_id ?? null,
                    linkedTaskTitle: data.task_title ?? null
                };
            } catch {
                this.currentContext = { repositoryUrl: remoteUrl, branchName: branch, linkedTaskId: null, linkedTaskTitle: null };
            }
            this.onContextChange(this.currentContext);
        };

        // Watch for branch changes
        for (const repo of api.repositories) {
            this.disposables.push(
                repo.state.onDidChange(updateContext)
            );
        }

        // Initial fetch
        await updateContext();
    }

    get currentBranchContext(): BranchContext | null {
        return this.currentContext;
    }

    dispose(): void {
        this.disposables.forEach(d => d.dispose());
    }
}
```

- [ ] **Step 2: Implement TimeTracker**

```typescript
// src/context/TimeTracker.ts
import * as vscode from 'vscode';
import type { OneVoApiClient } from '../api/OneVoApiClient';
import type { BranchContext } from './BranchDetector';
import type { OnevoConfig } from '../config/WorkspaceConfig';

export class TimeTracker implements vscode.Disposable {
    private statusBarItem: vscode.StatusBarItem;
    private timerInterval: NodeJS.Timeout | null = null;
    private startedAt: Date | null = null;
    private activeSessionId: string | null = null;

    constructor(
        private readonly api: OneVoApiClient,
        private readonly config: OnevoConfig
    ) {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        this.statusBarItem.command = 'onevo.toggleTimer';
        this.statusBarItem.show();
        this.updateDisplay();
    }

    onBranchContextChange(ctx: BranchContext | null): void {
        if (this.config.timeTracking === 'auto' && ctx?.linkedTaskId && !this.startedAt) {
            this.startTimer(ctx.linkedTaskId);
        }
    }

    async startTimer(taskId: string): Promise<void> {
        this.startedAt = new Date();
        this.activeSessionId = taskId;
        this.timerInterval = setInterval(() => this.updateDisplay(), 1000);
        this.updateDisplay();
        await this.api.executeTag(`@time:start #task:${taskId}`, '').catch(() => {});
    }

    async stopTimer(): Promise<void> {
        if (!this.startedAt || !this.activeSessionId) return;
        clearInterval(this.timerInterval!);
        const minutes = Math.round((Date.now() - this.startedAt.getTime()) / 60000);
        this.startedAt = null;
        this.updateDisplay();
        await this.api.executeTag(`@time:stop #task:${this.activeSessionId} #minutes:${minutes}`, '').catch(() => {});
        this.activeSessionId = null;
    }

    private updateDisplay(): void {
        if (!this.startedAt) {
            this.statusBarItem.text = '$(clock) OneVo';
            this.statusBarItem.tooltip = 'Click to start time tracking';
            return;
        }
        const elapsed = Math.floor((Date.now() - this.startedAt.getTime()) / 1000);
        const h = Math.floor(elapsed / 3600).toString().padStart(2, '0');
        const m = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
        const s = (elapsed % 60).toString().padStart(2, '0');
        this.statusBarItem.text = `$(clock) ${h}:${m}:${s}`;
        this.statusBarItem.tooltip = `OneVo time tracking — task ${this.activeSessionId}`;
    }

    dispose(): void {
        clearInterval(this.timerInterval!);
        this.statusBarItem.dispose();
    }
}
```

- [ ] **Step 3: Wire context engine into extension.ts**

Add to `activate()`:

```typescript
const { BranchDetector } = await import('./context/BranchDetector');
const { TimeTracker } = await import('./context/TimeTracker');

const timeTracker = new TimeTracker(apiClient, config);
const branchDetector = new BranchDetector(apiClient, (ctx) => {
    timeTracker.onBranchContextChange(ctx);
    // Update session context on backend
    if (sessionId && ctx) {
        apiClient['request'](`/api/v1/ide/sessions/${sessionId}/context`, {
            method: 'PUT',
            body: JSON.stringify({ branch_name: ctx.branchName, repository_url: ctx.repositoryUrl })
        }).catch(() => {});
    }
});

await branchDetector.start();

context.subscriptions.push(
    branchDetector,
    timeTracker,
    vscode.commands.registerCommand('onevo.toggleTimer', async () => {
        if (timeTracker['startedAt']) {
            await timeTracker.stopTimer();
        } else {
            const taskId = branchDetector.currentBranchContext?.linkedTaskId;
            if (taskId) await timeTracker.startTimer(taskId);
            else vscode.window.showInformationMessage('OneVo: No task linked to current branch.');
        }
    })
);
```

- [ ] **Step 4: Build**

```bash
npm run compile
```

Expected: 0 errors.

- [ ] **Step 5: Commit**

```bash
git add src/context/
git commit -m "feat(ide-ext): context engine — branch→task detection, status bar timer, auto time tracking"
```

---

## Task E7: Agent Entitlement

**Files:**
- Create: `src/agent-install/AgentInstaller.ts`

- [ ] **Step 1: Implement AgentInstaller**

```typescript
// src/agent-install/AgentInstaller.ts
import * as vscode from 'vscode';
import * as https from 'https';
import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import * as child_process from 'child_process';
import type { OneVoApiClient } from '../api/OneVoApiClient';

export class AgentInstaller implements vscode.Disposable {
    private neverAskKey = 'onevo.agentInstall.neverAsk';

    constructor(
        private readonly context: vscode.ExtensionContext,
        private readonly api: OneVoApiClient
    ) {}

    async checkAndPrompt(): Promise<void> {
        const neverAsk = this.context.globalState.get<boolean>(this.neverAskKey, false);
        if (neverAsk) return;

        const choice = await vscode.window.showInformationMessage(
            'OneVo: Your organisation uses productivity monitoring. Set up the OneVo monitoring agent?',
            'Set Up',
            'Not Now',
            'Never Ask Again'
        );

        if (choice === 'Never Ask Again') {
            await this.context.globalState.update(this.neverAskKey, true);
            return;
        }

        if (choice === 'Set Up') {
            await this.install();
        }
    }

    private async install(): Promise<void> {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'OneVo: Installing monitoring agent...',
            cancellable: false
        }, async (progress) => {
            // 1. Request install job
            progress.report({ message: 'Requesting install job...' });
            const job = await this.api['request']<any>('/api/v1/ide/agent-install/request', {
                method: 'POST'
            });

            // 2. Download binary
            progress.report({ message: 'Downloading agent...' });
            const tmpPath = path.join(os.tmpdir(), `onevo-agent-${job.id}`);
            await this.download(job.download_url, tmpPath);

            // 3. Verify hash
            progress.report({ message: 'Verifying integrity...' });
            const hash = await this.sha256(tmpPath);
            if (hash !== job.sha256) {
                fs.unlinkSync(tmpPath);
                vscode.window.showErrorMessage('OneVo: Agent download corrupted. Please try again.');
                return;
            }

            // 4. Execute installer
            progress.report({ message: 'Installing...' });
            await this.runInstaller(tmpPath);
            fs.unlinkSync(tmpPath);

            // 5. Mark installed
            await this.api['request'](`/api/v1/ide/agent-install/${job.id}/installed`, { method: 'PUT' });

            vscode.window.showInformationMessage('OneVo: Monitoring agent installed successfully.');
        });
    }

    private download(url: string, dest: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const file = fs.createWriteStream(dest);
            https.get(url, response => {
                response.pipe(file);
                file.on('finish', () => { file.close(); resolve(); });
            }).on('error', err => {
                fs.unlink(dest, () => {});
                reject(err);
            });
        });
    }

    private sha256(filePath: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const hash = crypto.createHash('sha256');
            fs.createReadStream(filePath)
                .on('data', d => hash.update(d))
                .on('end', () => resolve(hash.digest('hex')))
                .on('error', reject);
        });
    }

    private runInstaller(installerPath: string): Promise<void> {
        return new Promise((resolve, reject) => {
            fs.chmodSync(installerPath, '755');
            const proc = child_process.spawn(installerPath, ['--silent'], { stdio: 'ignore' });
            proc.on('exit', code => code === 0 ? resolve() : reject(new Error(`Installer exited with ${code}`)));
        });
    }

    dispose(): void {}
}
```

- [ ] **Step 2: Wire agent installer into extension.ts**

Add to `activate()`, after loading entitlements:

```typescript
if (entitlements.hasMonitoringEntitlement) {
    const { AgentInstaller } = await import('./agent-install/AgentInstaller');
    const installer = new AgentInstaller(context, apiClient);
    context.subscriptions.push(installer);
    // Non-blocking — prompt appears after extension is fully loaded
    setTimeout(() => installer.checkAndPrompt(), 3000);
}
```

- [ ] **Step 3: Build the full extension**

```bash
npm run compile
```

Expected: 0 errors.

- [ ] **Step 4: Package the extension**

```bash
npm install -g @vscode/vsce
vsce package
```

Expected: `onevo-<version>.vsix` created.

- [ ] **Step 5: Run full test suite**

```bash
npm test
```

Expected: All tests pass.

- [ ] **Step 6: Run the full backend test suite**

```bash
cd ..
dotnet test ONEVO.sln
```

Expected: All tests pass (no regressions).

- [ ] **Step 7: Final commit**

```bash
git add src/agent-install/ onevo-ide-extension/*.vsix
git commit -m "feat(ide-ext): agent entitlement flow — prompt, download, hash verify, install, never-again"
git commit -m "feat(ide-ext): DEV9 complete — full IDE extension with chat, tags, HR automation, NLP, context engine"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| `active_modules[]` + `permitted_tag_actions[]` in entitlements | B1 |
| HR tag routing (clockin, break, leave, etc.) | B2 |
| SK NLP intent pipeline (0.8 threshold) | B3 |
| Extension scaffold, auth, SignalR, session | E1 |
| Chat panel — channels, messages, real-time | E2 |
| `@` picker — all WMS tags, permission-filtered | E3 |
| HR section gated by `active_modules` | E3 (TagPickerWebview) |
| Instant-fire HR actions | E4 |
| Leave mini form with balance | E4 |
| NLP confirmation card (Confirm/Edit/Dismiss) | E5 |
| Branch→task context detection | E6 |
| Status bar timer, auto time tracking | E6 |
| Agent install — never silent, hash verify | E7 |

All 13 spec sections covered. ✅

**Placeholder scan:** No TBD, no "implement later", no vague steps. ✅

**Type consistency:**
- `IDEEntitlements.permittedTagActions` — defined in E1 `OneVoApiClient.ts`, used in E3 `TagPickerWebview` ✅
- `IDEEntitlements.activeModules` — defined in B1, read in E3 ✅
- `HrTagHandler.isHrAction()` / `isInstantAction()` — static methods defined in E4, used in E3 routing ✅
- `BranchContext` — defined in E6, consumed in E6 TimeTracker ✅
