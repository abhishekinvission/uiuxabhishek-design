# State management without framework lock-in

**Use for:** shared user/app context, persistent filters, session state, multi-step forms, complex synchronized UI.

## Choose smallest suitable scope
1. Local component state for local interactions.
2. URL/query state for shareable filters, paging and navigation.
3. Context/service/store for cross-screen coordinated state.
4. Persisted state only when it meaningfully improves UX and complies with privacy requirements.

## Rules
- Declare clear source of truth and ownership. Separate server-cache state from UI state; avoid duplicate mutable copies.
- Treat permission decisions as backend responsibility, never as a trust in client-side stored roles.
- Ensure state updates are predictable, selectors/computed values are pure, effects are cancellable, and subscriptions/listeners disposed.
- Reset context-specific state on account, tenant, workspace or organization switches; prevent cross-tenant data leakage.
- Persist only necessary nonsensitive values with clear versioning and expiry. Avoid storing access tokens in localStorage as a universal pattern; never embed client-side encryption keys as a substitute for proper protection.
- Model loading/error/freshness and out-of-order responses explicitly when needed.

## Verify
- Refresh, route changes, browser back, switching contexts, login/logout, concurrent requests, persistence migration, offline/online changes and invalid stored data.
