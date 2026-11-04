"""Build the upload ZIP for Claude.ai / Claude Desktop Chat (Customize > Skills).

Standard library only. Run from anywhere:  python3 tools/package_skill.py [out_dir]

The ZIP has one root folder, uiuxabhishek-design/, containing the complete
skill directory (SKILL.md, GUIDE.md, references/, templates/, LICENSE,
NOTICE.md, LICENSES/). Claude's upload form limits the description to 200
characters, so only the packaged SKILL.md swaps its description for
UPLOAD_DESCRIPTION; every other byte is copied unchanged. Output is
deterministic: sorted entries, fixed timestamps and permissions.
"""
import hashlib
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "uiuxabhishek-design")
NAME = "uiuxabhishek-design"
UPLOAD_DESCRIPTION = ("UI/UX design and frontend engineering router for visual craft, accessibility, "
                      "motion, frontend pages, APIs, CRUD, tests and Azure DevOps delivery. "
                      "Loads only what a task needs.")
UPLOAD_DESCRIPTION_MAX = 200
SKIP = {".DS_Store", "Thumbs.db"}
STAMP = (2026, 1, 1, 0, 0, 0)


def version():
    with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
        m = re.search(r"^  version: \"?(\d+\.\d+\.\d+)\"?$", f.read(), re.M)
    if not m:
        sys.exit("SKILL.md metadata.version is missing")
    return m.group(1)


def upload_skill_md():
    with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
        text = f.read()
    new, n = re.subn(r"^description: .*$", "description: " + UPLOAD_DESCRIPTION, text, count=1, flags=re.M)
    if n != 1 or len(UPLOAD_DESCRIPTION) > UPLOAD_DESCRIPTION_MAX or re.search(r":\s|\s#", UPLOAD_DESCRIPTION):
        sys.exit("cannot set upload description")
    return new.encode("utf-8")


def files():
    for root, dirs, names in os.walk(SKILL):
        dirs.sort()
        for n in sorted(names):
            if n not in SKIP:
                p = os.path.join(root, n)
                if os.path.islink(p):
                    sys.exit(f"refusing symlink {p}")
                yield p, os.path.relpath(p, SKILL).replace(os.sep, "/")


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{NAME}-v{version()}.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for src, rel in files():
            info = zipfile.ZipInfo(f"{NAME}/{rel}", STAMP)
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            if rel == "SKILL.md":
                data = upload_skill_md()
            else:
                with open(src, "rb") as f:
                    data = f.read()
            z.writestr(info, data)
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    with open(path + ".sha256", "w", encoding="utf-8") as f:
        f.write(f"{digest}  {os.path.basename(path)}\n")
    return path, digest


if __name__ == "__main__":
    out, digest = build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist"))
    print(f"{out}\nsha256 {digest}")
