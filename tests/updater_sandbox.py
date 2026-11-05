"""Sandbox checks for tools/updater/devkit-update.mjs.

Standard library plus Node.js. Run from anywhere:  python3 tests/updater_sandbox.py

Every case runs the real updater against a mock GitHub API (a local HTTP
server on 127.0.0.1), a mock Skills CLI that only records its arguments and
writes into a throwaway HOME, and scheduler files written in test mode
(DEVKIT_NO_EXEC_SCHEDULER=1, so launchctl, systemctl, crontab and schtasks are
never run). Nothing touches the network, real installations or schedulers.
"""
import datetime
import http.server
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPDATER = os.path.join(ROOT, "tools", "updater", "devkit-update.mjs")
OWNER, REPO, SKILL = "abhishekinvission", "uiuxabhishek-devkit", "uiuxabhishek-devkit"
REPO_ID = 1442633889
TREE = "a" * 40
AGENTS = ["claude-code", "codex", "gemini-cli", "github-copilot", "antigravity"]

MOCK_CLI = r"""
import fs from "node:fs"; import path from "node:path";
const home = process.env.HOME, args = process.argv.slice(2);
fs.appendFileSync(path.join(home, "cli-calls.jsonl"), JSON.stringify(args) + "\n");
if (process.env.MOCK_EXIT) process.exit(Number(process.env.MOCK_EXIT));
const tag = args[1].split("#")[1], version = process.env.MOCK_VERSION || tag.slice(1);
const dir = path.join(home, ".agents", "skills", "uiuxabhishek-devkit");
fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(path.join(dir, "SKILL.md"), `---\nname: uiuxabhishek-devkit\nmetadata:\n  version: "${version}"\n---\n`);
const lockPath = path.join(home, ".agents", ".skill-lock.json");
const lock = JSON.parse(fs.readFileSync(lockPath, "utf8"));
lock.skills["uiuxabhishek-devkit"] = { ...lock.skills["uiuxabhishek-devkit"], ref: tag, skillFolderHash: process.env.MOCK_HASH };
fs.writeFileSync(lockPath, JSON.stringify(lock));
"""


class Mock:
    """Mutable mock of the GitHub endpoints the updater reads."""

    def __init__(self):
        self.reset("v2.1.0")

    def reset(self, tag, **kw):
        self.repo = {"id": REPO_ID, "full_name": f"{OWNER}/{REPO}"}
        self.tag = tag
        self.release = {"tag_name": tag, "draft": False, "prerelease": False,
                        "html_url": f"https://github.com/{OWNER}/{REPO}/releases/tag/{tag}", "assets": []}
        self.skill_version = tag.lstrip("v")
        self.checksum = "b" * 64
        self.digest = "sha256:" + "b" * 64
        self.down = False
        for k, v in kw.items():
            setattr(self, k, v)

    def routes(self, base):
        zip_name = f"{SKILL}-{self.tag}.zip"
        rel = dict(self.release, assets=[
            {"name": zip_name, "digest": self.digest, "browser_download_url": f"{base}/dl/{zip_name}"},
            {"name": zip_name + ".sha256", "browser_download_url": f"{base}/dl/{zip_name}.sha256"}])
        return {
            f"/api/repos/{OWNER}/{REPO}": self.repo,
            f"/api/repos/{OWNER}/{REPO}/releases/latest": rel,
            f"/api/repos/{OWNER}/{REPO}/contents/skills?ref={self.tag}": [{"name": SKILL, "type": "dir", "sha": TREE}],
            f"/raw/{OWNER}/{REPO}/{self.tag}/skills/{SKILL}/SKILL.md":
                f'---\nname: {SKILL}\nmetadata:\n  version: "{self.skill_version}"\n---\n',
            f"/dl/{zip_name}.sha256": f"{self.checksum}  {zip_name}\n",
        }


