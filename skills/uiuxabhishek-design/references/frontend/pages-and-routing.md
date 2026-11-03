# Pages, routes and feature areas

**Use for:** creating, renaming or reorganizing navigable screens or feature modules in a web application.

## Discover
1. Inspect the existing router, layout shell, navigation, page-title and breadcrumb conventions; don't assume a framework.
2. Identify route path, parent layout, user roles/permissions, entry points, SEO/indexability needs, loading/error/404 states and navigation history expectations.
3. For protected content, establish authorization **server-side**; client-side guards only improve navigation UX.
4. Determine whether the route should be lazy-loaded or preloaded, and whether it has state persisted in URL parameters.

## Implement
- Reuse the established module/component conventions and design system; avoid new dependencies for a single page.
- Keep route constants, labels and menu entries consistent without assuming menus are permission authorities.
- Prefer progressive loading and URL-addressable shareable state where sensible.
- Provide keyboard-accessible navigation, clear headings, focus handling after route changes, stable skeleton/empty/error states, and useful navigation back.
- Preserve canonical URLs, metadata and crawl rules if applicable; don't index gated, draft or unpublished pages.
- When renaming: check incoming links, redirects, bookmarks, analytics events and test expectations.

## Verify
- Direct deep link, internal navigation, back/forward, refresh, 404, access denied, signed-out state, small viewport, keyboard navigation, low-network/failed-data response.
- Check page titles, breadcrumb labels, console errors and route-specific tests.
- Report any backend menu/role setup necessary for a route to become accessible.
