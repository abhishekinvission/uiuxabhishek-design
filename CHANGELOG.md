# Changelog

All notable changes to UIUX Abhishek DevKit (formerly UIUX Abhishek Design) are recorded here. The project follows [Semantic Versioning](https://semver.org): a skill ID change or removed capability is a major version, a new capability a minor one, and fixes a patch.

**Stable releases** are Git tags with a GitHub Release, a Claude upload ZIP and its SHA-256 checksum. These are what the optional updater installs. **Development versions** were set in `SKILL.md` on `main` but never tagged or released.

## [2.0.0] — 2026-11-04 (stable release)

**Breaking:** the skill ID changes from `uiuxabhishek-design` to `uiuxabhishek-devkit`, and the repository from `abhishekinvission/uiuxabhishek-design` to `abhishekinvission/uiuxabhishek-devkit`. Remove the old skill and install the new one; see [INSTALL.md](INSTALL.md#migrate-from-uiuxabhishek-design).

- Renamed to **UIUX Abhishek DevKit**, with the tagline *Design. Build. Automate. Deliver.* The skill folder is now `skills/uiuxabhishek-devkit/`.
- All capabilities from 1.1.0 are kept unchanged: design, motion, accessibility, the nine frontend engineering guides, Git workflows, Azure DevOps delivery, templates, notices and licenses. Impeccable and Apple Design files are byte-identical.
- Added an optional, opt-in updater, `tools/updater/devkit-update.mjs`, which isn't part of the installed skill:
  - It checks for stable releases and notifies by default, and installs updates only after `enable-auto-update --yes`.
  - It schedules through launchd, systemd or cron, or Task Scheduler.
  - Before installing, it verifies the repository's identity, the release, its checksum and the skill-folder hash.
- Added this changelog and migration instructions, and the README now covers updates and versioning.
- Tests:
  - an updater sandbox with a mock GitHub API and a mock Skills CLI;
  - an isolated migration from the old skill ID;
  - install, update and removal for each agent;
  - a check for leftover references to the old ID.

## [1.1.0] — 2026-11-04 (development version, not released)

Commit `82f5367` on `main`. It was never tagged and has no GitHub Release or ZIP; its contents ship in 2.0.0.

- Universal Git and repository workflow for any provider:
  - status, sync, branches, safe commits, push, PR/MR creation and review, merges;
  - conflicts, recovery, history rewrites, tags and releases;
  - explicit approval gates and work preservation.
- Azure DevOps delivery now reuses the shared Git guidance instead of repeating it.
- `plan` now outranks `deliver` when both are requested. Added 14 Git routing scenarios and a 27-check Git sandbox.

Commit `a05f8fe` disabled automatic Claude commit and PR attribution, in this repository only. The skill didn't change.

## [1.0.0] — 2026-11-04 (stable release)

Tag `v1.0.0` (commit `dbb612c`), with the GitHub Release asset `uiuxabhishek-design-v1.0.0.zip` (SHA-256 `5729a0f916232c63520b897bb05a5fc0d318ec9937099a5352ab199145fd799b`). This tag and release are kept unchanged.

- Cross-agent installation guide (`INSTALL.md`) and a versioned Claude upload ZIP built by `tools/package_skill.py`.

## Pre-1.0 development (2026-11-03 to 2026-11-04, untagged)

- `8a6b768`: `SKILL.md` rebuilt as a selective, agent-neutral capability router with a capability guide (`GUIDE.md`) and routing tests.
- `036b394`: frontend engineering expansion (nine guides, Azure DevOps ticket-to-draft-PR delivery, two templates).
- `f0b098f`: branding, ownership and licensing policy for integrating sources.
- `8c7c9e5`, `93b5815`, `72d0bbf`: initial skill with Impeccable and Apple Design, the integration workflow and corrected install commands.

[2.0.0]: https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/tag/v2.0.0
[1.1.0]: https://github.com/abhishekinvission/uiuxabhishek-devkit/commit/82f5367
[1.0.0]: https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/tag/v1.0.0