def serve(mock):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if mock.down:
                self.send_response(503)
                self.end_headers()
                return
            body = mock.routes(f"http://127.0.0.1:{self.server.server_port}").get(urllib.parse.unquote(self.path))
            self.send_response(200 if body is not None else 404)
            self.end_headers()
            if body is not None:
                self.wfile.write((body if isinstance(body, str) else json.dumps(body)).encode())

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class Home:
    def __init__(self, base, port, cli, version="2.0.0", platform="darwin"):
        self.path = tempfile.mkdtemp(dir=base)
        self.env = {"PATH": os.environ.get("PATH", ""), "HOME": self.path, "DEVKIT_USER_HOME": self.path,
                    "DEVKIT_API_BASE": f"http://127.0.0.1:{port}/api", "DEVKIT_RAW_BASE": f"http://127.0.0.1:{port}/raw",
                    "DEVKIT_SKILLS_CMD": json.dumps(["node", cli]), "DEVKIT_NO_EXEC_SCHEDULER": "1",
                    "DEVKIT_NOTIFY": "0", "DEVKIT_PLATFORM": platform, "DEVKIT_NPX": "/usr/bin/npx",
                    "MOCK_HASH": TREE}
        self.dir = os.path.join(self.path, ".uiuxabhishek-devkit")
        if version:
            self.install(SKILL, version)
            os.makedirs(os.path.join(self.path, ".claude", "skills"))
            os.symlink(os.path.join(self.path, ".agents", "skills", SKILL),
                       os.path.join(self.path, ".claude", "skills", SKILL))
            self.write(".agents/.skill-lock.json", json.dumps({"version": 3, "skills": {
                SKILL: {"source": f"{OWNER}/{REPO}", "ref": f"v{version}", "skillFolderHash": "0" * 40}}}))
        self.install("other-skill", "9.9.9")

    def write(self, rel, text):
        p = os.path.join(self.path, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)

    def read(self, rel):
        with open(os.path.join(self.path, rel)) as f:
            return f.read()

    def install(self, name, version):
        self.write(f".agents/skills/{name}/SKILL.md", f'---\nname: {name}\nmetadata:\n  version: "{version}"\n---\n')

    def version(self):
        return self.read(f".agents/skills/{SKILL}/SKILL.md").split('version: "')[1].split('"')[0]

    def calls(self):
        p = os.path.join(self.path, "cli-calls.jsonl")
        return [json.loads(line) for line in open(p)] if os.path.exists(p) else []

    def run(self, *args, updater=UPDATER, **extra):
        return subprocess.run(["node", updater, *args], env={**self.env, **extra},
                              capture_output=True, text=True, timeout=60)


def iso(hours_ago):
    t = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def node_path_checks(check, new, base, plist_rel):
    """Stable Node path: chosen, saved, reused, validated. Homebrew-style links in the sandbox."""
    real = os.path.realpath(shutil.which("node"))
    brew = os.path.join(base, "brew")

    def brew_install(version):  # bin/node -> ../Cellar/node/<version>/bin/node -> the real binary
        cellar = os.path.join(brew, "Cellar", "node", version, "bin")
        os.makedirs(cellar, exist_ok=True)
        if not os.path.lexists(os.path.join(cellar, "node")):
            os.symlink(real, os.path.join(cellar, "node"))
        stable = os.path.join(brew, "bin", "node")
        os.makedirs(os.path.dirname(stable), exist_ok=True)
        if os.path.lexists(stable):
            os.remove(stable)
        os.symlink(os.path.join("..", "Cellar", "node", version, "bin", "node"), stable)
        return stable

    stable = brew_install("26.0.0")
    on_path = {"PATH": os.path.dirname(stable) + os.pathsep + os.environ.get("PATH", "")}
    h = new()
    plist, cfg_path = os.path.join(h.path, plist_rel), os.path.join(h.dir, "config.json")
    cfg = lambda: json.load(open(cfg_path))
    text = lambda: open(plist).read()
    r = h.run("setup", **on_path)
    check("setup saves the stable Node link, not the versioned binary",
          r.returncode == 0 and cfg().get("node") == stable and f"<string>{stable}</string>" in text() and real not in text())

    brew_install("26.1.0")  # Homebrew upgrade: the link moves on, the old version is removed
    shutil.rmtree(os.path.join(brew, "Cellar", "node", "26.0.0"))
    st = h.run("status").stdout
    check("after a Homebrew Node upgrade the saved path still runs", f"Node: {stable}" in st and "WARNING" not in st)
    r = h.run("setup")  # no DEVKIT_NODE, and the brew directory is no longer on PATH
    check("re-setup reuses the saved Node path", r.returncode == 0 and cfg().get("node") == stable and stable in text())
    h.run("disable")
    r = h.run("setup")
    check("disable then setup restores the schedule with the saved Node path",
          r.returncode == 0 and stable in text() and cfg()["mode"] == "notify")
    h.run("disable")
    h.run("enable-auto-update", "--yes")
    check("re-enabling via enable-auto-update keeps the saved Node path", stable in text() and cfg()["mode"] == "auto")
    h.run("disable")
    h.run("setup")
    check("setup after disable returns to notify-only", cfg()["mode"] == "notify")

    os.remove(stable)  # Node uninstalled or the link removed
    st = h.run("status").stdout
    check("status warns when the saved Node path is missing", "missing or not runnable" in st)
    r = h.run("setup")
    check("re-setup replaces a missing Node path with a working one and says so",
          r.returncode == 0 and "no longer runs" in r.stdout and os.path.exists(cfg().get("node") or "") and (cfg().get("node") or "\0") in text())
    before = (open(cfg_path).read(), text())
    for label, bad in (("a missing", os.path.join(base, "nope", "node")), ("a non-Node", shutil.which("sh"))):
        r = h.run("setup", DEVKIT_NODE=bad)
        check(f"{label} DEVKIT_NODE is rejected without changing config or schedule",
              r.returncode == 1 and "not a runnable Node.js" in r.stderr and (open(cfg_path).read(), text()) == before)
    stable = brew_install("26.2.0")
    r = h.run("setup", DEVKIT_NODE=stable)
    check("an explicit DEVKIT_NODE is validated, saved and used", r.returncode == 0 and cfg().get("node") == stable and stable in text())


