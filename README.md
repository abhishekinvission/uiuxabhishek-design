# UIUX Abhishek Design

> Visual Craft. Fluid Motion. Exceptional Experiences.

**Skill name:** `uiuxabhishek-design`

A portable Agent Skill for visual design craft and fluid UI motion, combining documentation guidance from **Impeccable** (Paul Bakaus) and **Apple Design** (Emil Kowalski). Maintained as an independent integration under the uiuxabhishek identity; not affiliated with Apple or the upstream authors.

## Installation

Once this folder is pushed to your public GitHub repo named `uiuxabhishek-design`, install it with the official Skills CLI:

```bash
npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design
```

For global installation across commonly used agents:

```bash
npx skills add abhishekinvission/uiuxabhishek-design --skill uiuxabhishek-design -g -a antigravity -a claude-code -a codex -a gemini-cli -a github-copilot -y
```

Replace `abhishekinvission` with the actual GitHub account or organization owning the public repository. Supported agents and flags depend on your installed Skills CLI version. For internal agents, use their supported Agent Skills mechanism or GitHub repository import.

## Usage

Ask your agent: "Use uiuxabhishek-design to audit this UI for design consistency, typography, responsive spacing, press feedback and interruptible motion. Read-only; report findings without editing."

## What's included

- `skills/uiuxabhishek-design/SKILL.md` — one discoverable skill entry point with unified guidance and conflict handling.
- `skills/uiuxabhishek-design/references/impeccable/` — source Markdown guidance copied from the locally installed Impeccable skill.
- `skills/uiuxabhishek-design/references/apple-design/` — source Markdown guidance copied from the locally installed Apple Design skill.
- `LICENSES/` and `NOTICE.md` — upstream license notices and attribution.
- `SOURCES.md` — a record of included files and their SHA-256 hashes (no local paths).

This is a **guidance-only integration**. Advanced Impeccable CLI commands, scripts, hooks and engine are deliberately not bundled. To get those, install the original Impeccable skill separately and follow its security guidance.

## Upstream authors and licenses

- [Impeccable — Paul Bakaus](https://github.com/pbakaus/impeccable) (Apache License 2.0).
- [Apple Design — Emil Kowalski](https://github.com/emilkowalski/skills) (MIT License).

The integration-specific files are MIT-licensed; redistributed upstream material retains its original license. Keep LICENSES and NOTICE when redistributing.

## Before publishing

Review all exported Markdown for private/company-specific content and unexpected instructions, ensure third-party licenses are included, and commit only what you intend to publish. The generator does not create a repo or push files automatically.
