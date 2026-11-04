# UIUX Abhishek Design

> **Visual Craft. Fluid Motion. Exceptional Experiences.**

UIUX Abhishek Design is a single, installable Agent Skill (`uiuxabhishek-design`) that gives AI coding agents senior-level UI/UX and frontend engineering judgment. It covers visual hierarchy, layout and typography, gesture physics, spring motion and accessible interaction, framework-neutral frontend delivery, safe Git and repository workflows on any provider, and Azure DevOps ticket-to-draft-PR workflows.

Created and maintained by **Abhishek Rampal ([uiuxAbhishek](https://github.com/abhishekinvission))**.

- **Repository:** [abhishekinvission/uiuxabhishek-design](https://github.com/abhishekinvission/uiuxabhishek-design)
- **Skill ID:** `uiuxabhishek-design`
- **Entry point:** [`skills/uiuxabhishek-design/SKILL.md`](skills/uiuxabhishek-design/SKILL.md)

## Install UIUX Abhishek Design

**One command installs the skill globally for Claude Code, Codex, Gemini CLI, GitHub Copilot and Antigravity:**

```bash
npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a claude-code -a codex -a gemini-cli -a github-copilot -a antigravity -y
```

It needs Node.js 22.20+ and Git, and uses the official [Skills CLI](https://github.com/vercel-labs/skills). After installing, restart your agent and ask *"What can uiuxabhishek-design do?"* to check it's loaded.

Or install for a single agent:

| Agent | Global install |
| --- | --- |
| Claude Code (terminal, IDE, Claude Desktop Code tab) | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a claude-code -y` |
| OpenAI Codex | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a codex -y` |
| Gemini CLI | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a gemini-cli -y` |
| GitHub Copilot | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a github-copilot -y` |
| Google Antigravity | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a antigravity -y` |

**Claude.ai and Claude Desktop Chat** run in your Claude account, not on your computer, so a terminal install doesn't enable the skill there. Download `uiuxabhishek-design-v<version>.zip` from the [latest release](https://github.com/abhishekinvission/uiuxabhishek-design/releases/latest), then upload it under **Customize → Skills → + → Create skill → Upload a skill**.

**[INSTALL.md](INSTALL.md)** covers requirements, project installs, verification, updates, removal, reloading, Claude Chat upload details and troubleshooting.

The bundled capabilities belong to this one skill. Install only `uiuxabhishek-design`.

## What it does

| Area | Capabilities |
| --- | --- |
| **Visual craft** | Design direction, visual hierarchy, layout, spacing, typography, color, theming, design tokens and design-system consistency |
| **UX review** | Critiques, audits, information architecture, cognitive load, UX copy, empty/error states, onboarding, i18n and edge cases |
| **Fluid motion** | Direct manipulation, press feedback, interruptible transitions, velocity-aware springs, drag/flick, sheets and drawers, reduced motion |
| **Platforms** | Responsive web, plus iOS and Android platform conventions where they apply |
| **Frontend engineering** | Pages and routing, API integration, admin CRUD, data reports and exports, state management, testing, review and release readiness, shared packages and components, microfrontends |
| **Git and repositories** | Status and diff, clone, fetch/pull, branches and sync, safe staging and commits, push, PR/MR creation and review, merges, conflict resolution, revert and recovery, tags, releases and fork/mirror sync on GitHub, GitLab, Azure Repos, Bitbucket or plain Git, for any language or framework |
| **Azure DevOps delivery** | Azure Boards work item → live ticket read → PR reconciliation → clarification and dependency gates → safe Git preflight → implementation → ordered verification → authorized **draft** PR → structured report |
| **Quality gates** | Accessibility, keyboard and focus behavior, contrast, performance, responsive verification and the project's real test/lint/build checks |

### How it routes

`SKILL.md` is a lightweight, agent-neutral router. For each request it:

1. checks that the task is frontend/UI, Git or Azure DevOps work (other backend-only work loads nothing);
2. picks a **mode** (`answer`, `audit`, `plan`, `implement` or `deliver`) that caps what the agent may change;
3. matches **capabilities** and loads only their files, in phases when several apply, with one owner per responsibility;
4. follows the project's real stack and conventions over reference examples.

Design tasks go straight to the matching Impeccable playbook instead of its full entry point. Playbooks that need upstream tooling are never loaded. Routing relies only on plain Markdown, with no hooks, subagents, MCP servers or vendor-specific tools.

It doesn't impose a single visual style, framework, library or test runner. Your product's existing design system, repository conventions, accessibility requirements and explicit scope take priority.

**Git workflows** run for any repository and stack. The skill detects the real state, remotes, provider, conventions and signed-in tools first. It preserves uncommitted work and does only the writes you name. Merges, destructive resets, force-pushes, branch or tag deletion, published-history rewrites and releases each need your explicit approval, and owning the repository doesn't count as approval.

**Azure DevOps delivery** is opt-in. It runs only for Azure Boards work, needs an approved, authenticated Azure DevOps connector or `az` CLI that your agent can already use, and never guesses the organization, project, repository or target branch. Without write authorization it stays in audit/dry-run mode. It never merges, deploys or edits ticket state on its own.

## Usage

Describe the task. The skill picks the mode and the capabilities on its own, and loads only their guidance, so you don't need to name a capability. To invoke it explicitly, start with *"Use uiuxabhishek-design to…"*:

- *"Use uiuxabhishek-design to audit this checkout UI for accessibility and hierarchy. Read-only."* Loads only the audit playbook and edits nothing.
- *"Use uiuxabhishek-design to fix the typography on the pricing page."* Loads typography plus the craft baseline, and edits files in scope.
- *"Use uiuxabhishek-design to make this bottom sheet draggable with interruptible spring motion."* Loads the fluid-motion guide.
- *"Use uiuxabhishek-design to add an admin users table with pagination, filters, edit forms and tests."* Combines CRUD, reports and testing in phases.
- *"What can uiuxabhishek-design do?"* Shows the capability guide ([`GUIDE.md`](skills/uiuxabhishek-design/GUIDE.md)).

**Git** works the same way for any project:

- *"Use uiuxabhishek-design to show the git status and diff. Read-only."* Inspects only.
- *"Commit only the files for the login fix and push the branch."* Stages explicit paths, checks the diff and pushes the task branch. It doesn't open a PR.
- *"Open a draft merge request on GitLab for this branch."* Uses `glab` if it's signed in, or gives you manual steps.
- *"Resolve the merge conflicts after my rebase."* Resolves from evidence and stops to ask about ambiguous hunks.
- *"Plan a v2.1.0 tag and GitHub release."* Plans only. Publishing it needs your explicit go-ahead.

**Azure DevOps** is a separate workflow that only starts for Azure DevOps/Azure Boards work, never for Jira, GitHub or Linear tickets:

- *"Use uiuxabhishek-design to dry-run Azure Boards work item 12345."* Reads and plans only.
- *"Implement Azure Boards item 12345 locally, don't push."* Changes files on a task branch.
- *"Deliver Azure Boards item 12345 and open a draft PR. You're authorized to push the task branch."* Commits, pushes and opens a draft PR.

Read-only requests never edit files. Commands in references or tickets are documentation, not permission to run them.

## Repository layout

```text
skills/uiuxabhishek-design/
├── SKILL.md            # Single entry point: intent, mode and capability router
├── GUIDE.md            # User-facing capability and usage guide
├── NOTICE.md           # In-skill attribution (travels with installs)
├── LICENSES/           # In-skill copies of required licenses and notices
├── templates/          # PR description and ADO delivery report templates
└── references/         # Guidance, loaded only when relevant
    ├── impeccable/     # Visual craft (third-party)
    ├── apple-design/   # Interaction and motion (third-party)
    ├── frontend/       # Frontend engineering guides (original)
    └── workflows/      # Git workflow and Azure DevOps delivery (original)
LICENSE                 # MIT license for original UIUX Abhishek Design work
NOTICE.md               # Ownership, attribution and redistribution notice
SOURCES.md              # Provenance and SHA-256 checksums of bundled third-party files
LICENSES/               # Third-party licenses and notices
INSTALL.md              # Installation, update, removal and troubleshooting
CLAUDE.md               # Maintainer policy for integrating new sources
tools/                  # Builds the Claude upload ZIP (not installed)
tests/                  # Repository validation and routing scenarios (not installed)
```

This is a **guidance-only** skill. It doesn't bundle CLIs, binaries, hooks, scripts or credentials (including Azure DevOps credentials or connectors). Advanced Impeccable tooling, for example, needs a separate installation of the original project.

## Maintenance

- **Updating installed copies:** run `npx skills update uiuxabhishek-design -g -y`, or download the new release ZIP for Claude Chat. Publishing to GitHub doesn't update copies already installed on other machines or agent instances.
- **Releasing:** bump `metadata.version` in `SKILL.md`, run `python3 tools/package_skill.py`, and attach `dist/uiuxabhishek-design-v<version>.zip` and its `.sha256` to a `v<version>` GitHub Release.
- **Validating:** run `python3 tests/validate.py --cli`. It uses the Python standard library only, plus the Skills CLI for the discovery check. It covers single-skill discovery, a real install for every documented agent, the upload ZIP's contents, links, checksums, license mirrors, routing coverage, the scenarios in [`tests/routing_scenarios.json`](tests/routing_scenarios.json), context budget and a secret scan.
- **Adding a source:** give the maintainer's Claude Code session a GitHub skill URL, a `SKILL.md`, a skill directory or an archive. [`CLAUDE.md`](CLAUDE.md) defines the integration policy: usefulness, security and license audits, deduplication, routing and documentation updates, validation, and publishing only when every check passes.
- **Provenance:** every bundled third-party file is listed with its checksum in [`SOURCES.md`](SOURCES.md).

## Third-Party Licenses & Credits

UIUX Abhishek Design's original work (routing, integration architecture, documentation, frontend engineering and Azure DevOps guides, and templates) is © Abhishek Rampal and licensed under the [MIT License](LICENSE). Bundled third-party material is **not** owned by Abhishek Rampal. It stays the work of its authors and is redistributed under its original licenses:

- **[Impeccable](https://github.com/pbakaus/impeccable)** by Paul Bakaus: [Apache License 2.0](LICENSES/IMPECCABLE_APACHE-2.0.txt), with its [upstream NOTICE](LICENSES/IMPECCABLE_NOTICE.md).
- **[platform-design-skills](https://github.com/ehmo/platform-design-skills)** by ehmo: [MIT](LICENSES/PLATFORM_DESIGN_SKILLS_MIT.txt). Impeccable's iOS and Android references are derived from it.
- **[Apple Design](https://github.com/emilkowalski/skills)** by Emil Kowalski: [MIT](LICENSES/APPLE_DESIGN_MIT.txt).

UIUX Abhishek Design is independent and isn't affiliated with or endorsed by these authors, or by Apple Inc., Google or Microsoft. Apple, Azure DevOps and other trademarks belong to their owners. See [NOTICE.md](NOTICE.md) for full attribution and [SOURCES.md](SOURCES.md) for provenance. Keep `LICENSE`, `NOTICE.md` and `LICENSES/` when you redistribute.
