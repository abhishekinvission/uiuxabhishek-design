"""Sandbox checks for the commands in references/workflows/git-*.md.

Standard library plus the git CLI. Run from anywhere:  python3 tests/git_sandbox.py

Everything runs in a fresh temporary directory with a bare repository as the
mock remote and two clones as collaborators. Global and system Git config are
isolated, so no real repository, remote, credential or user setting is read
or changed. Each check confirms a behavior the guides rely on, including that
the safe options refuse to clobber work.
"""
import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Sandbox:
    def __init__(self, base):
        self.base = base
        cfg = os.path.join(base, "gitconfig")
        open(cfg, "w").close()
        self.env = {"PATH": os.environ.get("PATH", ""), "HOME": base, "GIT_CONFIG_GLOBAL": cfg,
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"}

    def git(self, cwd, *args, ok=True):
        r = subprocess.run(["git", *args], cwd=os.path.join(self.base, cwd), env=self.env,
                           capture_output=True, text=True)
        if ok and r.returncode:
            raise AssertionError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
        return r

    def out(self, cwd, *args):
        return self.git(cwd, *args).stdout.strip()

    def write(self, cwd, name, text):
        with open(os.path.join(self.base, cwd, name), "w") as f:
            f.write(text)

    def read(self, cwd, name):
        with open(os.path.join(self.base, cwd, name)) as f:
            return f.read()

    def commit(self, cwd, name, text, msg):
        self.write(cwd, name, text)
        self.git(cwd, "add", "--", name)
        self.git(cwd, "commit", "-q", "-m", msg)
        return self.out(cwd, "rev-parse", "HEAD")

    def clone(self, name):
        self.git(".", "clone", "-q", "remote.git", name)
        for k, v in (("user.name", name), ("user.email", f"{name}@example.invalid"),
                     ("pull.rebase", "false")):
            self.git(name, "config", k, v)  # repository-local identity only


def run_checks():
    results = []

    def check(name, cond):
        results.append((name, bool(cond)))

    with tempfile.TemporaryDirectory() as base:
        base = os.path.realpath(base)
        assert not base.startswith(os.path.realpath(ROOT)), "sandbox must be outside the repository"
        s = Sandbox(base)
        s.git(".", "init", "-q", "--bare", "-b", "main", "remote.git")
        s.clone("alice")
        s.commit("alice", "app.txt", "title=Home\n", "Initial commit")
        s.git("alice", "push", "-q", "-u", "origin", "main")
        s.clone("bob")

        # §1 detection
        check("detect: default branch via origin/HEAD",
              s.out("bob", "symbolic-ref", "refs/remotes/origin/HEAD") == "refs/remotes/origin/main")
        check("detect: porcelain status shows branch and upstream",
              s.out("bob", "status", "--porcelain=v1", "-b").startswith("## main...origin/main"))
        merge_head = s.out("bob", "rev-parse", "--git-path", "MERGE_HEAD")
        check("detect: no operation in progress", not os.path.exists(os.path.join(base, "bob", merge_head)))

        # §4 divergence and --ff-only pull keep local work
        s.commit("bob", "bob.txt", "b\n", "Bob change")
        s.git("bob", "push", "-q", "origin", "main")
        local = s.commit("alice", "alice.txt", "a\n", "Alice change")
        s.git("alice", "fetch", "-q", "--prune", "origin")
        check("divergence: behind/ahead counts",
              s.out("alice", "rev-list", "--left-right", "--count", "@{u}...HEAD").split() == ["1", "1"])
        check("pull --ff-only refuses a diverged branch", s.git("alice", "pull", "--ff-only", ok=False).returncode)
        check("pull --ff-only leaves local commit intact", s.out("alice", "rev-parse", "HEAD") == local)

        # §4 explicit staging
        s.write("alice", "keep.txt", "staged\n")
        s.write("alice", "other.txt", "not staged\n")
        s.git("alice", "add", "--", "keep.txt")
        check("stage explicit paths only", s.out("alice", "diff", "--cached", "--name-only") == "keep.txt")

        # §3 preserve work: named stash with untracked files, backup ref, worktree
        s.git("alice", "stash", "push", "-q", "-u", "-m", "preserve before sync")
        check("named stash keeps untracked work",
              "preserve before sync" in s.out("alice", "stash", "list")
              and not os.path.exists(os.path.join(base, "alice", "other.txt")))
        s.git("alice", "stash", "pop", "-q")
        check("stash pop restores work", s.read("alice", "other.txt") == "not staged\n")
        s.git("alice", "branch", "backup/main-20260101")
        check("backup ref records HEAD", s.out("alice", "rev-parse", "backup/main-20260101") == local)
        s.git("alice", "worktree", "add", "-q", "../alice-task", "-b", "task/1", "origin/main")
        check("worktree isolates a task branch from a dirty tree",
              s.out("alice-task", "status", "--porcelain") == ""
              and s.out("alice", "status", "--porcelain") != "")

        # git-recovery §1 conflicts: detect, inspect stages, abort restores
        s.git("alice", "stash", "push", "-q", "-u", "-m", "park")
        s.commit("bob", "app.txt", "title=Bob home\n", "Bob title")
        s.git("bob", "push", "-q", "origin", "main")
        s.commit("alice", "app.txt", "title=Alice home\n", "Alice title")
        before = s.out("alice", "rev-parse", "HEAD")
        s.git("alice", "fetch", "-q", "origin")
        check("merge conflict is reported", s.git("alice", "merge", "origin/main", ok=False).returncode)
        check("conflicted files listed",
              s.out("alice", "diff", "--name-only", "--diff-filter=U") == "app.txt")
        check("merge state file present",
              os.path.exists(os.path.join(base, "alice", s.out("alice", "rev-parse", "--git-path", "MERGE_HEAD"))))
        check("base/ours/theirs stages readable",
              [s.out("alice", "show", f":{n}:app.txt") for n in (1, 2, 3)]
              == ["title=Home", "title=Alice home", "title=Bob home"])
        check("diff --check flags conflict markers", s.git("alice", "diff", "--check", ok=False).returncode)
        s.git("alice", "merge", "--abort")
        check("merge --abort restores the starting point",
              s.out("alice", "rev-parse", "HEAD") == before and s.read("alice", "app.txt") == "title=Alice home\n")

        # git-recovery §3 force-with-lease refuses to clobber someone else's push
        s.git("alice", "switch", "-q", "-c", "feature/x")
        old = s.commit("alice", "x.txt", "1\n", "Feature x")
        s.git("alice", "push", "-q", "-u", "origin", "feature/x")
        s.git("bob", "fetch", "-q", "origin")
        s.git("bob", "switch", "-q", "feature/x")
        s.commit("bob", "x.txt", "2\n", "Bob on feature x")
        s.git("bob", "push", "-q", "origin", "feature/x")
        s.git("alice", "commit", "-q", "--amend", "-m", "Feature x (amended)")
        check("plain push of rewritten history is rejected",
              s.git("alice", "push", "origin", "feature/x", ok=False).returncode)
        check("--force-with-lease with stale expectation is rejected",
              s.git("alice", "push", f"--force-with-lease=feature/x:{old}", "origin", "feature/x",
                    ok=False).returncode)
        check("remote branch keeps the collaborator's commit",
              s.out("bob", "ls-remote", "origin", "feature/x").split()[0] == s.out("bob", "rev-parse", "HEAD"))

        # git-recovery §2 undo and recover
        s.git("alice", "switch", "-q", "main")
        s.git("alice", "reset", "-q", "--hard", "backup/main-20260101")  # sandbox only
        n = int(s.out("alice", "rev-list", "--count", "HEAD"))
        bad = s.commit("alice", "app.txt", "title=Broken\n", "Bad change")
        s.git("alice", "revert", "--no-edit", bad)
        check("revert adds a new commit and restores content",
              int(s.out("alice", "rev-list", "--count", "HEAD")) == n + 2
              and s.read("alice", "app.txt") == "title=Home\n")
        check("unpushed commit has no remote branch", s.out("alice", "branch", "-r", "--contains", "HEAD") == "")
        s.commit("alice", "soft.txt", "keep me\n", "Local only")
        s.git("alice", "reset", "-q", "--soft", "HEAD~1")
        check("reset --soft keeps changes staged", "soft.txt" in s.out("alice", "diff", "--cached", "--name-only"))
        s.git("alice", "commit", "-q", "-m", "Local only again")
        s.git("alice", "switch", "-q", "-c", "spike")
        lost = s.commit("alice", "spike.txt", "s\n", "Spike work")
        s.git("alice", "switch", "-q", "main")
        s.git("alice", "branch", "-q", "-D", "spike")  # sandbox only
        found = [line.split()[0] for line in s.out("alice", "reflog", "--format=%H %gs %s").splitlines()
                 if line.endswith("Spike work")]
        s.git("alice", "branch", "rescue/spike", found[0])
        check("reflog recovers a deleted branch", found and s.out("alice", "rev-parse", "rescue/spike") == lost)

        # git-recovery §4 tags: annotated, pushed individually, immutable without force
        s.git("alice", "tag", "-a", "v1.0.0", "-m", "Release 1.0.0", "origin/main")
        check("annotated tag", s.out("alice", "cat-file", "-t", "v1.0.0") == "tag")
        s.git("alice", "push", "-q", "origin", "v1.0.0")
        check("single tag pushed", "refs/tags/v1.0.0" in s.out("alice", "ls-remote", "--tags", "origin"))
        s.git("alice", "tag", "-f", "-a", "v1.0.0", "-m", "moved", "HEAD")
        check("moving a published tag is rejected without force",
              s.git("alice", "push", "origin", "v1.0.0", ok=False).returncode)
    return results


if __name__ == "__main__":
    res = run_checks()
    for name, ok in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    failed = [n for n, ok in res if not ok]
    print(f"\n{len(res) - len(failed)}/{len(res)} git sandbox checks passed")
    raise SystemExit(1 if failed else 0)
