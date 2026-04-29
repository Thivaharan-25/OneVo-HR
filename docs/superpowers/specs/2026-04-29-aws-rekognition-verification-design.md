# AWS Rekognition Identity Verification — Design Spec

**Date:** 2026-04-29  
**Status:** Approved  
**Phase:** 1  
**Module:** Identity Verification (`modules/identity-verification`)

---

## Prerequisites

Before any code is written, the following must exist:

1. **AWS account** — create at https://aws.amazon.com if not already done
2. **IAM user** — create a service account with the least-privilege policy in the Configuration section below (no console access, programmatic only)
3. **Access key pair** — generate `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` for the IAM user
4. **Region selected** — pick the AWS region closest to your Railway deployment (e.g., `ap-southeast-1` for Southeast Asia, `eu-west-1` for Europe)
5. **Secrets injected into Railway** — add the three env vars (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`) to the Railway service environment before deploying

---

## Overview

Replaces the current simple photo comparison in the Agent Gateway with a 4-step AWS Rekognition pipeline. The MAUI TrayApp is unchanged — it still captures a static JPEG and sends it to the backend. All AWS logic lives server-side.

---

## Pipeline

```
MAUI captures photo (PhotoCaptureWindow — unchanged)
  → POST /api/v1/verification/verify
  → RekognitionVerificationService
      │
      ├─ Step 1: DetectFaces
      │    • Face found? (confidence ≥ 90)
      │    • Quality: Sharpness ≥ 50, Brightness ≥ 40
      │    • Liveness signals: EyesOpen, no Sunglasses, Pose within ±30°
      │    ✗ Fail → failure_reason = "poor_quality" | "liveness_check_failed"
      │       → soft fail, employee continues
      │
      ├─ Step 2: Fetch employee profile photo bytes from Railway blob storage
      │    (only if Step 1 passes)
      │    • Download as byte stream via IImportFileStorage.DownloadFileAsync
      │    • Pass as Bytes to CompareFaces (not S3Object — Railway is MinIO, not AWS S3)
      │    • No enrollment changes required — profile photo stays in Railway blob storage
      │
      ├─ Step 3: CompareFaces
      │    • Similarity ≥ threshold (default 80, tenant-configurable)
      │    ✗ Fail → failure_reason = "identity_mismatch"
      │       → soft fail, employee continues
      │
      ├─ Step 4: DetectLabels (always runs — independent of Steps 1–3)
      │    • Non-work labels (Car, Outdoor, Restaurant, Bedroom, Bar)
      │      → environment_context = "suspicious"
      │      → publishes SuspiciousEnvironmentDetected to Exception Engine
      │    • Work labels (Office, Computer, Desk, Monitor)
      │      → environment_context = "work"
      │    • Neither → environment_context = "unknown"
      │
      └─ Write verification_record
           status:              verified | failed
           match_confidence:    0–100 (Similarity score from CompareFaces)
           failure_reason:      poor_quality | liveness_check_failed | identity_mismatch | no_profile_photo | null
           environment_context: work | suspicious | unknown
           environment_labels:  top 5 labels as JSONB
```

---

## New Backend Components

| Component | Location | Purpose |
|:----------|:---------|:--------|
| `IRekognitionService` | `Application/Contracts/IRekognitionService.cs` | Interface for AWS calls (mockable in tests) |
| `AwsRekognitionService` | `Infrastructure/Services/AwsRekognitionService.cs` | Wraps `AWSSDK.Rekognition` — DetectFaces, CompareFaces, DetectLabels |
| `RekognitionVerificationService` | `Application/Services/RekognitionVerificationService.cs` | Orchestrates 4-step pipeline, replaces current simple comparison |
| `VerificationPipelineResult` | `Application/Models/VerificationPipelineResult.cs` | Result record passed to command handler |

All components follow existing Clean Architecture layering:
- `IRekognitionService` in Application layer (no AWS dependency)
- `AwsRekognitionService` in Infrastructure layer (AWS SDK dependency)
- Registered via DI in `Infrastructure/DependencyInjection.cs`

---

## Data Model Changes

Two new columns on `verification_records` — no new tables:

```sql
ALTER TABLE verification_records
  ADD COLUMN environment_context  VARCHAR(20)  NULL,
  ADD COLUMN environment_labels   JSONB        NULL;
```

**`environment_labels` example:**
```json
[
  { "name": "Car", "confidence": 94.2 },
  { "name": "Vehicle", "confidence": 91.5 },
  { "name": "Outdoors", "confidence": 87.3 },
  { "name": "Road", "confidence": 72.1 },
  { "name": "Street", "confidence": 68.4 }
]
```

**`failure_reason` values (documented, column already exists):**
- `poor_quality` — DetectFaces quality thresholds not met
- `liveness_check_failed` — sunglasses, eyes closed, or pose > ±30°
- `identity_mismatch` — CompareFaces similarity below threshold
- `no_profile_photo` — employee has no enrolled profile photo in blob storage

---

## Configuration

**Environment variables (server-side only — never on agent devices):**
```
AWS_ACCESS_KEY_ID         = <from AWS IAM>
AWS_SECRET_ACCESS_KEY     = <from AWS IAM>
AWS_REGION                = ap-southeast-1
```

**`appsettings.json` thresholds (tenant-configurable via verification policy):**
```json
"Rekognition": {
  "FaceMatchThreshold": 80,
  "QualitySharpnessThreshold": 50,
  "QualityBrightnessThreshold": 40,
  "FaceConfidenceThreshold": 90,
  "MaxPoseDegrees": 30
}
```

**NuGet package:**
```
AWSSDK.Rekognition
```

**IAM policy — least privilege:**
```json
{
  "Effect": "Allow",
  "Action": [
    "rekognition:DetectFaces",
    "rekognition:CompareFaces",
    "rekognition:DetectLabels"
  ],
  "Resource": "*"
}
```

---

## Error Handling

| Failure | failure_reason | Employee Blocked | Exception Engine Alert |
|:--------|:--------------|:----------------|:----------------------|
| AWS unreachable / timeout | — | No | No — retry at next interval |
| No face detected | `poor_quality` | No | Yes — VerificationFailed |
| Quality check failed | `poor_quality` | No | Yes — VerificationFailed |
| Liveness check failed | `liveness_check_failed` | No | Yes — VerificationFailed |
| Profile photo missing | `no_profile_photo` | No | Yes — VerificationFailed |
| Face match below threshold | `identity_mismatch` | No | Yes — VerificationFailed |
| Suspicious environment | — | No | Yes — SuspiciousEnvironmentDetected |

**AWS call resilience (via existing Polly setup):**
- 2 retries with exponential backoff per call
- 5-second timeout per call
- All retries exhausted → log warning, skip verification, retry at next interval

**Photo cleanup:** unchanged — local JPEG deleted from MAUI temp after confirmed upload, regardless of pipeline result.

---

## Domain Events

| Event | When Published | Consumers |
|:------|:--------------|:----------|
| `VerificationFailed` | Steps 1–3 fail | Exception Engine, Notifications |
| `VerificationCompleted` | All steps pass | Workforce Presence |
| `SuspiciousEnvironmentDetected` | Step 4 detects non-work labels | Exception Engine |

`SuspiciousEnvironmentDetected` is a new event. It includes `employee_id`, `device_id`, `environment_labels`, and `verification_record_id`.

---

## What Does NOT Change

- MAUI TrayApp (`PhotoCaptureWindow`, `CameraService`) — no changes
- IPC protocol between TrayApp and Windows Service — no changes
- API endpoint path and request contract (`POST /api/v1/verification/verify`) — no changes
- Blob storage layout (`{tenantId}/{module}/{yyyy-MM}/{uuid}.jpg`) — no changes
- Existing `verification_records` columns — no changes

---

## Cost Shape

Rekognition is billed per API call. Three calls per verification (DetectFaces + CompareFaces + DetectLabels). At 100 employees verifying every 30 minutes over an 8-hour day: ~1,600 verifications/day → ~4,800 Rekognition calls/day per tenant. At AWS pricing (~$0.001 per call), roughly **$0.15/tenant/day** at that scale. Verify your expected employee count and verification interval before go-live.

---

## Docs to Update During Implementation

These existing docs describe photo verification as Phase 2 — they must be updated when this feature ships:

- `modules/identity-verification/photo-capture.md` — line: "Face detection: Optional Phase 2"
- `modules/identity-verification/photo-verification/overview.md` — line: "Phase 1 uses simple comparison, Phase 2 may add ML matching"

---

## Related

- `modules/identity-verification/photo-capture.md` — existing capture flow
- `modules/identity-verification/photo-verification/overview.md` — existing verification overview
- `infrastructure/file-storage.md` — blob storage interface
- `modules/agent-gateway/agent-overview.md` — WorkPulse Agent architecture
- `AI_CONTEXT/tech-stack.md` — backend stack (.NET 9, Polly, EF Core)
