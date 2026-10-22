#!/usr/bin/env bash
# PreToolUse guard: refuse an unbounded filesystem walk from a root directory.
#
# `find / -name x` under Git Bash walks all of C:\ plus every mount. One of these ran
# for 2h35m and burned 7,773 seconds of CPU in the background before anyone noticed,
# and the answer it was looking for was two directories deep. The same class of
# mistake as `grep -r` over a directory holding multi-gigabyte disk images.
#
# Blocks `find` rooted at /, ~, $HOME, /c, or a bare drive root with no
# -maxdepth. Anything with -maxdepth, or rooted at a real subdirectory, passes.
#
# The escape is to bound it: add -maxdepth N, or root the search where the file
# actually is. On Windows, `Get-ChildItem -Path <dir> -Depth N` is usually the
# faster answer anyway.
#
# Judged per find invocation from shell_vars.parse(): variables set earlier in the
# line substituted, quotes stripped, so `R=/; find $R`, a quoted root, and a
# -maxdepth on some OTHER find in the same line do not slip through, and the
# word "find" inside a quoted argument is never taken for a command.

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && (pwd -W 2>/dev/null || pwd))"
export HOOK_DIR
PY=$(command -v python || command -v python3)

payload=$(cat)

printf '%s' "$payload" | "$PY" -c '
import json, sys, re, os

sys.path.insert(0, os.environ["HOOK_DIR"])
from shell_vars import parse

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
cmd = str(ti.get("command") or "") if isinstance(ti, dict) else ""
if not cmd.strip():
    sys.exit(0)
if d.get("tool_name") == "PowerShell":
    sys.exit(0)  # find there is find.exe, a text search -- it walks nothing

# Roots that mean "the whole machine": /  ~  $HOME  ${HOME}  /c  C:  C:/  C:\  with an
# optional trailing slash. Anything deeper (/var, ~/src, /c/Users) is left alone.
ROOT = re.compile(r"^(?:/|~/?|\$HOME/?|\$\{HOME\}/?|/[A-Za-z]/?|[A-Za-z]:[\\/]?)$")

for c in parse(cmd):
    if c.name != "find":
        continue
    # Start points are the args before the first expression token (-name, !, ( ...),
    # after the -H/-L/-P options.
    roots = []
    for w in c.args:
        if w in ("-H", "-L", "-P"):
            continue
        if w.startswith("-") or w in ("!", "(", ")"):
            break
        roots.append(w)
    if any(ROOT.match(r) for r in roots) and "-maxdepth" not in c.args:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason":
                "Blocked: an unbounded `find` from a root directory walks the entire "
                "filesystem -- under Git Bash that is all of C:\\ plus every mount. One "
                "of these ran 2h35m and burned 7,773s of CPU unnoticed. "
                "Bound it or root it: add `-maxdepth N`, or point find at the directory "
                "the file is actually in. On Windows `Get-ChildItem -Path <dir> -Depth N "
                "-Filter <pat>` is usually faster. If you genuinely need a whole-disk "
                "sweep, run it with -maxdepth and widen it."}}))
        sys.exit(0)
' 2>/dev/null

exit 0
