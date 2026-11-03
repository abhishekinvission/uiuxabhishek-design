# Portable frontend testing and regression

**Use for:** new code, bug fixes, flaky tests, coverage changes and QA readiness.

## Discover the project
- Inspect the actual stack/test runner (e.g., Vitest, Jest, Jasmine, Playwright, Cypress), CI commands and coverage thresholds. Do not impose a framework or a fixed test command.
- Identify risk before selecting unit, component, integration, contract or end-to-end tests.

## Minimum behavior matrix
- Success and error, loading cleanup, empty data, invalid inputs, authorization/forbidden, navigation, sorting/pagination, responsive/keyboard behavior and changed business rules.
- Test output/behavior instead of private implementation when possible.
- Mock network only where appropriate; never let fixtures silently become production data. Mark unconfirmed contracts.
- Simulate cancellation, rapid interaction, double submission and stale responses where race conditions matter.
- Include accessibility checks and reduced-motion considerations for interactive components.

## Quality gates
- Run targeted tests early, then relevant broader regression and the project's actual lint/typecheck/build checks.
- Report exact commands and results; do not claim success for checks not run.
- Never increase coverage by excluding new code without explicit rationale. Treat snapshot changes as reviewable diffs, not automatic approvals.
- If gate fails: identify whether caused by change, environment or pre-existing issue; fix in scope, re-run affected checks, avoid bypassing hooks.

## Evidence
Provide tested scenarios, coverage or quality information if available, remaining unverified cases, and the exact reproduction command.
