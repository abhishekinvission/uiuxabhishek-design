#!/usr/bin/env node
// UIUX Abhishek DevKit updater: optional, opt-in, stable releases only.
//
//   node devkit-update.mjs <command> [options]
//
//   setup [--agents a,b] [--no-schedule]  copy the updater to ~/.uiuxabhishek-devkit and
//                                         schedule a daily check that only notifies
//   check [--json]                        compare the installed version with the latest
//                                         stable GitHub release; never changes anything
//   update --yes                          update uiuxabhishek-devkit now (manual)
//   enable-auto-update --yes              let the scheduled check install stable updates
//   status                                show settings, schedule, versions and last result
//   disable                               remove the schedule and stop automatic updates
//   uninstall                             remove the schedule and the updater's own files
//
// Requirements: Node.js 22.20+ (the Skills CLI needs it anyway). No credentials, no
// background service, no downloaded scripts: it calls the public GitHub API, then the
// official Skills CLI pinned to a verified release tag. Only uiuxabhishek-devkit is
// touched; agent settings, other skills and projects are never modified.

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const OWNER = "abhishekinvission";
const REPO = "uiuxabhishek-devkit";
const REPO_ID = 1442633889; // GitHub's numeric ID survives renames; a look-alike repo can't match it
const SKILL_ID = "uiuxabhishek-devkit";
const OLD_SKILL_ID = "uiuxabhishek-design";
const SKILLS_CLI = "skills@1.7.6"; // the CLI version these docs were verified with
const ALL_AGENTS = ["claude-code", "codex", "gemini-cli", "github-copilot", "antigravity"];
const LABEL = "com.uiuxabhishek.devkit-update";
const TASK = "UIUXAbhishekDevKitUpdate";
const MARKER = "# uiuxabhishek-devkit-update";
const LOCK_STALE_MS = 2 * 60 * 60 * 1000;
const OVERDUE_MS = 48 * 60 * 60 * 1000; // daily schedule plus a day of grace

const env = process.env;
const HOME = env.DEVKIT_USER_HOME || os.homedir();
const DIR = env.DEVKIT_HOME || path.join(HOME, ".uiuxabhishek-devkit");
const API = env.DEVKIT_API_BASE || "https://api.github.com";
const RAW = env.DEVKIT_RAW_BASE || "https://raw.githubusercontent.com";
const PLATFORM = env.DEVKIT_PLATFORM || process.platform;
const DRY_SCHEDULER = env.DEVKIT_NO_EXEC_SCHEDULER === "1"; // tests: write files, run nothing
const SELF = fileURLToPath(import.meta.url);
const files = {
  config: path.join(DIR, "config.json"),
  state: path.join(DIR, "state.json"),
  log: path.join(DIR, "update.log"),
  lock: path.join(DIR, "update.lock"),
  updater: path.join(DIR, "devkit-update.mjs"),
  backups: path.join(DIR, "backups"),
};
const skillDirs = (id) => [path.join(HOME, ".agents", "skills", id), path.join(HOME, ".claude", "skills", id)];

class UserError extends Error {}

// ------------------------------------------------------------------ helpers
const readJson = (p, fallback) => {
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch { return fallback; }
};
const writeJson = (p, data) => {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p + ".tmp", JSON.stringify(data, null, 2) + "\n");
  fs.renameSync(p + ".tmp", p);
};
const log = (msg) => {
  fs.mkdirSync(DIR, { recursive: true });
  fs.appendFileSync(files.log, `${new Date().toISOString()} ${msg}\n`);
};
const parseVersion = (v) => {
  const m = /^v?(\d+)\.(\d+)\.(\d+)$/.exec(String(v || "").trim());
  return m ? m.slice(1).map(Number) : null;
};
const compare = (a, b) => {
  for (let i = 0; i < 3; i++) if (a[i] !== b[i]) return a[i] < b[i] ? -1 : 1;
  return 0;
};
const frontmatter = (text) => {
  const m = /^---\n([\s\S]*?)\n---/.exec(text);
  const body = m ? m[1] : "";
  return {
    name: (/^name:\s*(.+)$/m.exec(body) || [])[1]?.trim(),
    version: (/^\s+version:\s*"?([^"\s]+)"?$/m.exec(body) || [])[1],
  };
};

