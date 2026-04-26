# HR Import Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a guided 7-step import wizard allowing new tenants to bulk-import employees + org structure from CSV/Excel files or PeopleHR API, replacing manual one-by-one employee creation.

**Architecture:** New `DataImport` module in the modular monolith handles ETL, PeopleHR adapter, bulk write, and reconciliation via Hangfire background jobs. Frontend wizard in Next.js App Router uses a Zustand state machine to drive 7 steps. Both phases are independent — backend can be built and tested before frontend starts.

**Tech Stack:** .NET 9 / ASP.NET Core / EF Core / Hangfire / PostgreSQL 16 / FluentValidation / xUnit + FluentAssertions (backend) · Next.js 14 / TypeScript / Tailwind / shadcn/ui / React Hook Form + Zod / TanStack Query / Zustand (frontend)

> ⚠️ **Spec note:** The design spec references BullMQ — this is a Node.js library and does not apply. Use **Hangfire Batch queue** instead. The spec also references Cloudflare R2 — use **Railway S3-compatible blob storage** (already in tech stack). If R2 is adopted later, the `IImportFileStorage` interface makes swapping trivial.

---

## Phase A — Backend

---

### Task 1: Database Migration — `migration_runs` table

**Files:**
- Create: `src/Modules/DataImport/Infrastructure/Persistence/Migrations/AddMigrationRunsTable.cs`
- Modify: `src/Modules/DataImport/Infrastructure/Persistence/DataImportDbContext.cs`

- [ ] **Step 1: Write the failing test**

```csharp
// tests/Modules/DataImport/Infrastructure/DataImportDbContextTests.cs
public class DataImportDbContextTests : IClassFixture<TestDatabaseFixture>
{
    [Fact]
    public async Task MigrationRuns_TableExists_AfterMigration()
    {
        var exists = await _db.Database.ExecuteSqlRawAsync(
            "SELECT 1 FROM information_schema.tables WHERE table_name = 'migration_runs'");
        Assert.Equal(1, exists);
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

```
dotnet test --filter "DataImportDbContextTests" -v normal
```
Expected: FAIL — table does not exist yet.

- [ ] **Step 3: Create the EF Core entity and migration**

```csharp
// src/Modules/DataImport/Domain/Entities/MigrationRun.cs
public class MigrationRun
{
    public Guid Id { get; private set; } = Guid.NewGuid();
    public Guid TenantId { get; private set; }
    public Guid InitiatedByUserId { get; private set; }
    public MigrationSource Source { get; private set; }
    public MigrationStatus Status { get; private set; } = MigrationStatus.Pending;
    public int TotalRows { get; private set; }
    public int ProcessedRows { get; private set; }
    public int SuccessRows { get; private set; }
    public int FailedRows { get; private set; }
    public int SkippedRows { get; private set; }
    public string? FileKey { get; private set; }
    public DateTime StartedAt { get; private set; } = DateTime.UtcNow;
    public DateTime? CompletedAt { get; private set; }
    public string? ErrorSummary { get; private set; }

    private MigrationRun() { }

    public static MigrationRun Create(Guid tenantId, Guid userId, MigrationSource source, string? fileKey = null)
        => new() { TenantId = tenantId, InitiatedByUserId = userId, Source = source, FileKey = fileKey };

    public void UpdateProgress(int processed, int success, int failed, int skipped)
    {
        ProcessedRows = processed; SuccessRows = success;
        FailedRows = failed; SkippedRows = skipped;
    }

    public void Complete() { Status = MigrationStatus.Completed; CompletedAt = DateTime.UtcNow; }
    public void Fail(string error) { Status = MigrationStatus.Failed; ErrorSummary = error; CompletedAt = DateTime.UtcNow; }
    public void SetTotal(int total) => TotalRows = total;
}

// src/Modules/DataImport/Domain/Enums/MigrationSource.cs
public enum MigrationSource { Csv, Excel, PeopleHr }

// src/Modules/DataImport/Domain/Enums/MigrationStatus.cs
public enum MigrationStatus { Pending, Processing, Completed, Failed, PartialSuccess }
```

```csharp
// src/Modules/DataImport/Infrastructure/Persistence/DataImportDbContext.cs
public class DataImportDbContext : DbContext
{
    public DbSet<MigrationRun> MigrationRuns => Set<MigrationRun>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<MigrationRun>(e =>
        {
            e.ToTable("migration_runs");
            e.HasKey(x => x.Id);
            e.Property(x => x.TenantId).IsRequired();
            e.Property(x => x.Source).HasConversion<string>();
            e.Property(x => x.Status).HasConversion<string>();
            e.HasIndex(x => x.TenantId);
        });
    }
}
```

Run migration:
```bash
dotnet ef migrations add AddMigrationRuns --project src/Modules/DataImport --context DataImportDbContext
dotnet ef database update --project src/Modules/DataImport --context DataImportDbContext
```

- [ ] **Step 4: Run test to verify it passes**

```
dotnet test --filter "DataImportDbContextTests" -v normal
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/Modules/DataImport/ tests/Modules/DataImport/Infrastructure/
git commit -m "feat(data-import): add migration_runs table and domain entities"
```

---

### Task 2: File Upload Infrastructure — Signed URL Generation

**Files:**
- Create: `src/Modules/DataImport/Infrastructure/FileStorage/IImportFileStorage.cs`
- Create: `src/Modules/DataImport/Infrastructure/FileStorage/S3ImportFileStorage.cs`
- Create: `tests/Modules/DataImport/Infrastructure/S3ImportFileStorageTests.cs`

- [ ] **Step 1: Write the failing test**

```csharp
// tests/Modules/DataImport/Infrastructure/S3ImportFileStorageTests.cs
public class S3ImportFileStorageTests
{
    [Fact]
    public async Task GenerateUploadUrl_ReturnsPresignedUrl_WithExpiry()
    {
        var storage = new S3ImportFileStorage(TestS3Config());
        var result = await storage.GenerateUploadUrlAsync("tenant-123", "employees.csv");

        Assert.NotNull(result.UploadUrl);
        Assert.NotNull(result.FileKey);
        Assert.Contains("tenant-123", result.FileKey);
        Assert.True(result.ExpiresAt > DateTime.UtcNow);
    }

