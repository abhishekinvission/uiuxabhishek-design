# Independently deployed frontend integration

**Use for:** microfrontends/modules loaded at runtime or independently deployed remotes. Do not prescribe this architecture for simple sites.

## Architecture contract
- Choose a remote/host model for an actual need (independent deploy cadence, team boundaries, incremental migration). Document the runtime contract before coding.
- Define mount, update and unmount lifecycle, emitted events, auth/session handoff, error boundaries, navigation ownership, style boundaries, accessibility/focus behavior and version compatibility.
- Treat host tokens as privileged: use shortest viable exposure; avoid query-string credentials, logs and local storage of sensitive tokens; define expiration and refresh behavior with explicit trust boundaries.
- Avoid relying on internals of the host framework/store. Use typed events/props or an agreed protocol.
- Define per-environment asset URLs, CORS/CSP requirements, cache strategy and graceful remote-unavailable fallback.
- Evaluate Module Federation, web components, iframe or other composition methods against actual constraints; not every remote requires federation.

## Verify
- Mount/unmount repeatedly, independent deploy/version skew, expired auth, remote failure, navigation/back, focus trap, responsive style isolation, asset loading, CSP/CORS and rollback.
