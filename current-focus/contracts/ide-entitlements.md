# Contract: IDE Entitlements + Tag Execution

**Backend owner:** DEV3 Task 4 (endpoint shell + tag execution), DEV4 Task 7 (monitoring entitlement registration)  
**Consumers:** DEV8 Tasks 1-5  
**Canonical source:** `ONEVO.Application/Features/IDEExtension/`

---

## GET `/api/v1/ide/entitlements`

```ts
interface IDEEntitlementsDto {
  workspace_id: string
  active_modules: string[]           // active module keys, e.g. ["core_hr", "work_management", "monitoring"]
  active_features: string[]          // commercially included and runtime-enabled feature keys
  permitted_tag_actions: string[]    // e.g. ["leave:request", "clockin", "task:view"]
  has_monitoring_entitlement: boolean
  agent_installed: boolean
  install_job_id: string | null      // non-null if an install job is in progress
}
```

## POST `/api/v1/ide/tags/execute`

```ts
interface TagExecutionRequestDto {
  tag_action: string                 // e.g. "leave:request"
  params: Record<string, string>
  context: {
    branch: string | null
    file_path: string | null
    repo_url: string | null
  }
}

interface TagExecutionResultDto {
  execution_id: string
  status: "success" | "denied" | "error"
  result_summary: string
  undo_available: boolean
  undo_expires_at: string | null     // ISO datetime; null if no undo window
}
```

## IAgentEntitlementProvider boundary note

DEV3 owns the `GET /api/v1/ide/entitlements` endpoint shell and registers a default `IAgentEntitlementProvider` that returns `has_monitoring_entitlement: false`.

DEV4 Task 7 registers the real `IAgentEntitlementProvider` implementation that reads `agent_install_entitlements`.

**DEV3 Task 4 does not require DEV4 Task 7 to complete** - the interface breaks the circular dependency.  
DEV8 gets a working endpoint immediately; `has_monitoring_entitlement` becomes accurate once DEV4 Task 7 ships.

## Notes

- `active_modules` gates module sections.
- `active_features` gates feature-specific IDE affordances. It must be resolved from active module entitlement, selected commercial feature keys, and runtime feature flags.
- `permitted_tag_actions` is the canonical list for picker rendering; never hard-code tag names client-side
- `agent_installed: true` suppresses the install prompt regardless of `has_monitoring_entitlement`
- Undo window is server-enforced; `undo_expires_at` is the client display deadline

