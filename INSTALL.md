# Install UIUX Abhishek Design

UIUX Abhishek Design is **one** skill, `uiuxabhishek-design`. Its design, motion, frontend and Azure DevOps capabilities are bundled inside it and load automatically, so never install them separately.

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
npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a claude-code -a codex -a gemini-cli -a github-copilot -a antigravity -y
```

`-g` installs for your user account, so every project can use it. `-a` picks the agents and `-y` skips the prompts. Leave out the agents you don't use.

### Install for one agent

| Agent | CLI identifier | Command |
| --- | --- | --- |
| Claude Code (including the Desktop Code tab) | `claude-code` | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a claude-code -y` |
| OpenAI Codex | `codex` | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a codex -y` |
| Gemini CLI | `gemini-cli` | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a gemini-cli -y` |
| GitHub Copilot | `github-copilot` | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a github-copilot -y` |
| Google Antigravity | `antigravity` | `npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a antigravity -y` |

To install into the current project only, so it's shared through the repository, leave out `-g`. Run `npx skills add --help` to see every option your CLI version supports.

**Where it lands.** With Skills CLI 1.7.6, a global install puts one copy in `~/.agents/skills/uiuxabhishek-design`, which Codex, Gemini CLI, GitHub Copilot and Antigravity read. Claude Code gets `~/.claude/skills/uiuxabhishek-design`, linked to that copy when you install for several agents. The CLI prints the exact paths when it finishes.

### Verify

1. Run `npx skills list -g`. It should show `uiuxabhishek-design` and the agents it's linked to.
2. Restart the agent or open a new session (see [Reload](#reload-after-install-update-or-removal)).
3. Ask: *"What can uiuxabhishek-design do?"* The agent should answer from the skill's capability guide. In Claude Code you can also type `/` and look for `uiuxabhishek-design` in the list.

### Update

```bash
npx skills update uiuxabhishek-design -g -y
```

Running the install command again also works. Copies on other machines and agent instances (for example, a shared office installation) don't update when this repository changes. Update each one.

### Remove

```bash
npx skills remove uiuxabhishek-design -g -y
```

To remove it from one agent only, add `-a <identifier>`, for example `-a codex`.

### Reload after install, update or removal

Agents usually read their skill list when a session starts. After any change, start a new session, or close and reopen the agent, IDE window or Claude Desktop.

## Claude.ai and Claude Desktop Chat

Claude.ai, Claude Desktop **Chat** and Cowork use skills stored in your Claude account, not files on your computer, so the CLI can't install there. Upload the packaged ZIP instead.

1. Download `uiuxabhishek-design-v<version>.zip` from the [latest release](https://github.com/abhishekinvission/uiuxabhishek-design/releases/latest). Its `.sha256` file is published alongside if you want to check the download.
2. In Claude, turn on **Settings → Capabilities → Code execution and file creation** (called "Create and edit files" in newer layouts). Skills need it.
3. Go to **Customize → Skills**, click **+**, choose **+ Create skill → Upload a skill** and select the ZIP. **Don't unzip it.**
4. Make sure the skill is toggled on. Then ask: *"What can uiuxabhishek-design do?"*

**What's in the ZIP.** It contains one folder, `uiuxabhishek-design/`, with the full skill: `SKILL.md`, `GUIDE.md`, `references/`, `templates/`, `LICENSE`, `NOTICE.md` and `LICENSES/`. Claude's upload form allows descriptions of up to 200 characters, so the packaged `SKILL.md` carries a shorter description. Every other file matches this repository byte for byte.

**Plans and organizations.** Skills are available on Claude's individual and organization plans. On Team and Enterprise, an owner may need to allow skills or user-created skills, or to provision the skill for everyone.

**What works in Chat.** Chat can't see your local repository or run your Git, test or Azure DevOps tools. Use it for design guidance, audits and critiques of screenshots or pasted code, UX copy and plans. Implementing changes and the Azure DevOps ticket-to-draft-PR workflow need a local coding agent with access to your repository.

**Updating.** Download the new release ZIP, delete the old skill under **Customize → Skills**, then upload the new ZIP.

**Claude Code and account skills.** Skills you turn on in your Claude account also load in Claude Code (v2.1.273 or later, signed in with the same Claude account, not an API key or cloud provider), in cloud sessions and in local sessions. If you also installed the skill with the CLI, Claude Code may see two copies. Keep just one for Claude Code.

To build the ZIP yourself from a checkout, run `python3 tools/package_skill.py`. It writes the ZIP and its checksum to `dist/` and uses only the Python standard library.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `npx: command not found`, or the CLI fails to start | Install or upgrade Node.js to 22.20 or later, then open a new terminal. |
| `Unknown agent`, or a flag is rejected | Check `npx skills add --help`. Use the identifiers exactly as listed above. |
| Installed, but the agent doesn't use it | Restart the agent or open a new session. Run `npx skills list -g` to check it's linked to that agent. Name it in your prompt: *"Use uiuxabhishek-design to…"* |
| Installed into the wrong project | Project installs (without `-g`) only apply to the folder you ran them in. Reinstall with `-g` or from the right project. |
| The skill appears twice | It's installed both globally and in the project, or both by the CLI and through your Claude account. Remove one copy. |
| Claude upload rejected | Upload the release ZIP unchanged. Re-zipping the folder contents loose, or using the repository's own `SKILL.md`, whose description is longer than 200 characters, fails. Check that code execution is on and that your organization allows skills. |
| The skill shows in Chat but can't edit your code | That's expected. Chat has no access to your local repository. Use a local coding agent for implementation and Azure DevOps delivery. |
| Azure DevOps steps stop at a dry run | That's intended without write authorization. You also need an approved, signed-in Azure DevOps connector or `az devops` CLI, and you have to say **implement** or **deliver** and grant the permissions. See [GUIDE.md](skills/uiuxabhishek-design/GUIDE.md). |

Licensing and credits travel with every install in `NOTICE.md` and `LICENSES/`. See the [README](README.md#third-party-licenses--credits).
