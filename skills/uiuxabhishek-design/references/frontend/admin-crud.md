# Accessible admin CRUD

**Use for:** reusable management screens with list, search, add, edit, archive/deactivate or delete.

## Decisions
- Define entity, identifier, backend contract, list columns, filters, searchable fields, defaults, sortable fields, pagination mode and authorization matrix.
- Decide create vs edit behavior, immutable fields, uniqueness, validation, draft/dirty form policy and delete semantics (archive, soft delete, hard delete).
- Reuse `data-reports.md` for table mechanics and `api-integration.md` for request lifecycle.

## UI behavior
- List: accessible table/grid, meaningful labels, sorting indicators, column visibility, pagination, loading/empty/error states, and actions with discernible names.
- Form: validated typed values, inline accessible error messaging, clearly distinguished required/optional fields, blocked duplicate submission and safe focus placement.
- Edit: populate from verified ID, distinguish missing/forbidden, prevent data loss with unsaved-changes confirmation, honor backend constraints.
- Destructive action: explicit impact, confirmation appropriate to risk, server-side checks, successful state refresh and audit trail if required.
- Role/access management must prevent privilege escalation and verify on server; test unavailable actions, not just hidden controls.
- Prefer reusable field components and schema-driven validation only when consistent with existing project conventions.

## Tests
- List loads/filters/pages; create/edit payload; invalid form blocks API; double-submit prevented; unsaved changes; permission checks; error recovery; accessible keyboard flow; audit behavior where configured.
- Check concurrent edits/conflict versioning when relevant.
