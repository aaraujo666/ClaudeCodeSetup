#!/usr/bin/env bash
# PreToolUse guard: refuse shell heredocs / PowerShell here-strings.
#
# Backslash escapes get mangled between the tool call and the shell, so a patch
# carrying `\n` (or any escape) silently fails to match and the same edit gets
# done twice -- once with the heredoc that fails, then again with a fixed one.
# The double work is the cost. Write and Edit have no such layer.
#
# Blocks:  cmd <<EOF / <<'EOF' / <<"EOF" / <<-EOF   and   @'...'@ / @"..."@
# Allows:  <<<  (a here-string, one line, no escape layer)
#          <<   used as a bit shift on digits (`1 << 2`)

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && (pwd -W 2>/dev/null || pwd))"
export HOOK_DIR
PY=$(command -v python || command -v python3)

payload=$(cat)

cmd=$(printf '%s' "$payload" | "$PY" -c 'import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
print(ti.get("command", ""))' 2>/dev/null)

[ -z "$cmd" ] && exit 0

deny() {
  # printf, not a heredoc -- this script has to obey its own rule.
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$1"
  exit 0
}

REASON='Blocked: heredocs and PowerShell here-strings are banned for file content. Backslash escapes get mangled in transit, so the patch silently fails to match and the edit ends up being done twice. Use the Write tool for a whole file and the Edit tool for a targeted change. Bash stays right for RUNNING things (git, pytest, grep, one-liners with no embedded content). If you need a temp file of content, Write it to the scratchpad and reference the path.'

# Bash heredoc: an UNQUOTED `<<` (not `<<<`), optional `-`, optional quote, then a
# word. shell_vars.parse() does the quote tracking, so `git commit -m "no <<EOF"`
# is not a heredoc. Only the Bash tool: PowerShell has no heredoc (and `<<` there is
# never one), its here-strings are checked below.
tool=$(printf '%s' "$payload" | "$PY" -c 'import json,sys
try:
    print(json.load(sys.stdin).get("tool_name") or "")
except Exception:
    pass' 2>/dev/null)
if [ "$tool" != "PowerShell" ] && printf '%s' "$cmd" | "$PY" -c 'import sys, os
sys.path.insert(0, os.environ["HOOK_DIR"])
from shell_vars import parse
sys.exit(0 if parse(sys.stdin.read()).heredoc else 1)' 2>/dev/null; then
  deny "$REASON"
fi

# PowerShell here-string: an opening @' or @" that is followed by its terminator.
if printf '%s' "$cmd" | grep -Eq "@'" && printf '%s' "$cmd" | grep -Eq "'@"; then
  deny "$REASON"
fi
if printf '%s' "$cmd" | grep -Eq '@"' && printf '%s' "$cmd" | grep -Eq '"@'; then
  deny "$REASON"
fi

exit 0
