# UIUX Abhishek Design

> **Visual Craft. Fluid Motion. Exceptional Experiences.**

UIUX Abhishek Design is a single, installable Agent Skill (`uiuxabhishek-design`) that gives AI coding agents senior-level UI/UX and frontend engineering judgment. It covers visual hierarchy, layout and typography, gesture physics, spring motion and accessible interaction, framework-neutral frontend delivery, and Azure DevOps ticket-to-draft-PR workflows.

Created and maintained by **Abhishek Rampal ([uiuxAbhishek](https://github.com/abhishekinvission))**.

- **Repository:** [abhishekinvission/uiuxabhishek-design](https://github.com/abhishekinvission/uiuxabhishek-design)
- **Skill ID:** `uiuxabhishek-design`
- **Entry point:** [`skills/uiuxabhishek-design/SKILL.md`](skills/uiuxabhishek-design/SKILL.md)

## What it does

| Area | Capabilities |
| --- | --- |
| **Visual craft** | Design direction, visual hierarchy, layout, spacing, typography, color, theming, design tokens and design-system consistency |
| **UX review** | Critiques, audits, information architecture, cognitive load, UX copy, empty/error states, onboarding, i18n and edge cases |
| **Fluid motion** | Direct manipulation, press feedback, interruptible transitions, velocity-aware springs, drag/flick, sheets and drawers, reduced motion |
| **Platforms** | Responsive web, plus iOS and Android platform conventions where they apply |
| **Frontend engineering** | Pages and routing, API integration, admin CRUD, data reports and exports, state management, testing, review and release readiness, shared packages and components, microfrontends |
| **Azure DevOps delivery** | Azure Boards work item → live ticket read → PR reconciliation → clarification and dependency gates → safe Git preflight → implementation → ordered verification → authorized **draft** PR → structured report |
| **Quality gates** | Accessibility, keyboard and focus behavior, contrast, performance, responsive verification and the project's real test/lint/build checks |

### How it routes

`SKILL.md` is a lightweight, agent-neutral router. For each request it:

1. checks that the task is frontend/UI work (backend-only work loads nothing);
2. picks a **mode** (`answer`, `audit`, `plan`, `implement` or `deliver`) that caps what the agent may change;
3. matches **capabilities** and loads only their files, in phases when several apply, with one owner per responsibility;
4. follows the project's real stack and conventions over reference examples.

Design tasks go straight to the matching Impeccable playbook instead of its full entry point. Playbooks that need upstream tooling are never loaded. Routing relies only on plain Markdown, with no hooks, subagents, MCP servers or vendor-specific tools.

It doesn't impose a single visual style, framework, library or test runner. Your product's existing design system, repository conventions, accessibility requirements and explicit scope take priority.

**Azure DevOps delivery** is opt-in. It runs only for Azure Boards work, needs an approved, authenticated Azure DevOps connector or `az` CLI that your agent can already use, and never guesses the organization, project, repository or target branch. Without write authorization it stays in audit/dry-run mode. It never merges, deploys or edits ticket state on its own.

## Supported agents

UIUX Abhishek Design follows the open [Agent Skills](https://agentskills.io) format, so it works with any agent that supports it, including:

- Claude Code
- OpenAI Codex
- Gemini CLI
- GitHub Copilot
- Google Antigravity
- other Agent Skills–compatible agents, through their own skill or repository-import mechanism

Agent names and flags depend on the version of the Skills CLI you have installed. Run `npx skills --help` to see the options it supports.

## Installation

Install into the current project:

```bash
npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design
```

Install globally for several agents at once:

```bash
npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a claude-code -a codex -a gemini-cli -a github-copilot -a antigravity -y
```

Preview what the repository provides before you install:

```bash
npx skills add abhishekinvission/uiuxabhishek-design --list
```

## Usage

Once it's installed, agents pick the skill up automatically for frontend design and engineering work. Ask *"What can uiuxabhishek-design do?"* to get the built-in capability guide ([`GUIDE.md`](skills/uiuxabhishek-design/GUIDE.md)). You can also name the skill directly:

- *"Use uiuxabhishek-design to audit this UI for hierarchy, typography, responsive spacing and press feedback. Read-only: report findings without editing."*
- *"Use uiuxabhishek-design to redesign this settings page so it's calmer and easier to scan."*
- *"Use uiuxabhishek-design to make this bottom sheet draggable with interruptible, velocity-aware spring motion and reduced-motion support."*
- *"Use uiuxabhishek-design to add an admin table with server pagination, filters, CSV export and edit forms, with tests."*
- *"Use uiuxabhishek-design to deliver Azure Boards work item 12345 as a dry run."* Add authorization to publish when you want a draft PR.

The skill respects your scope. Read-only audits never edit files, and code samples or commands in its references are documentation, not permission to run them.

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
    └── workflows/      # Azure DevOps delivery (original)
LICENSE                 # MIT license for original UIUX Abhishek Design work
NOTICE.md               # Ownership, attribution and redistribution notice
SOURCES.md              # Provenance and SHA-256 checksums of bundled third-party files
LICENSES/               # Third-party licenses and notices
CLAUDE.md               # Maintainer policy for integrating new sources
tests/                  # Repository validation and routing scenarios (not installed)
```

This is a **guidance-only** skill. It doesn't bundle CLIs, binaries, hooks, scripts or credentials (including Azure DevOps credentials or connectors). Advanced Impeccable tooling, for example, needs a separate installation of the original project.

## Maintenance

- **Updating installed copies:** run the install command again, or `npx skills update` if your Skills CLI version supports it. Publishing to GitHub doesn't update copies already installed on other machines or agent instances.
- **Validating:** run `python3 tests/validate.py --cli`. It uses the Python standard library only, plus the Skills CLI for the discovery check. It covers single-skill discovery, links, checksums, license mirrors, routing coverage, the scenarios in [`tests/routing_scenarios.json`](tests/routing_scenarios.json), context budget and a secret scan.
- **Adding a source:** give the maintainer's Claude Code session a GitHub skill URL, a `SKILL.md`, a skill directory or an archive. [`CLAUDE.md`](CLAUDE.md) defines the integration policy: usefulness, security and license audits, deduplication, routing and documentation updates, validation, and publishing only when every check passes.
- **Provenance:** every bundled third-party file is listed with its checksum in [`SOURCES.md`](SOURCES.md).

## Third-Party Licenses & Credits

UIUX Abhishek Design's original work (routing, integration architecture, documentation, frontend engineering and Azure DevOps guides, and templates) is © Abhishek Rampal and licensed under the [MIT License](LICENSE). Bundled third-party material is **not** owned by Abhishek Rampal. It stays the work of its authors and is redistributed under its original licenses:

- **[Impeccable](https://github.com/pbakaus/impeccable)** by Paul Bakaus: [Apache License 2.0](LICENSES/IMPECCABLE_APACHE-2.0.txt), with its [upstream NOTICE](LICENSES/IMPECCABLE_NOTICE.md).
- **[platform-design-skills](https://github.com/ehmo/platform-design-skills)** by ehmo: [MIT](LICENSES/PLATFORM_DESIGN_SKILLS_MIT.txt). Impeccable's iOS and Android references are derived from it.
- **[Apple Design](https://github.com/emilkowalski/skills)** by Emil Kowalski: [MIT](LICENSES/APPLE_DESIGN_MIT.txt).

UIUX Abhishek Design is independent and isn't affiliated with or endorsed by these authors, or by Apple Inc., Google or Microsoft. Apple, Azure DevOps and other trademarks belong to their owners. See [NOTICE.md](NOTICE.md) for full attribution and [SOURCES.md](SOURCES.md) for provenance. Keep `LICENSE`, `NOTICE.md` and `LICENSES/` when you redistribute.
