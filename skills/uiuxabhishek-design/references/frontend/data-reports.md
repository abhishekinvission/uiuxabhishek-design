# Reports, data tables, filters and exports

**Use for:** analytics screens, audit views, admin lists and data-heavy reports.

## Data contract
- Confirm row schema, filter semantics, sort keys, total count, date/timezone boundaries, permission restrictions, export formats and data volume.
- Establish server-side vs client-side sort/filter/page from scale and API capabilities. Do not silently mix modes.

## Build
- Keep filters understandable, resettable and optionally URL-shareable; debounce only when it improves behavior; give clear Apply/Reset actions if changes are expensive.
- Reuse the same table interaction baseline across CRUD and reports: meaningful headers, keyboard access, clear sort state, responsive overflow, empty/no-match/error states, and visible loading.
- Use server pagination for large datasets. Keep stable row identity and preserve filters across paging/export.
- Provide CSV/Excel export only if product requires it; ensure exported records honor permissions and the filter scope. Escape spreadsheet-formula prefixes if producing CSV from untrusted values.
- Charts require meaningful axis units, labels, legends and an accessible tabular alternative.
- For time-series, explicitly handle timezone, daylight-saving changes, missing samples, partial periods and data freshness.
- Avoid misrepresenting a filtered subset as a total; display definitions/denominators where needed.

## Verify
- Sort ascending/descending and ties; empty filters; first/last page; quick filter changes; export parity, formula injection defense, date boundaries, loading cleanup and accessibility.
