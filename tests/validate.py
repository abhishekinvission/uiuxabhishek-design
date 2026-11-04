"""Repository validation for the uiuxabhishek-design skill.

Standard library only. Run from anywhere:  python3 tests/validate.py [--cli]

Checks: single-skill discovery and frontmatter, Markdown links, SOURCES.md
checksums and inventory, license/notice mirrors, router parsing and
reference coverage, routing scenarios, context budget and a basic
secret/executable scan. --cli also runs `npx skills add . --list`.

Routing scenarios use a deterministic keyword simulation of SKILL.md's
signal tables. It checks that the router's signals, conditions and file
mappings are coherent; it is a proxy for, not a replacement of, an agent's
semantic judgment.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "uiuxabhishek-design")
THIRD_PARTY = ("references/impeccable/", "references/apple-design/")
BASELINE_COMMIT = "036b394"  # last commit before the router rewrite
FRONTMATTER_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
SKILL_MD_MAX_CHARS = 12000
GUIDE_MAX_CHARS = 5000
UI_WORDS = {"ui", "page", "screen", "dashboard", "component", "frontend", "design", "interface", "view"}

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
    return cond


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def rel(path, base=SKILL):
    return os.path.relpath(path, base).replace(os.sep, "/")


def md_files(base=ROOT):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            if f.lower().endswith(".md"):
                yield os.path.join(root, f)


# ---------------------------------------------------------------- discovery
def check_discovery():
    found = [p for p in md_files() if os.path.basename(p).lower() == "skill.md"]
    check([rel(p, ROOT) for p in found] == ["skills/uiuxabhishek-design/SKILL.md"],
          f"expected exactly one SKILL.md, found {[rel(p, ROOT) for p in found]}")
    text = read(os.path.join(SKILL, "SKILL.md"))
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not check(m, "SKILL.md has no frontmatter"):
        return
    top = dict(re.findall(r"^([a-z-]+):\s*(.*)$", m.group(1), re.M))
    check(set(top) <= FRONTMATTER_KEYS, f"unexpected frontmatter keys {set(top) - FRONTMATTER_KEYS}")
    check(top.get("name") == "uiuxabhishek-design", "frontmatter name must be uiuxabhishek-design")
    desc = top.get("description", "")
    check(0 < len(desc) <= 1024, f"description length {len(desc)} not in 1..1024")
    print(f"discovery: 1 skill, description {len(desc)} chars")


def check_cli():
    try:
        out = subprocess.run(["npx", "--yes", "skills", "add", ".", "--list"], cwd=ROOT,
                             capture_output=True, text=True, timeout=180).stdout
    except (OSError, subprocess.TimeoutExpired) as e:
        check(False, f"skills CLI unavailable: {e}")
        return
    names = re.findall(r"^│ {4}([a-z0-9-]+)\s*$", out, re.M)
    check(names == ["uiuxabhishek-design"], f"skills CLI discovered {names}")
    print(f"skills CLI: {names}")


# -------------------------------------------------------------------- links
def check_links():
    count = 0
    for path in md_files():
        for link in re.findall(r"\]\(([^)\s]+)\)", read(path)):
            if re.match(r"^(https?:|mailto:|#|<)", link):
                continue
            count += 1
            target = os.path.join(os.path.dirname(path), link.split("#")[0])
            check(os.path.exists(target), f"broken link {rel(path, ROOT)} -> {link}")
    print(f"links: {count} relative links checked")


# ---------------------------------------------------------------- integrity
def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_integrity():
    sources = read(os.path.join(ROOT, "SOURCES.md"))
    third, _, original = sources.partition("## Original project content")
    entries = [(os.path.join(SKILL, "references", p), h)
               for p, h in re.findall(r"^- `(\S+)  ([0-9a-f]{64})`$", third, re.M)]
    entries += [(os.path.join(SKILL, p), h)
                for p, h in re.findall(r"^- `(\S+)  ([0-9a-f]{64})`$", original, re.M)]
    for path, digest in entries:
        if check(os.path.exists(path), f"SOURCES.md lists missing file {rel(path)}"):
            check(sha256(path) == digest, f"checksum mismatch {rel(path)}")
    on_disk = {os.path.join(r, f) for d in ("references", "templates")
               for r, _, fs in os.walk(os.path.join(SKILL, d)) for f in fs}
    listed = {p for p, _ in entries}
    check(on_disk == listed, f"inventory drift: unlisted {sorted(rel(p) for p in on_disk - listed)}")
    for name in ("LICENSE", "NOTICE.md"):
        check(read(os.path.join(ROOT, name)) == read(os.path.join(SKILL, name)), f"{name} mirror differs")
    root_lic, skill_lic = os.path.join(ROOT, "LICENSES"), os.path.join(SKILL, "LICENSES")
    check(sorted(os.listdir(root_lic)) == sorted(os.listdir(skill_lic)), "LICENSES file lists differ")
    for f in os.listdir(root_lic):
        check(sha256(os.path.join(root_lic, f)) == sha256(os.path.join(skill_lic, f)), f"LICENSES/{f} differs")
    print(f"integrity: {len(entries)} checksums, mirrors compared")


# ------------------------------------------------------------------- router
def words(text):
    out = set()
    text = re.sub(r"https?://", " ", text.lower())  # a URL scheme is not an HTTP-integration signal
    for tok in re.sub(r"[^a-z0-9.\-'_]+", " ", text).split():
        tok = tok.strip(".-'")
        if len(tok) > 3 and tok.endswith("s"):
            tok = tok[:-1]
        if tok:
            out.add(tok)
    return out


def matches(signals, prompt_words):
    return any(words(sig) and words(sig) <= prompt_words for sig in signals.split(","))


def parse_router():
    text = read(os.path.join(SKILL, "SKILL.md"))
    modes = {m: sig for m, sig in re.findall(r"^\| `(\w+)` \| ([^|]+) \|", text.split("## 2.")[0], re.M)}
    caps, base = {}, ""
    section = text.split("## 2. Capability map")[1].split("## 3.")[0]
    for line in section.splitlines():
        b = re.search(r"bare names are in `([^`]+)`", line)
        if b:
            base = b.group(1)
        elif line.startswith("**"):
            base = ""
        row = re.match(r"^\| `([\w-]+)` \| (.+) \|$", line)
        if not row:
            continue
        segments = []
        for seg in row.group(2).split(" · "):
            cond = seg.startswith("+")
            sig, _, targets = seg.lstrip("+").partition(" → ")
            files = [p for p in re.findall(r"\]\(([^)]+)\)", targets)]
            files += [base + p for p in re.findall(r"(?<!\()`([\w./-]+\.md)`", targets)]
            check(files, f"router row {row.group(1)} segment has no files: {seg}")
            for f in files:
                check(os.path.exists(os.path.join(SKILL, f)), f"router target missing: {f}")
            segments.append({"cond": cond, "signals": sig, "files": files})
        caps[row.group(1)] = segments
    never = re.search(r"\*\*Never load\*\*[^:]*:(.*)", text).group(1)
    never = {"references/impeccable/reference/" + n.rstrip("*")
             for n in re.findall(r"`([\w/.*-]+)`", never)}
    craft_floor = re.search(r"\[craft-floor\.md\]\(([^)]+)\)", text).group(1)
    groups = {}
    for name, body in re.findall(r"^\*\*(Design|Engineering)\*\*(.*?)(?=^\*\*|\Z)",
                                 section, re.S | re.M):
        groups[name] = set(re.findall(r"^\| `([\w-]+)` \|", body, re.M))
    return text, modes, caps, never, craft_floor, groups


def is_never(path, never):
    return any(path == n or (n.endswith("/") and path.startswith(n)) for n in never)


def check_coverage(caps, never):
    routed = {f for segs in caps.values() for s in segs for f in s["files"]}
    expected = set()
    for d in ("references/frontend", "references/workflows", "templates", "references/impeccable/reference"):
        for r, _, fs in os.walk(os.path.join(SKILL, d)):
            expected |= {rel(os.path.join(r, f)) for f in fs if f.endswith(".md")}
    expected.add("references/apple-design/SOURCE_SKILL.md")
    expected -= {p for p in expected if is_never(p, never)}
    expected.discard("references/impeccable/reference/craft-floor.md")  # loaded by the shared UI-edit rule
    check(not (expected - routed), f"unrouted references: {sorted(expected - routed)}")
    check(not {p for p in routed if is_never(p, never)}, "a never-load file is routed")
    primary = {}
    for cap, segs in caps.items():
        for s in segs:
            if not s["cond"]:
                for f in s["files"]:
                    primary.setdefault(f, set()).add(cap)
    dup = {f: c for f, c in primary.items() if len(c) > 1}
    check(not dup, f"files routed as primary by several capabilities: {dup}")
    print(f"coverage: {len(routed)} routed files, {len(never)} never-load entries, no duplicate primaries")


LIMIT_AUDIT = "read-only, dry run, report only, don't change"
LIMIT_IMPLEMENT = "don't push, no pr, locally"


def detect_mode(prompt, modes):
    w = words(prompt)
    if matches(LIMIT_AUDIT, w):
        return "audit"
    capped = matches(LIMIT_IMPLEMENT, w)
    order = ["answer", "deliver", "plan", "implement", "audit"]
    found = [m for m in order if matches(modes[m], w)]
    if capped:
        found = [m for m in found if m != "deliver"]
    return found[0] if found else None


def route(prompt, modes, caps, craft_floor, groups):
    w = words(prompt)
    mode = detect_mode(prompt, modes)
    selected, files = [], []
    for cap, segs in caps.items():
        hit = [s for s in segs if not s["cond"] and matches(s["signals"], w)]
        if hit:
            selected.append(cap)
            files += [f for s in hit for f in s["files"]]
    if "ado" in selected and mode is None:
        mode = "audit"  # a bare work-item ID or URL is a dry run
    mode = mode or "implement"
    for cap in selected:
        for s in caps[cap]:
            if s["cond"]:
                cond = s["signals"]
                mode_cond = {m for m in ("implement", "deliver", "audit", "plan") if m in words(cond)}
                if (mode in mode_cond) if mode_cond else matches(cond, w):
                    files += s["files"]
    design = groups["Design"]
    if mode in ("implement", "deliver") and set(selected) & design:
        files.append(craft_floor)
    if not selected:
        outcome = "guide" if mode == "answer" else ("clarify" if w & UI_WORDS else "skip")
        files = ["GUIDE.md"] if outcome == "guide" else []
    else:
        outcome = "route"
    return set(selected), mode, outcome, list(dict.fromkeys(files))


def tokens(paths):
    return sum(len(read(os.path.join(SKILL, p))) for p in paths) // 4


def baseline_tokens(old_skill_chars, files, selected):
    """Approximate load under the previous router (entry points read first)."""
    base = set(files) - {"GUIDE.md"}
    if any(f.startswith("references/impeccable/") for f in base):
        base.add("references/impeccable/SOURCE_SKILL.md")
    if "ado" in selected:
        base |= {"references/frontend/testing.md", "references/frontend/review-and-release.md"}
    return old_skill_chars // 4 + tokens(sorted(base))


def check_scenarios(modes, caps, never, craft_floor, groups, text):
    data = json.loads(read(os.path.join(ROOT, "tests", "routing_scenarios.json")))
    try:
        old = subprocess.run(["git", "show", f"{BASELINE_COMMIT}:skills/uiuxabhishek-design/SKILL.md"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        old = None
    ado_files = {f for s in caps["ado"] for f in s["files"]} - {"references/frontend/testing.md",
                                                               "references/frontend/review-and-release.md",
                                                               "templates/pr-description.md"}
    skill_tokens = len(text) // 4
    print(f"\n{'scenario':30} {'mode':10} {'capabilities':34} {'tokens':>7} {'before':>7}  result")
    total_new = total_old = 0
    for sc in data["scenarios"]:
        selected, mode, outcome, files = route(sc["prompt"], modes, caps, craft_floor, groups)
        errs = []
        if selected != set(sc["caps"]):
            errs.append(f"caps {sorted(selected)} != {sorted(sc['caps'])}")
        if mode != sc["mode"]:
            errs.append(f"mode {mode} != {sc['mode']}")
        if outcome not in sc.get("outcome", ["route"]):
            errs.append(f"outcome {outcome}")
        errs += [f"missing {f}" for f in sc["must"] if f not in files]
        errs += [f"loaded forbidden {f}" for f in sc["forbid"] if f in files]
        errs += [f"loaded never-load {f}" for f in files if is_never(f, never)]
        if "ado" not in sc["caps"]:
            errs += [f"loaded ADO file {f}" for f in files if f in ado_files]
        new = skill_tokens + tokens(files)
        before = baseline_tokens(len(old), files, selected) if old else 0
        total_new += new
        total_old += before
        check(not errs, f"scenario {sc['id']}: {'; '.join(errs)}")
        print(f"{sc['id']:30} {mode:10} {','.join(sorted(selected)) or '-':34} {new:7} {before:7}  "
              f"{'PASS' if not errs else 'FAIL'}")
    n = len(data["scenarios"])
    check(n >= 12, "need at least 12 routing scenarios")
    if total_old:
        print(f"{n} scenarios: ~{total_new // n} tokens/scenario vs ~{total_old // n} before "
              f"({100 - 100 * total_new // total_old}% less context)")


# ------------------------------------------------------------------- budget
def check_budget(text):
    guide = read(os.path.join(SKILL, "GUIDE.md"))
    check(len(text) <= SKILL_MD_MAX_CHARS, f"SKILL.md {len(text)} chars > {SKILL_MD_MAX_CHARS}")
    check(len(guide) <= GUIDE_MAX_CHARS, f"GUIDE.md {len(guide)} chars > {GUIDE_MAX_CHARS}")
    check("GUIDE.md" in text, "SKILL.md must link GUIDE.md")
    print(f"budget: SKILL.md ~{len(text) // 4} tokens, GUIDE.md ~{len(guide) // 4} tokens")


# ----------------------------------------------------------------- security
def check_security():
    secret = re.compile(r"(ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|"
                        r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,})", re.I)
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
        for f in files:
            p = os.path.join(root, f)
            check(not os.path.islink(p), f"symlink {rel(p, ROOT)}")
            check(not os.access(p, os.X_OK), f"executable file {rel(p, ROOT)}")
            r = rel(p, SKILL)
            if f.endswith((".md", ".json", ".py", ".txt")) and not r.startswith(THIRD_PARTY):
                check(not secret.search(read(p)), f"possible secret in {rel(p, ROOT)}")
    print("security: secret, symlink and executable scan done")


def main():
    check_discovery()
    if "--cli" in sys.argv:
        check_cli()
    check_links()
    check_integrity()
    text, modes, caps, never, craft_floor, groups = parse_router()
    check(set(modes) == {"answer", "audit", "plan", "implement", "deliver"}, f"modes {sorted(modes)}")
    limits = text.lower().replace("\u2019", "'")
    for phrase in (LIMIT_AUDIT + "," + LIMIT_IMPLEMENT).split(","):
        check(phrase.strip() in limits, f"limit phrase {phrase.strip()!r} not documented in SKILL.md")
    check_coverage(caps, never)
    check_budget(text)
    check_security()
    check_scenarios(modes, caps, never, craft_floor, groups, text)
    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
