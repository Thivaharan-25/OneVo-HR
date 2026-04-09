# Search Architecture: ONEVO

## Phase 1: PostgreSQL Full-Text Search

Using PostgreSQL's built-in FTS with `tsvector` columns and GIN indexes.

### Searchable Entities

| Entity | Searchable Fields | Index Type |
|:-------|:-----------------|:-----------|
| `employees` | first_name, last_name, employee_no, email | GIN on tsvector |
| `documents` | title | GIN on tsvector |
| `courses` | title | GIN on tsvector |
| `skills` | name | GIN on tsvector |
| `departments` | name, code | GIN on tsvector |

### Implementation

```sql
-- Add tsvector column
ALTER TABLE employees ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(first_name, '') || ' ' || coalesce(last_name, '') || ' ' || coalesce(employee_no, ''))
    ) STORED;

-- GIN index for fast search
CREATE INDEX idx_employees_search ON employees USING GIN (search_vector);

-- Query
SELECT * FROM employees
WHERE tenant_id = @tenantId
AND search_vector @@ plainto_tsquery('english', @searchTerm)
ORDER BY ts_rank(search_vector, plainto_tsquery('english', @searchTerm)) DESC
LIMIT 20;
```

### EF Core Integration

```csharp
// In repository
public async Task<List<Employee>> SearchAsync(string query, CancellationToken ct)
{
    return await Query
        .Where(e => EF.Functions.ToTsVector("english", e.FirstName + " " + e.LastName + " " + e.EmployeeNo)
            .Matches(EF.Functions.PlainToTsQuery("english", query)))
        .Take(20)
        .ToListAsync(ct);
}
```

## Phase 2: Meilisearch (Future)

When search needs exceed PostgreSQL FTS capabilities (typo tolerance, faceted search, real-time indexing):

- Meilisearch instance alongside PostgreSQL
- Sync via domain events: entity created/updated → index in Meilisearch
- Tenant-isolated indexes: `onevo_{tenantId}_employees`
- Fallback to PostgreSQL FTS if Meilisearch is unavailable

## Related

- [[database/performance|Performance]] — indexing strategy and GIN indexes
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-isolated search indexes
- [[AI_CONTEXT/tech-stack|Tech Stack]] — search technology choices
