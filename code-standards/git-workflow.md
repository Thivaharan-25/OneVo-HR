# Git Workflow: ONEVO

## Branching Strategy

```
main ──────────────────────────────────────────────── (production-ready)
  │
  ├── develop ─────────────────────────────────────── (integration branch)
  │     │
  │     ├── feature/SEL-123-employee-crud ──────────── (feature branches)
  │     ├── feature/SEL-124-leave-module ───────────── 
  │     ├── bugfix/SEL-130-fix-tenant-filter ───────── (bug fixes)
  │     └── hotfix/SEL-140-fix-auth-crash ──────────── (production hotfix)
  │
  └── release/v1.0 ────────────────────────────────── (release candidates)
```

## Branch Naming

```
feature/SEL-{ticket}-{short-description}
bugfix/SEL-{ticket}-{short-description}
hotfix/SEL-{ticket}-{short-description}
release/v{major}.{minor}
```

## Commit Messages

```
type(scope): subject

Types:
  feat     → New feature
  fix      → Bug fix
  refactor → Code restructuring (no behavior change)
  test     → Adding/updating tests
  docs     → Documentation changes
  chore    → Build, CI, tooling changes
  perf     → Performance improvement

Scope: module name
  core-hr, auth, leave, attendance, payroll, performance, 
  skills, documents, notifications, config, calendar, reports,
  grievance, expense, shared-platform, infrastructure, shared-kernel

Examples:
  feat(core-hr): add employee dependent management endpoints
  fix(leave): correct carry-over calculation for part-time employees  
  refactor(auth): extract JWT validation to dedicated service
  test(attendance): add biometric webhook integration tests
  perf(payroll): batch payroll line item inserts for large runs
```

## Pull Request Rules

1. **Small PRs** — one feature or fix per PR
2. **At least 1 reviewer** — required before merge
3. **CI must pass** — all tests green, coverage threshold met
4. **No direct commits to main or develop** — always via PR
5. **Squash merge** — keep commit history clean on develop/main
6. **Delete branch after merge** — keep branch list clean

## PR Template

```markdown
## What
[Brief description of what this PR does]

## Why
[Why this change is needed]

## Module
[Which module(s) are affected: e.g., CoreHR, Leave]

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Architecture tests pass
- [ ] Manual testing done (describe scenarios)

## Checklist
- [ ] Follows coding standards
- [ ] No module boundary violations
- [ ] Multi-tenancy: all queries tenant-scoped
- [ ] No PII in logs
- [ ] API documentation updated (Swagger)
- [ ] No hardcoded secrets or connection strings
```

## Related

- [[ci-cd-pipeline]]
- [[rules]]
