# Framework-neutral API integration

**Use for:** adding/changing HTTP calls, endpoint versions, client contracts or API-driven UI.

## Contract first
- Identify base URL from existing environment configuration; method, route, auth method, query/body, pagination, response/error structures, rate limits, idempotency and file/content type.
- Inspect the **actual** project's API layer and available contract docs; do not invent paths, fields or response semantics.
- Separate verified contracts from `UNCONFIRMED` proposals. Keep mocks/test fixtures out of production paths unless explicit preview mode is specified.

## Implement
- Reuse the project's existing HTTP client/service abstraction, central error handling and typed request/response models.
- Keep secrets, API tokens and personal data out of client bundles, logs and repositories; route privileged requests through appropriate server controls.
- Model loading, success, empty, validation error, unauthorized/forbidden, not-found, rate-limit, network failure and timeout distinctly when relevant.
- Cancel stale requests or prevent stale results from winning; clean up subscriptions/listeners and reset loading in finally/finalize paths.
- Implement retry only for safe transient failures and honor backoff/`Retry-After`; avoid replaying non-idempotent mutations.
- Handle optimistic updates with rollback and accessible feedback only when appropriate.
- Distinguish transport success from domain-level failure; avoid duplicate toasts when interceptors already handle errors.
- For downloads, check content type, filename handling, authorization, streaming/size limits and error responses masquerading as files.
- Never rely on frontend permission hiding for data security; require backend authorization.

## Verify
- Contract tests/mocks for success, business error, HTTP failure, authorization, cancellation and malformed responses.
- Confirm endpoint base URLs match deployment environment and no development endpoint is hardcoded.
- Test pagination boundaries, timezone/date serialization, empty records, double submit, rapid navigation and cleanup.
