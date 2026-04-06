# WEEK1: Org Structure Module

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 3
**Sprint:** Week 1 (Apr 7-11)
**Module:** OrgStructure

## Description

Implement organizational hierarchy: legal entities, office locations, department tree, job families/levels/titles, and team management.

## Acceptance Criteria

- [ ] Legal entity CRUD (with country association)
- [ ] Office location CRUD (linked to legal entity + country)
- [ ] Department CRUD with hierarchical tree (unlimited nesting via parent_department_id)
- [ ] Department tree query (returns full hierarchy for a tenant)
- [ ] Job family CRUD (linked to department)
- [ ] Job family levels CRUD (rank ordering within family)
- [ ] Job title CRUD (linked to job family)
- [ ] Team CRUD (linked to department)
- [ ] Team member management (add/remove employees from teams)
- [ ] All entities tenant-scoped with proper indexes (see [[multi-tenancy]])

## Related Files

- [[module-catalog]] — OrgStructure module details
- [[module-boundaries]] — dependency rules
- [[shared-kernel]] — BaseEntity, BaseRepository
- [[coding-standards]] — naming conventions
- [[known-issues]] — self-referencing tables (departments)