def overdue_checks(check, new, mock, plist_rel):
    """status separates a pending first check, a recent check and a missed one."""
    h = new()
    h.run("setup")
    cfg_path, state_path = os.path.join(h.dir, "config.json"), os.path.join(h.dir, "state.json")
    copied = os.path.join(h.dir, "devkit-update.mjs")

    def edit(p, **kw):
        data = json.load(open(p)) if os.path.exists(p) else {}
        data.update(kw)
        json.dump(data, open(p, "w"))

    status = lambda: h.run("status").stdout
    st = status()
    check("a fresh setup reports the first scheduled check as pending, not overdue",
          "first run pending" in st and "overdue" not in st)
    edit(cfg_path, scheduledAt=iso(50))
    check("no scheduled run 50 h after setup is reported overdue",
          "WARNING: scheduled check overdue: none has run since" in status())
    h.run("check")  # a manual check doesn't prove the scheduler works
    check("a manual check doesn't hide a missed scheduled check", "overdue" in status())
    h.run("check", "--scheduled", updater=copied)
    st = status()
    check("a scheduled run clears the warning", "Scheduled check: last ran" in st and "overdue" not in st)
    edit(state_path, lastScheduledAt=iso(47))
    check("a scheduled run 47 h ago is not overdue", "overdue" not in status())
    edit(state_path, lastScheduledAt=iso(49))
    check("a scheduled run 49 h ago is overdue", "WARNING: scheduled check overdue: the last one ran" in status())
    mock.reset("v2.1.0", down=True)
    h.run("check", "--scheduled", updater=copied)
    st = status()
    check("a failing scheduled check counts as a run and shows its error",
          "overdue" not in st and "Last error" in st and "HTTP 503" in st)
    mock.reset("v2.1.0")
    stamp = iso(1)
    edit(state_path, lastScheduledAt=stamp)
    r = h.run("update", "--yes")
    check("a manual update keeps the scheduled-run record",
          r.returncode == 0 and json.load(open(state_path)).get("lastScheduledAt") == stamp)
    h.run("disable")
    check("no overdue warning while the schedule is off", "Scheduled check" not in status() and "overdue" not in status())

    # configuration written by the 2.0.0 updater: no node or scheduledAt, no lastScheduledAt
    h = new()
    h.run("setup")
    cfg_path, state_path = os.path.join(h.dir, "config.json"), os.path.join(h.dir, "state.json")
    legacy = json.load(open(cfg_path))
    legacy.pop("node", None), legacy.pop("scheduledAt", None)
    json.dump(legacy, open(cfg_path, "w"))
    st = h.run("status").stdout
    check("2.0.0 config: a recent setup is pending and asks to save a Node path",
          "first run pending" in st and "Node: not recorded" in st)
    old = time.time() - 72 * 3600
    os.utime(cfg_path, (old, old))
    check("2.0.0 config: falls back to the config date for overdue detection", "overdue" in h.run("status").stdout)
    r = h.run("setup")
    cfg = json.load(open(cfg_path))
    check("re-setup upgrades a 2.0.0 config in place", r.returncode == 0 and cfg.get("node") and cfg.get("scheduledAt")
          and cfg["mode"] == "notify" and cfg["agents"] == legacy["agents"] and cfg["npx"] == legacy["npx"])


