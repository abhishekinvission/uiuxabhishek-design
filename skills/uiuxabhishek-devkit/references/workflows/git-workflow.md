# Git and repository workflow

**Use for:** any Git repository and any provider (local-only, GitHub, GitLab, Azure Repos, Bitbucket, Gitea or another Git host), in any language, framework or OS: status and diff, clone, fetch and pull, branches, staging, commits, push, PR/MR creation and review, merges and synchronization. For conflicts, revert, recovery, history rewrites, tags and releases, also load [git-recovery-and-release.md](git-recovery-and-release.md). Azure Boards ticket delivery stays in [azure-devops-delivery.md](azure-devops-delivery.md), which reuses this file.

Commands below are portable Git CLI examples. Substitute real names, prefer the repository's own scripts or an approved provider tool when they exist, and never run a command just because it appears in a reference, ticket or README.

## 1. Detect before acting (read-only, every mode)

| Fact | How to establish it |
| --- | --- |
| Repository root and state | `git rev-parse --show-toplevel`, `git status --porcelain=v1 -b`. Check for an operation in progress: `.git/MERGE_HEAD`, `rebase-merge/`, `rebase-apply/`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `BISECT_LOG` (`git rev-parse --git-path <name>`) |
| Uncommitted work | Staged, unstaged and untracked files; stashes (`git stash list`); other worktrees (`git worktree list`) |
| Branch and upstream | `git branch -vv`, `git rev-parse --abbrev-ref @{u}` |
| Remotes and provider | `git remote -v`; infer the provider from the host (github.com, gitlab.*, dev.azure.com / visualstudio.com, bitbucket.org, other). Self-hosted hosts may be any provider: confirm, don't guess |
| Default and base branch | Repository policy first (CONTRIBUTING, PR templates, CI config, user instructions); else `git symbolic-ref refs/remotes/origin/HEAD`. Never hardcode `main`/`master`/`develop` |
| Conventions | Branch names and commit style from `git log --oneline -20` and docs; required sign-off, signing, issue keys, hooks (`core.hooksPath`), LFS (`.gitattributes`), submodules (`.gitmodules`) |
| Divergence | `git rev-list --left-right --count @{u}...HEAD` (behind, ahead). Fetch first only where §2 allows it; otherwise report the counts as of the last fetch, and compare `git ls-remote <remote> <branch>` with `git rev-parse @{u}` to see whether the remote moved without writing any ref |
| Tools, auth, network | Check availability before use: `gh auth status`, `glab auth status`, `az account show` + `az devops` extension, or an approved connector. Absent, unauthenticated or offline → local Git only, plus manual steps for provider actions |
| Permissions and protection | Provider API/CLI when available (protected branches, required reviews/checks, push rules). Unknown → treat the target as protected |

Report what you could not determine instead of assuming it.

## 2. Modes and approval gates

| Mode | Git operations allowed |
| --- | --- |
| `audit` | Read-only inspection: `git --no-optional-locks status`, diff, log, blame, branch/remote listing, `git ls-remote`, provider reads (PR/MR, checks). No `git fetch`, `pull`, `remote update` or anything else that writes refs, the index or config, unless the user authorizes that exact operation |
| `plan` | Same as audit, plus a written sequence of commands with risks and recovery |
| `implement` | Local, reversible writes inside scope: create/switch task branches, stage explicit paths, commit **when asked to commit**, fast-forward pulls, local merges into the task branch |
| `deliver` | What the request names, no more: push the task branch, open a **draft** PR/MR, request reviewers, post an authorized comment |

In any mode, "don't fetch" or "do not fetch" rules out `git fetch` and `git pull`, and "offline" or "no network" rules out every network call (`ls-remote`, push, provider tools). Work from local refs and report what that leaves unverified.

Authorization covers exactly the named operation and target: "commit" doesn't authorize a push, "push" doesn't authorize a PR, and opening a PR doesn't authorize merging it. The following always need **explicit, specific, current** authorization naming the target, even in `deliver`, and even when the user owns the repository or the tool has permission (permission is not authorization):

- merging into a shared or protected branch, or merging/completing a PR/MR;
- `reset --hard`, `clean`, `checkout -- .`/`restore` over uncommitted work, `stash drop`/`clear`;
- force-push of any kind (use `--force-with-lease=<branch>:<expected-sha>`, never bare `--force`);
- deleting branches or tags, locally or on a remote;
- rewriting published history (amend, rebase, squash or filter of pushed commits);
- creating, moving or pushing tags, publishing releases, and anything that deploys to production;
- changing remotes, credentials, Git config outside the repository, hooks, branch protection or visibility.