async function fetchOk(url) {
  const headers = { Accept: "application/vnd.github+json", "User-Agent": `${REPO}-updater` };
  let res;
  try {
    res = await fetch(url, { headers, redirect: "follow", signal: AbortSignal.timeout(20000) });
  } catch (e) {
    throw new UserError(`network error reaching ${new URL(url).host}: ${e.cause?.code || e.message}`);
  }
  if (!res.ok) throw new UserError(`${url} returned HTTP ${res.status}`);
  return res;
}
const getJson = async (url) => (await fetchOk(url)).json();
const getText = async (url) => (await fetchOk(url)).text();

// ------------------------------------------------------------- local state
function installed() {
  for (const dir of skillDirs(SKILL_ID)) {
    try {
      const fm = frontmatter(fs.readFileSync(path.join(dir, "SKILL.md"), "utf8"));
      if (fm.name === SKILL_ID) return { dir: fs.realpathSync(dir), version: fm.version };
    } catch {}
  }
  return null;
}
const lockEntry = () => readJson(path.join(HOME, ".agents", ".skill-lock.json"), {}).skills?.[SKILL_ID];
const oldSkillPresent = () => skillDirs(OLD_SKILL_ID).some((d) => fs.existsSync(d));
function detectAgents() {
  const [universal, claude] = skillDirs(SKILL_ID).map((d) => fs.existsSync(d));
  const agents = [];
  if (claude) agents.push("claude-code");
  if (universal) agents.push(...ALL_AGENTS.filter((a) => a !== "claude-code"));
  return agents;
}

// ------------------------------------------------- release, identity, integrity
async function latestRelease() {
  const repo = await getJson(`${API}/repos/${OWNER}/${REPO}`);
  if (repo.id !== REPO_ID || String(repo.full_name).toLowerCase() !== `${OWNER}/${REPO}`.toLowerCase()) {
    throw new UserError(`repository identity check failed (got ${repo.full_name} #${repo.id}); not updating`);
  }
  const rel = await getJson(`${API}/repos/${OWNER}/${REPO}/releases/latest`);
  const version = parseVersion(rel.tag_name);
  if (rel.draft || rel.prerelease || !version || !/^v\d+\.\d+\.\d+$/.test(rel.tag_name)) {
    throw new UserError(`latest release ${rel.tag_name} is not a stable vX.Y.Z release; not updating`);
  }
  if (!String(rel.html_url).startsWith(`https://github.com/${OWNER}/${REPO}/releases/tag/`)) {
    throw new UserError(`release URL ${rel.html_url} is not from ${OWNER}/${REPO}; not updating`);
  }
  const skill = frontmatter(await getText(`${RAW}/${OWNER}/${REPO}/${rel.tag_name}/skills/${SKILL_ID}/SKILL.md`));
  if (skill.name !== SKILL_ID || skill.version !== version.join(".")) {
    throw new UserError(`${rel.tag_name} contains ${skill.name}@${skill.version}, not ${SKILL_ID}@${version.join(".")}`);
  }
  const zipName = `${SKILL_ID}-${rel.tag_name}.zip`;
  const zip = (rel.assets || []).find((a) => a.name === zipName);
  const sum = (rel.assets || []).find((a) => a.name === `${zipName}.sha256`);
  let integrity = "no release checksum published";
  if (zip && sum) {
    const published = String(await getText(sum.browser_download_url)).trim().split(/\s+/)[0];
    if (zip.digest && zip.digest !== `sha256:${published}`) {
      throw new UserError(`${zipName} checksum mismatch (GitHub ${zip.digest}, published ${published}); not updating`);
    }
    integrity = zip.digest ? "release ZIP checksum matches GitHub's digest" : "release checksum published (no GitHub digest)";
  }
  const tree = await getJson(`${API}/repos/${OWNER}/${REPO}/contents/skills?ref=${encodeURIComponent(rel.tag_name)}`);
  const folder = Array.isArray(tree) ? tree.find((e) => e.name === SKILL_ID && e.type === "dir") : null;
  if (!folder) throw new UserError(`${rel.tag_name} has no skills/${SKILL_ID} folder; not updating`);
  return { tag: rel.tag_name, version: version.join("."), url: rel.html_url, treeSha: folder.sha, integrity };
}