def run_checks():
    results = []

    def check(name, cond):
        results.append((name, bool(cond)))

    mock = Mock()
    srv = serve(mock)
    port = srv.server_port
    base = tempfile.mkdtemp()
    try:
        cli = os.path.join(base, "mock-skills.mjs")
        with open(cli, "w") as f:
            f.write(MOCK_CLI)
        new = lambda **kw: Home(base, port, cli, **kw)

        # check: notify only, never modifies
        h = new()
        r = h.run("check")
        check("check reports an available stable update", r.returncode == 0 and "Update available" in r.stdout)
        check("check never calls the Skills CLI or changes the skill", not h.calls() and h.version() == "2.0.0")
        check("check verifies the release checksum", "checksum matches" in r.stdout)
        st = json.loads(h.run("check", "--json").stdout)
        check("check --json compares installed and latest", st["installed"] == "2.0.0" and st["latest"] == "2.1.0"
              and st["updateAvailable"] and st["tracking"] == "v2.0.0")
        mock.reset("v2.0.0")
        check("check: up to date", "No update needed" in new().run("check").stdout)

        # identity, stability and integrity gates (each must refuse without modifying)
        gates = {
            "prerelease rejected": dict(release={"tag_name": "v2.1.0", "draft": False, "prerelease": True,
                                                  "html_url": f"https://github.com/{OWNER}/{REPO}/releases/tag/v2.1.0"}),
            "non-semver tag rejected": dict(release={"tag_name": "v2.1.0-beta.1", "draft": False, "prerelease": False,
                                                      "html_url": f"https://github.com/{OWNER}/{REPO}/releases/tag/v2.1.0-beta.1"}),
            "repository ID mismatch rejected": dict(repo={"id": 1, "full_name": f"{OWNER}/{REPO}"}),
            "release from another repository rejected": dict(release={"tag_name": "v2.1.0", "draft": False, "prerelease": False,
                                                                       "html_url": "https://github.com/evil/uiuxabhishek-devkit/releases/tag/v2.1.0"}),
            "tag/version mismatch rejected": dict(skill_version="2.0.5"),
            "checksum mismatch rejected": dict(checksum="c" * 64),
        }
        for name, kw in gates.items():
            mock.reset("v2.1.0", **kw)
            h = new()
            r = h.run("update", "--yes")
            check(f"gate: {name}", r.returncode == 1 and not h.calls() and h.version() == "2.0.0")
        mock.reset("v2.1.0", down=True)
        h = new()
        r = h.run("check")
        check("network/API failure is a clean, non-destructive error",
              r.returncode == 1 and "HTTP 503" in r.stderr and h.version() == "2.0.0")
        mock.reset("v2.1.0")

        # manual update: confirmation, exact command, verification, backup, isolation
        h = new()
        check("update requires --yes", h.run("update").returncode == 1 and not h.calls())
        other_before = h.read(".agents/skills/other-skill/SKILL.md")
        r = h.run("update", "--yes")
        calls = h.calls()
        expected = ["add", f"{OWNER}/{REPO}#v2.1.0", "--skill", SKILL, "-g"] + [x for a in AGENTS for x in ("-a", a)] + ["-y"]
        check("update succeeds and reports the new version", r.returncode == 0 and h.version() == "2.1.0")
        check("update pins the verified tag and targets only this skill", calls == [expected])
        check("update leaves other skills untouched", h.read(".agents/skills/other-skill/SKILL.md") == other_before)
        backups = os.listdir(os.path.join(h.dir, "backups"))
        check("update backs up the previous version", len(backups) == 1 and backups[0].startswith("2.0.0-"))
        check("second update is a no-op", "already at 2.1.0" in h.run("update", "--yes").stdout and len(h.calls()) == 1)

        h = new()
        r = h.run("update", "--yes", MOCK_HASH="f" * 40)
        check("post-update hash mismatch is reported with recovery steps",
              r.returncode == 1 and "verification failed" in r.stderr and "backed up at" in r.stderr)
        h = new()
        r = h.run("update", "--yes", MOCK_EXIT="7")
        check("Skills CLI failure keeps the installed version and explains recovery",
              r.returncode == 1 and h.version() == "2.0.0" and "npx skills add" in r.stderr)
        h = new(version=None)
        check("update never installs from scratch", h.run("update", "--yes").returncode == 1 and not h.calls())

        # concurrency
        h = new()
        os.makedirs(h.dir)
        with open(os.path.join(h.dir, "update.lock"), "w") as f:
            json.dump({"pid": os.getpid(), "at": int(time.time() * 1000)}, f)
        r = h.run("update", "--yes")
        check("a live lock blocks a concurrent run", r.returncode == 1 and "in progress" in r.stderr and not h.calls())
        with open(os.path.join(h.dir, "update.lock"), "w") as f:
            json.dump({"pid": 999999, "at": 0}, f)
        check("a stale lock is recovered", h.run("update", "--yes").returncode == 0
              and not os.path.exists(os.path.join(h.dir, "update.lock")))

        # old skill detection never removes it
        h = new()
        h.install("uiuxabhishek-design", "1.1.0")
        r = h.run("check")
        check("old skill is reported, not removed", "npx skills remove uiuxabhishek-design" in r.stdout
              and os.path.exists(os.path.join(h.path, ".agents/skills/uiuxabhishek-design/SKILL.md")))

        # setup, scheduling per platform, modes, disable, uninstall
        sched = {"darwin": "Library/LaunchAgents/com.uiuxabhishek.devkit-update.plist",
                 "linux-systemd": ".config/systemd/user/uiuxabhishek-devkit-update.service",
                 "linux-cron": ".uiuxabhishek-devkit/crontab.test.json",
                 "win32": ".uiuxabhishek-devkit/schtasks.test.json"}
        for plat, rel in sched.items():
            platform, _, linux = plat.partition("-")
            h = new(platform=platform)
            extra = {"DEVKIT_LINUX_SCHEDULER": linux} if linux else {}
            r = h.run("setup", **extra)
            copied = os.path.join(h.dir, "devkit-update.mjs")
            artifact = os.path.join(h.path, rel)
            text = open(artifact).read() if os.path.exists(artifact) else ""
            ok = r.returncode == 0 and os.path.exists(copied) and "check" in text and "--scheduled" in text
            if plat == "darwin":
                ok = ok and "<key>StartCalendarInterval</key>" in text and copied in text
            if plat == "linux-cron":
                ok = ok and "# uiuxabhishek-devkit-update" in text
            if plat == "win32":
                ok = ok and json.loads(text)["args"][:3] == ["/Create", "/TN", "UIUXAbhishekDevKitUpdate"] and "DAILY" in text
            check(f"setup schedules a notify-only daily check ({plat})", ok and json.load(open(os.path.join(h.dir, "config.json")))["mode"] == "notify")
            r = h.run("check", "--scheduled", updater=copied, **extra)
            check(f"scheduled check in notify mode doesn't update ({plat})", r.returncode == 0 and not h.calls()
                  and "Update available" in h.read(".uiuxabhishek-devkit/update.log"))
            check(f"enable-auto-update requires --yes ({plat})", h.run("enable-auto-update", updater=copied, **extra).returncode == 1)
            h.run("enable-auto-update", "--yes", updater=copied, **extra)
            r = h.run("check", "--scheduled", updater=copied, **extra)
            check(f"scheduled check in auto mode installs the verified release ({plat})",
                  r.returncode == 0 and h.version() == "2.1.0" and len(h.calls()) == 1)
            status = h.run("status", updater=copied, **extra).stdout
            check(f"status shows mode, schedule and versions ({plat})", "Mode: auto" in status and "daily" in status and "2.1.0" in status)
            h.run("disable", updater=copied, **extra)
            gone = not os.path.exists(artifact) or "# uiuxabhishek-devkit-update" not in open(artifact).read()
            check(f"disable removes the schedule ({plat})", gone and "Mode: off" in h.run("status", updater=copied, **extra).stdout)
            r = h.run("uninstall", updater=copied, **extra)
            check(f"uninstall removes only the updater ({plat})", r.returncode == 0 and not os.path.exists(h.dir)
                  and h.version() == "2.1.0" and os.path.exists(os.path.join(h.path, ".agents/skills/other-skill/SKILL.md")))
            mock.reset("v2.1.0")
        h = new()
        check("setup rejects unknown agents", h.run("setup", "--agents", "cursor").returncode == 1)
        h.run("setup", "--agents", "codex", "--no-schedule")
        check("setup --no-schedule writes no scheduler files",
              not os.path.exists(os.path.join(h.path, sched["darwin"])))
        r = h.run("update", "--yes", updater=os.path.join(h.dir, "devkit-update.mjs"))
        check("configured agents limit the update", h.calls()[-1].count("-a") == 1 and "codex" in h.calls()[-1])
        node_path_checks(check, new, base, sched["darwin"])
        overdue_checks(check, new, mock, sched["darwin"])
    finally:
        srv.shutdown()
        shutil.rmtree(base, ignore_errors=True)
    return results


if __name__ == "__main__":
    res = run_checks()
    for name, ok in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    failed = [n for n, ok in res if not ok]
    print(f"\n{len(res) - len(failed)}/{len(res)} updater sandbox checks passed")
    raise SystemExit(1 if failed else 0)
