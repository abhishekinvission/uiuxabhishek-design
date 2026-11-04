# Git conflicts, recovery, history and releases

**Use with** [git-workflow.md](git-workflow.md), whose detection, approval gates and work-preservation rules apply to everything here. Every operation in this file either changes history or recovers from a change, so state the risk and the way back before acting.

## 1. Conflict resolution

1. **Identify the operation** (merge, rebase, cherry-pick, revert, stash pop) from `git status` and the state files listed in git-workflow.md. List conflicted files with `git diff --name-only --diff-filter=U`.
2. **Understand both sides before editing:** `git log --merge --oneline`, `git diff`, and the three versions `git show :1:<file>` (base), `:2:` (ours) and `:3:` (theirs). For a rebase, "ours" is the branch being rebased onto, not the user's commits.
3. **Resolve with evidence:** intent from commit messages, the PR/MR or ticket, tests and the surrounding code. Combine both changes when they're independent. Never take one side wholesale (`-X ours/theirs`, `checkout --ours/--theirs`) unless the evidence shows the other side is obsolete.
4. **Ambiguous?** If two changes encode different behavior and nothing settles which is correct, stop and show both versions with the question. Don't guess. `git merge --abort`, `git rebase --abort` or `git cherry-pick --abort` returns to the starting point.
5. **Verify:** no conflict markers (`git diff --check`), the project builds and the relevant tests pass. Then `git add -- <files>` and continue (`git merge --continue` or `git rebase --continue`). Report each file and how it was resolved.

Lock files and generated files: regenerate with the project's own tool rather than hand-merging, when the repository supports it.

## 2. Undo and recover

| Situation | Preferred action | Notes |
| --- | --- | --- |
| Undo a pushed or shared commit | `git revert <sha>` (merges: `-m 1`) | New commit; safe for shared history |
| Undo the last local, unpushed commit, keeping changes | `git reset --soft HEAD~1` | Local only; confirm it isn't pushed (`git branch -r --contains HEAD`) |
| Unstage files | `git restore --staged -- <paths>` | Keeps working-tree changes |
| Discard working-tree changes | `git restore -- <paths>` | **Gate:** destroys uncommitted work; back up first (`git stash push -u` or a patch) |
| Lost commit or deleted branch | `git reflog`, then `git branch <name> <sha>` | Reflog is local and expires; unreachable objects: `git fsck --lost-found` |
| Bad rebase, merge or reset | `git reflog` or `ORIG_HEAD`, then `git branch rescue/<name> <sha>` | Create a rescue branch before any reset back |
| Dropped stash | `git fsck --unreachable \| grep commit`, then inspect and `git stash apply <sha>` | Best effort |
| Wrong branch committed to | `git switch -c <correct-branch>` | Clean the original branch only with approval |
| Secret committed | Revoke/rotate the secret first, then remove it | Removing it from history is a published-history rewrite (below); rotation is required regardless |

Recovery is local first: create a rescue branch at the found SHA and verify it before changing any existing branch.

## 3. Rewriting history (approval gate)

Only when explicitly authorized for the named branches/tags, and only after a check-in on who else uses them.

1. **Back up:** `git clone --mirror <remote> <backup-dir>` or push `backup/*` refs; record old SHAs for every affected branch and tag.
2. **Rewrite** the smallest range with the least invasive tool: interactive rebase for a few local commits, `git filter-repo` (if installed) for messages, paths or secrets across history. Don't run `filter-branch` without a reason.
3. **Verify:** each rewritten commit has the intended tree (`git diff <old> <new>` empty when only messages changed), tags point to the equivalent commits, and checks still pass.
4. **Publish:** `git push --force-with-lease=<branch>:<old-sha> <remote> <branch>`, and tags individually. Expect rejection if branch protection forbids it; don't disable protection without separate authorization.
5. **Coordinate:** collaborators must re-clone or reset onto the new history. Old SHAs may remain reachable through provider caches, forks and existing PRs, so a rewrite does **not** guarantee removal of exposed data.

## 4. Tags and releases

- **Versioning:** follow the repository's scheme (SemVer, CalVer, `v` prefix or not) and changelog conventions. Derive the version from the project's version source, not memory.
- **Tag:** annotated (`git tag -a v<x.y.z> -m "<summary>" <sha>`), signed if the repository requires it, on a commit that passed checks. Push one tag explicitly (`git push <remote> v<x.y.z>`), never `--tags` wholesale.
- **Published tags are immutable:** don't move or delete them; issue a new version instead. Moving or deleting one is an approval gate with the same backup and coordination as a history rewrite.
- **Release:** create as a draft when the provider supports it, attach build artifacts produced by the project's own build with checksums, then read the release back.
  - GitHub: `gh release create v<x.y.z> <assets> --draft --title "…" --notes-file <file> --verify-tag`
  - GitLab: `glab release create v<x.y.z> <assets> --notes-file <file>`
  - Azure Repos has no release object: tag the commit and use the project's Azure Pipelines release process if one exists.
  - Other providers: tag, then give manual steps.
- **Production:** publishing a non-draft release, package publishing or deployment needs explicit authorization for that version and environment, and any required approvals in the provider.

## 5. Repository synchronization

- **Mirrors:** `git push --mirror` overwrites every ref on the target: approval gate. Prefer pushing named branches.
- **Fork sync:** fetch `upstream`, fast-forward the base, push to the fork only when asked.
- **Submodules:** `git submodule status`; update only the submodules the task needs and commit the pointer change deliberately.
- **LFS:** check `git lfs ls-files` when `.gitattributes` uses LFS; missing LFS objects are a blocker, not a reason to commit pointer files as content.