async function checkStatus() {
  const local = installed();
  const latest = await latestRelease();
  const cmp = local && parseVersion(local.version) ? compare(parseVersion(local.version), parseVersion(latest.version)) : null;
  return {
    installed: local?.version ?? null,
    installedPath: local?.dir ?? null,
    tracking: lockEntry()?.ref ?? (local ? "default branch" : null),
    latest: latest.version,
    tag: latest.tag,
    releaseUrl: latest.url,
    integrity: latest.integrity,
    treeSha: latest.treeSha,
    updateAvailable: cmp !== null && cmp < 0,
    oldSkillInstalled: oldSkillPresent(),
    checkedAt: new Date().toISOString(),
  };
}

// ------------------------------------------------------------------ locking
function withLock(fn) {
  fs.mkdirSync(DIR, { recursive: true });
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const fd = fs.openSync(files.lock, "wx");
      fs.writeSync(fd, JSON.stringify({ pid: process.pid, at: Date.now() }));
      fs.closeSync(fd);
      break;
    } catch (e) {
      if (e.code !== "EEXIST") throw e;
      const held = readJson(files.lock, {});
      let alive = false;
      try { process.kill(held.pid, 0); alive = true; } catch {}
      if (alive && Date.now() - (held.at || 0) < LOCK_STALE_MS) {
        throw new UserError(`another updater run is in progress (pid ${held.pid}); try again later`);
      }
      fs.rmSync(files.lock, { force: true }); // stale lock from a crashed run
      if (attempt) throw new UserError("could not acquire the updater lock");
    }
  }
  const release = () => fs.rmSync(files.lock, { force: true });
  return Promise.resolve().then(fn).finally(release);
}

// ------------------------------------------------------------------- update
function skillsCommand(cfg) {
  if (env.DEVKIT_SKILLS_CMD) return JSON.parse(env.DEVKIT_SKILLS_CMD);
  return [cfg.npx || (PLATFORM === "win32" ? "npx.cmd" : "npx"), "-y", SKILLS_CLI];
}

async function performUpdate(status, cfg) {
  const local = installed();
  if (!local) throw new UserError(`${SKILL_ID} isn't installed globally; install it first (see INSTALL.md)`);
  if (!status.updateAvailable) return { updated: false, message: `already at ${local.version}` };
  const agents = cfg.agents?.length ? cfg.agents : detectAgents();
  const backup = path.join(files.backups, `${local.version}-${Date.now()}`);
  fs.mkdirSync(files.backups, { recursive: true });
  fs.cpSync(local.dir, backup, { recursive: true, dereference: true });
  for (const old of fs.readdirSync(files.backups).sort().slice(0, -3)) {
    fs.rmSync(path.join(files.backups, old), { recursive: true, force: true });
  }
  const [cmd, ...pre] = skillsCommand(cfg);
  const args = [...pre, "add", `${OWNER}/${REPO}#${status.tag}`, "--skill", SKILL_ID, "-g", ...agents.flatMap((a) => ["-a", a]), "-y"];
  log(`updating ${local.version} -> ${status.latest}: ${cmd} ${args.join(" ")}`);
  const res = spawnSync(cmd, args, {
    encoding: "utf8",
    shell: PLATFORM === "win32" && /\.cmd$/i.test(cmd),
    env: { ...env, PATH: [path.dirname(process.execPath), env.PATH].join(path.delimiter), DISABLE_TELEMETRY: "1" },
    timeout: 10 * 60 * 1000,
  });
  const recovery = `Your previous version is backed up at ${backup}. To return to it, run: ` +
    `npx skills add ${OWNER}/${REPO}#v${local.version} --skill ${SKILL_ID} -g ${agents.map((a) => `-a ${a}`).join(" ")} -y`;
  if (res.status !== 0) {
    throw new UserError(`Skills CLI failed (${res.error?.message || `exit ${res.status}`}): ${(res.stderr || "").slice(-400)}\n${recovery}`);
  }
  const after = installed();
  const entry = lockEntry();
  if (after?.version !== status.latest || entry?.ref !== status.tag ||
      (entry?.skillFolderHash && entry.skillFolderHash !== status.treeSha)) {
    throw new UserError(`post-update verification failed (installed ${after?.version}, ref ${entry?.ref}, ` +
      `hash ${entry?.skillFolderHash} vs ${status.treeSha})\n${recovery}`);
  }
  log(`updated to ${status.latest}; backup ${backup}`);
  return { updated: true, message: `updated ${local.version} -> ${status.latest} for ${agents.join(", ")}`, backup };
}