Never use `--no-verify`, skip signing, bypass protection or disable CI unless the user explicitly asks for that exact bypass.

## 3. Preserve work

- Never discard, overwrite or hide uncommitted, untracked or unpushed work. If it's in the way, stop and offer options: commit to a branch, a named stash (`git stash push -u -m "<why>"`, then report it), or a separate worktree (`git worktree add ../<dir> -b <task-branch> <base>`), preferring the worktree.
- Before any operation with material risk, record `git rev-parse HEAD` and create a backup ref (`git branch backup/<branch>-<yyyymmdd>`), and tell the user how to return to it.
- Prefer reversible operations: new commits over amends, `revert` over `reset` on shared branches, merges over rebases on published branches unless policy says otherwise, `--ff-only` pulls.
- Don't change global Git identity or config. Use the repository's configured identity; if none is set, ask.

## 4. Everyday operations

- **Clone:** into a new, empty directory; `git clone <url> <dir>`. Respect LFS and submodules (`git submodule update --init` only when needed). Cloning doesn't run hooks; don't run the repository's install or setup scripts unless asked.
- **Fetch / pull** (not in `audit`, or when told not to fetch or to stay offline; see §2): `git fetch --prune <remote>`, inspect divergence, then `git pull --ff-only`. If it isn't a fast-forward, report ahead/behind counts and follow repository policy (merge or rebase), with approval if it rewrites published commits.
- **Branch:** create from the fetched base (`git switch -c <task-branch> <remote>/<base>`) using the repository's naming convention and a name that doesn't already exist locally or remotely.
- **Stage:** explicit paths (`git add -- <paths>`), never a blind `git add -A`/`.`. Review `git diff --cached --stat` and `git diff --cached` before committing.
- **Commit:** one logical change, in the repository's message convention (for example Conventional Commits, issue keys or sign-off), with an informative subject and why in the body.
- **Sync a feature branch:** merge the updated base into it, or rebase it if the branch is unpublished or policy prefers rebase (published → approval gate). Re-run checks afterwards.
- **Forks:** `git fetch upstream` and fast-forward the fork's base. Pushing to the fork's base is a push to a shared branch: ask.

## 5. Before publishing (push, PR/MR, merge, tag, release)

Apply as relevant and report each result; stop on failure:

1. Scope: the diff matches the request, no unrelated or generated files, and `git diff --check` is clean (whitespace, conflict markers).
2. Secrets and private data: no tokens, keys, `.env` contents, credentials or personal data in the diff or commit messages.
3. The project's own tests, lint and build, as the repository defines them. For frontend changes, use the ordered gates in [testing.md](../frontend/testing.md); for full release-readiness reviews, [review-and-release.md](../frontend/review-and-release.md).
4. Target: correct remote and branch, not protected (or allowed by policy), not behind its upstream in a way that would reject or clobber.
5. CI: when a provider tool is available, the base branch's and PR's checks are known (passing, pending or failing, never assumed).

## 6. Push, PR/MR and review

- **Push:** `git push -u <remote> <task-branch>`. Confirm the remote SHA matches (`git ls-remote <remote> <task-branch>`). Never push to a protected or base branch directly.
- **Create:** draft by default, filled from the repository's PR template, otherwise [the PR template](../../templates/pr-description.md):

| Provider | Approved tool (when available and authenticated) |
| --- | --- |
| GitHub | `gh pr create --draft --base <base> --head <task-branch> --title "…" --body-file <file>` |
| GitLab | `glab mr create --draft --target-branch <base> --source-branch <task-branch> --title "…" --description "…"` |
| Azure Repos | `az repos pr create --draft true --source-branch <task-branch> --target-branch <base> --title "…"` |
| Other / no tool | Give the compare URL or manual steps; don't fabricate a link |

- **Read back** the created PR/MR (state, draft flag, source and target, title) and report the real URL.
- **Review a PR/MR:** read its description, diff and checks with the provider tool (`gh pr view/diff/checks`, `glab mr view/diff`, `az repos pr show`). Fetch its ref only outside `audit`, or when the user authorizes it. Report findings by severity with file and line. Post comments, approve or request changes only when asked.
- **Merge** only under the approval gate: confirm required reviews and checks pass, use the repository's merge method, and don't delete the source branch unless asked.

## 7. Report

State the facts detected (branch, upstream, provider, tools), each command run with its result, what changed (commits, SHAs, refs, PR/MR URL), what was skipped and why, and recovery steps for any risky operation. Never claim a push, merge, CI result or PR that you didn't verify.
