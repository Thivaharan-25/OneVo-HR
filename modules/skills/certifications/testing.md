# Certifications — Testing

**Module:** Skills
**Feature:** Certifications
**Location:** `tests/ONEVO.Tests.Unit/Modules/Skills/CertificationServiceTests.cs`

---

## Unit Tests

```csharp
public class CertificationServiceTests
{
    private readonly Mock<ICertificationRepository> _repoMock = new();
    private readonly CertificationService _sut;

    [Fact]
    public async Task Add_certification_stores_file()
    {
        // Arrange
        // ... setup mocks for add certification stores file

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // File uploaded
    }

    [Fact]
    public async Task Expiry_job_sends_reminder_at_30_days()
    {
        // Arrange
        // ... setup mocks for expiry job sends reminder at 30 days

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Reminder sent
    }

    [Fact]
    public async Task Expired_cert_status_updated()
    {
        // Arrange
        // ... setup mocks for expired cert status updated

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = expired
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Add certification stores file | Unit | File uploaded |
| Expiry job sends reminder at 30 days | Unit | Reminder sent |
| Expired cert status updated | Unit | Status = expired |

## Related

- [[modules/skills/certifications/overview|Certifications]] — feature overview
- [[code-standards/testing-strategy|Testing Standards]] — project-wide testing conventions
