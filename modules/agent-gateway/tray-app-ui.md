# Tray App UI — MAUI System Tray Application

## Overview

The MAUI Tray App (`ONEVO.Agent.TrayApp`) is the user-facing component of the desktop agent. It provides:
- System tray icon with status indication
- Employee sign-in, login-based device enrollment, and logout
- Photo capture for identity verification
- Remote workplace setup and work-location verification prompts
- Status popup showing collector and sync state
- Notification toasts for important events

The TrayApp communicates with the Windows Service via Named Pipes. See [[modules/agent-gateway/ipc-protocol|Ipc Protocol]] for the full message contract.

**Phase 1 enrollment source of truth:** the TrayApp is the employee-facing enrollment surface. Employees do not type an API key, tenant key, tenant ID, or server URL. They click **Sign in**, authenticate through the system browser or a secure embedded auth flow, and the backend resolves tenant/user before issuing an internal device credential to the Service.

---

## System Tray Icon

The tray icon uses `CommunityToolkit.Maui` and changes appearance based on agent state.

### Icon States

Additional enrollment states required for login-based enrollment:

| State | Tooltip | When |
|:------|:--------|:-----|
| **Sign in required** | "ONEVO Agent - Sign in required" | Service is installed but device is not enrolled |
| **Enrolling device** | "ONEVO Agent - Enrolling device..." | User completed sign-in and Service is completing enrollment |
| **Consent required / policy blocked** | "ONEVO Agent - Monitoring paused" | Consent is missing, policy blocks collection, or Workforce Presence lifecycle is paused |

| State | Icon | Tooltip | When |
|:------|:-----|:--------|:-----|
| **Disconnected** | Gray circle | "ONEVO Agent — Not connected" | Service not running or pipe disconnected |
| **Connected (no employee)** | Blue circle | "ONEVO Agent — No employee logged in" | Service running, no employee login |
| **Collecting** | Green circle | "ONEVO Agent — Monitoring active" | Employee logged in, collectors running |
| **Syncing** | Green circle with arrows | "ONEVO Agent — Syncing data..." | During active data upload |
| **Error** | Red circle with ! | "ONEVO Agent — Error (click for details)" | Sync failure, auth error, or service error |
| **Verification needed** | Orange circle with camera | "ONEVO Agent — Verification required" | Photo capture pending |

| **Work location check** | Orange circle with location/camera | "ONEVO Agent - Work location verification required" | Work-location mismatch requires photo verification |

### Tray Icon Service

```csharp
// ONEVO.Agent.TrayApp/Services/TrayIconService.cs

public class TrayIconService
{
    private readonly INotificationService _notifications;

    public enum TrayState
    {
        Disconnected,
        ConnectedNoEmployee,
        Collecting,
        Syncing,
        Error,
        VerificationNeeded
    }

    public void UpdateState(TrayState state)
    {
        var (icon, tooltip) = state switch
        {
            TrayState.Disconnected => ("tray_gray.ico", "ONEVO Agent — Not connected"),
            TrayState.ConnectedNoEmployee => ("tray_blue.ico", "ONEVO Agent — No employee logged in"),
            TrayState.Collecting => ("tray_green.ico", "ONEVO Agent — Monitoring active"),
            TrayState.Syncing => ("tray_green_sync.ico", "ONEVO Agent — Syncing data..."),
            TrayState.Error => ("tray_red.ico", "ONEVO Agent — Error (click for details)"),
            TrayState.VerificationNeeded => ("tray_orange.ico", "ONEVO Agent — Verification required"),
            _ => ("tray_gray.ico", "ONEVO Agent")
        };

        // Update icon and tooltip via CommunityToolkit.Maui
        _trayIcon.Icon = icon;
        _trayIcon.ToolTipText = tooltip;
    }
}
```

### Tray Icon Context Menu

For the default Phase 1 flow, the employee-facing action is **Sign in**, not "enter tenant key" or "configure server". Sign in starts or resumes login-based enrollment.

Right-clicking the tray icon shows:

| Menu Item | Action | Visibility |
|:----------|:-------|:-----------|
| **Status** | Opens status popup | Always |
| **Sign in** | Opens enrollment flow (browser SSO) | Only when device is not yet enrolled (first-time setup) |
| **Clock In** | Triggers photo capture → then clock-in | When clocked out AND (`work_type = remote/hybrid` OR `policy.agent_clock_in_enabled = true`) |
| **Clock Out** | Triggers photo capture → then clock-out | When clocked in AND (`work_type = remote/hybrid` OR `policy.agent_clock_in_enabled = true`) |
| **Start Break** | Starts break, pauses monitoring | When clocked in and not on break |
| **End Break** | Ends break, resumes monitoring | When on break |
| **Remote Work Location** | Opens remote location setup/change request | When employee is remote/hybrid and policy allows |
| **About** | Shows version info | Always |

**Login is one-time.** After the employee signs in once and the device is enrolled, the tray app stays connected under their identity permanently. The device credential is stored via DPAPI and auto-renewed on heartbeat. There is no "sign in every shift" flow.

There is no "Exit" or "Quit" option. The agent is managed by IT — employees cannot stop it. The service continues running regardless of whether the TrayApp is open.

---

## Login Window

A modal window shown when the employee clicks "Sign in" from the tray menu or when the TrayApp first launches with no enrolled employee session.

The preferred UX is browser-based sign-in:

1. TrayApp sends `start_enrollment` to the Service over Named Pipes.
2. Service calls `POST /api/v1/agent/enroll/start`.
3. TrayApp opens the returned `auth_url` in the system browser, or a secure embedded auth flow if browser handoff is unavailable.
4. User signs in with normal OneVo auth/SSO.
5. Service calls `POST /api/v1/agent/enroll/complete`.
6. Service stores the returned device credential with DPAPI / Windows Credential Manager.
7. TrayApp changes state to "Monitoring active" only after policy fetch, consent gate, and lifecycle allow collection.

For remote or hybrid employees, the first approved remote clock-in may also require a remote workplace capture. The TrayApp asks the employee to confirm the current workplace, captures a verification photo, and sends network evidence to the Service. After the remote workplace is locked, changes must be requested from Employee Settings and approved by the reporting manager. See [[Userflow/Workforce-Intelligence/work-location-compliance|Work Location Compliance]].

The email/password form below is a fallback UI pattern only. It must not ask for API keys, tenant keys, tenant IDs, or server URLs.

### First Reference Photo Enrollment

After sign-in and policy fetch, if identity verification is enabled and the employee has no approved verification reference photo, the TrayApp starts **Reference Enrollment** before normal photo verification.

1. TrayApp shows the required monitoring/biometric disclosure if not already completed.
2. TrayApp opens the same camera window in reference-enrollment mode.
3. The captured image is uploaded as a `verification_reference_photos` candidate with `status = pending_review`.
4. The agent displays "Reference photo pending review" until approval by the configured identity-verification resolver or tenant-approved trusted SSO/MFA auto-approval.
5. Future verification prompts compare against the approved reference photo.

The first reference capture is not a verification failure or success. It must not trigger `VerificationFailed`.

### Layout

```
┌─────────────────────────────────────┐
│         ONEVO                       │
│         [Logo]                      │
│                                     │
│  Connect to your device             │
│                                     │
│  Email                              │
│  ┌─────────────────────────────┐    │
│  │ user@company.com            │    │
│  └─────────────────────────────┘    │
│                                     │
│  Password                           │
│  ┌─────────────────────────────┐    │
│  │ ••••••••                    │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │        Connect              │    │
│  └─────────────────────────────┘    │
│                                     │
│  [Spinner + "Connecting..."]        │
│  [Error message if login fails]     │
│                                     │
└─────────────────────────────────────┘
```

### XAML