// --------------------------------------------------------------- scheduling
function which(bin) {
  const r = spawnSync(PLATFORM === "win32" ? "where" : "which", [bin], { encoding: "utf8" });
  return r.status === 0 ? r.stdout.split(/\r?\n/)[0].trim() : null;
}
const run = (cmd, args, input) => DRY_SCHEDULER ? { status: 0, stdout: "" } :
  spawnSync(cmd, args, { encoding: "utf8", input });
const xml = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const realpath = (p) => { try { return fs.realpathSync(p); } catch { return null; } };

// The scheduler runs Node by absolute path. A version-specific path (Homebrew's
// Cellar/node/<version>/bin/node) disappears on upgrade, so prefer the stable
// link on PATH that resolves to the running binary, and keep it in config.json.
function runnableNode(p) {
  if (!p || !path.isAbsolute(p)) return false;
  try { fs.accessSync(p, fs.constants.X_OK); } catch { return false; }
  const r = spawnSync(p, ["--version"], { encoding: "utf8", timeout: 15000 });
  return r.status === 0 && /^v\d+\./.test(r.stdout);
}
function chooseNode(prev) {
  if (env.DEVKIT_NODE) {
    if (!runnableNode(env.DEVKIT_NODE)) {
      throw new UserError(`DEVKIT_NODE=${env.DEVKIT_NODE} is not a runnable Node.js executable; nothing changed`);
    }
    return { node: env.DEVKIT_NODE };
  }
  if (prev && runnableNode(prev)) return { node: prev };
  const onPath = which(PLATFORM === "win32" ? "node.exe" : "node");
  const node = onPath && realpath(onPath) === realpath(process.execPath) ? onPath : process.execPath;
  return { node, note: prev ? `the saved Node path ${prev} no longer runs; now using ${node}` : null };
}
const scheduledNode = () => config()?.node || env.DEVKIT_NODE || process.execPath;

function scheduleSpec() {
  const argv = [scheduledNode(), files.updater, "check", "--scheduled"];
  if (PLATFORM === "darwin") {
    const file = path.join(HOME, "Library", "LaunchAgents", `${LABEL}.plist`);
    const content = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key><array>${argv.map((a) => `<string>${xml(a)}</string>`).join("")}</array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>15</integer></dict>
  <key>StandardOutPath</key><string>${xml(files.log)}</string>
  <key>StandardErrorPath</key><string>${xml(files.log)}</string>
</dict></plist>
`;
    return { kind: "launchd", file, content };
  }
  if (PLATFORM === "win32") {
    const tr = argv.map((a) => `"${a}"`).join(" ");
    return { kind: "schtasks", args: ["/Create", "/TN", TASK, "/TR", tr, "/SC", "DAILY", "/ST", "10:15", "/F"] };
  }
  const q = (a) => `'${a.replace(/'/g, `'\\''`)}'`;
  const systemd = env.DEVKIT_LINUX_SCHEDULER ? env.DEVKIT_LINUX_SCHEDULER === "systemd"
    : run("systemctl", ["--user", "show-environment"]).status === 0;
  if (systemd) {
    const unit = path.join(HOME, ".config", "systemd", "user", "uiuxabhishek-devkit-update");
    return {
      kind: "systemd", file: unit + ".service", timer: unit + ".timer",
      content: `[Unit]\nDescription=UIUX Abhishek DevKit update check\n\n[Service]\nType=oneshot\nExecStart=${argv.map((a) => `"${a}"`).join(" ")}\n`,
      timerContent: "[Unit]\nDescription=Daily UIUX Abhishek DevKit update check\n\n[Timer]\nOnCalendar=daily\nRandomizedDelaySec=1h\nPersistent=true\n\n[Install]\nWantedBy=timers.target\n",
    };
  }
  return { kind: "cron", line: `15 10 * * * ${argv.map(q).join(" ")} >> ${q(files.log)} 2>&1 ${MARKER}` };
}

function readCrontab() {
  if (DRY_SCHEDULER) return readJson(path.join(DIR, "crontab.test.json"), { text: "" }).text;
  const r = spawnSync("crontab", ["-l"], { encoding: "utf8" });
  return r.status === 0 ? r.stdout : "";
}
function writeCrontab(text) {
  if (DRY_SCHEDULER) return writeJson(path.join(DIR, "crontab.test.json"), { text });
  const r = spawnSync("crontab", ["-"], { encoding: "utf8", input: text });
  if (r.status !== 0) throw new UserError(`crontab update failed: ${r.stderr}`);
}

