# AWS Rekognition Identity Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current simple photo comparison in `VerificationService` with a 4-step AWS Rekognition pipeline: face quality check → liveness signals → face match → environment context detection.

**Architecture:** All AWS logic lives in the backend (.NET 9). `IRekognitionService` (Application layer interface) is implemented by `AwsRekognitionService` (Infrastructure layer). `RekognitionVerificationService` orchestrates the 4-step pipeline and is called from the existing `VerificationService`. MAUI TrayApp is unchanged.

**Tech Stack:** `AWSSDK.Rekognition`, `AWSSDK.Core`, Polly (already in project), EF Core migrations, MediatR domain events, xUnit + Moq + FluentAssertions.

---

## Prerequisites (Manual — Do Before Task 1)

1. Create AWS account at https://aws.amazon.com
2. IAM → Users → Create User (programmatic only, no console)
3. Attach inline policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "rekognition:DetectFaces",
      "rekognition:CompareFaces",
      "rekognition:DetectLabels"
    ],
    "Resource": "*"
  }]
}
```
4. Generate access key pair → copy `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
5. Add to Railway environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` (e.g. `ap-southeast-1`)
6. Add to local `appsettings.Development.json` for dev/test

---

## File Map

| Action | File |
|:-------|:-----|
| Create | `src/ONEVO.Domain/ValueObjects/EnvironmentLabel.cs` |
| Create | `src/ONEVO.Application/Configuration/RekognitionOptions.cs` |
| Create | `src/ONEVO.Application/Contracts/IRekognitionService.cs` |
| Create | `src/ONEVO.Application/Contracts/IBlobStorage.cs` |
| Create | `src/ONEVO.Application/Models/RekognitionModels.cs` |
| Create | `src/ONEVO.Application/Models/VerificationPipelineResult.cs` |
| Create | `src/ONEVO.Application/Services/RekognitionVerificationService.cs` |
| Create | `src/ONEVO.Domain/Events/SuspiciousEnvironmentDetectedEvent.cs` |
| Create | `src/ONEVO.Infrastructure/Services/AwsRekognitionService.cs` |
| Create | `src/ONEVO.Infrastructure/Persistence/Migrations/<timestamp>_AddEnvironmentContextToVerificationRecords.cs` |
| Modify | `src/ONEVO.Infrastructure/DependencyInjection.cs` |
| Modify | `src/ONEVO.Api/appsettings.json` |
| Modify | `src/ONEVO.Application/Services/VerificationService.cs` |
| Modify | `src/ONEVO.Domain/Entities/VerificationRecord.cs` |
| Create | `tests/ONEVO.Tests.Unit/Modules/IdentityVerification/RekognitionVerificationServiceTests.cs` |
| Create | `tests/ONEVO.Tests.Unit/Infrastructure/AwsRekognitionServiceTests.cs` |
| Modify | `modules/identity-verification/photo-capture.md` |
| Modify | `modules/identity-verification/photo-verification/overview.md` |

---

## Task 1: Install NuGet Package and Add Configuration

**Files:**
- Modify: `src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj`
- Create: `src/ONEVO.Application/Configuration/RekognitionOptions.cs`
- Modify: `src/ONEVO.Api/appsettings.json`

- [ ] **Step 1: Add AWSSDK.Rekognition NuGet package**

```bash
cd src/ONEVO.Infrastructure
dotnet add package AWSSDK.Rekognition
dotnet add package AWSSDK.Core
```

Expected output: packages added, no errors.

- [ ] **Step 2: Create RekognitionOptions**

Create `src/ONEVO.Application/Configuration/RekognitionOptions.cs`:

```csharp
namespace ONEVO.Application.Configuration;

public class RekognitionOptions
{
    public float FaceMatchThreshold { get; set; } = 80f;
    public float QualitySharpnessThreshold { get; set; } = 50f;
    public float QualityBrightnessThreshold { get; set; } = 40f;
    public float FaceConfidenceThreshold { get; set; } = 90f;
    public float MaxPoseDegrees { get; set; } = 30f;
}
```

- [ ] **Step 3: Add Rekognition section to appsettings.json**

In `src/ONEVO.Api/appsettings.json`, add inside the root JSON object:

```json
"Rekognition": {
  "FaceMatchThreshold": 80,
  "QualitySharpnessThreshold": 50,
  "QualityBrightnessThreshold": 40,
  "FaceConfidenceThreshold": 90,
  "MaxPoseDegrees": 30
}
```

- [ ] **Step 4: Verify build**

```bash
cd src/ONEVO.Infrastructure
dotnet build
```

Expected: Build succeeded, 0 errors.

- [ ] **Step 5: Commit**

```bash
git add src/ONEVO.Infrastructure/ONEVO.Infrastructure.csproj \
        src/ONEVO.Application/Configuration/RekognitionOptions.cs \
        src/ONEVO.Api/appsettings.json