```xml
<!-- ONEVO.Agent.TrayApp/Views/LoginWindow.xaml -->
<Window x:Class="ONEVO.Agent.TrayApp.Views.LoginWindow"
        xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
        xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
        Title="ONEVO Agent"
        Width="400" Height="450"
        WindowStartupLocation="CenterScreen"
        ResizeMode="NoResize">

    <VerticalStackLayout Padding="32" Spacing="16">
        <!-- Logo -->
        <Image Source="logo.png" HeightRequest="48" HorizontalOptions="Center" />

        <!-- Title -->
        <Label Text="Connect to your device"
               FontSize="18" FontAttributes="Bold"
               HorizontalOptions="Center" />

        <!-- Email -->
        <Label Text="Email" FontSize="14" />
        <Entry x:Name="EmailEntry"
               Placeholder="user@company.com"
               Keyboard="Email"
               ReturnType="Next" />

        <!-- Password -->
        <Label Text="Password" FontSize="14" />
        <Entry x:Name="PasswordEntry"
               Placeholder="Password"
               IsPassword="True"
               ReturnType="Done"
               ReturnCommand="{Binding ConnectCommand}" />

        <!-- Connect Button -->
        <Button x:Name="ConnectButton"
                Text="Connect"
                Command="{Binding ConnectCommand}"
                BackgroundColor="{StaticResource PrimaryColor}"
                TextColor="White"
                HeightRequest="48"
                CornerRadius="8" />

        <!-- Loading Indicator -->
        <HorizontalStackLayout x:Name="LoadingIndicator" IsVisible="False" HorizontalOptions="Center">
            <ActivityIndicator IsRunning="True" Color="{StaticResource PrimaryColor}" />
            <Label Text="Connecting..." Margin="8,0,0,0" />
        </HorizontalStackLayout>

        <!-- Error Message -->
        <Label x:Name="ErrorLabel"
               TextColor="Red"
               IsVisible="False"
               HorizontalOptions="Center" />
    </VerticalStackLayout>
</Window>
```

### Login Flow

```csharp
// LoginWindow.xaml.cs — Connect command handler

private async Task OnConnectAsync()
{
    ErrorLabel.IsVisible = false;
    LoadingIndicator.IsVisible = true;
    ConnectButton.IsEnabled = false;

    try
    {
        // Send login via IPC to Service
        await _pipeClient.SendAsync(new EmployeeLoginMessage
        {
            Email = EmailEntry.Text,
            Password = PasswordEntry.Text
        }, _cts.Token);

        // Wait for status_update response from Service
        // (handled by the IPC message listener — see OnMessageReceived)
    }
    catch (Exception ex)
    {
        ErrorLabel.Text = "Connection failed. Please try again.";
        ErrorLabel.IsVisible = true;
        _logger.LogError(ex, "Login failed");
    }
    finally
    {
        LoadingIndicator.IsVisible = false;
        ConnectButton.IsEnabled = true;
    }
}

// When the Service responds with a status_update after login:
private void OnLoginSuccess(StatusUpdateMessage status)
{
    // Close login window, update tray icon
    _trayIconService.UpdateState(TrayState.Collecting);
    this.Close();
}

private void OnLoginFailure(string error)
{
    ErrorLabel.Text = error; // e.g., "Invalid credentials" or "Account not found"
    ErrorLabel.IsVisible = true;
}
```

---

## Status Popup

Shown when the user clicks "Status" from the tray menu or double-clicks the tray icon.

### Layout

```
┌────────────────────────────────────────┐
│  ONEVO Agent Status                    │
│                                        │
│  Employee: John Doe                    │
│  Status:   ● Connected                │
│                                        │
│  ── Collectors ──────────────────────  │
│  Activity Monitor    ● Running         │
│  App Tracker         ● Running         │
│  Idle Detector       ● Running         │
│  Meeting Detector    ● Running         │
│  Device Tracker      ● Running         │
│  Document Tracker    ● Running         │
│  Comm Tracker        ● Running         │
│                                        │
│  ── Sync ────────────────────────────  │
│  Last sync:    2 minutes ago           │
│  Buffered:     12 records              │
│  Connection:   ● Online                │
│                                        │
│  ── Monitoring ──────────────────────  │
│  This device is monitoring:            │
│  ✓ Keyboard/mouse activity counts      │
│  ✓ Application & document usage        │
│  ✓ Idle time                           │
│  ✓ Meeting detection                   │
│  ✓ Communication app activity          │
│  ✗ Screenshots (authorized request)    │
│                                        │
│               [Close]                  │
└────────────────────────────────────────┘
```

