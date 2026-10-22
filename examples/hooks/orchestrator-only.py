"""Orchestrator-only: the MAIN THREAD may not edit code; it must dispatch to subagents.

  python orchestrator-only.py pretool   PreToolUse on Edit|Write|MultiEdit|NotebookEdit
  python orchestrator-only.py prompt    UserPromptSubmit

Why: the main thread's context is the expensive, long-lived one. If it edits code itself,
every diff and test log stays in it and is re-sent on every later request; dispatched
subagents (quick-fix, coder, hard-problem) start cold, do the work, and return a few lines.
This hook turns that habit into a rule the main thread cannot forget.

pretool: a call carrying `agent_id` (made inside a subagent) is allowed. A main-thread edit
of a file under a PROTECTED directory (see CONFIG) is denied unless unlocked by
  (a) a tracking-DB run for this session with outcome fail/partial (OPTIONAL: needs a
      SQLite file with a table runs(session_id, outcome); with no DB this unlock is
      simply never taken), or
  (b) the override marker state/orchestrator-override/<session_id> (the user said "do it
      yourself"; the prompt mode creates it).
The first allowed-by-unlock edit per session per reason is appended to
tracking/orchestrator-overrides-<host>.log. Anything else (memory, ~/.claude, scratchpad,
deliverables, ...) is main-thread work and is allowed. Any unexpected exception fails OPEN
and is logged to tracking/hook_errors-<host>.log: a broken hook must not brick the session.

Test overrides (environment): ORCH_DB, ORCH_STATE_DIR, ORCH_LOG_DIR, TRACK_HOST.
"""
import datetime
import json
import os
import re
import socket
import sqlite3
import sys
import traceback

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")


def _clean_host(name):
    # Same rule as scripts/track.py.
    return re.sub(r"[^a-z0-9-]", "-", name.split(".")[0].lower())


HOST = _clean_host(os.environ.get("TRACK_HOST") or socket.gethostname())
LOG_DIR = os.environ.get("ORCH_LOG_DIR") or os.path.join(CLAUDE, "tracking")
STATE_DIR = os.environ.get("ORCH_STATE_DIR") or os.path.join(CLAUDE, "state", "orchestrator-override")
DB_PATH = os.environ.get("ORCH_DB") or os.path.join(CLAUDE, "tracking", "agents-" + HOST + ".db")

# =============================== CONFIG ===============================================
# Directories under ~/source whose files the main thread may not edit directly. Anything
# else (memory, ~/.claude, scratchpads, docs) stays main-thread work.
PROTECTED = [os.path.join(HOME, "source", d) for d in ("repos", "tools", "WORK")]
# A staging directory inside a protected tree that holds working notes, not code.
STAGING_DIR_RE = r"/source/work/(.+/)?_work/"
# ======================================================================================

OVERRIDE_PHRASES = ("do it yourself", "do it directly", "you do it", "edit it yourself",
                    "fix it yourself", "don't delegate", "do not delegate", "no subagent",
                    "no agent")

DENY_TEXT = ("Main thread is orchestrator-only for code (standing rule). Dispatch this "
             "edit of {f}: trivial (typo/rename/one-liner) -> quick-fix agent; specified "
             "feature/fix/tests -> coder; resisted two attempts or hard design -> hard-problem. "
             "Unlocks: a dispatched agent recorded fail/partial via track.py outcome in this "
             "session, or the user says 'do it yourself'.")


def norm(path, cwd=None):
    """Lowercase, forward-slash, drive-letter form of a path, for prefix comparison."""
    p = str(path).strip().replace("\\", "/")
    if p == "~" or p.startswith("~/"):
        p = HOME.replace("\\", "/") + p[1:]
    m = re.match(r"^/([a-zA-Z])(/|$)", p)          # Git-Bash /c/Users/...
    if m:
        p = m.group(1) + ":" + p[2:]
    if not re.match(r"^[a-zA-Z]:", p) and not p.startswith("//") and cwd:
        p = str(cwd).replace("\\", "/") + "/" + p
    p = os.path.normpath(p).replace("\\", "/")
    return p.lower()


def protected(path, cwd=None):
    p = norm(path, cwd)
    # A staging dir inside a protected tree holds working notes, not code: main-thread work.
    if re.search(STAGING_DIR_RE, p):
        return False
    return any(p.startswith(norm(root) + "/") for root in PROTECTED)


def safe_sid(sid):
    return re.sub(r"[^\w.-]", "_", str(sid))


def marker_path(sid):
    return os.path.join(STATE_DIR, safe_sid(sid))


def db_unlocked(sid):
    if not sid or not os.path.exists(DB_PATH):
        return False
    uri = "file:" + os.path.abspath(DB_PATH).replace("\\", "/") + "?mode=ro"
    db = sqlite3.connect(uri, uri=True, timeout=2)
    try:
        row = db.execute("SELECT 1 FROM runs WHERE session_id = ? AND outcome IN ('fail','partial') "
                         "LIMIT 1", (sid,)).fetchone()
        return row is not None
    finally:
        db.close()


def log_override(sid, reason, target):
    """Append one line per (session, reason); later edits for the same pair add nothing."""
    os.makedirs(LOG_DIR, exist_ok=True)
    path = os.path.join(LOG_DIR, "orchestrator-overrides-" + HOST + ".log")
    needle = "\t" + str(sid) + "\t" + reason + "\t"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            if any(needle in line for line in f):
                return
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{sid}\t{reason}\t{target}\n")


def log_error():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(os.path.join(LOG_DIR, "hook_errors-" + HOST + ".log"), "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} orchestrator-only "
                    f"{' '.join(sys.argv[1:])}\n{traceback.format_exc()}\n")
    except Exception:
        pass


def pretool(data):
    if data.get("agent_id"):
        return
    ti = data.get("tool_input") or {}
    target = ti.get("file_path") or ti.get("notebook_path")
    if not target or not protected(target, data.get("cwd")):
        return
    sid = data.get("session_id") or ""
    reason = None
    if db_unlocked(sid):
        reason = "tracking-fail-partial"
    elif sid and os.path.exists(marker_path(sid)):
        reason = "override-marker"
    if reason:
        log_override(sid, reason, target)
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": DENY_TEXT.format(f=target)}}))


def prompt(data):
    text = str(data.get("prompt") or "").lower().replace("’", "'")
    sid = data.get("session_id")
    if sid and any(p in text for p in OVERRIDE_PHRASES):
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(marker_path(sid), "a", encoding="utf-8"):
            pass


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("stdin JSON is not an object")
        if mode == "pretool":
            pretool(data)
        elif mode == "prompt":
            prompt(data)
    except Exception:
        log_error()
    sys.exit(0)


if __name__ == "__main__":
    main()
