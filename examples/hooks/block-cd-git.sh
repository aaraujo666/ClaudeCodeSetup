#!/usr/bin/env bash
# PreToolUse guard: refuse `cd <repo> && git ...` (and the PowerShell equivalents).
#
# A leading `cd` defeats the permission allowlist - the harness matches on a
# command prefix, and `cd <varying-dir> &&` never matches a stable one, so every
# call turns into a prompt. `git-in.sh` exists precisely to keep that prefix
# stable via `git -C <dir>`. See examples/scripts/git-in.sh.
#
# Blocks only when a cd-like command precedes a git call in the same line.
# `git clone x && cd x` (cd after git) is left alone.
#
# `git` counts only as a segment's COMMAND word (after any VAR=x prefixes or sudo),
# in any segment after the cd. Matching the word anywhere in the next segment
# would refuse `ls .git` or a file named block-cd-git.sh (- and . are word
# boundaries) while letting `cd x && make && git commit` through.

# =============================== CONFIG ===============================================
# Where git-in.sh is installed, as shown in the deny message.
GIT_IN='~/.claude/scripts/git-in.sh'
# ======================================================================================

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && (pwd -W 2>/dev/null || pwd))"
export HOOK_DIR GIT_IN
PY=$(command -v python || command -v python3)

payload=$(cat)

printf '%s' "$payload" | "$PY" -c '
import json, sys, os

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
git_in = os.environ.get("GIT_IN") or "~/.claude/scripts/git-in.sh"

# Commands come from shell_vars.parse(), so a quoted `;` (a commit message) never
# splits the line and "git" inside a quoted argument is never a command.
seen_cd = False
for c in parse(cmd, ps=d.get("tool_name") == "PowerShell"):
    if c.name in ("cd", "pushd", "set-location", "sl", "chdir", "push-location") and c.args:
        seen_cd = True
    elif seen_cd and c.name == "git":
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason":
                "Blocked: `cd <dir> && git ...` defeats the permission allowlist, so it "
                "prompts every time. Use the allowlisted wrapper instead -- `bash "
                + git_in + " <repo-dir> <git args...>` (it runs `git -C <dir> ...`, no "
                "cd). Example: bash " + git_in + " ~/source/repos/foo status -s"}}))
        sys.exit(0)
' 2>/dev/null

exit 0