### XAML

```xml
<!-- ONEVO.Agent.TrayApp/Views/StatusPopup.xaml -->
<Window x:Class="ONEVO.Agent.TrayApp.Views.StatusPopup"
        Title="ONEVO Agent Status"
        Width="380" Height="520"
        WindowStartupLocation="CenterScreen"
        ResizeMode="NoResize">

    <ScrollView Padding="24">
        <VerticalStackLayout Spacing="12">
            <!-- Header -->
            <Label Text="ONEVO Agent Status" FontSize="20" FontAttributes="Bold" />

            <!-- Employee Info -->
            <HorizontalStackLayout Spacing="8">
                <Label Text="Employee:" FontAttributes="Bold" />
                <Label x:Name="EmployeeNameLabel" Text="{Binding EmployeeName}" />
            </HorizontalStackLayout>
            <HorizontalStackLayout Spacing="8">
                <Label Text="Status:" FontAttributes="Bold" />
                <Label x:Name="StatusLabel" Text="{Binding ConnectionStatus}" TextColor="{Binding StatusColor}" />
            </HorizontalStackLayout>

            <!-- Collectors Section -->
            <BoxView HeightRequest="1" Color="LightGray" Margin="0,8" />
            <Label Text="Collectors" FontAttributes="Bold" FontSize="16" />
            <CollectionView x:Name="CollectorsList" ItemsSource="{Binding Collectors}">
                <CollectionView.ItemTemplate>
                    <DataTemplate>
                        <HorizontalStackLayout Spacing="8" Padding="0,4">
                            <Label Text="{Binding Name}" WidthRequest="180" />
                            <Label Text="{Binding StatusIcon}" />
                            <Label Text="{Binding Status}" TextColor="{Binding StatusColor}" />
                        </HorizontalStackLayout>
                    </DataTemplate>
                </CollectionView.ItemTemplate>
            </CollectionView>

            <!-- Sync Section -->
            <BoxView HeightRequest="1" Color="LightGray" Margin="0,8" />
            <Label Text="Sync" FontAttributes="Bold" FontSize="16" />
            <Label Text="{Binding LastSyncText}" />
            <Label Text="{Binding BufferedCountText}" />

            <!-- Monitoring Transparency Section -->
            <BoxView HeightRequest="1" Color="LightGray" Margin="0,8" />
            <Label Text="Monitoring" FontAttributes="Bold" FontSize="16" />
            <Label Text="This device is monitoring:" />
            <CollectionView ItemsSource="{Binding MonitoringFeatures}">
                <CollectionView.ItemTemplate>
                    <DataTemplate>
                        <HorizontalStackLayout Spacing="4" Padding="0,2">
                            <Label Text="{Binding Icon}" />
                            <Label Text="{Binding Description}" />
                        </HorizontalStackLayout>
                    </DataTemplate>
                </CollectionView.ItemTemplate>
            </CollectionView>

            <!-- Close -->
            <Button Text="Close" Command="{Binding CloseCommand}"
                    HorizontalOptions="Center" Margin="0,16,0,0" />
        </VerticalStackLayout>
    </ScrollView>
</Window>
```

The status popup sends `get_status` via IPC when opened and updates when `status_update` messages arrive. See [[modules/agent-gateway/ipc-protocol|Ipc Protocol]].

---

## Photo Capture Window

Opened when the Service sends a `capture_photo` IPC message. See [[modules/identity-verification/photo-capture|Photo Capture]] for the full verification flow.

### Layout

