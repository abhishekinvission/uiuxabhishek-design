# Azure DevOps delivery — project configuration

This is a **configuration contract**, not a set of environment defaults. Resolve values from the current repository, ticket URL, Azure DevOps connection or explicit user instructions. Never guess tenant, organization, project, repo, base branch or work-item type.

| Setting | What to detect or establish |
|---|---|
| Azure organization URL | Current connected Azure DevOps organization; no fixed URLs |
| Azure project | Work item or active project |
| Code repository | Exact repo for the work item; Azure Repos or a supported linked GitHub repo |
| Work item ID | Provided Azure Boards item or URL; ID alone only when Azure context unambiguous |
| Target/base branch | Repository policy; otherwise repository default branch, confirmed before writes |
| Branch naming | Repo conventions; include ticket ID when required |
| Test/build gates | Existing scripts/CI; do not invent generic command success |
| Credentials | Official authorized connector, Azure CLI, or user-managed auth; never copy tokens into files |
| PR visibility/type | Draft unless user/project policy says otherwise; approval/merge separate |
| Write permissions | Explicit user authorization and permitted tool scope; reporting alone is not authorization to publish |

## Capability detection
1. Prefer existing approved Azure DevOps MCP/connector with read/write capabilities appropriate to the action. Resolve exact schema before use.
2. If absent, use `az devops` CLI only when installed, configured, authenticated and authorized. `az boards work-item show --id ...` reads a ticket; `az repos pr create` creates an Azure Repos PR. Check installed extension/help because CLI variants differ.
3. For GitHub-hosted code linked to Azure Boards, use approved GitHub tools/CLI to open the GitHub PR and link the work item through the supported mechanism; don't assume Azure Repos commands apply.
4. If tools/permissions are unavailable, provide a dry-run report and manual steps. Never fabricate PR URLs, ticket states or successful writes.
5. Azure DevOps Server may not support the Azure CLI extension; use its available official UI/API where authorized.

## Project policy precedence
Repository branch protections, enterprise security policy, user scope and permissions override this guide. Do not alter Git config globally, disable checks, run force-push, merge, deploy, complete PRs or edit ticket metadata without explicit authorization.