function installSchedule() {
  const spec = scheduleSpec();
  if (spec.kind === "launchd") {
    fs.mkdirSync(path.dirname(spec.file), { recursive: true });
    fs.writeFileSync(spec.file, spec.content);
    const uid = process.getuid?.() ?? 0;
    run("launchctl", ["bootout", `gui/${uid}`, spec.file]);
    const r = run("launchctl", ["bootstrap", `gui/${uid}`, spec.file]);
    if (r.status !== 0) throw new UserError(`launchctl bootstrap failed: ${r.stderr}`);
  } else if (spec.kind === "systemd") {
    fs.mkdirSync(path.dirname(spec.file), { recursive: true });
    fs.writeFileSync(spec.file, spec.content);
    fs.writeFileSync(spec.timer, spec.timerContent);
    run("systemctl", ["--user", "daemon-reload"]);
    const r = run("systemctl", ["--user", "enable", "--now", path.basename(spec.timer)]);
    if (r.status !== 0) throw new UserError(`systemctl enable failed: ${r.stderr}`);
  } else if (spec.kind === "cron") {
    const kept = readCrontab().split("\n").filter((l) => l && !l.includes(MARKER));
    writeCrontab([...kept, spec.line].join("\n") + "\n");
  } else {
    if (DRY_SCHEDULER) writeJson(path.join(DIR, "schtasks.test.json"), { args: spec.args });
    const r = run("schtasks", spec.args);
    if (r.status !== 0) throw new UserError(`schtasks failed: ${r.stderr || r.stdout}`);
  }
  return spec.kind;
}

function removeSchedule() {
  const spec = scheduleSpec();
  if (spec.kind === "launchd") {
    if (fs.existsSync(spec.file)) run("launchctl", ["bootout", `gui/${process.getuid?.() ?? 0}`, spec.file]);
    fs.rmSync(spec.file, { force: true });
  } else if (spec.kind === "systemd") {
    if (fs.existsSync(spec.timer)) run("systemctl", ["--user", "disable", "--now", path.basename(spec.timer)]);
    fs.rmSync(spec.file, { force: true });
    fs.rmSync(spec.timer, { force: true });
  } else if (spec.kind === "cron") {
    const text = readCrontab();
    if (text.includes(MARKER)) writeCrontab(text.split("\n").filter((l) => l && !l.includes(MARKER)).join("\n") + "\n");
  } else {
    if (DRY_SCHEDULER) fs.rmSync(path.join(DIR, "schtasks.test.json"), { force: true });
    run("schtasks", ["/Delete", "/TN", TASK, "/F"]);
  }
}

function scheduleInstalled() {
  const spec = scheduleSpec();
  if (spec.kind === "launchd" || spec.kind === "systemd") return fs.existsSync(spec.timer || spec.file);
  if (spec.kind === "cron") return readCrontab().includes(MARKER);
  if (DRY_SCHEDULER) return fs.existsSync(path.join(DIR, "schtasks.test.json"));
  return spawnSync("schtasks", ["/Query", "/TN", TASK], { encoding: "utf8" }).status === 0;
}

function notify(message) {
  log(message);
  if (env.DEVKIT_NOTIFY === "0" || DRY_SCHEDULER) return;
  const title = "UIUX Abhishek DevKit";
  if (PLATFORM === "darwin") {
    spawnSync("osascript", ["-e", `display notification ${JSON.stringify(message)} with title ${JSON.stringify(title)}`]);
  } else if (PLATFORM === "linux" && which("notify-send")) {
    spawnSync("notify-send", [title, message]);
  } // Windows: the message is in update.log and `status`.
}

