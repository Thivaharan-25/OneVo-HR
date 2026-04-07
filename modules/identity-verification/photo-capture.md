# Photo Capture & Identity Verification

## Flow

```
Server Policy says "verify now"
  → Service sends IPC message to MAUI app: "capture_photo"
  → MAUI app opens camera, captures photo
  → MAUI sends photo path back to Service via IPC
  → Service sends photo to Agent Gateway
  → Server compares with employee profile photo
  → Server creates verification_record (verified/failed)
```

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
        // Use MediaPicker (MAUI built-in)
        var photo = await MediaPicker.Default.CapturePhotoAsync(new MediaPickerOptions
        {
            Title = "Identity Verification"
        });
        
        if (photo == null) return null; // User cancelled
        
        // Save to temp location
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
- **Face detection:** Optional Phase 2 — basic face detection before sending

## Privacy

- Photo is captured ONLY when policy requires it
- Photo is sent to server immediately after capture
- Local photo file is **deleted** after successful upload confirmation
- If upload fails, photo stays in temp (encrypted) and retries on next sync
- Photos are classified as **RESTRICTED** data

## User Experience

When verification is triggered:
1. Tray icon flashes/notification appears: "Identity verification required"
2. Small camera window opens (not full screen)
3. User sees their camera feed + "Capture" button
4. Photo is taken, window closes
5. If user ignores for 2 minutes → `skipped` status sent to server
6. If user dismisses → `skipped` status sent to server

**Transparency mode affects UX:**
- `full_transparency`: Shows "Verification photo will be compared with your profile photo"
- `partial`: Shows "Identity verification required"
- `covert`: Not applicable — verification always requires user interaction (can't be covert)

## Related

- [[identity-verification|Identity Verification Module]] — parent module
- [[photo-verification]] — server-side photo comparison
- [[verification-policies]] — when photos are required
- [[biometric-enrollment]] — profile photo enrollment
- [[agent-server-protocol]] — IPC communication
- [[data-classification]] — RESTRICTED classification for photos
- [[compliance]] — privacy requirements
- [[WEEK3-identity-verification]] — implementation task
