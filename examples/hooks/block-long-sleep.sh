#!/usr/bin/env bash
# PreToolUse guard: refuse a long foreground sleep used as a timer.
#
# Subagents wait on a background job with `sleep 590; grep ... suite5.log`: sleep
# just under the 600s foreground timeout, then look once. It always costs the full
# ten minutes even when the job finished in forty seconds, it is blind to a crash
# in the meantime, and chaining it with a grep slips past the harness's own
# bare-sleep block.
#
# Blocks `sleep N` (bash, or the PowerShell `sleep` alias) and `Start-Sleep` when
# any single call exceeds MAX_SECONDS. A short sleep inside a poll loop passes:
#   timeout 590 bash -c 'until grep -q "^# fail" x.log; do sleep 5; done'
# A call with run_in_background=true passes; it blocks nobody.
#
# The escape is to wait on the condition, not the clock: run the job with
# run_in_background and take the completion notification, or use Monitor, or a
# bounded until-loop with a short sleep.
#
# Judged per segment, with variables set earlier in the line substituted
# (shell_vars.py). An unresolved `sleep $N` passes.

# =============================== CONFIG ===============================================
# Longest single foreground sleep allowed, in seconds.
MAX_SECONDS=30
# ======================================================================================

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && (pwd -W 2>/dev/null || pwd))"
export HOOK_DIR MAX_SECONDS
PY=$(command -v python || command -v python3)

payload=$(cat)

printf '%s' "$payload" | "$PY" -c '
import json, sys, re, os

sys.path.insert(0, os.environ["HOOK_DIR"])
from shell_vars import segments

MAX_SECONDS = int(os.environ.get("MAX_SECONDS") or 30)

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
if not isinstance(ti, dict) or ti.get("run_in_background") is True:
    sys.exit(0)
cmd = str(ti.get("command") or "")
if not cmd.strip():
    sys.exit(0)

UNIT = {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}
# coreutils sleep: one or more NUMBER[smhd] arguments, summed.
SLEEP = re.compile(
    r"(?:^|[\s(`\x27\"])sleep\s+((?:[0-9]*\.?[0-9]+[smhd]?\s*)+)(?=$|[\s)`\x27\"])",
    re.I)
# PowerShell: Start-Sleep [-Seconds|-s] N  |  Start-Sleep -Milliseconds|-m N
PS = re.compile(
    r"Start-Sleep\s+(?:(-(?:Seconds|s)\s+)|(-(?:Milliseconds|ms|m)\s+))?([0-9]*\.?[0-9]+)",
    re.I)

def longest(seg):
    worst = 0.0
    for m in SLEEP.finditer(seg):
        total = 0.0
        for n, u in re.findall(r"([0-9]*\.?[0-9]+)([smhd]?)", m.group(1), re.I):
            total += float(n) * UNIT[u.lower()]
        worst = max(worst, total)
    for m in PS.finditer(seg):
        n = float(m.group(3))
        worst = max(worst, n / 1000 if m.group(2) else n)
    return worst

for seg in segments(cmd):
    secs = longest(seg)
    if secs > MAX_SECONDS:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason":
                "Blocked: a %gs foreground sleep used as a timer (limit %ds). It always "
                "costs the full wait even when the job finished seconds in, and it is "
                "blind to a crash meanwhile. Wait on the condition, not the clock: "
                "(1) start the job with run_in_background=true and act on the completion "
                "notification; (2) use the Monitor tool; or (3) poll with a short sleep "
                "under a cap, e.g. timeout 590 bash -c \x27until grep -q PATTERN FILE; "
                "do sleep 5; done\x27." % (secs, MAX_SECONDS)}}))
        sys.exit(0)
' 2>/dev/null

exit 0
