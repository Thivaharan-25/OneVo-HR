# Form Patterns

## Stack

| Concern | Library | Role |
|:--------|:--------|:-----|
| Form state | React Hook Form | Uncontrolled inputs, minimal re-renders |
| Validation | Zod | Schema-first, shared with API DTOs |
| UI | shadcn/ui Form components | Label, Input, Select, Error display |
| URL state | React Router `useSearchParams` | Filter forms that sync to URL |

## Form Architecture

```tsx
// 1. Define Zod schema (shared with backend DTO if possible)
const createEmployeeSchema = z.object({
  firstName: z.string().min(1, 'Required').max(100),
  lastName: z.string().min(1, 'Required').max(100),
  email: z.string().email('Invalid email'),
  departmentId: z.string().uuid('Select a department'),
  startDate: z.date({ required_error: 'Select a start date' }),
  role: z.enum(['employee', 'manager', 'hr_admin']),
  salary: z.number().positive().optional(),
});

type CreateEmployeeInput = z.infer<typeof createEmployeeSchema>;

// 2. Form component
export function EmployeeCreateForm({ onSuccess }: { onSuccess: () => void }) {
  const form = useForm<CreateEmployeeInput>({
    resolver: zodResolver(createEmployeeSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      role: 'employee',
    },
  });

  const createEmployee = useCreateEmployee();

  async function onSubmit(data: CreateEmployeeInput) {
    await createEmployee.mutateAsync(data);
    onSuccess();
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Server-side validation errors (400 response) */}
        {createEmployee.error instanceof ValidationError && (
          <FormAlert errors={createEmployee.error.fieldErrors} />
        )}

        <div className="grid grid-cols-2 gap-4">
          <FormField control={form.control} name="firstName" render={...} />
          <FormField control={form.control} name="lastName" render={...} />
        </div>
        <FormField control={form.control} name="email" render={...} />
        <FormField control={form.control} name="departmentId" render={...} />
        ...

        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
          <Button type="submit" disabled={createEmployee.isPending}>
            {createEmployee.isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
            Create Employee
          </Button>
        </div>
      </form>
    </Form>
  );
}
```

## Multi-Step Form Wizard

For complex flows like employee onboarding, payroll setup, or review cycle creation.

### Architecture

```tsx
// hooks/use-multi-step-form.ts
interface UseMultiStepFormOptions<T extends z.ZodObject<any>> {
  steps: {
    id: string;
    label: string;
    schema: z.ZodObject<any>;   // Per-step validation
    component: React.ComponentType<StepProps>;
  }[];
  fullSchema: T;                 // Full schema for final validation
  onSubmit: (data: z.infer<T>) => Promise<void>;
}

export function useMultiStepForm<T extends z.ZodObject<any>>({
  steps, fullSchema, onSubmit
}: UseMultiStepFormOptions<T>) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<Partial<z.infer<T>>>({});

  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === steps.length - 1;

  function next(stepData: Record<string, any>) {
    setFormData(prev => ({ ...prev, ...stepData }));
    setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  }

  function back() {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  }

  async function submit(stepData: Record<string, any>) {
    const finalData = { ...formData, ...stepData };
    const validated = fullSchema.parse(finalData);
    await onSubmit(validated);
  }

  return { currentStep, steps, formData, isFirstStep, isLastStep, next, back, submit };
}
```

### Wizard UI

```tsx
<div className="space-y-6">
  {/* Step indicator */}
  <StepIndicator steps={steps} currentStep={currentStep} />

  {/* Step content */}
  <Card className="p-6">
    <CurrentStepComponent
      defaultValues={formData}
      onNext={isLastStep ? submit : next}
      onBack={back}
      isFirstStep={isFirstStep}
      isLastStep={isLastStep}
    />
  </Card>
</div>
```

### Step Indicator
```
Step 1          Step 2          Step 3          Step 4
[●]─────────────[●]─────────────[○]─────────────[○]
Personal Info   Employment      Compensation    Review & Submit
                                ← current
```

## Inline Editing Pattern

For detail pages where individual fields can be edited in-place:

```tsx
function InlineEditField({ label, value, fieldName, onSave }) {
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(value);

  if (!isEditing) {
    return (
      <div className="group flex items-center justify-between py-2">
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-sm">{value}</p>
        </div>
        <PermissionGate permission={`employees:update:${fieldName}`}>
          <Button
            variant="ghost" size="icon"
            className="opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={() => setIsEditing(true)}
          >
            <Pencil className="h-3.5 w-3.5" />
          </Button>
        </PermissionGate>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 py-1">
      <Input value={draft} onChange={e => setDraft(e.target.value)} autoFocus />
      <Button size="sm" onClick={() => { onSave(draft); setIsEditing(false); }}>Save</Button>
      <Button size="sm" variant="ghost" onClick={() => setIsEditing(false)}>Cancel</Button>
    </div>
  );
}
```

## Filter Form Pattern

Filters that sync to URL for bookmarkable/shareable state:

```tsx
import { useSearchParams } from 'react-router-dom';

function EmployeeFilters() {
  const [searchParams, setSearchParams] = useSearchParams();

  const search = searchParams.get('q') ?? '';
  const department = searchParams.get('dept') ?? '';
  const status = searchParams.get('status') ?? '';
  const dateFrom = searchParams.get('from') ?? '';
  const dateTo = searchParams.get('to') ?? '';

  const set = (key: string, value: string) =>
    setSearchParams(prev => { value ? prev.set(key, value) : prev.delete(key); prev.delete('page'); return prev; });

  const clearAll = () => setSearchParams({});
  const hasActiveFilters = search || department || status || dateFrom;

  return (
    <div className="flex flex-wrap items-center gap-2">
      <SearchInput value={search} onChange={v => set('q', v)} placeholder="Search employees..." />
      <DepartmentSelect value={department} onChange={v => set('dept', v)} />
      <StatusFilter value={status} onChange={v => set('status', v)} options={employeeStatuses} />
      <DateRangePicker
        from={dateFrom} to={dateTo}
        onChange={(f, t) => { set('from', f); set('to', t); }}
      />
      {hasActiveFilters && (
        <Button variant="ghost" size="sm" onClick={clearAll}>
          <X className="h-3.5 w-3.5 mr-1" /> Clear
        </Button>
      )}
    </div>
  );
}
```

## Server-Side Validation Error Mapping

When the API returns RFC 7807 with field errors:

```tsx
// Map API validation errors to react-hook-form
function useServerErrors(form: UseFormReturn, error: ApiError | null) {
  useEffect(() => {
    if (error instanceof ValidationError && error.fieldErrors) {
      Object.entries(error.fieldErrors).forEach(([field, messages]) => {
        form.setError(field as any, {
          type: 'server',
          message: messages[0],
        });
      });
    }
  }, [error]);
}
```

## Unsaved Changes Protection

```tsx
function useUnsavedChangesWarning(isDirty: boolean) {
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [isDirty]);
}
```

## Related

- [[frontend/design-system/components/component-catalog|Composed Components]] — form components
- [[frontend/design-system/patterns/table-patterns|Table Patterns]] — filter + table integration
- [[frontend/data-layer/api-integration|Api Integration]] — validation error types
- [[frontend/coding-standards|Coding Standards]] — form conventions
