"""Work content goes to Anthropic models only. No exceptions, no override.

Content from your employer or a client (the "work" systems) must never reach a
third-party AI: Codex / ChatGPT, Gemini, opencode or OpenRouter models, or any other
hosted model whose free tier may log or train on what it is sent. Claude models (main
thread, subagents) are the only ones allowed to see work content. This hook enforces
that. Edit the CONFIG section below (and work_markers.py) for your own employer.

Two halves, one script, wired to PreToolUse AND PostToolUse on every tool:

  TAINT  Two tiers (a single output scan alone tainted about half of all sessions,
         nearly all of them unrelated to work, hence the split).
         HARD -> <sid>.taint, for the rest of the session: the work MCPs (WORK_MCP);
         any tool input naming a path under the work checkout (except a Write/Edit INTO
         ~/.claude, whose files name it to describe the rules, or into a GUARD_CONFIGS
         file where it appears only in the deny-list); a browser/fetch to a work host.
         SUSPECT -> <sid>.suspect: tool OUTPUT that carries a strong work identifier
         as text. Image blocks and base64 runs are not scanned (output_text); output
         from Claude's own config (~/.claude) and from the NOISY tools is exempt. Each
         new hit drops any earlier clearance.
         Every first hit is announced to the user as a systemMessage.

  GATE   Any route to a third-party AI is DENIED when the session is hard-tainted,
         or when the request itself (the command line, or a task / request file it
         names) carries a work marker. A SUSPECT session not yet cleared gets a
         permission prompt instead (`ask`): the user decides. The egress call's
         PostToolUse firing means they approved, and writes <sid>.cleared. Where an
         `ask` would not reach them (ASK_PROMPTS false for the session's permission
         mode) the gate denies and names the terminal command that clears it.

  CLI    `python block-work-to-third-party.py status|clear|taint <session_id>`.
         `clear` drops a suspect flag, never a hard taint, and the hook refuses to
         let Claude run it: only the user clears their own guard.

Fails open on its own bugs (a broken hook must not wedge every session); errors go
to ~/.claude/state/work-taint/errors.log.
"""
import json
import os
import re
import sys
import time

STATE = os.path.join(os.path.expanduser("~"), ".claude", "state", "work-taint")
CLAUDE_DIR = re.compile(r"[\\/]\.claude([\\/]|$)", re.I)

# The markers (WORK_PATH, STRONG, WORK, WORK_WORDS) live in work_markers.py beside this
# file, shared with tools that must withhold work content before it leaves the box.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from work_markers import WORK_PATH, STRONG, WORK, WORK_WORDS  # noqa: E402
from shell_vars import parse  # noqa: E402

# =============================== CONFIG ===============================================
# Everything employer-specific. Placeholders: replace with your own.
#   WORK_MCP    MCP tool-name prefixes that talk to work systems (tracker, mail, wiki).
#               Calling any of them hard-taints the session.
#   WORK_HOSTS  hostnames that mark a browser / fetch call as touching a work system.
#   EGRESS_*    the routes to a third-party AI: CLIs, hosts, helper scripts, MCP tools.
WORK_MCP = ("mcp__worktracker__", "mcp__workmail__", "mcp__workwiki__")
WORK_HOSTS = re.compile(
    r"work\.example\.com|tracker\.example\.net|mail\.example\.com|"
    r"wiki\.example\.com|examplecorp", re.I)
# ======================================================================================
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
BROWSERY = re.compile(r"WebFetch|claude-in-chrome|Claude_Browser|playwright|computer-use", re.I)

# Routes to third-party AI, judged on the commands shell_vars.parse() finds -- with
# variables substituted, quotes stripped, and `$(...)` / `bash -c` bodies included.
# Invocations only: compiling, diffing or committing a helper script is not egress, and
# 'codex' in a quoted argument (a process-name filter; a commit message) is not a command.
EGRESS_CLIS = {"codex", "gemini", "opencode"}
EGRESS_HOSTS = re.compile(
    r"openrouter\.ai|api\.openai\.com|generativelanguage\.googleapis\.com", re.I)
