"""Sandbox checks for tools/updater/devkit-update.mjs.

Standard library plus Node.js. Run from anywhere:  python3 tests/updater_sandbox.py

Every case runs the real updater against a mock GitHub API (a local HTTP
server on 127.0.0.1), a mock Skills CLI that only records its arguments and
writes into a throwaway HOME, and scheduler files written in test mode
(DEVKIT_NO_EXEC_SCHEDULER=1, so launchctl, systemctl, crontab and schtasks are
never run). Nothing touches the network, real installations or schedulers.
"""
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
