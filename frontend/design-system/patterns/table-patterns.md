# Table Patterns

## DataTable Architecture

The `<DataTable>` is the most-used component in ONEVO. It handles sorting, filtering, pagination, row selection, bulk actions, and row-level actions through a composable API built on TanStack Table.

## Standard Table Page

```tsx
function EmployeesPage() {
  // URL-synced state
  const [search, setSearch] = useQueryState('q');
  const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
  const [sort, setSort] = useQueryState('sort', parseAsString.withDefault('name'));
  const [order, setOrder] = useQueryState('order', parseAsStringEnum(['asc', 'desc']).withDefault('asc'));

  // Server data
  const { data, isLoading } = useEmployees({ search, page, sort, order });

  // Column definitions
  const columns: ColumnDef<Employee>[] = [
    { accessorKey: 'name', header: 'Name', cell: ({ row }) => <EmployeeCell employee={row.original} /> },
    { accessorKey: 'department', header: 'Department' },
    { accessorKey: 'status', header: 'Status', cell: ({ row }) => <StatusBadge status={row.original.status} /> },
    { accessorKey: 'startDate', header: 'Start Date', cell: ({ row }) => formatDate(row.original.startDate) },
    { id: 'actions', cell: ({ row }) => <EmployeeRowActions employee={row.original} /> },
  ];

  return (
    <>
      <PageHeader title="Employees" actions={[{ label: 'Add Employee', permission: 'employees:create' }]} />
      <EmployeeFilters />
      <DataTable
        columns={columns}
        data={data?.items ?? []}
        isLoading={isLoading}
        pagination={{ page, pageSize: 25, total: data?.totalCount ?? 0, onChange: setPage }}
        sorting={{ sort, order, onChange: (s, o) => { setSort(s); setOrder(o); } }}
        selectable
        bulkActions={<EmployeeBulkActions />}
        emptyState={<EmptyState title="No employees" description="Add your first employee to get started." />}
        onRowClick={(row) => router.push(`/people/employees/${row.id}`)}
      />
    </>
  );
}
```

## Column Types

### Text Column
```tsx
{ accessorKey: 'name', header: 'Name', enableSorting: true }
```

### Employee Cell (Avatar + Name + Email)
```tsx
function EmployeeCell({ employee }: { employee: Employee }) {
  return (
    <div className="flex items-center gap-3">
      <Avatar className="h-8 w-8">
        <AvatarImage src={employee.avatarUrl} />
        <AvatarFallback>{getInitials(employee.name)}</AvatarFallback>
      </Avatar>
      <div>
        <p className="text-sm font-medium">{employee.name}</p>
        <p className="text-xs text-muted-foreground">{employee.email}</p>
      </div>
    </div>
  );
}
```

### Status Badge Column
```tsx
{
  accessorKey: 'status',
  header: 'Status',
  cell: ({ row }) => (
    <StatusBadge status={row.original.status} />
    // Renders: <Badge variant="outline" className="text-green-600 bg-green-50">Active</Badge>
  ),
  filterFn: 'equals',
}
```

### Date Column
```tsx
{
  accessorKey: 'createdAt',
  header: 'Created',
  cell: ({ row }) => (
    <span className="text-sm text-muted-foreground tabular-nums">
      {formatRelativeDate(row.original.createdAt)}
    </span>
  ),
}
```

### Currency Column
```tsx
{
  accessorKey: 'salary',
  header: () => <div className="text-right">Salary</div>,
  cell: ({ row }) => (
    <PermissionGate permission="payroll:view-salary" fallback={<span className="text-muted-foreground">***</span>}>
      <div className="text-right font-mono text-sm tabular-nums">
        {formatCurrency(row.original.salary, row.original.currency)}
      </div>
    </PermissionGate>
  ),
}
```

### Actions Column
```tsx
{
  id: 'actions',
  cell: ({ row }) => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => router.push(`/people/employees/${row.original.id}`)}>
          <Eye className="h-4 w-4 mr-2" /> View
        </DropdownMenuItem>
        <PermissionGate permission="employees:update">
          <DropdownMenuItem onClick={() => openEditDialog(row.original)}>
            <Pencil className="h-4 w-4 mr-2" /> Edit
          </DropdownMenuItem>
        </PermissionGate>
        <PermissionGate permission="employees:delete">
          <DropdownMenuSeparator />
          <DropdownMenuItem className="text-destructive" onClick={() => confirmDelete(row.original)}>
            <Trash2 className="h-4 w-4 mr-2" /> Delete
          </DropdownMenuItem>
        </PermissionGate>
      </DropdownMenuContent>
    </DropdownMenu>
  ),
}
```

## Row Selection & Bulk Actions

```tsx
// Selection state
const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

// Bulk actions bar (appears when rows selected)
function EmployeeBulkActions() {
  const count = selectedIds.size;
  if (count === 0) return null;

  return (
    <div className="flex items-center gap-2 p-2 bg-muted rounded-md">
      <span className="text-sm font-medium">{count} selected</span>
      <Button size="sm" variant="outline" onClick={handleBulkExport}>
        <Download className="h-3.5 w-3.5 mr-1" /> Export
      </Button>
      <PermissionGate permission="employees:bulk-update">
        <Button size="sm" variant="outline" onClick={handleBulkDepartmentChange}>
          Change Department
        </Button>
      </PermissionGate>
      <Button size="sm" variant="ghost" onClick={() => setSelectedIds(new Set())}>
        Clear
      </Button>
    </div>
  );
}
```

## Pagination

### Offset-Based (Default)
```tsx
<div className="flex items-center justify-between py-4">
  <p className="text-sm text-muted-foreground">
    Showing {startRow}-{endRow} of {total} results
  </p>
  <div className="flex items-center gap-2">
    <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>
      Previous
    </Button>
    <span className="text-sm tabular-nums">Page {page} of {totalPages}</span>
    <Button variant="outline" size="sm" disabled={page === totalPages} onClick={() => setPage(page + 1)}>
      Next
    </Button>
  </div>
</div>
```

### Cursor-Based (Activity Logs, Infinite Scroll)
```tsx
const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useActivityLogsInfinite(employeeId);

// Load more trigger at bottom of list
<div ref={loadMoreRef}>
  {isFetchingNextPage && <Spinner />}
</div>
```

## Table Export

```tsx
function ExportButton({ filters }: { filters: EmployeeFilters }) {
  const exportMutation = useExportEmployees();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm">
          <Download className="h-4 w-4 mr-2" /> Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={() => exportMutation.mutate({ ...filters, format: 'csv' })}>
          CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => exportMutation.mutate({ ...filters, format: 'xlsx' })}>
          Excel
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => exportMutation.mutate({ ...filters, format: 'pdf' })}>
          PDF Report
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

## Related

- [[frontend/design-system/patterns/form-patterns|Form Patterns]] — filter forms
- [[frontend/design-system/components/component-catalog|Composed Components]] — DataTable component spec
- [[frontend/data-layer/state-management|State Management]] — TanStack Query patterns
- [[frontend/data-layer/api-integration|Api Integration]] — pagination types
