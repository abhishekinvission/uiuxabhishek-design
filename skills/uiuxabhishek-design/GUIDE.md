# UIUX Abhishek Design: what you can ask for

**Visual Craft. Fluid Motion. Exceptional Experiences.**

Describe the task in plain language. The skill picks the right guidance and loads only that. Naming a capability is optional.

## Capabilities

| Area | Ask for | Example |
| --- | --- | --- |
| New visual work | landing pages, redesigns, new visual identity, UX planning | "Plan the UX for a new onboarding flow." |
| Visual refinement | layout, typography, color, UX copy, polish, bolder, quieter, simpler, more delight | "The pricing headings feel cramped; fix the typography." |
| Product UI | dashboards, settings, data-dense app screens | "Make this settings screen easier to scan." |
| Accessibility and quality | accessibility audits, critiques, edge cases, error and empty states, responsive, UI performance | "Audit checkout for keyboard and contrast issues, read-only." |
| Native platforms | iOS (SwiftUI/UIKit) and Android (Compose) conventions | "Review this SwiftUI screen against iOS conventions." |
| Motion | purposeful animation, gestures, drag/swipe, springs, sheets, reduced motion | "Make the bottom sheet draggable with spring dismissal." |
| Design systems | tokens, component extraction, design-system documentation | "Extract our button styles into tokens." |
| Frontend engineering | pages and routing, API integration, admin CRUD, reports and exports, state, tests, code review, shared packages, microfrontends | "Add an admin users table with pagination and edit forms." |
| Azure DevOps delivery | Azure Boards work item → plan → implementation → draft PR | "Dry-run Azure Boards item 4521." |

## Control what it may do

| Say | It will |
| --- | --- |
| "audit", "review", "read-only", "dry run" | report findings only, with no edits |
| "plan", "spec" | write a plan, with no edits |
| "build", "fix", "add" | edit files in scope and run your project's own checks. It doesn't commit, push or open PRs |
| "commit", "push", "open a draft PR", with your authorization | publish the task branch and a **draft** PR, following your repository's rules |

It never merges, deploys, force-pushes or changes ticket state unless you ask separately.

## Azure DevOps delivery

- Works only for Azure DevOps or Azure Boards work items, not Jira, GitHub or Linear tickets.
- Needs an approved, signed-in Azure DevOps connector or the `az devops` CLI already available to your agent. No credentials are bundled.
- It reads the live ticket, checks for existing PRs, asks about blocking gaps, works on a safe branch, runs your project's real checks and reports with a structured template.
- A bare work-item ID or URL is a **dry run**. Say "implement" for local changes, or "deliver" plus explicit authorization for a draft PR.

## Good to know

- It follows your existing framework, design system and conventions, and never imposes a style or library.
- Upstream Impeccable tooling (live mode, detector hooks, `doctor`, image generation, `init`) isn't bundled. Install the original Impeccable project if you need it.
- Credits and licenses: [NOTICE.md](NOTICE.md).