    [Fact]
    public async Task DeleteFile_RemovesFileFromStorage()
    {
        var storage = new S3ImportFileStorage(TestS3Config());
        // Upload a test file first
        await storage.UploadTestFileAsync("test-key", "name,email\nJohn,john@test.com");
        await storage.DeleteFileAsync("test-key");
        var exists = await storage.FileExistsAsync("test-key");
        Assert.False(exists);
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

```
dotnet test --filter "S3ImportFileStorageTests" -v normal
```
Expected: FAIL — type not found.

- [ ] **Step 3: Implement the interface and S3 storage**

```csharp
// src/Modules/DataImport/Infrastructure/FileStorage/IImportFileStorage.cs
public interface IImportFileStorage
{
    Task<UploadUrlResult> GenerateUploadUrlAsync(string tenantId, string filename, CancellationToken ct = default);
    Task<Stream> DownloadFileAsync(string fileKey, CancellationToken ct = default);
    Task DeleteFileAsync(string fileKey, CancellationToken ct = default);
    Task<bool> FileExistsAsync(string fileKey, CancellationToken ct = default);
}

public record UploadUrlResult(string UploadUrl, string FileKey, DateTime ExpiresAt);
```

```csharp
// src/Modules/DataImport/Infrastructure/FileStorage/S3ImportFileStorage.cs
public class S3ImportFileStorage : IImportFileStorage
{
    private readonly IAmazonS3 _s3;
    private readonly string _bucket;
    private static readonly TimeSpan UrlExpiry = TimeSpan.FromHours(1);

    public S3ImportFileStorage(IOptions<S3Options> options, IAmazonS3 s3)
    {
        _s3 = s3;
        _bucket = options.Value.ImportBucket;
    }

    public async Task<UploadUrlResult> GenerateUploadUrlAsync(string tenantId, string filename, CancellationToken ct = default)
    {
        var ext = Path.GetExtension(filename).ToLowerInvariant();
        if (ext is not (".csv" or ".xlsx" or ".xls"))
            throw new ArgumentException("Only .csv, .xlsx, and .xls files are accepted. Email transfer is not supported.");

        var fileKey = $"imports/{tenantId}/{Guid.NewGuid()}{ext}";
        var request = new GetPreSignedUrlRequest
        {
            BucketName = _bucket,
            Key = fileKey,
            Verb = HttpVerb.PUT,
            Expires = DateTime.UtcNow.Add(UrlExpiry)
        };
        var url = _s3.GetPreSignedURL(request);
        return new UploadUrlResult(url, fileKey, DateTime.UtcNow.Add(UrlExpiry));
    }

    public async Task<Stream> DownloadFileAsync(string fileKey, CancellationToken ct = default)
    {
        var response = await _s3.GetObjectAsync(_bucket, fileKey, ct);
        return response.ResponseStream;
    }

    public async Task DeleteFileAsync(string fileKey, CancellationToken ct = default)
        => await _s3.DeleteObjectAsync(_bucket, fileKey, ct);

    public async Task<bool> FileExistsAsync(string fileKey, CancellationToken ct = default)
    {
        try { await _s3.GetObjectMetadataAsync(_bucket, fileKey, ct); return true; }
        catch (AmazonS3Exception e) when (e.StatusCode == HttpStatusCode.NotFound) { return false; }
    }
}
```

- [ ] **Step 4: Run tests**

```
dotnet test --filter "S3ImportFileStorageTests" -v normal
```
Expected: PASS (use LocalStack or MinIO for integration test)

- [ ] **Step 5: Commit**

```bash
git add src/Modules/DataImport/Infrastructure/FileStorage/ tests/Modules/DataImport/Infrastructure/S3ImportFileStorageTests.cs
git commit -m "feat(data-import): add S3 file storage for import uploads with signed URLs"
```

---

### Task 3: ETL Transform Service

**Files:**
- Create: `src/Modules/DataImport/Application/Services/EtlTransformService.cs`
- Create: `src/Modules/DataImport/Application/Models/RawImportRow.cs`
- Create: `src/Modules/DataImport/Application/Models/TransformedRow.cs`
- Create: `tests/Modules/DataImport/Application/EtlTransformServiceTests.cs`

- [ ] **Step 1: Write failing tests**

```csharp
// tests/Modules/DataImport/Application/EtlTransformServiceTests.cs
public class EtlTransformServiceTests
{
    private readonly EtlTransformService _sut = new();

    [Theory]
    [InlineData("01/03/2024", "2024-03-01")]
    [InlineData("2024-03-01", "2024-03-01")]
    [InlineData("03/01/2024", "2024-01-03")]
    public void NormaliseDate_ReturnsIso8601(string input, string expected)
    {
        var result = _sut.NormaliseDate(input);
        Assert.Equal(expected, result.Value.ToString("yyyy-MM-dd"));
    }

    [Theory]
    [InlineData("07911123456", "+44 7911 123456", "+447911123456")]
    [InlineData("+94771234567", null, "+94771234567")]
    [InlineData("not-a-phone", null, null)]
    public void NormalisePhone_ReturnsE164OrNull(string input, string? hint, string? expected)
    {
        var result = _sut.NormalisePhone(input, defaultCountryCode: hint != null ? "GB" : "LK");
        Assert.Equal(expected, result);
    }

    [Theory]
    [InlineData("50000", true)]
    [InlineData("50,000", true)]
    [InlineData("not-a-number", false)]
    public void ValidateSalary_ReturnsCorrectValidity(string input, bool expectedValid)
    {
        var (valid, _) = _sut.ValidateSalary(input);
        Assert.Equal(expectedValid, valid);
    }

    [Fact]
    public void DetectDuplicateEmails_FlagsRows()
    {
        var rows = new List<RawImportRow>
        {
            new() { RowNumber = 1, Fields = new() { ["email"] = "a@b.com" } },
            new() { RowNumber = 2, Fields = new() { ["email"] = "a@b.com" } },
            new() { RowNumber = 3, Fields = new() { ["email"] = "c@d.com" } },
        };
        var flags = _sut.DetectDuplicateEmails(rows, emailField: "email");
        Assert.Contains(2, flags); // Row 2 is the duplicate
        Assert.DoesNotContain(1, flags);
        Assert.DoesNotContain(3, flags);
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```
dotnet test --filter "EtlTransformServiceTests" -v normal
```
Expected: FAIL — EtlTransformService not found.

- [ ] **Step 3: Implement ETL transform service**

```csharp
// src/Modules/DataImport/Application/Models/RawImportRow.cs
public class RawImportRow
{
    public int RowNumber { get; init; }
    public Dictionary<string, string?> Fields { get; init; } = new();
}

// src/Modules/DataImport/Application/Models/TransformedRow.cs
public class TransformedRow
{
    public int RowNumber { get; init; }
    public Dictionary<string, object?> Fields { get; init; } = new();
    public List<string> Warnings { get; init; } = new();
    public List<string> Errors { get; init; } = new();
    public bool IsValid => !Errors.Any();
}
```

```csharp
// src/Modules/DataImport/Application/Services/EtlTransformService.cs
public class EtlTransformService
{
    private static readonly string[] DateFormats = ["dd/MM/yyyy", "MM/dd/yyyy", "yyyy-MM-dd", "yyyy/MM/dd"];
    private static readonly Regex E164Pattern = new(@"^\+[1-9]\d{6,14}$", RegexOptions.Compiled);
    private static readonly Regex PhoneDigits = new(@"[\s\-\(\)]", RegexOptions.Compiled);

    public DateTime? NormaliseDate(string? value)
    {
        if (string.IsNullOrWhiteSpace(value)) return null;
        foreach (var fmt in DateFormats)
            if (DateTime.TryParseExact(value.Trim(), fmt, CultureInfo.InvariantCulture,
                DateTimeStyles.None, out var dt)) return dt;
        return null;
    }

    public string? NormalisePhone(string? value, string defaultCountryCode = "GB")
    {
        if (string.IsNullOrWhiteSpace(value)) return null;
        var digits = PhoneDigits.Replace(value.Trim(), "");
        if (!digits.StartsWith("+"))
        {
            var prefix = defaultCountryCode switch { "GB" => "+44", "LK" => "+94", _ => "+" };
            digits = prefix + digits.TrimStart('0');
        }
        return E164Pattern.IsMatch(digits) ? digits : null;
    }

    public (bool Valid, decimal? Value) ValidateSalary(string? value)
    {
        if (string.IsNullOrWhiteSpace(value)) return (false, null);
        var cleaned = value.Replace(",", "").Trim();
        if (decimal.TryParse(cleaned, out var d)) return (true, d);
        return (false, null);
    }

    public HashSet<int> DetectDuplicateEmails(IEnumerable<RawImportRow> rows, string emailField)
    {
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var duplicates = new HashSet<int>();
        foreach (var row in rows)
        {
            var email = row.Fields.GetValueOrDefault(emailField)?.Trim() ?? "";
            if (!seen.Add(email)) duplicates.Add(row.RowNumber);
        }
        return duplicates;
    }

    public TransformedRow Transform(RawImportRow raw, ColumnMappingResult mapping)
    {
        var result = new TransformedRow { RowNumber = raw.RowNumber };
        foreach (var (sourceCol, targetField) in mapping.Mappings)
        {
            var value = raw.Fields.GetValueOrDefault(sourceCol);
            result.Fields[targetField] = targetField switch
            {
                "start_date" or "date_of_birth" => NormaliseDate(value),
                "phone" => NormalisePhone(value),
                "salary" => ValidateSalary(value).Value,
                _ => value
            };
        }
        return result;
    }
}
```

- [ ] **Step 4: Run tests**

```
dotnet test --filter "EtlTransformServiceTests" -v normal
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/Modules/DataImport/Application/ tests/Modules/DataImport/Application/EtlTransformServiceTests.cs
git commit -m "feat(data-import): ETL transform service — date, E.164 phone, salary, duplicate detection"
```

---

### Task 4: Field Mapping Service

**Files:**
- Create: `src/Modules/DataImport/Application/Services/FieldMappingService.cs`
- Create: `src/Modules/DataImport/Application/Models/ColumnMappingResult.cs`
- Create: `tests/Modules/DataImport/Application/FieldMappingServiceTests.cs`

- [ ] **Step 1: Write failing tests**

```csharp
// tests/Modules/DataImport/Application/FieldMappingServiceTests.cs
public class FieldMappingServiceTests
{
    private readonly FieldMappingService _sut = new();

    [Theory]
    [InlineData("first_name", "FirstName")]
    [InlineData("FirstName", "FirstName")]
    [InlineData("fname", "FirstName")]
    [InlineData("email", "Email")]
    [InlineData("dept", "Department")]
    [InlineData("start_date", "StartDate")]
    [InlineData("hire_date", "StartDate")]
    [InlineData("manager", "ReportingManager")]
    [InlineData("line_manager", "ReportingManager")]
    public void AutoMatch_MatchesCommonColumnNames(string source, string expected)
    {
        var result = _sut.AutoMatch(source, alreadyMapped: []);
        Assert.Equal(expected, result);
    }

    [Fact]
    public void GetDropdownOptions_ExcludesAlreadyMappedFields()
    {
        var options = _sut.GetDropdownOptions("random_col",
            sampleValue: "John",
            alreadyMapped: new HashSet<string> { "FirstName" });
        Assert.DoesNotContain(options, o => o.FieldKey == "FirstName");
    }

    [Fact]
    public void GetDropdownOptions_FiltersDateFieldsForDateSampleValue()
    {
        var options = _sut.GetDropdownOptions("col1", sampleValue: "01/03/2024", alreadyMapped: []);
        var keys = options.Select(o => o.FieldKey).ToList();
        Assert.Contains("StartDate", keys);
        Assert.Contains("DateOfBirth", keys);
        Assert.DoesNotContain("Email", keys);
        Assert.DoesNotContain("FirstName", keys);
    }

    [Fact]
    public void GetDropdownOptions_FiltersEmailFieldForEmailSampleValue()
    {
        var options = _sut.GetDropdownOptions("col1", sampleValue: "john@acme.com", alreadyMapped: []);
        var keys = options.Select(o => o.FieldKey).ToList();
        Assert.Contains("Email", keys);
        Assert.Single(keys.Where(k => k != "Skip"));
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```
dotnet test --filter "FieldMappingServiceTests" -v normal
```
Expected: FAIL

- [ ] **Step 3: Implement field mapping service**

```csharp
// src/Modules/DataImport/Application/Models/ColumnMappingResult.cs
public class ColumnMappingResult
{
    public Dictionary<string, string> Mappings { get; init; } = new(); // sourceCol -> fieldKey
    public List<string> UnmappedSourceColumns { get; init; } = new();
    public List<string> UnmappedRequiredFields { get; init; } = new();
}

public record FieldOption(string FieldKey, string DisplayName, string Group, bool Required);
```

```csharp
// src/Modules/DataImport/Application/Services/FieldMappingService.cs
public class FieldMappingService
{
    private static readonly Regex DatePattern = new(
        @"^\d{1,4}[\/\-]\d{1,2}[\/\-]\d{1,4}$", RegexOptions.Compiled);
    private static readonly Regex EmailPattern = new(
        @"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);
    private static readonly Regex PhonePattern = new(
        @"^[\+\d\s\-\(\)]{7,20}$", RegexOptions.Compiled);

    private static readonly Dictionary<string, string[]> AliasMap = new(StringComparer.OrdinalIgnoreCase)
    {
        ["FirstName"]        = ["first_name", "firstname", "fname", "given_name", "forename"],
        ["LastName"]         = ["last_name", "lastname", "lname", "surname", "family_name"],
        ["Email"]            = ["email", "email_address", "work_email", "corporate_email"],
        ["Department"]       = ["department", "dept", "team_department", "division"],
        ["JobTitle"]         = ["job_title", "jobtitle", "title", "position", "role"],
        ["EmploymentType"]   = ["employment_type", "emp_type", "contract_type", "type"],
        ["StartDate"]        = ["start_date", "hire_date", "joining_date", "commencement_date", "date_started"],
        ["ReportingManager"] = ["manager", "line_manager", "reports_to", "direct_manager", "supervisor"],
        ["Phone"]            = ["phone", "phone_number", "mobile", "contact_number", "telephone"],
        ["DateOfBirth"]      = ["date_of_birth", "dob", "birth_date", "birthday"],
        ["Skills"]           = ["skills", "skill_set", "competencies", "expertise"],
        ["Salary"]           = ["salary", "base_salary", "annual_salary", "compensation"],
        ["Team"]             = ["team", "squad", "group"],
    };

    private static readonly List<FieldOption> AllFields =
    [
        new("FirstName",        "First Name",        "Personal",    true),
        new("LastName",         "Last Name",         "Personal",    true),
        new("Email",            "Email",             "Personal",    true),
        new("Phone",            "Phone",             "Personal",    false),
        new("DateOfBirth",      "Date of Birth",     "Personal",    false),
        new("Gender",           "Gender",            "Personal",    false),
        new("Nationality",      "Nationality",       "Personal",    false),
        new("Address",          "Address",           "Personal",    false),
        new("Department",       "Department",        "Employment",  true),
        new("JobTitle",         "Job Title",         "Employment",  true),
        new("EmploymentType",   "Employment Type",   "Employment",  true),
        new("StartDate",        "Start Date",        "Employment",  true),
        new("ReportingManager", "Reporting Manager", "Employment",  true),
        new("Team",             "Team",              "Employment",  false),
        new("Salary",           "Salary",            "Compensation",false),
        new("Currency",         "Currency",          "Compensation",false),
        new("Skills",           "Skills",            "Skills",      false),
        new("Skip",             "— Skip this column —", "Skip",    false),
    ];

    public string? AutoMatch(string sourceColumn, HashSet<string> alreadyMapped)
    {
        foreach (var (fieldKey, aliases) in AliasMap)
        {
            if (alreadyMapped.Contains(fieldKey)) continue;
            if (aliases.Contains(sourceColumn, StringComparer.OrdinalIgnoreCase))
                return fieldKey;
        }
        return null;
    }

    public List<FieldOption> GetDropdownOptions(string sourceColumn, string? sampleValue, HashSet<string> alreadyMapped)
    {
        var type = DetectType(sampleValue);
        return AllFields
            .Where(f => f.FieldKey == "Skip" || !alreadyMapped.Contains(f.FieldKey))
            .Where(f => f.FieldKey == "Skip" || IsTypeCompatible(f.FieldKey, type))
            .ToList();
    }

    private enum ColumnType { Date, Email, Phone, Numeric, CommaSeparated, Text }

    private ColumnType DetectType(string? value)
    {
        if (string.IsNullOrWhiteSpace(value)) return ColumnType.Text;
        if (DatePattern.IsMatch(value)) return ColumnType.Date;
        if (EmailPattern.IsMatch(value)) return ColumnType.Email;
        if (PhonePattern.IsMatch(value) && value.Any(char.IsDigit)) return ColumnType.Phone;
        if (decimal.TryParse(value.Replace(",", ""), out _)) return ColumnType.Numeric;
        if (value.Contains(',')) return ColumnType.CommaSeparated;
        return ColumnType.Text;
    }

    private bool IsTypeCompatible(string fieldKey, ColumnType type) => type switch
    {
        ColumnType.Date   => fieldKey is "StartDate" or "DateOfBirth",
        ColumnType.Email  => fieldKey is "Email",
        ColumnType.Phone  => fieldKey is "Phone",
        ColumnType.Numeric => fieldKey is "Salary",
        ColumnType.CommaSeparated => fieldKey is "Skills",
        _ => true
    };
}
```

- [ ] **Step 4: Run tests**

```
dotnet test --filter "FieldMappingServiceTests" -v normal
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/Modules/DataImport/Application/Services/FieldMappingService.cs \
        src/Modules/DataImport/Application/Models/ColumnMappingResult.cs \
        tests/Modules/DataImport/Application/FieldMappingServiceTests.cs
git commit -m "feat(data-import): field mapping service with type detection and auto-match"
```

---

### Task 5: PeopleHR API Adapter

**Files:**
- Create: `src/Modules/DataImport/Application/Adapters/IHrSystemAdapter.cs`
- Create: `src/Modules/DataImport/Infrastructure/Adapters/PeopleHrAdapter.cs`
- Create: `tests/Modules/DataImport/Infrastructure/PeopleHrAdapterTests.cs`

- [ ] **Step 1: Write failing tests**

```csharp
// tests/Modules/DataImport/Infrastructure/PeopleHrAdapterTests.cs
public class PeopleHrAdapterTests
{
    [Fact]
    public async Task FetchEmployees_ReturnsNormalisedRows_OnSuccess()
    {
        var httpClient = new HttpClient(new MockHttpMessageHandler(
            responseBody: """
            {"isError":false,"Result":[
              {"employeeId":"E001","firstname":"John","lastname":"Smith",
               "email":"john@acme.com","department":"Engineering",
               "jobtitle":"Senior Software Engineer","startdate":"2024-03-01"}
            ]}
            """));

        var adapter = new PeopleHrAdapter(httpClient);
        var rows = await adapter.FetchEmployeesAsync("test-api-key");

        Assert.Single(rows);
        Assert.Equal("John", rows[0].Fields["first_name"]);
        Assert.Equal("john@acme.com", rows[0].Fields["email"]);
    }

    [Fact]
    public async Task FetchEmployees_ThrowsAdapterException_OnApiError()
    {
        var httpClient = new HttpClient(new MockHttpMessageHandler(
            responseBody: """{"isError":true,"Message":"Invalid API key"}"""));

        var adapter = new PeopleHrAdapter(httpClient);
        await Assert.ThrowsAsync<HrAdapterException>(() =>
            adapter.FetchEmployeesAsync("bad-key"));
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```
dotnet test --filter "PeopleHrAdapterTests" -v normal
```
Expected: FAIL

- [ ] **Step 3: Implement the adapter**

```csharp
// src/Modules/DataImport/Application/Adapters/IHrSystemAdapter.cs
public interface IHrSystemAdapter
{
    Task<List<RawImportRow>> FetchEmployeesAsync(string apiKey, CancellationToken ct = default);
    string SystemName { get; }
}

public class HrAdapterException(string message) : Exception(message);
```

```csharp
// src/Modules/DataImport/Infrastructure/Adapters/PeopleHrAdapter.cs
public class PeopleHrAdapter : IHrSystemAdapter
{
    private readonly HttpClient _http;
    private const string BaseUrl = "https://api.peoplehr.net";
    public string SystemName => "PeopleHR";

    public PeopleHrAdapter(HttpClient http) => _http = http;

    public async Task<List<RawImportRow>> FetchEmployeesAsync(string apiKey, CancellationToken ct = default)
    {
        var payload = JsonSerializer.Serialize(new { APIKey = apiKey, Action = "GetAllEmployeeDetail" });
        var response = await _http.PostAsync($"{BaseUrl}/Employee",
            new StringContent(payload, Encoding.UTF8, "application/json"), ct);
        response.EnsureSuccessStatusCode();

        var json = await JsonDocument.ParseAsync(await response.Content.ReadAsStreamAsync(ct), cancellationToken: ct);
        var root = json.RootElement;

        if (root.GetProperty("isError").GetBoolean())
            throw new HrAdapterException(root.GetProperty("Message").GetString() ?? "PeopleHR API error");

        var rows = new List<RawImportRow>();
        int rowNum = 1;
        foreach (var emp in root.GetProperty("Result").EnumerateArray())
        {
            rows.Add(new RawImportRow
            {
                RowNumber = rowNum++,
                Fields = new Dictionary<string, string?>
                {
                    ["first_name"]  = emp.TryGetProperty("firstname",  out var v1) ? v1.GetString() : null,
                    ["last_name"]   = emp.TryGetProperty("lastname",   out var v2) ? v2.GetString() : null,
                    ["email"]       = emp.TryGetProperty("email",      out var v3) ? v3.GetString() : null,
                    ["department"]  = emp.TryGetProperty("department", out var v4) ? v4.GetString() : null,
                    ["job_title"]   = emp.TryGetProperty("jobtitle",   out var v5) ? v5.GetString() : null,
                    ["start_date"]  = emp.TryGetProperty("startdate",  out var v6) ? v6.GetString() : null,
                    ["manager"]     = emp.TryGetProperty("reportingmanager", out var v7) ? v7.GetString() : null,
                }
            });
        }
        return rows;
    }
}
```

- [ ] **Step 4: Run tests**

```
dotnet test --filter "PeopleHrAdapterTests" -v normal
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/Modules/DataImport/Application/Adapters/ \
        src/Modules/DataImport/Infrastructure/Adapters/ \
        tests/Modules/DataImport/Infrastructure/PeopleHrAdapterTests.cs
git commit -m "feat(data-import): PeopleHR API adapter with error handling"
```

---

### Task 6: Bulk Import Endpoint + Hangfire Background Job

**Files:**
- Create: `src/Modules/DataImport/Application/Jobs/ImportBackgroundJob.cs`
- Create: `src/Modules/DataImport/Api/ImportController.cs`
- Create: `tests/Modules/DataImport/Application/ImportBackgroundJobTests.cs`

- [ ] **Step 1: Write failing tests**

```csharp
// tests/Modules/DataImport/Application/ImportBackgroundJobTests.cs
public class ImportBackgroundJobTests
{
    [Fact]
    public async Task ExecuteImport_CreatesEmployees_InCorrectOrder()
    {
        // Arrange — seed migration run with 2 transformed rows
        var run = MigrationRun.Create(tenantId: _tenantId, userId: _userId, MigrationSource.Csv);
        var rows = new List<TransformedRow>
        {
            BuildRow(email: "mgr@acme.com", firstName: "Sarah", manager: null, jobTitle: "Engineering Lead"),
            BuildRow(email: "emp@acme.com", firstName: "John",  manager: "Sarah Johnson", jobTitle: "Senior Software Engineer"),
        };

        var job = new ImportBackgroundJob(_fakeOrchestration, _fakeDb, _fakeProgressHub);
        await job.ExecuteAsync(run.Id, rows);

        // Manager must be created before the employee who reports to them
        var createdEmails = _fakeDb.Employees.Select(e => e.Email).ToList();
        Assert.Contains("mgr@acme.com", createdEmails);
        Assert.Contains("emp@acme.com", createdEmails);
        Assert.True(_fakeDb.CreationOrder.IndexOf("mgr@acme.com") < _fakeDb.CreationOrder.IndexOf("emp@acme.com"));
    }

    [Fact]
    public async Task ExecuteImport_IsIdempotent_WhenRunTwice()
    {
        var rows = new List<TransformedRow>
        {
            BuildRow(email: "john@acme.com", firstName: "John", manager: null, jobTitle: "Engineer")
        };
        var job = new ImportBackgroundJob(_fakeOrchestration, _fakeDb, _fakeProgressHub);
        await job.ExecuteAsync(Guid.NewGuid(), rows);
        await job.ExecuteAsync(Guid.NewGuid(), rows); // Same email, second run

        Assert.Single(_fakeDb.Employees); // No duplicate
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```
dotnet test --filter "ImportBackgroundJobTests" -v normal
```
Expected: FAIL

- [ ] **Step 3: Implement the background job and controller**

```csharp
// src/Modules/DataImport/Application/Jobs/ImportBackgroundJob.cs
public class ImportBackgroundJob
{
    private readonly ImportOrchestrationService _orchestration;
    private readonly DataImportDbContext _db;
    private readonly IHubContext<ImportProgressHub> _hub;
    private const int BatchSize = 500;

    public ImportBackgroundJob(ImportOrchestrationService orchestration,
        DataImportDbContext db, IHubContext<ImportProgressHub> hub)
    { _orchestration = orchestration; _db = db; _hub = hub; }

    [AutomaticRetry(Attempts = 3, OnAttemptsExceeded = AttemptsExceededAction.Fail)]
    public async Task ExecuteAsync(Guid migrationRunId, List<TransformedRow> rows, CancellationToken ct = default)
    {
        var run = await _db.MigrationRuns.FindAsync([migrationRunId], ct)
            ?? throw new InvalidOperationException($"MigrationRun {migrationRunId} not found");

        run.SetTotal(rows.Count);
        await _db.SaveChangesAsync(ct);

        // Sort: managers before their reports
        var ordered = TopologicalSort(rows);
        int processed = 0, success = 0, failed = 0, skipped = 0;

        foreach (var batch in ordered.Chunk(BatchSize))
        {
            await _orchestration.BulkUpsertAsync(batch, run.TenantId, ct);
            processed += batch.Length;
            success += batch.Length;
            run.UpdateProgress(processed, success, failed, skipped);
            await _db.SaveChangesAsync(ct);

            // Push live progress over SignalR
            await _hub.Clients.Group($"import-{migrationRunId}")
                .SendAsync("Progress", new { Processed = processed, Total = rows.Count }, ct);
        }

        run.Complete();
        await _db.SaveChangesAsync(ct);
    }

    private static List<TransformedRow> TopologicalSort(List<TransformedRow> rows)
    {
        // Managers (no manager field or manager not in this import) go first
        var withManager = rows.Where(r => r.Fields.ContainsKey("reporting_manager") && r.Fields["reporting_manager"] != null).ToList();
        var withoutManager = rows.Except(withManager).ToList();
        return [..withoutManager, ..withManager];
    }
}
```

```csharp
// src/Modules/DataImport/Api/ImportController.cs
[ApiController]
[Route("api/migration")]
[RequirePermission("employees:write")]
public class ImportController : ControllerBase
{
    private readonly IBackgroundJobClient _jobs;
    private readonly IImportFileStorage _storage;
    private readonly FieldMappingService _mapping;
    private readonly DataImportDbContext _db;

    [HttpPost("upload-url")]
    public async Task<IActionResult> GetUploadUrl([FromBody] GetUploadUrlRequest req)
    {
        var tenantId = User.GetTenantId().ToString();
        var result = await _storage.GenerateUploadUrlAsync(tenantId, req.Filename);
        return Ok(new { result.UploadUrl, result.FileKey, result.ExpiresAt });
    }

    [HttpPost("analyse")]
    public async Task<IActionResult> AnalyseFile([FromBody] AnalyseFileRequest req)
    {
        // Parse file from S3, return column headers + Row 1 sample values
        var stream = await _storage.DownloadFileAsync(req.FileKey);
        var (headers, sampleRow) = FileParser.ParseFirstRow(stream, req.FileKey);
        var suggestions = headers.Select(h => new
        {
            SourceColumn = h,
            SuggestedField = _mapping.AutoMatch(h, alreadyMapped: []),
            SampleValue = sampleRow.GetValueOrDefault(h)
        });
        return Ok(suggestions);
    }

    [HttpPost("bulk-import")]
    public async Task<IActionResult> BulkImport([FromBody] BulkImportRequest req)
    {
        var run = MigrationRun.Create(User.GetTenantId(), User.GetUserId(), req.Source, req.FileKey);
        _db.MigrationRuns.Add(run);
        await _db.SaveChangesAsync();

        _jobs.Enqueue<ImportBackgroundJob>(job => job.ExecuteAsync(run.Id, req.TransformedRows, default));
        return Accepted(new { MigrationRunId = run.Id });
    }

    [HttpGet("runs")]
    public async Task<IActionResult> GetRuns()
    {
        var tenantId = User.GetTenantId();
        var runs = await _db.MigrationRuns
            .Where(r => r.TenantId == tenantId)
            .OrderByDescending(r => r.StartedAt)
            .Take(20)
            .ToListAsync();
        return Ok(runs);
    }

    [HttpGet("runs/{runId}/report")]
    public async Task<IActionResult> GetReport(Guid runId)
    {
        var report = await _reconciliation.GenerateReportAsync(runId);
        return File(report.PdfBytes, "application/pdf", $"import-report-{runId}.pdf");
    }
}
```

- [ ] **Step 4: Run tests**

```
dotnet test --filter "ImportBackgroundJobTests" -v normal
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/Modules/DataImport/Application/Jobs/ src/Modules/DataImport/Api/ \
        tests/Modules/DataImport/Application/ImportBackgroundJobTests.cs
git commit -m "feat(data-import): Hangfire bulk import job + import API controller"
```

---

### Task 7: Reconciliation Service + File Cleanup Job

**Files:**
- Create: `src/Modules/DataImport/Application/Services/ReconciliationService.cs`
- Create: `src/Modules/DataImport/Application/Jobs/ImportFileCleanupJob.cs`
- Create: `tests/Modules/DataImport/Application/ReconciliationServiceTests.cs`

- [ ] **Step 1: Write failing tests**

```csharp
// tests/Modules/DataImport/Application/ReconciliationServiceTests.cs
public class ReconciliationServiceTests
{
    [Fact]
    public async Task Reconcile_DetectsCountMismatch()
    {
        var svc = new ReconciliationService(_fakeDb);
        var result = await svc.ReconcileAsync(migrationRunId: _runId,
            sourceRowCount: 100, ct: default);

        // Seeded DB has only 98 employees for this tenant
        Assert.False(result.CountMatch);
        Assert.Equal(100, result.SourceCount);
        Assert.Equal(98, result.DestinationCount);
    }

    [Fact]
    public async Task Reconcile_GeneratesSpotCheckList_Of10To15Records()
    {
        var svc = new ReconciliationService(_fakeDb);
        var result = await svc.ReconcileAsync(migrationRunId: _runId,
            sourceRowCount: 50, ct: default);

        Assert.InRange(result.SpotCheckSample.Count, 10, 15);
    }
}
```

- [ ] **Step 2: Run tests to verify they fail**

```
dotnet test --filter "ReconciliationServiceTests" -v normal
```
Expected: FAIL

- [ ] **Step 3: Implement reconciliation and cleanup**

```csharp
// src/Modules/DataImport/Application/Services/ReconciliationService.cs
public class ReconciliationService
{
    private readonly DataImportDbContext _db;
    private readonly EmployeeDbContext _employees;

    public async Task<ReconciliationResult> ReconcileAsync(Guid migrationRunId, int sourceRowCount, CancellationToken ct)
    {
        var run = await _db.MigrationRuns.FindAsync([migrationRunId], ct)!;
        var destCount = await _employees.Employees
            .Where(e => e.TenantId == run.TenantId)
            .CountAsync(ct);

        var allEmployees = await _employees.Employees
            .Where(e => e.TenantId == run.TenantId)
            .Select(e => new { e.Id, e.FirstName, e.LastName, e.Email, e.Department })
            .ToListAsync(ct);

        var sampleSize = Math.Clamp((int)(allEmployees.Count * 0.05), 10, 15);
        var spotCheck = allEmployees.OrderBy(_ => Random.Shared.Next()).Take(sampleSize).ToList();

        var totalSalary = await _employees.EmployeeCompensations
            .Where(c => c.Employee.TenantId == run.TenantId)
            .SumAsync(c => c.BaseSalary, ct);

        return new ReconciliationResult
        {
            CountMatch = destCount == sourceRowCount,
            SourceCount = sourceRowCount,
            DestinationCount = destCount,
            TotalSalary = totalSalary,
            SpotCheckSample = spotCheck.Select(e => new SpotCheckEntry(e.Id, e.FirstName, e.LastName, e.Email)).ToList()
        };
    }
}
```

```csharp
// src/Modules/DataImport/Application/Jobs/ImportFileCleanupJob.cs
public class ImportFileCleanupJob
{
    private readonly DataImportDbContext _db;
    private readonly IImportFileStorage _storage;

    // Scheduled via Hangfire recurring job — runs every hour
    [DisableConcurrentExecution(timeoutInSeconds: 300)]
    public async Task CleanupExpiredFilesAsync(CancellationToken ct = default)
    {
        var cutoff = DateTime.UtcNow.AddHours(-48);
        var runsToClean = await _db.MigrationRuns
            .Where(r => r.Status == MigrationStatus.Completed
                     && r.CompletedAt < cutoff
                     && r.FileKey != null)
            .ToListAsync(ct);

        foreach (var run in runsToClean)
        {
            if (await _storage.FileExistsAsync(run.FileKey!, ct))
                await _storage.DeleteFileAsync(run.FileKey!, ct);
        }
    }
}
```

Register the recurring job in `Program.cs`:
```csharp
RecurringJob.AddOrUpdate<ImportFileCleanupJob>(
    "import-file-cleanup",
    job => job.CleanupExpiredFilesAsync(default),
    Cron.Hourly);
```

- [ ] **Step 4: Run tests**

```
dotnet test --filter "ReconciliationServiceTests" -v normal
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/Modules/DataImport/Application/Services/ReconciliationService.cs \
        src/Modules/DataImport/Application/Jobs/ImportFileCleanupJob.cs \
        tests/Modules/DataImport/Application/ReconciliationServiceTests.cs
git commit -m "feat(data-import): reconciliation service + 48h file cleanup Hangfire job"
```

---

## Phase B — Frontend

---

### Task 8: Wizard State Machine (Zustand)

**Files:**
- Create: `src/app/(dashboard)/hr/import/_hooks/useImportWizard.ts`
- Create: `src/app/(dashboard)/hr/import/_lib/import-types.ts`
- Create: `src/app/(dashboard)/hr/import/_lib/import-types.test.ts`

- [ ] **Step 1: Write failing tests**

```typescript
// src/app/(dashboard)/hr/import/_lib/import-types.test.ts
import { describe, it, expect } from 'vitest'
import { createImportWizardStore } from '../_hooks/useImportWizard'

describe('ImportWizard state machine', () => {
  it('starts at step 1', () => {
    const store = createImportWizardStore()
    expect(store.getState().currentStep).toBe(1)
  })

  it('advances to step 2 when method is chosen', () => {
    const store = createImportWizardStore()
    store.getState().chooseMethod('csv')
    expect(store.getState().currentStep).toBe(2)
    expect(store.getState().method).toBe('csv')
  })

  it('skips step 4 when job family columns are mapped', () => {
    const store = createImportWizardStore()
    store.getState().chooseMethod('csv')
    store.getState().setMapping({ mappings: { 'job_family': 'JobFamily', 'job_level': 'JobLevel' }, hasJobTitleOnly: false })
    store.getState().advance() // from step 3
    expect(store.getState().currentStep).toBe(5) // skips step 4
  })

  it('shows step 4 when only job title is mapped', () => {
    const store = createImportWizardStore()
    store.getState().chooseMethod('csv')
    store.getState().setMapping({ mappings: { 'job_title': 'JobTitle' }, hasJobTitleOnly: true })
    store.getState().advance()
    expect(store.getState().currentStep).toBe(4)
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

```
pnpm vitest run src/app/\(dashboard\)/hr/import/_lib/import-types.test.ts
```
Expected: FAIL

- [ ] **Step 3: Implement the store**

```typescript
// src/app/(dashboard)/hr/import/_lib/import-types.ts
export type ImportMethod = 'csv' | 'peoplehr'
export type WizardStep = 1 | 2 | 3 | 4 | 5 | 6 | 7

export interface ColumnMapping {
  sourceColumn: string
  fieldKey: string | null
  sampleValue: string
  status: 'matched' | 'review' | 'missing' | 'skipped'
}

export interface JobGrouping {
  familyName: string
  titles: Array<{ title: string; level: string; employeeCount: number }>
}

export interface ImportWizardState {
  currentStep: WizardStep
  method: ImportMethod | null
  fileKey: string | null
  mappings: ColumnMapping[]
  hasJobTitleOnly: boolean
  jobGroupings: JobGrouping[]
  migrationRunId: string | null
  chooseMethod: (method: ImportMethod) => void
  setFileKey: (key: string) => void
  setMapping: (data: { mappings: Record<string, string>; hasJobTitleOnly: boolean }) => void
  setJobGroupings: (groupings: JobGrouping[]) => void
  setMigrationRunId: (id: string) => void
  advance: () => void
  back: () => void
  reset: () => void
}
```

```typescript
// src/app/(dashboard)/hr/import/_hooks/useImportWizard.ts
import { create } from 'zustand'
import type { ImportWizardState, ImportMethod, WizardStep } from '../_lib/import-types'

export const createImportWizardStore = () => create<ImportWizardState>((set, get) => ({
  currentStep: 1,
  method: null,
  fileKey: null,
  mappings: [],
  hasJobTitleOnly: false,
  jobGroupings: [],
  migrationRunId: null,

  chooseMethod: (method) => set({ method, currentStep: 2 }),
  setFileKey: (key) => set({ fileKey: key }),
  setMigrationRunId: (id) => set({ migrationRunId: id }),

  setMapping: ({ mappings, hasJobTitleOnly }) =>
    set({ hasJobTitleOnly }),

  setJobGroupings: (groupings) => set({ jobGroupings: groupings }),

  advance: () => set((s) => {
    const next = s.currentStep === 3 && !s.hasJobTitleOnly ? 5 : s.currentStep + 1
    return { currentStep: Math.min(next, 7) as WizardStep }
  }),

  back: () => set((s) => ({ currentStep: Math.max(s.currentStep - 1, 1) as WizardStep })),
  reset: () => set({ currentStep: 1, method: null, fileKey: null, mappings: [], migrationRunId: null }),
}))

export const useImportWizard = createImportWizardStore()
```

- [ ] **Step 4: Run tests**

```
pnpm vitest run src/app/\(dashboard\)/hr/import/_lib/import-types.test.ts
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app/\(dashboard\)/hr/import/_hooks/ src/app/\(dashboard\)/hr/import/_lib/
git commit -m "feat(import-wizard): Zustand state machine with step skip logic"
```

---

### Task 9: Wizard Shell + Steps 1 & 2

**Files:**
- Create: `src/app/(dashboard)/hr/import/page.tsx`
- Create: `src/app/(dashboard)/hr/import/_components/ImportWizard.tsx`
- Create: `src/app/(dashboard)/hr/import/_components/steps/Step1ChooseMethod.tsx`
- Create: `src/app/(dashboard)/hr/import/_components/steps/Step2aUploadFile.tsx`
- Create: `src/app/(dashboard)/hr/import/_components/steps/Step2bConnectPeopleHR.tsx`

- [ ] **Step 1: Write failing tests**

```typescript
// src/app/(dashboard)/hr/import/_components/ImportWizard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { ImportWizard } from './ImportWizard'

describe('ImportWizard', () => {
  it('renders step 1 on mount', () => {
    render(<ImportWizard />)
    expect(screen.getByText('Choose Import Method')).toBeInTheDocument()
  })

  it('advances to step 2 when CSV is selected', () => {
    render(<ImportWizard />)
    fireEvent.click(screen.getByText('Upload CSV or Excel file'))
    expect(screen.getByText('Upload Your File')).toBeInTheDocument()
  })

  it('shows PeopleHR connect form when API option selected', () => {
    render(<ImportWizard />)
    fireEvent.click(screen.getByText('Connect PeopleHR'))
    expect(screen.getByPlaceholderText('Paste your PeopleHR API key')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

```
pnpm vitest run src/app/\(dashboard\)/hr/import/_components/ImportWizard.test.tsx
```
Expected: FAIL

- [ ] **Step 3: Implement shell and steps 1–2**

```typescript
// src/app/(dashboard)/hr/import/page.tsx
import { ImportWizard } from './_components/ImportWizard'

export default function ImportPage() {
  return (
    <div className="fixed inset-0 z-50 bg-background flex flex-col">
      <ImportWizard />
    </div>
  )
}
```

```typescript
// src/app/(dashboard)/hr/import/_components/ImportWizard.tsx
'use client'
import { useImportWizard } from '../_hooks/useImportWizard'
import { Step1ChooseMethod } from './steps/Step1ChooseMethod'
import { Step2aUploadFile } from './steps/Step2aUploadFile'
import { Step2bConnectPeopleHR } from './steps/Step2bConnectPeopleHR'
import { Step3FieldMapping } from './steps/Step3FieldMapping'
import { Step4JobGrouping } from './steps/Step4JobGrouping'
import { Step5Validation } from './steps/Step5Validation'
import { Step6ConfirmImport } from './steps/Step6ConfirmImport'
import { Step7Done } from './steps/Step7Done'

const STEP_LABELS = ['Method', 'Upload', 'Map Fields', 'Job Setup', 'Validate', 'Confirm', 'Done']

export function ImportWizard() {
  const { currentStep, method } = useImportWizard()

  return (
    <div className="flex flex-col h-full">
      {/* Progress bar */}
      <div className="border-b px-8 py-4 flex items-center gap-4">
        <h1 className="text-lg font-semibold mr-8">Import Employees</h1>
        <div className="flex gap-2">
          {STEP_LABELS.map((label, i) => (
            <div key={label} className={`flex items-center gap-1 text-sm ${
              i + 1 === currentStep ? 'text-primary font-medium' :
              i + 1 < currentStep ? 'text-muted-foreground line-through' : 'text-muted-foreground'
            }`}>
              <span className={`w-5 h-5 rounded-full text-xs flex items-center justify-center ${
                i + 1 < currentStep ? 'bg-primary text-primary-foreground' :
                i + 1 === currentStep ? 'border-2 border-primary' : 'border border-muted'
              }`}>{i + 1}</span>
              {label}
              {i < STEP_LABELS.length - 1 && <span className="mx-1 text-muted-foreground">›</span>}
            </div>
          ))}
        </div>
      </div>

      {/* Step content */}
      <div className="flex-1 overflow-auto p-8">
        {currentStep === 1 && <Step1ChooseMethod />}
        {currentStep === 2 && method === 'csv' && <Step2aUploadFile />}
        {currentStep === 2 && method === 'peoplehr' && <Step2bConnectPeopleHR />}
        {currentStep === 3 && <Step3FieldMapping />}
        {currentStep === 4 && <Step4JobGrouping />}
        {currentStep === 5 && <Step5Validation />}
        {currentStep === 6 && <Step6ConfirmImport />}
        {currentStep === 7 && <Step7Done />}
      </div>
    </div>
  )
}
```

```typescript
// src/app/(dashboard)/hr/import/_components/steps/Step1ChooseMethod.tsx
'use client'
import { useImportWizard } from '../../_hooks/useImportWizard'
import { FileSpreadsheet, Plug } from 'lucide-react'

export function Step1ChooseMethod() {
  const { chooseMethod } = useImportWizard()
  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-2">Choose Import Method</h2>
      <p className="text-muted-foreground mb-8">How would you like to bring in your employee data?</p>
      <div className="grid grid-cols-2 gap-4">
        <button onClick={() => chooseMethod('csv')}
          className="border-2 rounded-xl p-6 text-left hover:border-primary hover:bg-primary/5 transition-all">
          <FileSpreadsheet className="w-8 h-8 mb-3 text-primary" />
          <h3 className="font-semibold text-lg mb-1">Upload CSV or Excel file</h3>
          <p className="text-sm text-muted-foreground">Works with any HR system. Export from your current system and upload here.</p>
        </button>
        <button onClick={() => chooseMethod('peoplehr')}
          className="border-2 rounded-xl p-6 text-left hover:border-primary hover:bg-primary/5 transition-all">
          <Plug className="w-8 h-8 mb-3 text-primary" />
          <h3 className="font-semibold text-lg mb-1">Connect PeopleHR</h3>
          <p className="text-sm text-muted-foreground">Connect directly with your API key — we'll pull your employees automatically.</p>
        </button>
      </div>
    </div>
  )
}
```

```typescript
// src/app/(dashboard)/hr/import/_components/steps/Step2aUploadFile.tsx
'use client'
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useImportWizard } from '../../_hooks/useImportWizard'
import { Upload } from 'lucide-react'

export function Step2aUploadFile() {
  const { setFileKey, advance } = useImportWizard()
  const [dragging, setDragging] = useState(false)

  const upload = useMutation({
    mutationFn: async (file: File) => {
      // 1. Get signed upload URL from backend
      const res = await fetch('/api/v1/migration/upload-url', {
        method: 'POST',
        body: JSON.stringify({ filename: file.name }),
        headers: { 'Content-Type': 'application/json' }
      })
      const { uploadUrl, fileKey } = await res.json()
      // 2. Upload directly to S3 — never through ONEVO servers
      await fetch(uploadUrl, { method: 'PUT', body: file })
      return fileKey as string
    },
    onSuccess: (fileKey) => { setFileKey(fileKey); advance() }
  })

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) upload.mutate(file)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-2">Upload Your File</h2>
      <p className="text-muted-foreground mb-6">Accepts .csv, .xlsx, and .xls files.</p>
      <div onDrop={handleDrop} onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        className={`border-2 border-dashed rounded-xl p-16 text-center transition-colors ${
          dragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/30'}`}>
        <Upload className="w-10 h-10 mx-auto mb-4 text-muted-foreground" />
        <p className="font-medium mb-1">Drop your file here</p>
        <p className="text-sm text-muted-foreground mb-4">or</p>
        <label className="cursor-pointer">
          <span className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium">Browse files</span>
          <input type="file" accept=".csv,.xlsx,.xls" className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) upload.mutate(f) }} />
        </label>
        {upload.isPending && <p className="mt-4 text-sm text-muted-foreground">Uploading...</p>}
        {upload.isError && <p className="mt-4 text-sm text-destructive">Upload failed. Please try again.</p>}
      </div>
      <p className="text-xs text-muted-foreground mt-3">
        Files are uploaded securely and deleted automatically within 48 hours.
      </p>
    </div>
  )
}
```

```typescript
// src/app/(dashboard)/hr/import/_components/steps/Step2bConnectPeopleHR.tsx
'use client'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { useImportWizard } from '../../_hooks/useImportWizard'

const schema = z.object({ apiKey: z.string().min(10, 'API key is too short') })
type Form = z.infer<typeof schema>

export function Step2bConnectPeopleHR() {
  const { advance } = useImportWizard()
  const { register, handleSubmit, formState: { errors } } = useForm<Form>({ resolver: zodResolver(schema) })

  const connect = useMutation({
    mutationFn: async (data: Form) => {
      const res = await fetch('/api/v1/migration/peoplehr/test', {
        method: 'POST', body: JSON.stringify({ apiKey: data.apiKey }),
        headers: { 'Content-Type': 'application/json' }
      })
      if (!res.ok) throw new Error('Invalid API key')
      return data.apiKey
    },
    onSuccess: () => advance()
  })

  return (
    <div className="max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-2">Connect PeopleHR</h2>
      <p className="text-muted-foreground mb-6">Find your API key in PeopleHR → Settings → API.</p>
      <form onSubmit={handleSubmit((d) => connect.mutate(d))} className="space-y-4">
        <div>
          <label className="text-sm font-medium">API Key</label>
          <input {...register('apiKey')} placeholder="Paste your PeopleHR API key"
            className="w-full mt-1 border rounded-lg px-3 py-2 text-sm font-mono" />
          {errors.apiKey && <p className="text-destructive text-xs mt-1">{errors.apiKey.message}</p>}
        </div>
        <button type="submit" disabled={connect.isPending}
          className="w-full bg-primary text-primary-foreground rounded-lg py-2 font-medium">
          {connect.isPending ? 'Connecting...' : 'Connect & Fetch Employees →'}
        </button>
        {connect.isError && <p className="text-destructive text-sm">Connection failed. Check your API key and try again.</p>}
      </form>
    </div>
  )
}
```

- [ ] **Step 4: Run tests**

```
pnpm vitest run src/app/\(dashboard\)/hr/import/_components/ImportWizard.test.tsx
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app/\(dashboard\)/hr/import/
git commit -m "feat(import-wizard): wizard shell + step 1 method choice + step 2 upload and PeopleHR connect"
```

---

### Task 10: Step 3 — Field Mapping Table

**Files:**
- Create: `src/app/(dashboard)/hr/import/_components/steps/Step3FieldMapping.tsx`
- Create: `src/app/(dashboard)/hr/import/_components/FieldMappingTable.tsx`
- Create: `src/app/(dashboard)/hr/import/_lib/fieldTypeDetector.ts`
- Create: `src/app/(dashboard)/hr/import/_lib/fieldTypeDetector.test.ts`

- [ ] **Step 1: Write failing tests**

```typescript
// src/app/(dashboard)/hr/import/_lib/fieldTypeDetector.test.ts
import { describe, it, expect } from 'vitest'
import { detectColumnType, filterDropdownOptions } from './fieldTypeDetector'

describe('fieldTypeDetector', () => {
  it.each([
    ['01/03/2024', 'date'],
    ['john@acme.com', 'email'],
    ['Full Time', 'text'],
    ['50000', 'numeric'],
    ['React, Python', 'csv'],
  ])('detects %s as %s', (value, expected) => {
    expect(detectColumnType(value)).toBe(expected)
  })

  it('filters date columns to only date fields', () => {
    const options = filterDropdownOptions({ sampleValue: '01/03/2024', alreadyMapped: new Set() })
    expect(options.map(o => o.fieldKey)).toEqual(
      expect.arrayContaining(['StartDate', 'DateOfBirth', 'Skip'])
    )
    expect(options.map(o => o.fieldKey)).not.toContain('Email')
    expect(options.map(o => o.fieldKey)).not.toContain('FirstName')
  })

  it('excludes already-mapped fields from options', () => {
    const options = filterDropdownOptions({
      sampleValue: 'John',
      alreadyMapped: new Set(['FirstName'])
    })
    expect(options.map(o => o.fieldKey)).not.toContain('FirstName')
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

```
pnpm vitest run src/app/\(dashboard\)/hr/import/_lib/fieldTypeDetector.test.ts
```
Expected: FAIL

- [ ] **Step 3: Implement type detector and mapping table**

```typescript
// src/app/(dashboard)/hr/import/_lib/fieldTypeDetector.ts
export type ColumnType = 'date' | 'email' | 'phone' | 'numeric' | 'csv' | 'text'

export interface FieldOption {
  fieldKey: string
  displayName: string
  group: string
  required: boolean
}

const ALL_FIELDS: FieldOption[] = [
  { fieldKey: 'FirstName',        displayName: 'First Name',        group: 'Personal',    required: true },
  { fieldKey: 'LastName',         displayName: 'Last Name',         group: 'Personal',    required: true },
  { fieldKey: 'Email',            displayName: 'Email',             group: 'Personal',    required: true },
  { fieldKey: 'Phone',            displayName: 'Phone',             group: 'Personal',    required: false },
  { fieldKey: 'DateOfBirth',      displayName: 'Date of Birth',     group: 'Personal',    required: false },
  { fieldKey: 'Department',       displayName: 'Department',        group: 'Employment',  required: true },
  { fieldKey: 'JobTitle',         displayName: 'Job Title',         group: 'Employment',  required: true },
  { fieldKey: 'EmploymentType',   displayName: 'Employment Type',   group: 'Employment',  required: true },
  { fieldKey: 'StartDate',        displayName: 'Start Date',        group: 'Employment',  required: true },
  { fieldKey: 'ReportingManager', displayName: 'Reporting Manager', group: 'Employment',  required: true },
  { fieldKey: 'Team',             displayName: 'Team',              group: 'Employment',  required: false },
  { fieldKey: 'Salary',           displayName: 'Salary',            group: 'Compensation',required: false },
  { fieldKey: 'Skills',           displayName: 'Skills',            group: 'Skills',      required: false },
  { fieldKey: 'Skip',             displayName: '— Skip this column —', group: 'Skip',     required: false },
]

export function detectColumnType(value: string): ColumnType {
  if (/^\d{1,4}[\/\-]\d{1,2}[\/\-]\d{1,4}$/.test(value)) return 'date'
  if (/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value)) return 'email'
  if (/^[\+\d\s\-\(\)]{7,20}$/.test(value) && /\d/.test(value)) return 'phone'
  if (/^\d[\d,\.]*$/.test(value)) return 'numeric'
  if (value.includes(',')) return 'csv'
  return 'text'
}

const TYPE_COMPAT: Record<ColumnType, string[]> = {
  date:    ['StartDate', 'DateOfBirth', 'Skip'],
  email:   ['Email', 'Skip'],
  phone:   ['Phone', 'Skip'],
  numeric: ['Salary', 'Skip'],
  csv:     ['Skills', 'Skip'],
  text:    ALL_FIELDS.map(f => f.fieldKey),
}

export function filterDropdownOptions({ sampleValue, alreadyMapped }: {
  sampleValue: string
  alreadyMapped: Set<string>
}): FieldOption[] {
  const type = detectColumnType(sampleValue)
  const allowed = new Set(TYPE_COMPAT[type])
  return ALL_FIELDS.filter(f => allowed.has(f.fieldKey) && !alreadyMapped.has(f.fieldKey))
}
```

```typescript
// src/app/(dashboard)/hr/import/_components/FieldMappingTable.tsx
'use client'
import { filterDropdownOptions, FieldOption } from '../_lib/fieldTypeDetector'

export interface MappingRow {
  sourceColumn: string
  mappedTo: string | null
  sampleValue: string
  status: 'matched' | 'review' | 'missing' | 'skipped'
}

interface Props {
  rows: MappingRow[]
  onChange: (sourceColumn: string, fieldKey: string | null) => void
}

const STATUS_STYLES = {
  matched: 'border-green-500 bg-green-50 text-green-700',
  review:  'border-amber-400 bg-amber-50 text-amber-700',
  missing: 'border-red-400 bg-red-50',
  skipped: 'border-slate-200',
}

const STATUS_LABELS = { matched: '✓ Matched', review: '⚠ Review', missing: '✗ Missing', skipped: '—' }

export function FieldMappingTable({ rows, onChange }: Props) {
  const alreadyMapped = new Set(rows.map(r => r.mappedTo).filter(Boolean) as string[])

  return (
    <div className="border rounded-xl overflow-hidden">
      <div className="grid grid-cols-[1fr_1.2fr_1.2fr_90px] bg-slate-50 px-4 py-3 gap-3 border-b text-xs font-semibold text-slate-500 uppercase tracking-wide">
        <span>Your Column</span><span>Mapped To</span><span>Sample Value (Row 1)</span><span>Status</span>
      </div>
      {rows.map((row) => {
        const options = filterDropdownOptions({ sampleValue: row.sampleValue, alreadyMapped })
        return (
          <div key={row.sourceColumn}
            className={`grid grid-cols-[1fr_1.2fr_1.2fr_90px] px-4 py-3 gap-3 border-b items-center last:border-0 ${
              row.status === 'review' ? 'bg-amber-50' :
              row.status === 'missing' ? 'bg-red-50' : 'bg-white'}`}>
            <span className="font-mono text-sm text-slate-500">{row.sourceColumn}</span>
            <select
              value={row.mappedTo ?? ''}
              onChange={(e) => onChange(row.sourceColumn, e.target.value || null)}
              className={`text-sm border-2 rounded-lg px-2 py-1.5 w-full ${STATUS_STYLES[row.status]}`}>
              <option value="">— Select or skip —</option>
              {options.map(o => (
                <option key={o.fieldKey} value={o.fieldKey}>{o.displayName}</option>
              ))}
            </select>
            <span className="text-sm text-slate-500 truncate">{row.sampleValue}</span>
            <span className={`text-xs font-semibold ${
              row.status === 'matched' ? 'text-green-600' :
              row.status === 'review' ? 'text-amber-600' :
              row.status === 'missing' ? 'text-red-600' : 'text-slate-400'}`}>
              {STATUS_LABELS[row.status]}
            </span>
          </div>
        )
      })}
    </div>
  )
}
```

- [ ] **Step 4: Run tests**

```
pnpm vitest run src/app/\(dashboard\)/hr/import/_lib/fieldTypeDetector.test.ts
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app/\(dashboard\)/hr/import/_components/FieldMappingTable.tsx \
        src/app/\(dashboard\)/hr/import/_components/steps/Step3FieldMapping.tsx \
        src/app/\(dashboard\)/hr/import/_lib/fieldTypeDetector.ts \
        src/app/\(dashboard\)/hr/import/_lib/fieldTypeDetector.test.ts
git commit -m "feat(import-wizard): step 3 field mapping table with type detection and editable dropdowns"
```

---

### Task 11: Steps 4–7 + Import Progress

**Files:**
- Create: `src/app/(dashboard)/hr/import/_components/steps/Step4JobGrouping.tsx`
- Create: `src/app/(dashboard)/hr/import/_components/steps/Step5Validation.tsx`
- Create: `src/app/(dashboard)/hr/import/_components/steps/Step6ConfirmImport.tsx`
- Create: `src/app/(dashboard)/hr/import/_components/steps/Step7Done.tsx`
- Create: `src/app/(dashboard)/hr/import/_hooks/useImportProgress.ts`

- [ ] **Step 1: Write failing test for progress hook**

```typescript
// src/app/(dashboard)/hr/import/_hooks/useImportProgress.test.ts
import { renderHook, act } from '@testing-library/react'
import { useImportProgress } from './useImportProgress'

it('calculates percentage from processed/total', () => {
  const { result } = renderHook(() => useImportProgress({ total: 100, processed: 42 }))
  expect(result.current.percentage).toBe(42)
})

it('returns 100 when complete', () => {
  const { result } = renderHook(() => useImportProgress({ total: 50, processed: 50 }))
  expect(result.current.percentage).toBe(100)
  expect(result.current.isComplete).toBe(true)
})
```

- [ ] **Step 2: Run tests to verify they fail**

```
pnpm vitest run src/app/\(dashboard\)/hr/import/_hooks/useImportProgress.test.ts
```
Expected: FAIL

- [ ] **Step 3: Implement remaining steps**

```typescript
// src/app/(dashboard)/hr/import/_hooks/useImportProgress.ts
export function useImportProgress({ total, processed }: { total: number; processed: number }) {
  const percentage = total > 0 ? Math.round((processed / total) * 100) : 0
  return { percentage, isComplete: processed >= total && total > 0 }
}
```

```typescript
// src/app/(dashboard)/hr/import/_components/steps/Step4JobGrouping.tsx
'use client'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useImportWizard } from '../../_hooks/useImportWizard'
import { ChevronRight } from 'lucide-react'

interface TitleGroup {
  familyName: string
  titles: Array<{ title: string; level: string; count: number }>
}

const DEFAULT_LEVELS = ['Junior', 'Senior', 'Lead', 'Director']

export function Step4JobGrouping() {
  const { fileKey, setJobGroupings, advance, back } = useImportWizard()
  const { data: detected } = useQuery({
    queryKey: ['import-titles', fileKey],
    queryFn: async () => {
      const res = await fetch(`/api/v1/migration/detect-job-titles?fileKey=${fileKey}`)
      return res.json() as Promise<TitleGroup[]>
    }
  })

  const [groups, setGroups] = useState<TitleGroup[]>(detected ?? [])

  const updateFamilyName = (idx: number, name: string) =>
    setGroups(g => g.map((grp, i) => i === idx ? { ...grp, familyName: name } : grp))

  const updateLevel = (groupIdx: number, titleIdx: number, level: string) =>
    setGroups(g => g.map((grp, i) => i === groupIdx ? {
      ...grp,
      titles: grp.titles.map((t, j) => j === titleIdx ? { ...t, level } : t)
    } : grp))

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-2">Organise Job Titles</h2>
      <p className="text-muted-foreground mb-6">
        We found {groups.flatMap(g => g.titles).length} unique job titles. Group them into Job Families and assign a level to each.
      </p>

      <div className="space-y-4">
        {groups.map((group, gi) => (
          <div key={gi} className="border-2 border-primary/30 rounded-xl overflow-hidden">
            <div className="bg-primary/5 px-4 py-3 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold">Job Family:</span>
                <input value={group.familyName} onChange={(e) => updateFamilyName(gi, e.target.value)}
                  className="border rounded-lg px-2 py-1 text-sm font-semibold" />
              </div>
              <span className="text-xs text-muted-foreground">
                {group.titles.reduce((s, t) => s + t.count, 0)} employees
              </span>
            </div>
            <div>
              {group.titles.map((t, ti) => (
                <div key={ti} className="grid grid-cols-[1fr_140px_80px] px-4 py-3 gap-3 items-center border-b last:border-0">
                  <span className="font-medium text-sm">{t.title}</span>
                  <select value={t.level} onChange={(e) => updateLevel(gi, ti, e.target.value)}
                    className="border rounded-lg px-2 py-1.5 text-sm">
                    {DEFAULT_LEVELS.map(l => <option key={l}>{l}</option>)}
                  </select>
                  <span className="text-xs text-muted-foreground">{t.count} people</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <p className="text-sm text-muted-foreground mt-4 bg-slate-50 rounded-lg p-3">
        ℹ️ All employees will be assigned the default <strong>Employee</strong> role.
        Configure roles per level in Organisation → Job Families after import.
      </p>

      <div className="flex justify-between mt-6">
        <button onClick={back} className="border px-4 py-2 rounded-lg text-sm">← Back</button>
        <button onClick={() => { setJobGroupings(groups); advance() }}
          className="bg-primary text-primary-foreground px-6 py-2 rounded-lg text-sm font-semibold">
          Confirm → Run Validation
        </button>
      </div>
    </div>
  )
}
```

```typescript
// src/app/(dashboard)/hr/import/_components/steps/Step6ConfirmImport.tsx
'use client'
import { useMutation } from '@tanstack/react-query'
import { useImportWizard } from '../../_hooks/useImportWizard'
import { useImportProgress } from '../../_hooks/useImportProgress'
import { useState } from 'react'

export function Step6ConfirmImport() {
  const { fileKey, mappings, jobGroupings, setMigrationRunId, advance } = useImportWizard()
  const [progress, setProgress] = useState({ processed: 0, total: 0 })
  const { percentage } = useImportProgress(progress)

  const startImport = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/migration/bulk-import', {
        method: 'POST',
        body: JSON.stringify({ fileKey, mappings, jobGroupings }),
        headers: { 'Content-Type': 'application/json' }
      })
      const { migrationRunId, total } = await res.json()
      setProgress(p => ({ ...p, total }))
      return migrationRunId as string
    },
    onSuccess: (runId) => {
      setMigrationRunId(runId)
      // Poll progress via REST (SignalR available for real-time if needed)
      const interval = setInterval(async () => {
        const res = await fetch(`/api/v1/migration/runs/${runId}/progress`)
        const data = await res.json()
        setProgress({ processed: data.processedRows, total: data.totalRows })
        if (data.status === 'Completed' || data.status === 'Failed') {
          clearInterval(interval)
          advance()
        }
      }, 1500)
    }
  })

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Confirm & Import</h2>
      {!startImport.isPending && !startImport.isSuccess && (
        <button onClick={() => startImport.mutate()}
          className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-semibold text-lg">
          Start Import →
        </button>
      )}
      {startImport.isPending && (
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span>Importing employees...</span>
            <span className="font-semibold">{percentage}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-3">
            <div className="bg-primary h-3 rounded-full transition-all duration-300"
              style={{ width: `${percentage}%` }} />
          </div>
          <p className="text-xs text-muted-foreground text-center">
            {progress.processed} / {progress.total} employees
          </p>
        </div>
      )}
    </div>
  )
}
```

```typescript
// src/app/(dashboard)/hr/import/_components/steps/Step7Done.tsx
'use client'
import { useImportWizard } from '../../_hooks/useImportWizard'
import { CheckCircle } from 'lucide-react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'

export function Step7Done() {
  const { migrationRunId, reset } = useImportWizard()
  const { data: run } = useQuery({
    queryKey: ['migration-run', migrationRunId],
    queryFn: async () => {
      const res = await fetch(`/api/v1/migration/runs/${migrationRunId}`)
      return res.json()
    },
    enabled: !!migrationRunId
  })

  return (
    <div className="max-w-2xl mx-auto text-center">
      <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
      <h2 className="text-2xl font-bold mb-2">Import Complete</h2>
      <p className="text-muted-foreground mb-6">
        {run?.successRows ?? 0} employees imported successfully.
        {run?.skippedRows > 0 && ` ${run.skippedRows} skipped.`}
      </p>

      <div className="bg-slate-50 rounded-xl p-5 text-left mb-6 space-y-2">
        <p className="font-semibold text-sm mb-3">What to do next:</p>
        {[
          'Assign department heads in Organisation → Departments',
          'Configure roles per job level in Organisation → Job Families',
          'Set required skills on job families for gap analysis',
          'Enrich skill taxonomy in Skills & Talent',
          'Review employees flagged "Needs Completion"',
        ].map(item => (
          <div key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
            <span className="text-slate-400 mt-0.5">□</span> {item}
          </div>
        ))}
      </div>

      <div className="flex gap-3 justify-center">
        <a href={`/api/v1/migration/runs/${migrationRunId}/report`}
          className="border px-4 py-2 rounded-lg text-sm">Download Report (PDF)</a>
        <Link href="/hr/employees" onClick={reset}
          className="bg-primary text-primary-foreground px-6 py-2 rounded-lg text-sm font-semibold">
          View Employees →
        </Link>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Run tests**

```
pnpm vitest run src/app/\(dashboard\)/hr/import/_hooks/useImportProgress.test.ts
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app/\(dashboard\)/hr/import/_components/steps/ \
        src/app/\(dashboard\)/hr/import/_hooks/useImportProgress.ts
git commit -m "feat(import-wizard): steps 4-7 — job grouping, validation, confirm, done with live progress"
```

---

### Task 12: Integrations Screen + Employee List Button

**Files:**
- Create: `src/app/(dashboard)/settings/integrations/page.tsx`
- Create: `src/app/(dashboard)/settings/integrations/_components/IntegrationCard.tsx`
- Modify: `src/app/(dashboard)/hr/employees/page.tsx` — add Import button

- [ ] **Step 1: Write failing test**

```typescript
// src/app/(dashboard)/settings/integrations/_components/IntegrationCard.test.tsx
import { render, screen } from '@testing-library/react'
import { IntegrationCard } from './IntegrationCard'

it('shows connected status with masked API key', () => {
  render(<IntegrationCard
    name="PeopleHR"
    status="connected"
    maskedKey="••••abcd"
    lastImport={{ date: '2026-04-24', employeeCount: 247 }}
  />)
  expect(screen.getByText('Connected')).toBeInTheDocument()
  expect(screen.getByText('••••abcd')).toBeInTheDocument()
  expect(screen.getByText('247 employees')).toBeInTheDocument()
})

it('shows not connected state', () => {
  render(<IntegrationCard name="PeopleHR" status="not_connected" />)
  expect(screen.getByText('Not connected')).toBeInTheDocument()
})
```

- [ ] **Step 2: Run tests to verify they fail**

```
pnpm vitest run src/app/\(dashboard\)/settings/integrations/_components/IntegrationCard.test.tsx
```
Expected: FAIL

- [ ] **Step 3: Implement integrations screen and employee list button**

```typescript
// src/app/(dashboard)/settings/integrations/_components/IntegrationCard.tsx
interface Props {
  name: string
  status: 'connected' | 'not_connected'
  maskedKey?: string
  lastImport?: { date: string; employeeCount: number }
}

export function IntegrationCard({ name, status, maskedKey, lastImport }: Props) {
  return (
    <div className="border rounded-xl p-5">
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold">{name}</h3>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
          status === 'connected' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
          {status === 'connected' ? 'Connected' : 'Not connected'}
        </span>
      </div>
      {maskedKey && <p className="text-sm text-muted-foreground font-mono mb-2">{maskedKey}</p>}
      {lastImport && (
        <p className="text-sm text-muted-foreground">
          Last import: {lastImport.date} · <strong>{lastImport.employeeCount} employees</strong>
        </p>
      )}
    </div>
  )
}
```

Add Import button to employee list page:
```typescript
// In src/app/(dashboard)/hr/employees/page.tsx — add this button alongside existing "Add Employee":
import Link from 'next/link'

// Inside the page header action area:
<Link href="/hr/import"
  className="border px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
  <Upload className="w-4 h-4" /> Import Employees
</Link>
```

- [ ] **Step 4: Run tests**

```
pnpm vitest run src/app/\(dashboard\)/settings/integrations/_components/IntegrationCard.test.tsx
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app/\(dashboard\)/settings/integrations/ src/app/\(dashboard\)/hr/employees/page.tsx
git commit -m "feat(integrations): integrations screen with PeopleHR card + Import Employees button on employee list"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| CSV/Excel upload via signed S3 URL | Task 2, Task 9 Step2a |
| Email transfer explicitly not supported | Task 2 (throws on email format) |
| Date normalisation, E.164 phone, salary validation | Task 3 |
| Duplicate employee ID detection | Task 3 |
| BullMQ → Hangfire background job | Task 6 |
| `POST /api/migration/bulk-import` batched 500–1000 | Task 6 |
| Idempotency (INSERT ON CONFLICT) | Task 6 (BulkUpsertAsync) |
| Live progress percentage | Task 11 (Step6) |
| PeopleHR API adapter | Task 5 |
| Job title grouping step | Task 11 (Step4) |
| Field mapping with type detection + editable dropdowns | Tasks 4, 10 |
| "Map one employee, apply to all" preview | Task 10 (Step3) |
| Dept/family/level auto-create with transaction order | Task 6 (ImportBackgroundJob) |
| Employee default "Employee" role | Task 6 (orchestration) |
| Employee skills → taxonomy drafts + profile | Task 6 (orchestration) |
| Record count + checksum reconciliation | Task 7 |
| PDF reconciliation report | Task 7 + Task 6 (controller /report endpoint) |
| Spot-check 10–15 records | Task 7 |
| `migration_runs` audit table | Task 1 |
| 48-hour R2/S3 file deletion | Task 7 (cleanup job) |
| Settings → Integrations screen | Task 12 |
| Import Employees button on employee list | Task 12 |
