# WEEK3: Performance Module

**Status:** Planned
**Priority:** High
**Assignee:** Dev 2
**Sprint:** Week 3 (Apr 21-25)
**Module:** Performance

## Description

Implement review cycles, multi-rater reviews, peer feedback, goals (OKR), recognition, succession planning, and optional productivity score intake from [[productivity-analytics]].

## Acceptance Criteria

- [ ] `review_cycles` table + CRUD — includes `include_productivity_data` boolean flag
- [ ] `reviews` table — multi-rater: self, manager, peer, 360
- [ ] Review includes optional `productivity_score` from [[productivity-analytics]] (nullable)
- [ ] Rating scale: 1.0–5.0 decimal
- [ ] `goals` table — OKR-style with parent-child hierarchy (`parent_goal_id`)
- [ ] Goal types: `individual`, `team`, `company`
- [ ] Goal progress tracking: `current_value` vs `target_value` with `unit`
- [ ] `recognitions` table — peer recognition with points (uses `tenant_id`)
- [ ] `succession_plans` table — position successor mapping with readiness levels
- [ ] `feedback_requests` table — ad hoc and cycle-linked
- [ ] `performance_improvement_plans` table — PIP with objectives, timeline, outcome
- [ ] Domain events for review submission/finalization
- [ ] Unit tests ≥80% coverage

## Related

- [[performance]] — module architecture
- [[productivity-analytics]] — optional productivity score integration into reviews
- [[core-hr]] — employee context for reviews and goals
- [[multi-tenancy]] — tenant-scoped review cycles and recognitions
- [[WEEK2-core-hr-profile]] — employee data referenced in reviews
- [[WEEK1-org-structure]] — team and company goals reference org hierarchy
- [[WEEK4-productivity-analytics]] — productivity scores consumed here (built same week, nullable)