// A daily schedule with no run for ~2 days means the scheduler isn't starting the
// check (computer off for days, schedule unloaded, Node path gone). A schedule
// that hasn't had its first run yet is normal, not overdue.
function scheduleHealth(cfg, state) {
  if (cfg.mode === "off") return null;
  const ago = (t) => Date.now() - Date.parse(t);
  const hours = (t) => `${Math.floor(ago(t) / 3600000)} h ago`;
  const help = "The computer may have been off, or the schedule or its Node path is broken. " +
    "Run check now, and setup to repair the schedule (see INSTALL.md).";
  if (state.lastScheduledAt) {
    return ago(state.lastScheduledAt) > OVERDUE_MS
      ? `WARNING: scheduled check overdue: the last one ran ${state.lastScheduledAt} (${hours(state.lastScheduledAt)}). ${help}`
      : `Scheduled check: last ran ${state.lastScheduledAt}`;
  }
  let since = cfg.scheduledAt;
  if (!since) try { since = fs.statSync(files.config).mtime.toISOString(); } catch {}
  if (since && ago(since) > OVERDUE_MS) {
    return `WARNING: scheduled check overdue: none has run since the schedule was set up ${since} (${hours(since)}). ${help}`;
  }
  return `Scheduled check: first run pending (daily at 10:15${since ? `; set up ${since}` : ""})`;
}

// ----------------------------------------------------------------- commands
const config = () => readJson(files.config, null);
const arg = (name) => process.argv.includes(name);
const argValue = (name) => {
  const i = process.argv.indexOf(name);
  return i > 0 ? process.argv[i + 1] : undefined;
};
const requireSetup = () => {
  const cfg = config();
  if (!cfg) throw new UserError(`not set up yet; run: node ${path.basename(SELF)} setup`);
  return cfg;
};