# Your own helper scripts that forward text to a hosted model, as (script name, subcommands
# that send; empty tuple = any subcommand sends). Placeholders.
EGRESS_SCRIPTS = {"delegate.py": ("run", "followup"), "llm_helper.py": ()}
# Commands whose arguments are only text -- a host named there goes nowhere.
TEXT_ONLY = {"git", "echo", "printf", "grep", "rg", "findstr", "select-string",
             "write-output", "write-host", "gh", "glab"}


def egress_command(raw, ps):
    """True when the line invokes a third-party AI."""
    for c in parse(raw, ps=ps):
        if c.name in EGRESS_CLIS:
            return True
        if c.name.startswith("python"):
            for k, w in enumerate(c.args):
                nxt = c.args[k + 1:k + 2]
                for script, verbs in EGRESS_SCRIPTS.items():
                    if w.endswith(script) and nxt and (not verbs or nxt[0] in verbs):
                        return True
        if c.name not in TEXT_ONLY and EGRESS_HOSTS.search(c.text):
            return True
    return False
EGRESS_TOOL = re.compile(
    # An MCP server that forwards prompts to a hosted app builder (placeholder names).
    r"create_app_from_prompt|update_app_using_prompt|"
    # An MCP server of your own that sends text to a hosted model, except its
    # help / restart tools (placeholder name).
    r"mcp__llm_helper__(?!(help|restart_self)$)|"
    # Tracker tools that send issue text to a hosted model when a check is switched on.
    r"mcp__tracker__issue_(create|update|ready|ask)$", re.I)


# Whether a PreToolUse `ask` actually puts a prompt in front of the user, per permission
# mode. Where it does not (the call would just run), the gate denies instead: an `ask`
# that auto-approves would write .cleared with nobody having decided anything.
ASK_PROMPTS = {"default": True, "acceptEdits": True, "plan": True, "auto": True,
               "bypassPermissions": True, "dontAsk": False}
# bypassPermissions was probed: the hook returned `ask` and the prompt reached the user.
# dontAsk stays False: by name, it never prompts.

# Tools whose output is the harness's own bookkeeping or an echo of what Claude just
# wrote, never new work data: session lists name other sessions by title, an
# Edit/Write response echoes the edit.
NOISY = re.compile(r"^(ListAgents|SendMessage|ReadNotifications|Edit|Write|MultiEdit|"
                   r"NotebookEdit|TodoWrite|mcp__ccd_\w+)$")

# A line that only reads git's own config: a global user.email can be a work address.
GIT_CONFIG = re.compile(r"^\s*(git(\s+-C\s+\S+)?|bash\s+\S*git-in\.sh\s+\S+)\s+config\b[^;&|]*$")

_notes = []


def note(msg):
    """Tell the user (a systemMessage, shown to them, not to the model)."""
    _notes.append(msg)


def emit(decision, reason):
    out = {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason}}
    if _notes:
        out["systemMessage"] = "\n".join(_notes)
    print(json.dumps(out))
    sys.exit(0)


def flush_notes():
    if _notes:
        print(json.dumps({"systemMessage": "\n".join(_notes)}))


def state_path(sid, ext):
    return os.path.join(STATE, re.sub(r"[^\w.-]", "_", sid or "unknown") + ext)


def taint_path(sid):
    return state_path(sid, ".taint")


def mask(text):
    """Every work marker in `text` masked to its first and last character. A reason or
    deny message that spells the marker out gets echoed back as tool output (a
    subagent's report quoting the deny) and taints the session all over again."""
    return WORK.sub(lambda m: m.group(0)[0] + "*" * (len(m.group(0)) - 2) + m.group(0)[-1],
                    text)


def _stamp(reason):
    return f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {mask(reason)}\n"


