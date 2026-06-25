# HR Coverage Routing

**Status:** Deprecated for Phase 1
**Replacement:** Position-based access

---

## Phase 1 Source of Truth

Separate HR Coverage is not an active Phase 1 configuration concept. It duplicated the new position-based access model.

HR visibility and operational authority now come from:

- Role granted from position
- Can manage employees in
- Requires approval before sensitive access is applied
- Explicit authorized overrides where needed

Phase 1 does not route HR coverage through Workflow Engine. Sensitive position-derived access uses `access_grant_requests` and deterministic `position:approve` approval resolution.

---

## Phase 2 Option

Advanced HR coverage routing may return in Phase 2 with Workflow / Automation Engine support. Until then, do not build an HR Coverage sidebar item, workflow resolver, or separate coverage setup screen.

---

## Related

- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[Userflow/Auth-Access/access-policy|Management Coverage Reference]]
