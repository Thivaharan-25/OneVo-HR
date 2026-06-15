# Photo Capture & Identity Verification

## Flow

```
Server policy says "verify now"
  -> Service sends IPC message to MAUI app: "capture_photo"
  -> MAUI app opens camera and captures photo
  -> MAUI sends photo path back to Service via IPC
  -> Service sends photo to Agent Gateway
  -> Server compares with approved verification reference photo
  -> Server creates verification_record (verified/failed/skipped)
```

Normal verification compares captured photos against the approved reference photo, not a casual avatar/profile image.

## First Agent Sign-In Reference Enrollment

If identity verification is enabled but the employee has no approved `verification_reference_photos` row, the camera UI runs in **Reference Enrollment** mode during first TrayApp sign-in.

```
Employee signs in to TrayApp
  -> Backend resolves tenant + employee + policy
  -> Identity verification enabled
  -> No approved reference photo exists
  -> TrayApp shows required WorkPulse photo/biometric notice or consent if needed
  -> TrayApp captures first reference photo
  -> Backend stores verification_reference_photos.status = 'pending_review'
  -> Configured identity-verification resolver approves OR tenant auto-approval policy approves trusted SSO/MFA enrollment
  -> Future verification photos compare against this approved reference
```

The first captured photo is **enrollment**, not verification. It must not produce a failed-verification alert. Until approval, verification records should use `skipped` or `reference_pending`.

## Triggers

| Trigger | When | Policy Field |
|:--------|:-----|:-------------|
| Login verification | Employee logs in via tray app | `verification_on_login` |
| Logout verification | Employee logs out | `verification_on_logout` |
| Interval verification | Every N minutes | `verification_interval_minutes` |

## MAUI Camera Implementation

```csharp
public class CameraService
{
    public async Task<string?> CapturePhotoAsync(CancellationToken ct)
    {
        var photo = await MediaPicker.Default.CapturePhotoAsync(new MediaPickerOptions
        {
            Title = "Identity Verification"
        });

        if (photo == null) return null;

        var tempPath = Path.Combine(Path.GetTempPath(), $"onevo_verify_{Guid.NewGuid()}.jpg");
        using var stream = await photo.OpenReadAsync();
        using var fileStream = File.Create(tempPath);
        await stream.CopyToAsync(fileStream, ct);

        return tempPath;
    }
}
```

## Photo Quality Requirements

- **Resolution:** Minimum 640x480, recommended 1280x720
- **Format:** JPEG, quality 80%
- **Max size:** 500KB (resize if larger)
- **Lighting:** Warn user if image is too dark (basic luminance check)
- **Face detection:** Optional Phase 2 - basic face detection before sending

## Privacy

- Photo is captured ONLY when policy requires it or when first-sign-in reference enrollment is required.
- Photo is sent to server immediately after capture.
- Local photo file is **deleted** after successful upload confirmation.
- If upload fails, photo stays in temp storage and retries on next sync.
- Photos are classified as **RESTRICTED** data.

## User Experience

When verification is triggered:

1. Tray icon flashes/notification appears: "Identity verification required"
2. Small camera window opens (not full screen)
3. User sees their camera feed + "Capture" button
4. Photo is taken, window closes
5. If user ignores for 2 minutes -> `skipped` status sent to server
6. If user dismisses -> `skipped` status sent to server

When reference enrollment is triggered:

1. TrayApp shows "Reference photo enrollment required"
2. Employee captures the first reference photo
3. Agent shows "Reference photo pending review" until approval
4. No failed-verification alert is created while reference is missing or pending

**Transparency mode affects UX:**
- `full_transparency`: Shows "Verification photo will be compared with your approved reference photo"
- `partial`: Shows "Identity verification required"
- `covert`: Not applicable - verification always requires user interaction

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[modules/identity-verification/photo-verification/overview|Photo Verification]]
- [[modules/identity-verification/verification-policies/overview|Verification Policies]]
- [[modules/identity-verification/biometric-enrollment/overview|Biometric Enrollment]]
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