def taint(sid, reason):
    p = taint_path(sid)
    if os.path.exists(p):
        return
    os.makedirs(STATE, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(_stamp(reason))
    note(f"work-taint: session TAINTED ({mask(reason)}). Third-party AI routes are "
         "closed for the rest of this session.")


def suspect(sid, reason):
    """A soft hit: logged, announced on the first one since the last clearance."""
    if os.path.exists(taint_path(sid)):
        return
    os.makedirs(STATE, exist_ok=True)
    cleared = state_path(sid, ".cleared")
    fresh = os.path.exists(cleared) or not os.path.exists(state_path(sid, ".suspect"))
    if os.path.exists(cleared):
        os.replace(cleared, state_path(sid, ".cleared.old"))
    with open(state_path(sid, ".suspect"), "a", encoding="utf-8") as f:
        f.write(_stamp(reason))
    if fresh:
        note(f"work-taint: possible work content ({mask(reason)}). Nothing is blocked; "
             "the next third-party AI call will ask you first.")


def _first_line(p):
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return mask(f.readline().strip())  # masked again: files written before mask()


def tainted(sid):
    return _first_line(taint_path(sid))


def suspected(sid):
    """The latest uncleared suspect hit, or None."""
    p = state_path(sid, ".suspect")
    if not os.path.exists(p) or os.path.exists(state_path(sid, ".cleared")):
        return None
    with open(p, encoding="utf-8") as f:
        lines = [x.strip() for x in f if x.strip()]
    return mask(lines[-1]) if lines else None


def clear(sid, how):
    os.makedirs(STATE, exist_ok=True)
    with open(state_path(sid, ".cleared"), "w", encoding="utf-8") as f:
        f.write(_stamp(how))


DATA_EXT = r"\.(md|txt|json|jsonl|diff|patch|csv|html|eml)"


def referenced_files(cmd):
    """Files named on a command line that could carry a task or request body."""
    # Quoted strings whole (paths with spaces), plus any data-file path run found
    # anywhere, so `$(cat x.md)`, `<x.md` and `--task=x.md` count. A whole-token
    # match missed those: `$(cat x.md)` ends in `)`, not `.md`.
    cands = [q[0] or q[1] for q in re.findall(r"\"([^\"]+)\"|'([^']+)'", cmd)]
    cands += [m.group(0) for m in re.finditer(r"[^\s\"'()<>;|&=`]+" + DATA_EXT + r"(?![\w.])", cmd, re.I)]
    out = []
    for t in dict.fromkeys(cands):
        # Data files only: the helper scripts themselves name the work path in order
        # to refuse it, and must not count as payload.
        if re.search(DATA_EXT + r"$", t, re.I) \
                and not CLAUDE_DIR.search(t) and not re.search(r"source[\\/]+tools", t, re.I):
            p = t
            m = re.match(r"^/([a-zA-Z])/(.*)", p)  # Git Bash /c/... -> C:/...
            if m:
                p = f"{m.group(1)}:/{m.group(2)}"
            if os.path.isfile(p) and os.path.getsize(p) < 4_000_000:
                out.append(p)
    return out


# Guard configs outside ~/.claude that name the work path in a deny-list, in order to
# keep work content OUT (an Edit adding a key to such a config carries the existing
# deny entry in its old_string and would taint the session).
# Target file -> the JSON key whose array is a deny-list. Only that array is exempt.
# Example (placeholder): a config for a tool of your own that refuses work paths.
GUARD_CONFIGS = {
    os.path.normcase(os.path.join(os.path.expanduser("~"), ".config", "llm-helper", "config.json")):
        "deny_roots",
}


def _strings(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, dict):
        for x in v.values():
            yield from _strings(x)
    elif isinstance(v, list):
        for x in v:
            yield from _strings(x)


def guard_config_deny_only(tool, ti):
    """True when a Write/Edit to a known guard config names the work path ONLY inside
    that config's deny-list array, and nothing else in the edit is a work marker."""
    if tool not in WRITE_TOOLS:
        return False
    target = str(ti.get("file_path") or ti.get("notebook_path") or "")
    key = GUARD_CONFIGS.get(os.path.normcase(os.path.normpath(target))) if target else None
    if not key:
        return False
    # The array whole, or cut off by the end of an Edit fragment.
    deny = re.compile(r'"' + re.escape(key) + r'"\s*:\s*\[[^\]]*(\]|$)')
    rest = "\n".join(deny.sub("", s) for k, v in ti.items()
                     if k not in ("file_path", "notebook_path") for s in _strings(v))
    return not (WORK_PATH.search(rest) or WORK.search(rest) or WORK_WORDS.search(rest))


# Binary payloads in tool output are not text. A Read of a PNG returns it as base64, and a
# run of it can contain a marker by chance, which would taint the session for nothing.
# Image/document blocks are dropped whole; any other long
# base64 run (a data: URI, an attachment body) is cut out before matching. Real text
# breaks such a run with a space, '.', '@' or '-' long before 100 characters.
BINARY_BLOCK = {"image", "document"}
B64_RUN = re.compile(r"[A-Za-z0-9+/]{100,}={0,2}")


def _drop_binary(v):
    if isinstance(v, dict):
        src = v.get("source")
        if v.get("type") in BINARY_BLOCK or (isinstance(src, dict) and src.get("type") == "base64"):
            return None
        return {k: _drop_binary(x) for k, x in v.items() if k != "base64"}
    if isinstance(v, list):
        return [_drop_binary(x) for x in v]
    return v


def output_text(resp):
    """Tool output as text for the STRONG scan, with binary payloads removed."""
    text = resp if isinstance(resp, str) else json.dumps(_drop_binary(resp))
    return B64_RUN.sub(" ", text or "")


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    event = d.get("hook_event_name") or "PreToolUse"
    tool = d.get("tool_name") or ""
    ti = d.get("tool_input") or {}
    sid = d.get("session_id") or ""
    tin = json.dumps(ti) if not isinstance(ti, str) else ti

    # ---- TAINT ------------------------------------------------------------
    if tool.startswith(WORK_MCP):
        taint(sid, f"work MCP tool {tool}")
    elif WORK_PATH.search(tin) and not (
            # Writes into Claude's own config (memory, skills, hooks, handoffs) name the
            # work path in order to describe the rule; the mirror of the output exemption
            # below. Writing a file is not egress.
            tool in WRITE_TOOLS and CLAUDE_DIR.search(str(ti.get("file_path")
                                                          or ti.get("notebook_path") or ""))
            or guard_config_deny_only(tool, ti)):
        taint(sid, f"{tool} input names a path under the work checkout")
    elif BROWSERY.search(tool) and WORK_HOSTS.search(tin):
        taint(sid, f"{tool} to a work host")
    if event == "PostToolUse":
        if is_egress(tool, ti) and suspected(sid) and not tainted(sid):
            # The gate asked and the call ran: the user approved it.
            clear(sid, f"approved at the prompt for {tool}")
        if tool != "Skill" and not NOISY.match(tool) and not CLAUDE_DIR.search(tin) \
                and not (tool in ("Bash", "PowerShell")
                         and GIT_CONFIG.match(str(ti.get("command") or ""))):
            m = STRONG.search(output_text(d.get("tool_response")))
            if m:
                suspect(sid, f"{tool} output contained work identifier '{m.group(0)}'")
        flush_notes()
        return

    # ---- GATE (PreToolUse only) --------------------------------------------
    if tool in ("Bash", "PowerShell") and SELF_CLEAR.search(str(ti.get("command") or "")):
        emit("deny",
             "Blocked: clearing the work-taint state is the user's call, made "
             "in their own terminal, never a Claude tool call. Ask them to run it.")
    egress, hay = payload(tool, ti)
    if not egress:
        flush_notes()
        return

    why = tainted(sid)
    if why:
        emit("deny",
             "Blocked: this session has touched work (employer / client) content -- "
             f"first contact: {why}. Work content goes to Anthropic models only, so every "
             "third-party AI route (Codex, Gemini, opencode/OpenRouter, your own helper "
             "scripts and MCP servers) is closed for the rest of this session. "
             "Use a Claude subagent (coder, doc-analyst, researcher, drafter, "
             "hard-problem) instead, or start a NEW session for non-work third-party "
             "work. There is no override.")
    m = WORK.search(hay) or WORK_WORDS.search(hay)
    if m:
        emit("deny",
             f"Blocked: this request to a third-party AI carries work content (matched "
             f"'{mask(m.group(0))}'). Work content goes to Anthropic models "
             "only -- use a Claude subagent instead. There is no override.")
    hit = suspected(sid)
    if hit:
        mode = d.get("permission_mode") or "default"
        if ASK_PROMPTS.get(mode, False):
            emit("ask",
                 f"work-taint: this session MAY have seen work content ({hit}). The "
                 f"request itself carries no work marker. Allow {tool} to reach a "
                 "third-party AI? Approving clears the flag until the next hit; denying "
                 "keeps the route closed.")
        emit("deny",
             f"Blocked pending the user: this session may have seen work content ({hit}), "
             f"and in '{mode}' mode a permission prompt would not reach them. If it was "
             "not work, they clear it from their own terminal with: python "
             "~/.claude/hooks/block-work-to-third-party.py clear " + sid + " -- if it "
             "was, they run `... taint " + sid + "`. Ask them; do not route around it.")
    flush_notes()


# Claude may TAINT (the safe direction: the user says "yes, taint it"), never clear, and
# never touch the state files by hand.
SELF_CLEAR = re.compile(r"block-work-to-third-party\.py\W+clear\b"
                        r"|work-taint[\\/][^\s\"']*\.(suspect|cleared|taint)\b", re.I)


def payload(tool, ti):
    """(is this a route to a third-party AI, the text it would carry)."""
    if tool in ("Bash", "PowerShell"):
        raw = str(ti.get("command") or "")
        ps = tool == "PowerShell"
        if not egress_command(raw, ps):
            return False, ""
        # The payload check reads the raw line AND the parsed one (`T=task.md;
        # ... $T` substituted), so nothing either form shows is lost.
        hay = raw + "\n" + "; ".join(c.text for c in parse(raw, ps=ps))
        for p in referenced_files(hay):
            with open(p, encoding="utf-8", errors="replace") as f:
                hay += "\n" + f.read()
        return True, hay
    if EGRESS_TOOL.search(tool):
        return True, json.dumps(ti)
    return False, ""


def is_egress(tool, ti):
    if tool in ("Bash", "PowerShell"):
        return egress_command(str(ti.get("command") or ""), tool == "PowerShell")
    return bool(EGRESS_TOOL.search(tool))


def cli(argv):
    """The user's terminal: status / clear / taint for one session."""
    if len(argv) != 2 or argv[0] not in ("status", "clear", "taint"):
        print("usage: block-work-to-third-party.py status|clear|taint <session_id>")
        return 2
    verb, sid = argv
    if verb == "clear":
        if tainted(sid):
            print(f"HARD taint, not clearable: {tainted(sid)}")
            return 1
        clear(sid, "cleared by the user from the terminal")
    elif verb == "taint":
        taint(sid, "tainted by the user from the terminal")
        _notes.clear()
    print(f"taint:   {tainted(sid) or '-'}")
    print(f"suspect: {_first_line(state_path(sid, '.suspect')) or '-'}"
          f"{'  (pending)' if suspected(sid) else ''}")
    print(f"cleared: {_first_line(state_path(sid, '.cleared')) or '-'}")
    return 0


if len(sys.argv) > 1:
    sys.exit(cli(sys.argv[1:]))

try:
    main()
except SystemExit:
    raise
except Exception as e:  # never wedge a session on a hook bug
    try:
        os.makedirs(STATE, exist_ok=True)
        with open(os.path.join(STATE, "errors.log"), "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {type(e).__name__}: {e}\n")
    except Exception:
        pass
sys.exit(0)