git commit -m "feat: add AWSSDK.Rekognition package and RekognitionOptions config"
```

---

## Task 2: Define IRekognitionService Interface and Models

**Files:**
- Create: `src/ONEVO.Domain/ValueObjects/EnvironmentLabel.cs`
- Create: `src/ONEVO.Application/Contracts/IRekognitionService.cs`
- Create: `src/ONEVO.Application/Contracts/IBlobStorage.cs`
- Create: `src/ONEVO.Application/Models/RekognitionModels.cs`
- Create: `src/ONEVO.Application/Models/VerificationPipelineResult.cs`

- [ ] **Step 1: Create EnvironmentLabel value object in Domain**

Create `src/ONEVO.Domain/ValueObjects/EnvironmentLabel.cs`:

```csharp
namespace ONEVO.Domain.ValueObjects;

public record EnvironmentLabel(string Name, float Confidence);
```

This lives in Domain so both Domain events and Application services can reference it without a layer violation.

- [ ] **Step 2: Create IBlobStorage contract**

Create `src/ONEVO.Application/Contracts/IBlobStorage.cs`:

```csharp
namespace ONEVO.Application.Contracts;

public interface IBlobStorage
{
    Task<Stream> DownloadFileAsync(string key, CancellationToken ct = default);
}
```

- [ ] **Step 3: Create shared model types**

Create `src/ONEVO.Application/Models/RekognitionModels.cs`:

```csharp
using ONEVO.Domain.ValueObjects;

namespace ONEVO.Application.Models;

public record DetectFacesResult(
    bool FaceFound,
    float Confidence,
    float Sharpness,
    float Brightness,
    bool EyesOpen,
    bool HasSunglasses,
    float PoseYaw,
    float PosePitch,
    float PoseRoll);

public record CompareFacesResult(
    bool FaceMatched,
    float Similarity);

public record DetectLabelsResult(IReadOnlyList<EnvironmentLabel> Labels);
```

- [ ] **Step 4: Create VerificationPipelineResult**

Create `src/ONEVO.Application/Models/VerificationPipelineResult.cs`:

```csharp
namespace ONEVO.Application.Models;

public record VerificationPipelineResult(
    bool Success,
    float MatchConfidence,
    string? FailureReason,
    string EnvironmentContext,
    IReadOnlyList<EnvironmentLabel> EnvironmentLabels,
    bool Skipped = false)
{
    public static VerificationPipelineResult AwsSkipped() =>
        new(false, 0f, null, "unknown", Array.Empty<EnvironmentLabel>(), Skipped: true);
}
```

- [ ] **Step 5: Create IRekognitionService interface**

Create `src/ONEVO.Application/Contracts/IRekognitionService.cs`:

```csharp
using ONEVO.Application.Models;

namespace ONEVO.Application.Contracts;

public interface IRekognitionService
{
    Task<DetectFacesResult> DetectFacesAsync(byte[] imageBytes, CancellationToken ct = default);
    Task<CompareFacesResult> CompareFacesAsync(byte[] sourceBytes, byte[] targetBytes, CancellationToken ct = default);
    Task<DetectLabelsResult> DetectLabelsAsync(byte[] imageBytes, CancellationToken ct = default);
}
```

- [ ] **Step 6: Build Application and Domain layers**

```bash
cd src/ONEVO.Domain && dotnet build
cd ../ONEVO.Application && dotnet build
```

Expected: Both build succeeded, 0 errors.

- [ ] **Step 7: Commit**

```bash
git add src/ONEVO.Domain/ValueObjects/EnvironmentLabel.cs \
        src/ONEVO.Application/Configuration/RekognitionOptions.cs \
        src/ONEVO.Application/Contracts/IRekognitionService.cs \
        src/ONEVO.Application/Contracts/IBlobStorage.cs \
        src/ONEVO.Application/Models/RekognitionModels.cs \
        src/ONEVO.Application/Models/VerificationPipelineResult.cs
git commit -m "feat: add EnvironmentLabel (Domain), IBlobStorage, IRekognitionService, and Rekognition result models"
```

---

## Task 3: Implement AwsRekognitionService

**Files:**
- Create: `src/ONEVO.Infrastructure/Services/AwsRekognitionService.cs`
- Create: `tests/ONEVO.Tests.Unit/Infrastructure/AwsRekognitionServiceTests.cs`

- [ ] **Step 1: Write failing tests**

Create `tests/ONEVO.Tests.Unit/Infrastructure/AwsRekognitionServiceTests.cs`:

```csharp
using Amazon.Rekognition;
using Amazon.Rekognition.Model;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using ONEVO.Infrastructure.Services;
using Xunit;

namespace ONEVO.Tests.Unit.Infrastructure;

public class AwsRekognitionServiceTests
{
    private readonly Mock<IAmazonRekognition> _clientMock = new();
    private readonly AwsRekognitionService _sut;

    public AwsRekognitionServiceTests()
    {
        _sut = new AwsRekognitionService(_clientMock.Object, NullLogger<AwsRekognitionService>.Instance);
    }