```
┌────────────────────────────────────────┐
│  Identity Verification                 │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │                                  │  │
│  │         Camera Feed              │  │
│  │         (Live Preview)           │  │
│  │                                  │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
│                                        │
│  Please look at the camera and         │
│  click Capture.                        │
│                                        │
│  ┌──────────┐    ┌──────────┐          │
│  │  Capture  │    │   Skip   │         │
│  └──────────┘    └──────────┘          │
│                                        │
│  ⚠ Photo will be compared with        │
│    your approved reference photo       │
│                                        │
│  Auto-skip in: 1:45                    │
│                                        │
└────────────────────────────────────────┘
```

### XAML

```xml
<!-- ONEVO.Agent.TrayApp/Views/PhotoCaptureWindow.xaml -->
<Window x:Class="ONEVO.Agent.TrayApp.Views.PhotoCaptureWindow"
        Title="Identity Verification"
        Width="480" Height="560"
        WindowStartupLocation="CenterScreen"
        ResizeMode="NoResize"
        Topmost="True">

    <VerticalStackLayout Padding="24" Spacing="16">
        <Label Text="Identity Verification" FontSize="20" FontAttributes="Bold" />

        <!-- Camera Preview -->
        <Border Stroke="LightGray" StrokeThickness="1" HeightRequest="320">
            <ContentView x:Name="CameraPreview" />
            <!-- Camera feed rendered via CameraService -->
        </Border>

        <!-- Instructions -->
        <Label x:Name="InstructionLabel"
               Text="Please look at the camera and click Capture."
               HorizontalOptions="Center" />

        <!-- Buttons -->
        <HorizontalStackLayout Spacing="16" HorizontalOptions="Center">
            <Button x:Name="CaptureButton"
                    Text="Capture"
                    Command="{Binding CaptureCommand}"
                    BackgroundColor="{StaticResource PrimaryColor}"
                    TextColor="White"
                    WidthRequest="120" HeightRequest="44" CornerRadius="8" />
            <Button x:Name="SkipButton"
                    Text="Skip"
                    Command="{Binding SkipCommand}"
                    BackgroundColor="LightGray"
                    WidthRequest="120" HeightRequest="44" CornerRadius="8" />
        </HorizontalStackLayout>

        <!-- Transparency message (varies by mode) -->
        <Label x:Name="TransparencyLabel"
               FontSize="12" TextColor="Gray"
               HorizontalOptions="Center" />

        <!-- Auto-skip countdown -->
        <Label x:Name="CountdownLabel"
               Text="Auto-skip in: 2:00"
               FontSize="12" TextColor="Gray"
               HorizontalOptions="Center" />
    </VerticalStackLayout>
</Window>
```

### Behavior

- Window appears as **topmost** (always on top) but not fullscreen
- 2-minute countdown timer — auto-skips if user does not respond
- After capture, window closes immediately
- After skip (manual or timeout), sends `photo_captured` with `skipped: true`

See [[modules/identity-verification/photo-capture|Photo Capture]] for photo quality requirements, privacy rules, and server-side verification.

---

## Notification Toasts

The TrayApp shows Windows toast notifications for important events.

### Notification Types

| Event | Title | Body | Trigger |
|:------|:------|:-----|:--------|
| Verification required | "Identity Verification" | "Please verify your identity" | `capture_photo` IPC message |
| Verification passed | "Verification Complete" | "Identity verified successfully" | `verification_result` with `result: "verified"` |
| Verification failed | "Verification Failed" | "Identity could not be verified" | `verification_result` with `result: "failed"` |
| Sync error | "Sync Error" | "Unable to sync data. Will retry automatically." | Consecutive sync failures (3+) |
| Update available | "Update Available" | "A new version of ONEVO Agent is available" | Heartbeat response with `update_available: true` |
| Connection lost | "Connection Lost" | "Unable to reach ONEVO server" | After 3 consecutive heartbeat failures |
| Connection restored | "Connected" | "Connection to ONEVO server restored" | First successful heartbeat after failures |

### Implementation

