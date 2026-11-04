# Install UIUX Abhishek DevKit

UIUX Abhishek DevKit is **one** skill, `uiuxabhishek-devkit`. Its design, motion, frontend, Git and Azure DevOps capabilities are bundled inside it and load automatically, so never install them separately.

How you install it depends on where your agent runs:

| Where you use Claude or your agent | How the skill gets there | Section |
| --- | --- | --- |
| **Local coding agents:** Claude Code (terminal, IDE or the Claude Desktop **Code** tab, local sessions), Codex, Gemini CLI, GitHub Copilot, Antigravity | Skills CLI, installed on your computer | [Local agents](#local-coding-agents) |
| **Cloud / account-based Chat:** Claude.ai, Claude Desktop **Chat** and Cowork, Claude Code cloud sessions | ZIP upload in your Claude account | [Claude Chat upload](#claudeai-and-claude-desktop-chat) |

A local install doesn't reach cloud Chat, and an uploaded ZIP doesn't install anything for Codex, Gemini CLI, Copilot or Antigravity. Set up each environment you use.

## Local coding agents

### Requirements

- [Node.js](https://nodejs.org) **22.20 or later** (for `npx`) and Git.
- The agent itself, installed and signed in, in a version that supports Agent Skills.
- Network access to GitHub.

### Install globally (all supported agents)

```bash
npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a claude-code -a codex -a gemini-cli -a github-copilot -a antigravity -y
```

`-g` installs for your user account, so every project can use it. `-a` picks the agents and `-y` skips the prompts. Leave out the agents you don't use.

### Install for one agent

| Agent | CLI identifier | Command |
| --- | --- | --- |
| Claude Code (including the Desktop Code tab) | `claude-code` | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a claude-code -y` |
| OpenAI Codex | `codex` | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a codex -y` |
| Gemini CLI | `gemini-cli` | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a gemini-cli -y` |
| GitHub Copilot | `github-copilot` | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a github-copilot -y` |
| Google Antigravity | `antigravity` | `npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a antigravity -y` |

To install into the current project only, so it's shared through the repository, leave out `-g`. Run `npx skills add --help` to see every option your CLI version supports.

**Stable releases only.** The commands above follow the repository's `main` branch. To pin a release, add the tag: `npx skills add abhishekinvission/uiuxabhishek-devkit#v2.0.0 --skill uiuxabhishek-devkit -g -a claude-code -y`. A pinned install stays on that tag when you run `update`, until you install a newer tag or use the [updater](#optional-update-notifications-and-automatic-updates).

**Where it lands.** With Skills CLI 1.7.6, a global install puts one copy in `~/.agents/skills/uiuxabhishek-devkit`, which Codex, Gemini CLI, GitHub Copilot and Antigravity read. Claude Code gets `~/.claude/skills/uiuxabhishek-devkit`, linked to that copy when you install for several agents. The CLI prints the exact paths when it finishes.

### Verify

1. Run `npx skills list -g`. It should show `uiuxabhishek-devkit`.
2. Restart the agent or open a new session (see [Reload](#reload-after-install-update-or-removal)).
3. Ask: *"What can uiuxabhishek-devkit do?"* The agent should answer from the skill's capability guide. In Claude Code you can also type `/` and look for `uiuxabhishek-devkit` in the list.

### Update

```bash
npx skills update uiuxabhishek-devkit -g -y
```

Running the install command again also works. Copies on other machines and agent instances (for example, a shared office installation) don't update when this repository changes. Update each one, or set up the [updater](#optional-update-notifications-and-automatic-updates) on each machine.

### Remove

```bash
npx skills remove uiuxabhishek-devkit -g -y
```

To remove it from one agent only, add `-a <identifier>`, for example `-a codex`.

### Reload after install, update or removal

Agents usually read their skill list when a session starts. After any change, start a new session, or close and reopen the agent, IDE window or Claude Desktop.

## Migrate from `uiuxabhishek-design`

Version 2.0.0 renamed the skill from `uiuxabhishek-design` to `uiuxabhishek-devkit` and the repository to `abhishekinvission/uiuxabhishek-devkit`. Because the skill ID changed, `npx skills update` can't migrate an old install. Remove the old skill, then install the new one. The capabilities are the same, plus everything added since your last update.

### On a Mac (or Linux)

1. See what's installed: `npx skills list -g`. Also run `npx skills list` inside any project where you installed it without `-g`.
2. Remove the old skill:

   ```bash
   npx skills remove uiuxabhishek-design -g -y
   ```

   For a project install, run `npx skills remove uiuxabhishek-design -y` inside that project.
3. Install the new skill for the agents you use:

   ```bash
   npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a claude-code -a codex -a gemini-cli -a github-copilot -a antigravity -y
   ```

4. Check: `npx skills list -g` shows `uiuxabhishek-devkit` and no `uiuxabhishek-design`. Then restart your agents and ask *"What can uiuxabhishek-devkit do?"*.
5. Claude Chat: under **Customize → Skills**, delete `uiuxabhishek-design` and upload `uiuxabhishek-devkit-v2.0.0.zip` (see [below](#claudeai-and-claude-desktop-chat)).
6. If you cloned this repository, `git remote set-url origin https://github.com/abhishekinvission/uiuxabhishek-devkit.git` points it at the new name. GitHub also redirects the old URL.

### Another user (Windows, macOS or Linux)

The same commands work in Terminal, PowerShell or Command Prompt once Node.js 22.20+ and Git are installed:

```bash
npx skills remove uiuxabhishek-design -g -y
npx skills add abhishekinvission/uiuxabhishek-devkit --skill uiuxabhishek-devkit -g -a claude-code -a codex -a gemini-cli -a github-copilot -a antigravity -y
npx skills list -g
```

Leave out the agents they don't use, restart their agents, and replace the Claude Chat upload if they use one. Removing the old skill only deletes that skill's folder: other skills, agent settings and projects aren't touched.

## Claude.ai and Claude Desktop Chat

Claude.ai, Claude Desktop **Chat** and Cowork use skills stored in your Claude account, not files on your computer, so the CLI can't install there. Upload the packaged ZIP instead.

1. Download `uiuxabhishek-devkit-v<version>.zip` from the [latest release](https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/latest). Its `.sha256` file is published alongside if you want to check the download.
2. In Claude, turn on **Settings → Capabilities → Code execution and file creation** (called "Create and edit files" in newer layouts). Skills need it.
3. Go to **Customize → Skills**, click **+**, choose **+ Create skill → Upload a skill** and select the ZIP. **Don't unzip it.**
4. Make sure the skill is toggled on. Then ask: *"What can uiuxabhishek-devkit do?"*

**Replacing a version.** Uploaded skills don't update themselves, and the updater can't reach your Claude account. To move to a new release, delete the old skill (including `uiuxabhishek-design` if you have it) under **Customize → Skills**, then upload the new ZIP.

**What's in the ZIP.** It contains one folder, `uiuxabhishek-devkit/`, with the full skill: `SKILL.md`, `GUIDE.md`, `references/`, `templates/`, `LICENSE`, `NOTICE.md` and `LICENSES/`. Claude's upload form allows descriptions of up to 200 characters, so the packaged `SKILL.md` carries a shorter description. Every other file matches the release tag byte for byte. The build is reproducible: `python3 tools/package_skill.py` at the same tag produces the same checksum.

**Plans and organizations.** Skills are available on Claude's individual and organization plans. On Team and Enterprise, an owner may need to allow skills or user-created skills, or to provision the skill for everyone.

**What works in Chat.** Chat can't see your local repository or run your Git, test or Azure DevOps tools. Use it for design guidance, audits and critiques of screenshots or pasted code, UX copy and plans. Implementing changes, Git operations and the Azure DevOps workflow need a local coding agent with access to your repository.

**Claude Code and account skills.** Skills you turn on in your Claude account also load in Claude Code (v2.1.273 or later, signed in with the same Claude account, not an API key or cloud provider), in cloud sessions and in local sessions. If you also installed the skill with the CLI, Claude Code may see two copies. Keep just one for Claude Code.

## Optional update notifications and automatic updates

The updater is a single Node.js script, `devkit-update.mjs`, published with each release. It's optional and nothing installs it for you.

- **Default: check and notify.** Once a day it asks GitHub for the latest **stable** release (not drafts, prereleases or unreleased commits), compares it with your installed version and shows a desktop notification on macOS and Linux. On Windows, the result goes to the log and `status`. It changes nothing.
- **Automatic updates: only if you opt in** with `enable-auto-update --yes`.
- **Before any install, it verifies:**
  - the repository by its permanent GitHub ID;
  - that the release is a stable `vX.Y.Z` tag;
  - that the tag's `SKILL.md` has the same ID and version;
  - that the release ZIP checksum matches GitHub's digest, when one is published.
- **How it installs:** it runs the official Skills CLI pinned to that tag, for `uiuxabhishek-devkit` only and for the agents you chose. Afterwards it checks the installed version, tag and folder hash against the release.
- **Rollback:** it backs up the previous version first (it keeps the last three) and prints exact rollback steps if anything fails.
- **Safety:** it never touches other skills, agent settings, permissions or projects. It needs no credentials and runs no background service. The only code it runs is the official Skills CLI, through `npx`, pinned to the version these docs were tested with (`skills@1.7.6`). A lock file prevents overlapping runs.
- **Scheduling** uses each platform's own scheduler: a launchd agent on macOS, a systemd user timer or cron on Linux, and Task Scheduler on Windows.

**Set it up** (read the script first; it's short). On macOS or Linux:

```bash
curl -fsSLO https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/latest/download/devkit-update.mjs
curl -fsSLO https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/latest/download/devkit-update.mjs.sha256
shasum -a 256 -c devkit-update.mjs.sha256      # Linux: sha256sum -c devkit-update.mjs.sha256
node devkit-update.mjs check                   # one-off check, changes nothing
node devkit-update.mjs setup                   # copies itself to ~/.uiuxabhishek-devkit and schedules daily notify-only checks
```

On Windows (PowerShell):

```powershell
Invoke-WebRequest https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/latest/download/devkit-update.mjs -OutFile devkit-update.mjs
Invoke-WebRequest https://github.com/abhishekinvission/uiuxabhishek-devkit/releases/latest/download/devkit-update.mjs.sha256 -OutFile devkit-update.mjs.sha256
(Get-FileHash devkit-update.mjs -Algorithm SHA256).Hash.ToLower()   # must equal the first word of devkit-update.mjs.sha256
node devkit-update.mjs setup
```

After `setup`, run the installed copy, for example `node ~/.uiuxabhishek-devkit/devkit-update.mjs status` (Windows: `node $HOME\.uiuxabhishek-devkit\devkit-update.mjs status`):

| Command | What it does |
| --- | --- |
| `setup [--agents claude-code,codex] [--no-schedule]` | Installs the updater and a daily notify-only check. Agents default to the ones the skill is installed for |
| `check` | Checks now and prints installed vs. latest stable. Changes nothing |
| `update --yes` | Installs the latest verified stable release now |
| `enable-auto-update --yes` | Lets the daily check install verified stable releases |
| `status` | Shows mode, schedule, agents, versions, last result, errors and the log path |
| `disable` | Removes the schedule and stops automatic updates. Manual `check`/`update` still work |
| `uninstall` | Removes the schedule and `~/.uiuxabhishek-devkit`. The skill stays installed |

**If an update fails,** the installed skill is either unchanged or restorable. `status` and `update.log` show the error, the backup folder and the exact command to reinstall the previous tag. A lock left by a crashed run is cleared automatically after two hours. The updater only handles installs made with the Skills CLI; Claude Chat uploads stay manual.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `npx: command not found`, or the CLI fails to start | Install or upgrade Node.js to 22.20 or later, then open a new terminal. |
| `Unknown agent`, or a flag is rejected | Check `npx skills add --help`. Use the identifiers exactly as listed above. |
| Installed, but the agent doesn't use it | Restart the agent or open a new session. Run `npx skills list -g` to check it's installed. Name it in your prompt: *"Use uiuxabhishek-devkit to…"* |
| Both `uiuxabhishek-design` and `uiuxabhishek-devkit` appear | Remove the old one: `npx skills remove uiuxabhishek-design -g -y`, then restart. |
| `npx skills update` reports the old skill is missing | The skill was renamed in 2.0.0. [Migrate](#migrate-from-uiuxabhishek-design) instead of updating. |
| Installed into the wrong project | Project installs (without `-g`) only apply to the folder you ran them in. Reinstall with `-g` or from the right project. |
| The skill appears twice | It's installed both globally and in the project, or both by the CLI and through your Claude account. Remove one copy. |
| Claude upload rejected | Upload the release ZIP unchanged. Re-zipping the folder contents loose, or using the repository's own `SKILL.md`, whose description is longer than 200 characters, fails. Check that code execution is on and that your organization allows skills. |
| The skill shows in Chat but can't edit your code | That's expected. Chat has no access to your local repository. Use a local coding agent for implementation, Git and Azure DevOps delivery. |
| The updater says "another updater run is in progress" | Wait for it to finish. If nothing is running, the lock clears after two hours, or delete `~/.uiuxabhishek-devkit/update.lock`. |
| The updater reports a verification failure | It didn't update. Check `status` and keep your current version, or reinstall a known tag with the command it prints. |
| Azure DevOps steps stop at a dry run | That's intended without write authorization. You also need an approved, signed-in Azure DevOps connector or `az devops` CLI, and you have to say **implement** or **deliver** and grant the permissions. See [GUIDE.md](skills/uiuxabhishek-devkit/GUIDE.md). |

Licensing and credits travel with every install in `NOTICE.md` and `LICENSES/`. See the [README](README.md#third-party-licenses--credits).