    [Fact]
    public async Task DetectFacesAsync_NoFacesReturned_ReturnsFaceNotFound()
    {
        _clientMock.Setup(c => c.DetectFacesAsync(It.IsAny<DetectFacesRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectFacesResponse { FaceDetails = new List<FaceDetail>() });

        var result = await _sut.DetectFacesAsync(new byte[] { 1, 2, 3 });

        result.FaceFound.Should().BeFalse();
    }

    [Fact]
    public async Task DetectFacesAsync_FaceFound_MapsAllFields()
    {
        _clientMock.Setup(c => c.DetectFacesAsync(It.IsAny<DetectFacesRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectFacesResponse
            {
                FaceDetails = new List<FaceDetail>
                {
                    new()
                    {
                        Confidence = 99f,
                        Quality = new FaceQuality { Sharpness = 75f, Brightness = 65f },
                        EyesOpen = new EyeOpen { Value = true },
                        Sunglasses = new Sunglasses { Value = false },
                        Pose = new Pose { Yaw = 5f, Pitch = 3f, Roll = 2f }
                    }
                }
            });

        var result = await _sut.DetectFacesAsync(new byte[] { 1, 2, 3 });

        result.FaceFound.Should().BeTrue();
        result.Confidence.Should().Be(99f);
        result.Sharpness.Should().Be(75f);
        result.Brightness.Should().Be(65f);
        result.EyesOpen.Should().BeTrue();
        result.HasSunglasses.Should().BeFalse();
        result.PoseYaw.Should().Be(5f);
    }

    [Fact]
    public async Task CompareFacesAsync_NoMatchFound_ReturnsFaceNotMatched()
    {
        _clientMock.Setup(c => c.CompareFacesAsync(It.IsAny<CompareFacesRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new CompareFacesResponse { FaceMatches = new List<CompareFacesMatch>() });

        var result = await _sut.CompareFacesAsync(new byte[] { 1 }, new byte[] { 2 });

        result.FaceMatched.Should().BeFalse();
        result.Similarity.Should().Be(0f);
    }

    [Fact]
    public async Task CompareFacesAsync_MatchFound_ReturnsBestSimilarity()
    {
        _clientMock.Setup(c => c.CompareFacesAsync(It.IsAny<CompareFacesRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new CompareFacesResponse
            {
                FaceMatches = new List<CompareFacesMatch>
                {
                    new() { Similarity = 91f, Face = new ComparedFace() }
                }
            });

        var result = await _sut.CompareFacesAsync(new byte[] { 1 }, new byte[] { 2 });

        result.FaceMatched.Should().BeTrue();
        result.Similarity.Should().Be(91f);
    }

    [Fact]
    public async Task DetectLabelsAsync_ReturnsTopFiveLabels()
    {
        var labels = Enumerable.Range(1, 8).Select(i =>
            new Amazon.Rekognition.Model.Label { Name = $"Label{i}", Confidence = 90f - i }).ToList();

        _clientMock.Setup(c => c.DetectLabelsAsync(It.IsAny<DetectLabelsRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectLabelsResponse { Labels = labels });

        var result = await _sut.DetectLabelsAsync(new byte[] { 1 });

        result.Labels.Should().HaveCount(5);
        result.Labels[0].Name.Should().Be("Label1");
    }
}
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd tests/ONEVO.Tests.Unit
dotnet test --filter "FullyQualifiedName~AwsRekognitionServiceTests" -v minimal
```

Expected: FAIL with compilation errors (AwsRekognitionService not found).

- [ ] **Step 3: Implement AwsRekognitionService**

Create `src/ONEVO.Infrastructure/Services/AwsRekognitionService.cs`:

```csharp
using Amazon.Rekognition;
using Amazon.Rekognition.Model;
using Microsoft.Extensions.Logging;
using ONEVO.Application.Contracts;
using ONEVO.Application.Models;
using ONEVO.Domain.ValueObjects;

namespace ONEVO.Infrastructure.Services;

public class AwsRekognitionService : IRekognitionService
{
    private readonly IAmazonRekognition _client;
    private readonly ILogger<AwsRekognitionService> _logger;

    public AwsRekognitionService(IAmazonRekognition client, ILogger<AwsRekognitionService> logger)
    {
        _client = client;
        _logger = logger;
    }

    public async Task<DetectFacesResult> DetectFacesAsync(byte[] imageBytes, CancellationToken ct = default)
    {
        var response = await _client.DetectFacesAsync(new DetectFacesRequest
        {
            Image = new Image { Bytes = new MemoryStream(imageBytes) },
            Attributes = new List<string> { "ALL" }
        }, ct);

        if (response.FaceDetails.Count == 0)
            return new DetectFacesResult(false, 0, 0, 0, false, false, 0, 0, 0);

        var face = response.FaceDetails[0];
        return new DetectFacesResult(
            FaceFound: true,
            Confidence: face.Confidence,
            Sharpness: face.Quality.Sharpness,
            Brightness: face.Quality.Brightness,
            EyesOpen: face.EyesOpen.Value,
            HasSunglasses: face.Sunglasses.Value,
            PoseYaw: face.Pose.Yaw,
            PosePitch: face.Pose.Pitch,
            PoseRoll: face.Pose.Roll);
    }

    public async Task<CompareFacesResult> CompareFacesAsync(byte[] sourceBytes, byte[] targetBytes, CancellationToken ct = default)
    {
        var response = await _client.CompareFacesAsync(new CompareFacesRequest
        {
            SourceImage = new Image { Bytes = new MemoryStream(sourceBytes) },
            TargetImage = new Image { Bytes = new MemoryStream(targetBytes) },
            SimilarityThreshold = 0f
        }, ct);

        if (response.FaceMatches.Count == 0)
            return new CompareFacesResult(false, 0f);

        var best = response.FaceMatches.OrderByDescending(m => m.Similarity).First();
        return new CompareFacesResult(true, best.Similarity);
    }

    public async Task<DetectLabelsResult> DetectLabelsAsync(byte[] imageBytes, CancellationToken ct = default)
    {
        var response = await _client.DetectLabelsAsync(new DetectLabelsRequest
        {
            Image = new Image { Bytes = new MemoryStream(imageBytes) },
            MaxLabels = 10,
            MinConfidence = 60f
        }, ct);

        var labels = response.Labels
            .OrderByDescending(l => l.Confidence)
            .Take(5)
            .Select(l => new EnvironmentLabel(l.Name, l.Confidence))
            .ToList();

        return new DetectLabelsResult(labels);
    }
}
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
cd tests/ONEVO.Tests.Unit
dotnet test --filter "FullyQualifiedName~AwsRekognitionServiceTests" -v minimal
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/ONEVO.Infrastructure/Services/AwsRekognitionService.cs \
        tests/ONEVO.Tests.Unit/Infrastructure/AwsRekognitionServiceTests.cs
git commit -m "feat: implement AwsRekognitionService wrapping DetectFaces, CompareFaces, DetectLabels"
```

---

## Task 4: Add SuspiciousEnvironmentDetectedEvent Domain Event

**Files:**
- Create: `src/ONEVO.Domain/Events/SuspiciousEnvironmentDetectedEvent.cs`

- [ ] **Step 1: Create the domain event**

Create `src/ONEVO.Domain/Events/SuspiciousEnvironmentDetectedEvent.cs`:

```csharp
using MediatR;
using ONEVO.Domain.ValueObjects;

namespace ONEVO.Domain.Events;

public record SuspiciousEnvironmentDetectedEvent(
    Guid EmployeeId,
    Guid DeviceId,
    Guid VerificationRecordId,
    IReadOnlyList<EnvironmentLabel> EnvironmentLabels) : INotification;
```

- [ ] **Step 2: Build Domain layer**

```bash
cd src/ONEVO.Domain
dotnet build
```

Expected: Build succeeded, 0 errors.

- [ ] **Step 3: Commit**

```bash
git add src/ONEVO.Domain/Events/SuspiciousEnvironmentDetectedEvent.cs
git commit -m "feat: add SuspiciousEnvironmentDetectedEvent domain event"
```

---

## Task 5: Implement RekognitionVerificationService

**Files:**
- Create: `src/ONEVO.Application/Services/RekognitionVerificationService.cs`
- Create: `tests/ONEVO.Tests.Unit/Modules/IdentityVerification/RekognitionVerificationServiceTests.cs`

> **Note:** This service uses `IBlobStorage` (defined in Task 2) — not `IImportFileStorage`. `IImportFileStorage` belongs to the data-import module and must not be reused here.

- [ ] **Step 1: Write failing tests**

Create `tests/ONEVO.Tests.Unit/Modules/IdentityVerification/RekognitionVerificationServiceTests.cs`:

```csharp
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Moq;
using ONEVO.Application.Contracts;
using ONEVO.Application.Configuration;
using ONEVO.Application.Models;
using ONEVO.Application.Services;
using Xunit;

namespace ONEVO.Tests.Unit.Modules.IdentityVerification;

public class RekognitionVerificationServiceTests
{
    private readonly Mock<IRekognitionService> _rekognitionMock = new();
    private readonly Mock<IBlobStorage> _storageMock = new();
    private readonly RekognitionVerificationService _sut;

    private static readonly byte[] FakePhoto = new byte[] { 1, 2, 3 };
    private const string ProfileKey = "tenant/profile/photo.jpg";

    public RekognitionVerificationServiceTests()
    {
        var options = Options.Create(new RekognitionOptions());
        _sut = new RekognitionVerificationService(
            _rekognitionMock.Object,
            _storageMock.Object,
            options,
            NullLogger<RekognitionVerificationService>.Instance);
    }

    private void SetupGoodFace() =>
        _rekognitionMock.Setup(r => r.DetectFacesAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectFacesResult(true, 99f, 75f, 65f, true, false, 5f, 3f, 2f));

    private void SetupGoodMatch(float similarity = 90f)
    {
        _storageMock.Setup(s => s.DownloadFileAsync(ProfileKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync((Stream)new MemoryStream(new byte[] { 9, 8, 7 }));
        _rekognitionMock.Setup(r => r.CompareFacesAsync(It.IsAny<byte[]>(), FakePhoto, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new CompareFacesResult(true, similarity));
    }

    private void SetupWorkLabels() =>
        _rekognitionMock.Setup(r => r.DetectLabelsAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectLabelsResult(new[] { new EnvironmentLabel("Office", 95f) }));

    private void SetupSuspiciousLabels() =>
        _rekognitionMock.Setup(r => r.DetectLabelsAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectLabelsResult(new[] { new EnvironmentLabel("Car", 94f) }));

    [Fact]
    public async Task RunAsync_FaceNotFound_ReturnsPoorQuality()
    {
        _rekognitionMock.Setup(r => r.DetectFacesAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectFacesResult(false, 0, 0, 0, false, false, 0, 0, 0));
        SetupWorkLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.Success.Should().BeFalse();
        result.FailureReason.Should().Be("poor_quality");
    }

    [Fact]
    public async Task RunAsync_QualityBelowThreshold_ReturnsPoorQuality()
    {
        _rekognitionMock.Setup(r => r.DetectFacesAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectFacesResult(true, 99f, 20f, 65f, true, false, 5f, 3f, 2f)); // Sharpness=20 < 50
        SetupWorkLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.Success.Should().BeFalse();
        result.FailureReason.Should().Be("poor_quality");
    }

    [Fact]
    public async Task RunAsync_SunglassesDetected_ReturnsLivenessCheckFailed()
    {
        _rekognitionMock.Setup(r => r.DetectFacesAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectFacesResult(true, 99f, 75f, 65f, true, true, 5f, 3f, 2f)); // HasSunglasses=true
        SetupWorkLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.Success.Should().BeFalse();
        result.FailureReason.Should().Be("liveness_check_failed");
    }

    [Fact]
    public async Task RunAsync_EyesClosed_ReturnsLivenessCheckFailed()
    {
        _rekognitionMock.Setup(r => r.DetectFacesAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectFacesResult(true, 99f, 75f, 65f, false, false, 5f, 3f, 2f)); // EyesOpen=false
        SetupWorkLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.FailureReason.Should().Be("liveness_check_failed");
    }

    [Fact]
    public async Task RunAsync_ExcessivePose_ReturnsLivenessCheckFailed()
    {
        _rekognitionMock.Setup(r => r.DetectFacesAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DetectFacesResult(true, 99f, 75f, 65f, true, false, 45f, 3f, 2f)); // Yaw=45 > 30
        SetupWorkLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.FailureReason.Should().Be("liveness_check_failed");
    }

    [Fact]
    public async Task RunAsync_ProfilePhotoMissing_ReturnsNoProfilePhoto()
    {
        SetupGoodFace();
        _storageMock.Setup(s => s.DownloadFileAsync(ProfileKey, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new FileNotFoundException("Profile photo not found"));
        SetupWorkLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.Success.Should().BeFalse();
        result.FailureReason.Should().Be("no_profile_photo");
    }

    [Fact]
    public async Task RunAsync_SimilarityBelowThreshold_ReturnsIdentityMismatch()
    {
        SetupGoodFace();
        SetupGoodMatch(similarity: 50f); // below default 80
        SetupWorkLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.Success.Should().BeFalse();
        result.FailureReason.Should().Be("identity_mismatch");
    }

    [Fact]
    public async Task RunAsync_AllChecksPassed_ReturnsSuccess()
    {
        SetupGoodFace();
        SetupGoodMatch(similarity: 92f);
        SetupWorkLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.Success.Should().BeTrue();
        result.MatchConfidence.Should().Be(92f);
        result.FailureReason.Should().BeNull();
    }

    [Fact]
    public async Task RunAsync_SuspiciousEnvironment_SetsContextToSuspicious()
    {
        SetupGoodFace();
        SetupGoodMatch();
        SetupSuspiciousLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.EnvironmentContext.Should().Be("suspicious");
        result.EnvironmentLabels.Should().ContainSingle(l => l.Name == "Car");
    }

    [Fact]
    public async Task RunAsync_WorkEnvironment_SetsContextToWork()
    {
        SetupGoodFace();
        SetupGoodMatch();
        SetupWorkLabels();

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.EnvironmentContext.Should().Be("work");
    }

    [Fact]
    public async Task RunAsync_AwsDetectFacesFails_ReturnsSkipped()
    {
        _rekognitionMock.Setup(r => r.DetectFacesAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new AmazonRekognitionException("Service unavailable"));

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.Skipped.Should().BeTrue();
        result.EnvironmentContext.Should().Be("unknown");
    }

    [Fact]
    public async Task RunAsync_DetectLabelsFails_EnvironmentContextIsUnknown()
    {
        SetupGoodFace();
        SetupGoodMatch();
        _rekognitionMock.Setup(r => r.DetectLabelsAsync(FakePhoto, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new AmazonRekognitionException("Service unavailable"));

        var result = await _sut.RunAsync(FakePhoto, ProfileKey);

        result.EnvironmentContext.Should().Be("unknown");
        result.Success.Should().BeTrue(); // labels failure does not fail verification
    }
}
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd tests/ONEVO.Tests.Unit
dotnet test --filter "FullyQualifiedName~RekognitionVerificationServiceTests" -v minimal
```

Expected: FAIL with compilation errors (RekognitionVerificationService not found).

- [ ] **Step 3: Implement RekognitionVerificationService**

Create `src/ONEVO.Application/Services/RekognitionVerificationService.cs`:

```csharp
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using ONEVO.Application.Configuration;
using ONEVO.Application.Contracts;
using ONEVO.Application.Models;
using ONEVO.Domain.ValueObjects;

namespace ONEVO.Application.Services;

public class RekognitionVerificationService
{
    private static readonly HashSet<string> NonWorkLabels = new(StringComparer.OrdinalIgnoreCase)
    {
        "Car", "Vehicle", "Automobile", "Outdoor", "Outdoors", "Road", "Street",
        "Restaurant", "Food", "Bedroom", "Bar", "Nightclub", "Beach", "Park"
    };

    private static readonly HashSet<string> WorkLabels = new(StringComparer.OrdinalIgnoreCase)
    {
        "Office", "Computer", "Laptop", "Desk", "Monitor", "Screen",
        "Chair", "Interior Design", "Furniture", "Indoors"
    };

    private readonly IRekognitionService _rekognition;
    private readonly IBlobStorage _storage;
    private readonly IOptions<RekognitionOptions> _options;
    private readonly ILogger<RekognitionVerificationService> _logger;

    public RekognitionVerificationService(
        IRekognitionService rekognition,
        IBlobStorage storage,
        IOptions<RekognitionOptions> options,
        ILogger<RekognitionVerificationService> logger)
    {
        _rekognition = rekognition;
        _storage = storage;
        _options = options;
        _logger = logger;
    }

    public async Task<VerificationPipelineResult> RunAsync(
        byte[] capturedPhotoBytes,
        string profilePhotoKey,
        CancellationToken ct = default)
    {
        var opts = _options.Value;

        // Step 1: DetectFaces — quality + liveness signals
        DetectFacesResult faceResult;
        try
        {
            faceResult = await _rekognition.DetectFacesAsync(capturedPhotoBytes, ct);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "AWS DetectFaces unavailable — skipping verification");
            return VerificationPipelineResult.AwsSkipped();
        }

        if (!faceResult.FaceFound
            || faceResult.Confidence < opts.FaceConfidenceThreshold
            || faceResult.Sharpness < opts.QualitySharpnessThreshold
            || faceResult.Brightness < opts.QualityBrightnessThreshold)
        {
            return await BuildResultAsync(capturedPhotoBytes, 0f, "poor_quality", ct);
        }

        if (!faceResult.EyesOpen
            || faceResult.HasSunglasses
            || Math.Abs(faceResult.PoseYaw) > opts.MaxPoseDegrees
            || Math.Abs(faceResult.PosePitch) > opts.MaxPoseDegrees)
        {
            return await BuildResultAsync(capturedPhotoBytes, 0f, "liveness_check_failed", ct);
        }

        // Step 2: Fetch profile photo bytes from blob storage
        byte[] profileBytes;
        try
        {
            using var stream = await _storage.DownloadFileAsync(profilePhotoKey, ct);
            using var ms = new MemoryStream();
            await stream.CopyToAsync(ms, ct);
            profileBytes = ms.ToArray();
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Profile photo not found for key {Key}", profilePhotoKey);
            return await BuildResultAsync(capturedPhotoBytes, 0f, "no_profile_photo", ct);
        }

        // Step 3: CompareFaces — face matching
        CompareFacesResult compareResult;
        try
        {
            compareResult = await _rekognition.CompareFacesAsync(profileBytes, capturedPhotoBytes, ct);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "AWS CompareFaces unavailable — skipping verification");
            return VerificationPipelineResult.AwsSkipped();
        }

        var similarity = compareResult.FaceMatched ? compareResult.Similarity : 0f;
        var failureReason = (!compareResult.FaceMatched || similarity < opts.FaceMatchThreshold)
            ? "identity_mismatch"
            : null;

        return await BuildResultAsync(capturedPhotoBytes, similarity, failureReason, ct);
    }

    private async Task<VerificationPipelineResult> BuildResultAsync(
        byte[] imageBytes,
        float matchConfidence,
        string? failureReason,
        CancellationToken ct)
    {
        // Step 4: DetectLabels — always runs, never blocks
        DetectLabelsResult labelsResult;
        try
        {
            labelsResult = await _rekognition.DetectLabelsAsync(imageBytes, ct);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "AWS DetectLabels unavailable — environment context unknown");
            labelsResult = new DetectLabelsResult(Array.Empty<EnvironmentLabel>());
        }

        var environmentContext = ClassifyEnvironment(labelsResult.Labels);

        return new VerificationPipelineResult(
            Success: failureReason == null,
            MatchConfidence: matchConfidence,
            FailureReason: failureReason,
            EnvironmentContext: environmentContext,
            EnvironmentLabels: labelsResult.Labels);
    }

    private static string ClassifyEnvironment(IReadOnlyList<EnvironmentLabel> labels)
    {
        if (labels.Any(l => NonWorkLabels.Contains(l.Name)))
            return "suspicious";
        if (labels.Any(l => WorkLabels.Contains(l.Name)))
            return "work";
        return "unknown";
    }
}
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
cd tests/ONEVO.Tests.Unit
dotnet test --filter "FullyQualifiedName~RekognitionVerificationServiceTests" -v minimal
```

Expected: 11 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/ONEVO.Application/Services/RekognitionVerificationService.cs \
        tests/ONEVO.Tests.Unit/Modules/IdentityVerification/RekognitionVerificationServiceTests.cs
git commit -m "feat: implement RekognitionVerificationService with 4-step pipeline"
```

---

## Task 6: EF Core Migration — Add Environment Columns

**Files:**
- Modify: `src/ONEVO.Domain/Entities/VerificationRecord.cs`
- Create: `src/ONEVO.Infrastructure/Persistence/Migrations/<timestamp>_AddEnvironmentContextToVerificationRecords.cs`

- [ ] **Step 1: Add new properties to VerificationRecord entity**

In `src/ONEVO.Domain/Entities/VerificationRecord.cs`, add these two properties to the class body:

```csharp
public string? EnvironmentContext { get; set; }  // "work" | "suspicious" | "unknown"
public string? EnvironmentLabels { get; set; }   // JSON: [{name, confidence}]
```

- [ ] **Step 2: Generate EF Core migration**

```bash
cd src/ONEVO.Api
dotnet ef migrations add AddEnvironmentContextToVerificationRecords \
  --project ../ONEVO.Infrastructure \
  --startup-project . \
  --output-dir Persistence/Migrations
```

Expected: Migration file created in `src/ONEVO.Infrastructure/Persistence/Migrations/`.

- [ ] **Step 3: Verify the generated migration**

Open the generated migration file and confirm it contains:

```csharp
migrationBuilder.AddColumn<string>(
    name: "environment_context",
    table: "verification_records",
    type: "character varying(20)",
    maxLength: 20,
    nullable: true);

migrationBuilder.AddColumn<string>(
    name: "environment_labels",
    table: "verification_records",
    type: "jsonb",
    nullable: true);
```

If the types are wrong, edit them manually to match the above.

- [ ] **Step 4: Build to verify**

```bash
cd src/ONEVO.Infrastructure
dotnet build
```

Expected: Build succeeded, 0 errors.

- [ ] **Step 5: Commit**

```bash
git add src/ONEVO.Domain/Entities/VerificationRecord.cs \
        src/ONEVO.Infrastructure/Persistence/Migrations/
git commit -m "feat: add environment_context and environment_labels columns to verification_records"
```

---

## Task 7: Wire Pipeline into VerificationService and Register DI

**Files:**
- Modify: `src/ONEVO.Application/Services/VerificationService.cs`
- Modify: `src/ONEVO.Infrastructure/DependencyInjection.cs`

- [ ] **Step 1: Inject RekognitionVerificationService into VerificationService**

In `src/ONEVO.Application/Services/VerificationService.cs`, add the dependency and replace the simple comparison block:

Add to constructor parameters:
```csharp
private readonly RekognitionVerificationService _rekognitionPipeline;
```

Replace the existing Step 4 (simple comparison) in `VerifyPhotoAsync`:

```csharp
// Step 4: Run Rekognition pipeline
var pipeline = await _rekognitionPipeline.RunAsync(
    capturedPhotoBytes,   // byte[] of the uploaded photo
    employee.ProfilePhotoKey,  // blob storage key for profile photo
    ct);

// If AWS was unavailable (Skipped), log and return without writing a record
if (pipeline.Skipped)
{
    _logger.LogWarning("Rekognition unavailable for employee {EmployeeId} — verification skipped", employeeId);
    return Result.Success<VerificationDto>(null);
}

// Step 5: Determine status from pipeline result
var status = pipeline.Success ? "verified" : "failed";
var matchConfidence = pipeline.MatchConfidence;

// Step 6: INSERT verification_record
var record = new VerificationRecord
{
    EmployeeId = employeeId,
    DeviceId = deviceId,
    Method = "photo",
    PhotoFileId = photoFileId,
    MatchConfidence = (int)matchConfidence,
    Status = status,
    FailureReason = pipeline.FailureReason,
    EnvironmentContext = pipeline.EnvironmentContext,
    EnvironmentLabels = pipeline.EnvironmentLabels.Count > 0
        ? System.Text.Json.JsonSerializer.Serialize(pipeline.EnvironmentLabels)
        : null,
    VerifiedAt = DateTime.UtcNow
};
await _repository.AddAsync(record, ct);
await _unitOfWork.SaveChangesAsync(ct);

// Step 7: Publish domain events
if (!pipeline.Success)
{
    await _publisher.Publish(new VerificationFailedEvent(employeeId, deviceId, record.Id, pipeline.FailureReason), ct);
}
else
{
    await _publisher.Publish(new VerificationCompletedEvent(employeeId, deviceId, record.Id), ct);
}

if (pipeline.EnvironmentContext == "suspicious")
{
    await _publisher.Publish(new SuspiciousEnvironmentDetectedEvent(
        employeeId, deviceId, record.Id, pipeline.EnvironmentLabels), ct);
}
```

- [ ] **Step 2: Register new services in DI**

In `src/ONEVO.Infrastructure/DependencyInjection.cs`, add inside `AddInfrastructure`:

```csharp
using Amazon;
using Amazon.Rekognition;
using ONEVO.Application.Configuration;
using ONEVO.Application.Contracts;
using ONEVO.Application.Services;
using ONEVO.Infrastructure.Services;

// AWS Rekognition — RekognitionOptions lives in Application layer, not Infrastructure
services.Configure<RekognitionOptions>(config.GetSection("Rekognition"));

var rekognitionConfig = new AmazonRekognitionConfig
{
    RegionEndpoint = RegionEndpoint.GetBySystemName(
        config["AWS_REGION"] ?? "ap-southeast-1")
};
services.AddSingleton<IAmazonRekognition>(new AmazonRekognitionClient(
    config["AWS_ACCESS_KEY_ID"],
    config["AWS_SECRET_ACCESS_KEY"],
    rekognitionConfig));

services.AddScoped<IRekognitionService, AwsRekognitionService>();
services.AddScoped<RekognitionVerificationService>();

// IBlobStorage — register the existing blob storage implementation against this contract.
// If MinIO/S3 storage is already registered under a different interface, add an adapter here.
// Example: services.AddScoped<IBlobStorage, MinioStorageService>();
```

- [ ] **Step 3: Build entire solution**

```bash
cd src/ONEVO.Api
dotnet build
```

Expected: Build succeeded, 0 errors.

- [ ] **Step 4: Run all existing VerificationService tests**

```bash
cd tests/ONEVO.Tests.Unit
dotnet test --filter "FullyQualifiedName~VerificationServiceTests" -v minimal
```

Expected: All existing tests pass (they mock IRekognitionService, so they are unaffected).

- [ ] **Step 5: Commit**

```bash
git add src/ONEVO.Application/Services/VerificationService.cs \
        src/ONEVO.Infrastructure/DependencyInjection.cs
git commit -m "feat: wire RekognitionVerificationService into VerificationService and DI"
```

---

## Task 8: Update Module Docs

**Files:**
- Modify: `modules/identity-verification/photo-capture.md`
- Modify: `modules/identity-verification/photo-verification/overview.md`
- Modify: `modules/identity-verification/photo-verification/end-to-end-logic.md`

- [ ] **Step 1: Update photo-capture.md**

In `modules/identity-verification/photo-capture.md`, replace:

```
- **Face detection:** Optional Phase 2 — basic face detection before sending
```

With:

```
- **Face detection:** Phase 1 — AWS Rekognition 4-step pipeline (quality + liveness signals + face match + environment context). See `docs/superpowers/specs/2026-04-29-aws-rekognition-verification-design.md`.
```

- [ ] **Step 2: Update photo-verification/overview.md**

In `modules/identity-verification/photo-verification/overview.md`, replace:

```
Verifies employee identity via photo capture from desktop agent. Phase 1 uses simple comparison, Phase 2 may add ML matching.
```

With:

```
Verifies employee identity via photo capture from desktop agent using AWS Rekognition: DetectFaces (quality + liveness) → CompareFaces (face match) → DetectLabels (environment context).
```

- [ ] **Step 3: Update end-to-end-logic.md**

In `modules/identity-verification/photo-verification/end-to-end-logic.md`, replace:

```
      -> 4. Compare captured photo vs profile photo
         -> Phase 1: Simple comparison service (basic similarity)
         -> Phase 2: ML-based facial recognition
      -> 5. Calculate match_confidence (0-100)
```

With:

```
      -> 4. Run RekognitionVerificationService pipeline:
         -> Step 1: DetectFaces — quality check + liveness signals
         -> Step 2: Fetch profile photo bytes from blob storage
         -> Step 3: CompareFaces — similarity score (0-100)
         -> Step 4: DetectLabels — environment context (always runs)
      -> 5. match_confidence = CompareFaces Similarity score (0-100)
```

- [ ] **Step 4: Commit**

```bash
git add modules/identity-verification/photo-capture.md \
        modules/identity-verification/photo-verification/overview.md \
        modules/identity-verification/photo-verification/end-to-end-logic.md
git commit -m "docs: update identity verification docs — Rekognition pipeline is Phase 1"
```

---

## Final Verification

- [ ] Run all tests:
```bash
cd tests/ONEVO.Tests.Unit
dotnet test -v minimal
```
Expected: All tests pass, 0 failures.

- [ ] Run full solution build:
```bash
cd src/ONEVO.Api
dotnet build
```
Expected: Build succeeded, 0 errors.

- [ ] Apply migration to local dev database:
```bash
cd src/ONEVO.Api
dotnet ef database update
```
Expected: Migration applied successfully.