```csharp
// Using CommunityToolkit.Maui notifications

public class NotificationService
{
    public async Task ShowToastAsync(string title, string body, bool isUrgent = false)
    {
        var request = new NotificationRequest
        {
            Title = title,
            Description = body,
            CategoryType = isUrgent
                ? NotificationCategoryType.Alarm
                : NotificationCategoryType.Status
        };

        await LocalNotificationCenter.Current.Show(request);
    }
}
```

---

## Transparency Mode

The monitoring policy includes a transparency level that affects what the user sees in the TrayApp UI. This is set at the tenant level.

| Mode | Status Popup Shows | Photo Capture Shows | Login Shows |
|:-----|:-------------------|:-------------------|:------------|
| `full_transparency` | Full collector list, what is monitored, sync status | "Photo will be compared with your approved reference photo" | "This device will monitor your activity" |
| `partial` | "Monitoring active" (no details) | "Identity verification required" | "Connect to your device" |
| `covert` | N/A — not applicable to desktop agent (always visible in tray) | N/A — verification always requires interaction | Standard login |

**Important:** The desktop agent is always visible in the system tray and Task Manager. There is no covert/hidden mode. See [[modules/agent-gateway/tamper-resistance|Tamper Resistance]] for the reasoning.

The transparency level comes from the policy (see [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]]) and is communicated to the TrayApp via the `policy_updated` IPC message (see [[modules/agent-gateway/ipc-protocol|Ipc Protocol]]).

---

## XAML Guidelines

### Design Principles

- **Minimal and functional** — the agent is not the main product. Keep UI small and unobtrusive.
- **No branding customization** — uses ONEVO brand colors. Tenant branding applies to the web dashboard only.
- **System-native feel** — follow Windows 11 design language (rounded corners, Segoe UI font, subtle shadows).
- **Accessible** — support high-contrast mode, keyboard navigation, screen readers.

### Color Palette

```xml
<!-- ONEVO.Agent.TrayApp/Resources/Styles.xaml -->
<ResourceDictionary>
    <Color x:Key="PrimaryColor">#2563EB</Color>          <!-- Blue -->
    <Color x:Key="SuccessColor">#16A34A</Color>           <!-- Green -->
    <Color x:Key="ErrorColor">#DC2626</Color>             <!-- Red -->
    <Color x:Key="WarningColor">#F59E0B</Color>           <!-- Orange -->
    <Color x:Key="TextPrimary">#1F2937</Color>            <!-- Dark gray -->
    <Color x:Key="TextSecondary">#6B7280</Color>          <!-- Medium gray -->
    <Color x:Key="BackgroundColor">#FFFFFF</Color>        <!-- White -->
    <Color x:Key="SurfaceColor">#F9FAFB</Color>           <!-- Light gray -->
</ResourceDictionary>
```

### Window Sizing

| Window | Size | Position |
|:-------|:-----|:---------|
| Login | 400 x 450 | Center screen |
| Status popup | 380 x 520 | Center screen |
| Photo capture | 480 x 560 | Center screen, topmost |

All windows are non-resizable. The TrayApp does not have a main window — it runs entirely from the system tray.

---

## Related

- [[modules/identity-verification/photo-capture|Photo Capture]] — Photo capture flow, quality requirements, privacy
- [[modules/agent-gateway/ipc-protocol|Ipc Protocol]] — All IPC messages between TrayApp and Service
- [[modules/agent-gateway/agent-overview|Agent Overview]] — Architecture overview (TrayApp is one of three components)
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — Server endpoints called via the Service
- [[modules/agent-gateway/mock-mode|Mock Mode]] — TrayApp works identically in mock mode
- [[modules/agent-gateway/agent-installer|Agent Installer]] — TrayApp starts via MSIX startup task
- [[modules/agent-gateway/tamper-resistance|Tamper Resistance]] — Why the agent is always visible
- [[AI_CONTEXT/rules|Rules]] — Section 10: Desktop Agent Rules (UI thread rules)
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]] — Implementation task
