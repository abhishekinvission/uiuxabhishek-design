# Review and release readiness

**Use for:** pre-PR checks, change audits, security review and release decisions.

## Scope and diff
- Identify intended change, source branch and repository policy. Inspect `git diff` and `git status` before staging.
- Confirm no secrets, private URLs, access tokens, build artifacts, third-party source without rights, or unexpected generated files.
- Don't silently modify unrelated code, disable checks, rewrite branch history or publish.

## Checks (choose applicable)
- User acceptance criteria and regression scenarios mapped to tests.
- Relevant unit/contract/e2e tests; type checking; lint/format; build; accessibility, keyboard and responsive smoke tests.
- API schema and authorization; no accidental public routes; dependency and secret checks.
- Performance regressions, asset sizing, hydration/runtime console, SEO if public, telemetry and error handling.
- Confirm app-specific feature flags, migration/rollback, environments and docs are ready.
- Re-run changed checks after any review-fix.

## PR report
Use [`templates/pr-description.md`](../../templates/pr-description.md), adapted to the repository's own PR template if one exists. Include screenshots only when authorized and necessary.

## Guardrails
Use repository-specific branch/PR rules; prefer a draft PR for in-progress work. Never claim a completed deployment, merge or passed test without evidence.
