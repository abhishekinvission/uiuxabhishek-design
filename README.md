# UIUX Abhishek DevKit

> **Design. Build. Automate. Deliver.**

UIUX Abhishek DevKit is one installable Agent Skill, `uiuxabhishek-devkit`, that gives AI coding agents senior-level judgment for UI/UX design, motion, frontend engineering, Git and repository workflows, and Azure DevOps delivery. It works with Claude Code, Codex, Gemini CLI, GitHub Copilot and Antigravity. For each task it loads only the guidance that task needs.

Created and maintained by **Abhishek Rampal ([uiuxAbhishek](https://github.com/abhishekinvission))**.

- **Repository:** [abhishekinvission/uiuxabhishek-devkit](https://github.com/abhishekinvission/uiuxabhishek-devkit)
- **Skill ID:** `uiuxabhishek-devkit` (formerly `uiuxabhishek-design`; see [upgrading](#upgrading-from-uiuxabhishek-design))
- **Current version:** 2.0.1 ([changelog](CHANGELOG.md))

## Install UIUX Abhishek DevKit

**One command installs it globally for all five supported agents:**

```bash
npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a claude-code -a codex -a gemini-cli -a github-copilot -a antigravity -y
```

It needs Node.js 22.20+ and Git, and uses the official [Skills CLI](https://github.com/vercel-labs/skills). Restart your agent afterwards, then ask *"What can uiuxabhishek-devkit do?"* to check it's loaded.

Or install for a single agent:

| Agent | Global install |
| --- | --- |
| Claude Code (terminal, IDE, Claude Desktop Code tab) | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a claude-code -y` |
| OpenAI Codex | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a codex -y` |
| Gemini CLI | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a gemini-cli -y` |
| GitHub Copilot | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a github-copilot -y` |
| Google Antigravity | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a antigravity -y` |

**Local agents vs. Claude Chat.** The commands above install files on your computer for local coding agents. **Claude.ai and Claude Desktop Chat** use skills stored in your Claude account instead, so a terminal install doesn't enable the skill there. For Chat, download `uiuxabhishek-devkit-v<version>.zip` from the [latest release](https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/latest) and upload it under **Customize → Skills → + → Create skill → Upload a skill**.

The bundled capabilities belong to this one skill. Install only `uiuxabhishek-devkit`. **[INSTALL.md](INSTALL.md)** covers requirements, project installs, verification, updates, removal, reloading, migration, Chat uploads and troubleshooting.

### Upgrading from `uiuxabhishek-design`

Version 2.0.0 renamed the skill, so remove the old one and install the new one:

```bash
npx skills remove uiuxabhishek-design -g -y
npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a claude-code -a codex -a gemini-cli -a github-copilot -a antigravity -y
```

Then restart your agents. In Claude Chat, delete the old skill and upload the 2.0.0 ZIP. See [INSTALL.md](INSTALL.md#migrate-from-uiuxabhishek-design) for details.

## What's included

| Area | Capabilities |
| --- | --- |
| **Visual craft** | Design direction, visual hierarchy, layout, spacing, typography, color, theming, design tokens and design-system consistency |
| **UX review** | Critiques, audits, information architecture, UX copy, empty and error states, onboarding, i18n and edge cases |
| **Accessibility and platforms** | WCAG audits, keyboard and focus behavior, contrast, responsive web, iOS and Android conventions |
| **Fluid motion** | Purposeful animation, gestures, drag and flick, interruptible spring motion, sheets and drawers, reduced motion |
| **Frontend engineering** | Pages and routing, API integration, admin CRUD, data reports and exports, state management, testing, code review and release readiness, shared packages and components, microfrontends |
| **Git and repositories** | Status and diff, clone, fetch/pull, branches and sync, safe commits, push, PR/MR creation and review, merges, conflicts, revert and recovery, tags and releases on GitHub, GitLab, Azure Repos, Bitbucket or plain Git |
| **Azure DevOps delivery** | Azure Boards work item → live ticket read → PR reconciliation → clarification and dependency gates → safe Git preflight → implementation → ordered verification → authorized **draft** PR → structured report, for frontend, backend, full-stack or infrastructure work |

### How it picks what to load

`SKILL.md` is a short, agent-neutral router. For each request it:

1. **checks scope:** UI and frontend guidance is for UI work, while Git and Azure DevOps workflows apply to any repository and stack. Other backend-only work loads nothing;
2. **picks a mode** (`answer`, `audit`, `plan`, `implement` or `deliver`) that caps what the agent may change. "Read-only" or "dry run" means no edits; "don't push" means no publishing;
3. **matches capabilities** and loads only their files, in phases when several apply, with one owner per responsibility;
4. **follows your project:** its stack, design system, conventions and checks take priority over reference examples.

Merges, destructive resets, force-pushes, branch or tag deletion, published-history rewrites, releases, deployments and ticket writes always need your explicit approval for that exact operation. Owning the repository doesn't count as approval. Routing relies only on plain Markdown, with no hooks, subagents, MCP servers or vendor-specific tools.

## Using it

Describe the task in plain language. Naming the skill is optional, but you can start with *"Use uiuxabhishek-devkit to…"*. To see everything it can do, ask *"What can uiuxabhishek-devkit do?"*, which shows the built-in [capability guide](skills/uiuxabhishek-devkit/GUIDE.md).

| Area | Example prompt |
| --- | --- |
| UI/UX | "Audit this checkout UI for accessibility and hierarchy. Read-only." |
| Typography | "The pricing headings feel cramped; fix the typography." |
| Motion | "Make this bottom sheet draggable with interruptible spring motion and reduced-motion support." |
| Frontend | "Add a settings page with its own route and keep the form state in the URL." |
| API | "Connect the orders screen to the REST API with typed errors and retry on timeouts." |
| CRUD and reports | "Add an admin users table with server pagination, filters, CSV export and edit forms." |
| Testing | "Write Playwright end-to-end tests for the login flow." |
| Git | "My branch is behind main; sync it without losing my work." · "Commit only the login fix and push the branch." · "Open a draft merge request on GitLab." · "Resolve the merge conflicts after my rebase." |
| Releases | "Plan a v2.1.0 tag and GitHub release." Plans only; publishing needs your go-ahead |
| Azure DevOps | "Dry-run Azure Boards work item 12345." · "Implement item 12345 locally, don't push." · "Deliver item 12345 and open a draft PR; you're authorized to push the task branch." |

**Azure DevOps** runs only for Azure DevOps/Azure Boards work. It needs an approved, signed-in Azure DevOps connector or the `az devops` CLI, and it never guesses the organization, project, repository or target branch. **Git** provider actions use `gh`, `glab` or `az` only when they're installed and signed in. Otherwise the agent does the local Git part and gives you the remaining manual steps.

## Updates and versions

- **Stable releases** are tagged `vX.Y.Z` on GitHub with a Claude upload ZIP and its SHA-256 checksum. See [CHANGELOG.md](CHANGELOG.md).
- **Update a local install:** `npx skills update uiuxabhishek-devkit -g -y`. An install made with the commands above follows `main`, which only receives validated changes. To stay on stable releases only, install a tag (`abhishekinvission/uiuxabhishek-devkit#v2.0.1`) or use the optional updater.
- **Update notifications (optional):** the [updater](INSTALL.md#optional-update-notifications-and-automatic-updates) checks GitHub once a day for a newer stable release and notifies you. It never changes anything unless you opt in with `enable-auto-update --yes`. It runs on macOS, Linux and Windows and touches only `uiuxabhishek-devkit`.
- **Claude Chat uploads** are always updated by hand: delete the old skill and upload the new ZIP.
- **Remove:** `npx skills remove uiuxabhishek-devkit -g -y`.

## Repository layout

```text
skills/uiuxabhishek-devkit/
├── SKILL.md            # Single entry point: intent, mode and capability router
├── GUIDE.md            # User-facing capability and usage guide
├── NOTICE.md, LICENSE  # In-skill attribution and license (travel with installs)
├── LICENSES/           # In-skill copies of required third-party licenses and notices
├── templates/          # PR description and ADO delivery report templates
└── references/         # Guidance, loaded only when relevant
    ├── impeccable/     # Visual craft (third-party)
    ├── apple-design/   # Interaction and motion (third-party)
    ├── frontend/       # Frontend engineering guides (original)
    └── workflows/      # Git workflow and Azure DevOps delivery (original)
INSTALL.md              # Installation, migration, updates, removal and troubleshooting
CHANGELOG.md            # Versions and releases
tools/                  # Upload ZIP builder and the optional updater (not installed)
tests/                  # Validation, routing, Git, updater and migration tests (not installed)
LICENSE, NOTICE.md, SOURCES.md, LICENSES/, CLAUDE.md
```

This is a **guidance-only** skill. The installed skill doesn't include CLIs, binaries, hooks, scripts or credentials. The optional updater lives in `tools/` and is never installed with the skill.

## Maintenance

- **Validate:** `python3 tests/validate.py --cli`. It uses the Python standard library, plus Node.js and the Skills CLI for the install, migration and updater checks. It covers:
  - discovery and routing scenarios;
  - the Git and updater sandboxes;
  - links, checksums, license mirrors and the security scan;
  - the upload ZIP;
  - leftover references to the old skill ID.
- **Release:**
  1. Bump `metadata.version` in `SKILL.md` and add a `CHANGELOG.md` entry.
  2. Run `python3 tools/package_skill.py`.
  3. Attach the files from `dist/` to a `v<version>` GitHub Release.
- **Add a source:** follow [CLAUDE.md](CLAUDE.md). Every bundled third-party file is checksummed in [SOURCES.md](SOURCES.md).

## Third-Party Licenses & Credits

UIUX Abhishek DevKit's original work is © Abhishek Rampal and licensed under the [MIT License](LICENSE). That covers the routing, architecture, documentation, frontend, Git and Azure DevOps guides, templates and tooling. Bundled third-party material is **not** owned by Abhishek Rampal. It stays the work of its authors and is redistributed under its original licenses:

- **[Impeccable](https://github.com/pbakaus/impeccable)** by Paul Bakaus: [Apache License 2.0](LICENSES/IMPECCABLE_APACHE-2.0.txt), with its [upstream NOTICE](LICENSES/IMPECCABLE_NOTICE.md).
- **[platform-design-skills](https://github.com/ehmo/platform-design-skills)** by ehmo: [MIT](LICENSES/PLATFORM_DESIGN_SKILLS_MIT.txt). Impeccable's iOS and Android references are derived from it.
- **[Apple Design](https://github.com/emilkowalski/skills)** by Emil Kowalski: [MIT](LICENSES/APPLE_DESIGN_MIT.txt).

UIUX Abhishek DevKit is independent and isn't affiliated with or endorsed by these authors, or by Apple Inc., Google or Microsoft. Apple, Azure DevOps and other trademarks belong to their owners. See [NOTICE.md](NOTICE.md) for full attribution and [SOURCES.md](SOURCES.md) for provenance. Keep `LICENSE`, `NOTICE.md` and `LICENSES/` when you redistribute.
