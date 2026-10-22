#!/usr/bin/env bash
# PreToolUse guard: never delete files -- archive instead.
#
# Enforces the standing rule "never delete, archive". A stated rule that nothing
# enforces gets forgotten; the archive-not-delete habit is load-bearing because the
# files that look worthless are the ones you want back a month later.
#
# Two decisions:
#
#   deny  Bulk or unrecoverable removal -- a recursive/forced flag, a glob, a
#         cmd /s /q, find -delete, or git clean -f. These take out more than
#         was aimed at and there is nothing left to recover from.
#
#   ask   A plain single-target rm/del/Remove-Item. Deliberately not a wall:
#         a named one-off is exactly the case where confirming beats blocking.
#
# Deliberately ALLOWED:
#
#   git rm / git-in.sh <dir> rm   -- a versioned deletion. Git history IS the
#                                    archive, so the rule is already satisfied.
#   anything under the session scratchpad, /tmp, or a regenerable cache
#                                 -- node_modules, __pycache__, .pytest_cache,
#                                    .ruff_cache, .mypy_cache. Nothing there is
#                                    an original.
#   anything under WORKTREE_RE    -- agent workspace: disposable git worktrees,
#                                    run directories, evidence. git clean -f is
#                                    exempt there too.
#
# The escape when a delete is genuinely right: move it aside instead --
#   mv <path> <dir>/_archive/
#
# Note this is a drift guard, not a security boundary. Exemption is matched per
# command's own targets, so `rm -rf /real/path` is still caught when a later
# command in the same line touches /tmp.
#
# The line is parsed by shell_vars.parse(), not grepped: commands are judged by
# their command word and real arguments, so quoted text (a commit message naming
# "find" and "-delete") is never read as a command, variables set earlier in the
# line are substituted, and a relative target is resolved against the session cwd
# and any `cd` before it -- `cd $W && rm src/x.tmp.ts` inside a worktree is exempt.

# =============================== CONFIG ===============================================
# Regex (matched against the target path) for the agent-workspace tree where deletes are
# allowed. Placeholder: ~/source/worktrees.
WORKTREE_RE='source[\\/]worktrees[\\/]'
# ======================================================================================

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && (pwd -W 2>/dev/null || pwd))"
export HOOK_DIR WORKTREE_RE
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
if not isinstance(ti, dict):
    sys.exit(0)

cmd = str(ti.get("command") or "")
if not cmd.strip():
    sys.exit(0)
cmds = parse(cmd, ps=d.get("tool_name") == "PowerShell")
WORKTREE_RE = os.environ.get("WORKTREE_RE") or r"source[\\/]worktrees[\\/]"


def emit(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason}}))
    sys.exit(0)


ARCHIVE = (" The rule is archive, never delete: move it aside instead -- "
           "mv <path> <dir>/_archive/ -- or, for a tracked file, use git rm so "
           "history keeps the copy. Scratchpad, /tmp and regenerable caches "
           "(node_modules, __pycache__, .pytest_cache) are exempt and need no "
           "workaround.")

# Regenerable or throwaway locations. Nothing here is an original.
EXEMPT = re.compile(
    r"AppData[\\/]Local[\\/]Temp|[\\/]tmp[\\/]|scratchpad|node_modules|"
    r"__pycache__|\.pytest_cache|\.ruff_cache|\.mypy_cache|"
    r"\.venv[\\/]|[\\/]dist[\\/]|[\\/]build[\\/]|" + WORKTREE_RE, re.I)

DELVERBS = {"rm", "rmdir", "rd", "del", "erase", "remove-item", "ri"}

# -r -f -rf -fr -R --force -Recurse, and cmd style /s /q
FORCE = re.compile(r"^--?[A-Za-z]*[rRfF][A-Za-z]*$|^/[sSqQ]$")
BRACE = re.compile(r"\{[^}]*,[^}]*\}")


def absolute(p):
    return bool(re.match(r"^(/|~|[A-Za-z]:[\\/]|\\\\)", p))


def located(p, cwd):
    """The target as a path the exemption can judge: relative ones joined to cwd."""
    return p if absolute(p) or not cwd else cwd.rstrip("/\\") + "/" + p


cwd = str(d.get("cwd") or "")
for c in cmds:
    if c.name in ("cd", "pushd", "set-location", "sl", "chdir") and c.args:
        dest = [a for a in c.args if not a.startswith("-")]
        if dest:
            cwd = dest[0] if absolute(dest[0]) else located(dest[0], cwd)
        continue

    # `find ... -delete` and `find ... -exec rm` are bulk deletes wearing a hat.
    if c.name == "find":
        a = [w.lower() for w in c.args]
        bulk = "-delete" in a or any(
            w in ("-exec", "-execdir", "-ok") and a[k + 1:k + 2] in (["rm"], ["sudo"])
            for k, w in enumerate(a))
        roots = [w for w in c.args[:1] if not w.startswith("-")] or ["."]
        if bulk and not all(EXEMPT.search(located(r, cwd)) for r in roots):
            emit("deny",
                 "Blocked: a find -delete / find -exec rm removes every match at "
                 "once, and nothing survives to recover from." + ARCHIVE)
        continue

    # git clean -f permanently removes untracked files -- not in history, not undoable.
    gargs = None
    if c.name == "git":
        gargs = c.args
    elif c.name in ("bash", "sh") and c.args and c.args[0].endswith("git-in.sh"):
        gargs = c.args[2:]
    if gargs is not None and "clean" in gargs:
        where = " ".join(c.args) + " " + cwd
        if any(re.match(r"^-[A-Za-z]*f", w) for w in gargs) \
                and not re.search(WORKTREE_RE, where, re.I):
            emit("deny",
                 "Blocked: git clean -f permanently removes UNTRACKED files -- they "
                 "are not in history, so this is the one git command with nothing to "
                 "recover from." + ARCHIVE + " To see what it would take out first, "
                 "run it with -n instead of -f.")
        continue

    if c.name not in DELVERBS:
        continue
    flags = [w for w in c.args if FORCE.match(w)]
    targets = [w for w in c.args if not w.startswith("-") and not FORCE.match(w)]
    if targets and all(EXEMPT.search(located(t, cwd)) for t in targets):
        continue

    verb = c.name
    if flags or any(t.glob or BRACE.search(t) for t in targets):
        emit("deny",
             "Blocked: `" + verb + "` here is recursive, forced or globbed, so it "
             "removes more than one named thing and leaves nothing to recover." +
             ARCHIVE)

    emit("ask",
         "This deletes a file (`" + verb + "`), and the standing rule is to "
         "archive rather than delete." + ARCHIVE + " Confirm only if this file "
         "genuinely has no value.")
' 2>/dev/null

exit 0
