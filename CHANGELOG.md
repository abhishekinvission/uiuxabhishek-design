# Changelog

All notable changes to UIUX Abhishek DevKit (formerly UIUX Abhishek Design) are recorded here. The project follows [Semantic Versioning](https://semver.org): a skill ID change or removed capability is a major version, a new capability a minor one, and fixes a patch.

**Stable releases** are Git tags with a GitHub Release, a Claude upload ZIP and its SHA-256 checksum. These are what the optional updater installs. **Development versions** were set in `SKILL.md` on `main` but never tagged or released.

## [2.0.1] — 2026-11-05 (stable release)

Fixes only. The skill ID, capabilities, install commands and the Claude upload ZIP format are unchanged.

- **Updater: reliable Node path.**
  - `setup` saves the stable Node link on `PATH` (for Homebrew, `/opt/homebrew/bin/node`, not `Cellar/node/<version>/bin/node`) as `node` in `config.json`.
  - Later `setup` runs, `disable` followed by `setup`, and `enable-auto-update` reuse the saved path.
  - A missing or non-Node path is replaced and reported. An invalid `DEVKIT_NODE` is rejected without changing anything.
  - Re-running `setup` upgrades a 2.0.0 configuration in place.
- **Updater: missed-check detection.**
  - `status` shows the scheduled Node path.
  - It warns when no scheduled check has run for about 48 hours, or when the saved Node path no longer runs.
  - It shows a first check after `setup` as pending, not overdue.
  - A scheduled run that fails still counts as a run and shows its error.
- **Strict read-only Git.**
  - `audit`, `plan` and ADO dry runs never run `git fetch` or write refs unless the user authorizes that exact operation. They use `git --no-optional-locks status` and `git ls-remote` instead.
  - In any mode, "don't fetch" rules out fetch and pull, and "offline" or "no network" rules out every network call.
- **Routing.**
  - The backend part of a full-stack or Azure DevOps task selects no Design or Engineering guide.
  - `harden` now matches "offline state", "offline support" or "network failure" rather than the bare word "offline", so an offline session no longer loads it.
- **Docs.** INSTALL.md documents `DEVKIT_NODE`, the saved Node path, updating from the 2.0.0 updater, and recovery when a check is overdue or Node is missing. GUIDE.md lists the no-fetch and offline limits.
- **Tests.**
  - 9 new routing scenarios (44 in total): backend-only ADO, frontend part of a full-stack task, a GitHub issue that isn't ADO, offline and no-fetch Git and ADO, and an offline UI state.
  - 3 Git sandbox checks (30 in total), which show the audit command set leaves `.git` byte-identical.
  - 23 updater sandbox checks (78 in total): Homebrew upgrade, re-setup, disable and re-enable, a missing or invalid Node, and stale, pending and failing checks.

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

[2.0.1]: https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/tag/v2.0.1
[2.0.0]: https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/tag/v2.0.0
[1.1.0]: https://github.com/abhishekinvission/uiuxabhishek-devkit/commit/82f5367
[1.0.0]: https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/tag/v1.0.0
