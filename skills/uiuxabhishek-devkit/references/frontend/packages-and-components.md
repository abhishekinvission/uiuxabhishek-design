# Shared components and publishable packages

**Use for:** extracting reusable UI libraries, design-system components, cross-project packages and reusable modules.

## Requirements
- Define consumer use cases, supported frameworks/platforms, semantic versioning, public API, peer dependencies, CSS isolation/theming and accessibility contract.
- Avoid over-extraction when a component serves only one call site. Prefer composable API instead of copying an entire app-specific module.
- Keep auth/session context explicit and injected by the host; no direct access to host-private stores or hardcoded organization endpoints.
- Expose stable events for lifecycle, data updates and failures, and clean up listeners on unmount/disposal.
- Include type declarations, CSS/assets, provenance, licenses, tree-shaking, build outputs and reproducible installation instructions.
- Publish to private or public registries only with correct rights and user authorization; never copy private package names/feeds.

## Verify
- Installation in a minimal consumer, props/inputs/events, theme isolation, CSS collisions, compatibility, token-safe error handling, SSR/CSR if relevant, build and versioned upgrade regression.
