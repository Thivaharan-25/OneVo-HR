# Tray App UI — MAUI System Tray Application

## Overview

The MAUI Tray App (`ONEVO.Agent.TrayApp`) is the user-facing component of the desktop agent. It provides:
- System tray icon with status indication
- Employee login/logout
- Photo capture for identity verification
- Status popup showing collector and sync state
- Notification toasts for important events

The TrayApp communicates with the Windows Service via Named Pipes. See [[modules/agent-gateway/ipc-protocol|Ipc Protocol]] for the full message contract.

---

## System Tray Icon

The tray icon uses `CommunityToolkit.Maui` and changes appearance based on agent state.

### Icon States

| State | Icon | Tooltip | When |
|:------|:-----|:--------|:-----|
| **Disconnected** | Gray circle | "ONEVO Agent — Not connected" | Service not running or pipe disconnected |
| **Connected (no employee)** | Blue circle | "ONEVO Agent — No employee logged in" | Service running, no employee login |
| **Collecting** | Green circle | "ONEVO Agent — Monitoring active" | Employee logged in, collectors running |
| **Syncing** | Green circle with arrows | "ONEVO Agent — Syncing data..." | During active data upload |
| **Error** | Red circle with ! | "ONEVO Agent — Error (click for details)" | Sync failure, auth error, or service error |
| **Verification needed** | Orange circle with camera | "ONEVO Agent — Verification required" | Photo capture pending |

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

Right-clicking the tray icon shows:

| Menu Item | Action | Visibility |
|:----------|:-------|:-----------|
| **Status** | Opens status popup | Always |
| **Login** | Opens login window | When no employee logged in |
| **Logout** | Sends logout IPC message | When employee logged in |
| **About** | Shows version info | Always |

There is no "Exit" or "Quit" option. The agent is managed by IT — employees cannot stop it. The service continues running regardless of whether the TrayApp is open.

---

## Login Window

A modal window shown when the employee clicks "Login" from the tray menu or when the TrayApp first launches with no logged-in employee.

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
│  ✗ Screenshots (manager request only)  │
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
│    your profile photo                  │
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
| `full_transparency` | Full collector list, what is monitored, sync status | "Photo will be compared with your profile photo" | "This device will monitor your activity" |
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