const commands = {
  async setup() {
    const agents = argValue("--agents") ? argValue("--agents").split(",").map((a) => a.trim()) : detectAgents();
    const unknown = agents.filter((a) => !ALL_AGENTS.includes(a));
    if (unknown.length) throw new UserError(`unknown agents: ${unknown.join(", ")} (use ${ALL_AGENTS.join(", ")})`);
    const prev = config() || {};
    const { node, note } = chooseNode(prev.node); // validated before anything is written
    fs.mkdirSync(DIR, { recursive: true });
    if (path.resolve(SELF) !== path.resolve(files.updater)) fs.copyFileSync(SELF, files.updater);
    const schedule = !arg("--no-schedule");
    const cfg = { mode: prev.mode === "auto" ? "auto" : "notify", agents, npx: env.DEVKIT_NPX || which(PLATFORM === "win32" ? "npx.cmd" : "npx"),
      node, schedule, scheduledAt: schedule ? (prev.schedule && prev.scheduledAt) || new Date().toISOString() : null };
    writeJson(files.config, cfg);
    const kind = cfg.schedule ? installSchedule() : "none";
    if (note) console.log(`Note: ${note}`);
    console.log(`Updater installed in ${DIR}\nMode: ${cfg.mode} (checks and notifies; never installs unless you run enable-auto-update)\n` +
      `Agents: ${agents.join(", ") || "none detected yet"}\nNode: ${node}\nSchedule: ${kind === "none" ? "off" : `daily (${kind})`}`);
  },

  async check() {
    const cfg = config() || { mode: "notify" };
    const scheduled = arg("--scheduled");
    if (scheduled && cfg.mode === "off") return;
    await withLock(async () => {
      const prevState = readJson(files.state, {});
      // A scheduled run counts as "ran" even if it then fails, so status can tell
      // a failing check (lastError) from a scheduler that never started (overdue).
      const ran = { lastScheduledAt: scheduled ? new Date().toISOString() : prevState.lastScheduledAt ?? null };
      let status;
      try {
        status = { ...(await checkStatus()), ...ran };
      } catch (e) {
        writeJson(files.state, { ...prevState, ...ran, lastError: e.message, checkedAt: new Date().toISOString() });
        throw e;
      }
      let result = null;
      if (scheduled && cfg.mode === "auto" && status.updateAvailable) {
        try {
          result = await performUpdate(status, cfg);
          notify(result.message);
        } catch (e) {
          notify(`Automatic update failed: ${e.message.split("\n")[0]}. Run the updater's status command for recovery steps.`);
          writeJson(files.state, { ...status, lastError: e.message });
          throw e;
        }
      } else if (status.updateAvailable && scheduled) {
        notify(`Update available: ${status.installed} -> ${status.latest}. Run: node ${files.updater} update --yes`);
      }
      writeJson(files.state, { ...status, lastResult: result?.message ?? null, lastError: null });
      if (arg("--json")) return console.log(JSON.stringify(status, null, 2));
      if (scheduled) return;
      console.log(status.installed ? `Installed: ${status.installed} (tracking ${status.tracking})` : `${SKILL_ID} is not installed globally`);
      console.log(`Latest stable: ${status.latest} ${status.releaseUrl}\nIntegrity: ${status.integrity}`);
      console.log(status.updateAvailable ? `Update available. To install it: node ${path.basename(SELF)} update --yes` : "No update needed.");
      if (status.oldSkillInstalled) {
        console.log(`Note: the old skill ${OLD_SKILL_ID} is still installed. Remove it with: npx skills remove ${OLD_SKILL_ID} -g -y`);
      }
    });
  },

  async update() {
    if (!arg("--yes")) throw new UserError("update changes your installed skill; re-run with --yes to confirm");
    const cfg = config() || { agents: detectAgents() };
    await withLock(async () => {
      const status = { ...(await checkStatus()), lastScheduledAt: readJson(files.state, {}).lastScheduledAt ?? null };
      const result = await performUpdate(status, cfg);
      writeJson(files.state, { ...status, updateAvailable: !result.updated && status.updateAvailable, lastResult: result.message, lastError: null });
      console.log(result.message + (result.backup ? `\nBackup of the previous version: ${result.backup}` : ""));
      if (result.updated) console.log("Restart your agents or open a new session to load the new version.");
    });
  },

  async "enable-auto-update"() {
    const cfg = requireSetup();
    if (!arg("--yes")) throw new UserError("automatic updates install new stable releases without asking; re-run with --yes to opt in");
    const installedAlready = scheduleInstalled();
    if (!installedAlready) {
      cfg.node = chooseNode(cfg.node).node;
      cfg.scheduledAt = new Date().toISOString();
    }
    cfg.mode = "auto";
    cfg.schedule = true;
    writeJson(files.config, cfg);
    if (!installedAlready) installSchedule();
    console.log("Automatic updates enabled: the daily check installs verified stable releases of uiuxabhishek-devkit only.");
  },

  async disable() {
    const cfg = requireSetup();
    removeSchedule();
    writeJson(files.config, { ...cfg, mode: "off", schedule: false });
    console.log("Scheduled checks and automatic updates are off. Manual check and update still work; setup turns notifications back on.");
  },

  async status() {
    const cfg = config();
    const state = readJson(files.state, {});
    const local = installed();
    const scheduleOn = cfg ? scheduleInstalled() : false;
    const nodeLine = !scheduleOn ? null
      : !cfg.node ? "Node: not recorded (set up by an older updater); re-run setup to save a stable path"
      : `Node: ${cfg.node}${runnableNode(cfg.node) ? "" : " (WARNING: missing or not runnable, so scheduled checks can't start; re-run setup)"}`;
    console.log([
      `Updater: ${cfg ? DIR : "not set up"}`,
      `Mode: ${cfg?.mode ?? "-"}   Schedule: ${cfg ? (scheduleOn ? `daily (${scheduleSpec().kind})` : "off") : "-"}`,
      nodeLine,
      scheduleOn ? scheduleHealth(cfg, state) : null,
      `Agents: ${cfg?.agents?.join(", ") || "-"}`,
      `Installed: ${local?.version ?? "not installed"}${local ? ` at ${local.dir}` : ""}`,
      `Last check: ${state.checkedAt ?? "never"}${state.latest ? `, latest ${state.latest}` : ""}${state.updateAvailable ? " (update available)" : ""}`,
      state.lastResult ? `Last result: ${state.lastResult}` : null,
      state.lastError ? `Last error: ${state.lastError}` : null,
      fs.existsSync(files.lock) ? `Lock: ${files.lock} (a run is in progress, or remove it if none is)` : null,
      `Log: ${files.log}`,
    ].filter(Boolean).join("\n"));
  },

  async uninstall() {
    if (config()) removeSchedule();
    fs.rmSync(DIR, { recursive: true, force: true });
    console.log(`Removed the updater and its schedule (${DIR}). The ${SKILL_ID} skill itself is unchanged.`);
  },
};

const name = process.argv[2];
if (!commands[name]) {
  console.log(fs.readFileSync(SELF, "utf8").split("\n").filter((l) => l.startsWith("//")).slice(0, 14).map((l) => l.slice(3)).join("\n"));
  process.exit(name && name !== "help" && name !== "--help" ? 2 : 0);
}
try {
  await commands[name]();
} catch (e) {
  if (!(e instanceof UserError)) throw e;
  console.error(`uiuxabhishek-devkit updater: ${e.message}`);
  try { log(`error: ${e.message.split("\n")[0]}`); } catch {}
  process.exit(1);
}
