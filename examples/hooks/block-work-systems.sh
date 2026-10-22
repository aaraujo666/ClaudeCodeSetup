#!/usr/bin/env bash
# PreToolUse guard: work systems are never touched without an explicit OK.
#
# Enforces the highest-priority rule in a consultant's setup: "never touch work
# systems without an explicit OK, every time". Work means your employer's or a
# client's systems (tracker, mail, source tree). A memory line only binds sessions that
# read it; this binds every session.
#
# Two decisions, deliberately different:
#
#   deny  The work PRODUCTION host (WORK_PROD_RE). Absolute: no reads, no writes, no
#         exceptions. The named trap is that URLs pasted from tickets point at the
#         production host while the work is meant to happen on the DEV one, so the
#         regex matches production only and deliberately NOT the dev host.
#
#   ask   Tracker writes, file writes under the work checkout, mailbox mutations.
#         These are real work you do, so they must stay possible -- "ask" IS the
#         explicit OK, collected every time, which is what the rule says.
#         Exception: any _work directory under the work checkout is allowed silently --
#         the staging area for intermediate files.
#
# Reads are untouched throughout. You work in these systems daily and your allowlist
# already covers the read side; gating reads would break the tools rather than protect
# anything.
#
# Note this is a drift guard, not a security boundary.

# =============================== CONFIG ===============================================
# Every employer-specific value lives here. Placeholders: replace with your own.
#
# WORK_PROD_RE        Regex for the PRODUCTION host. `work-prod(?!-dev)` style lookahead
#                     keeps a sibling dev host allowed. Matched case-insensitively.
WORK_PROD_RE='work-prod\.example\.com'
# WORK_DEV_HOST       The host work should happen on; named in the deny message.
WORK_DEV_HOST='work-dev.example.com'
# WORK_TRACKER_PREFIX MCP prefix of the work tracker (reads open, writes ask).
WORK_TRACKER_PREFIX='mcp__worktracker__'
# WORK_TRACKER_EXTRA  Tracker tools that write but do not end in _write.
WORK_TRACKER_EXTRA='pipelines_run,create_branch,upsert_page,add_attachment'
# WORK_MAIL_PREFIX    MCP prefix of the work mailbox; WORK_MAIL_WRITES are its mutating verbs.
WORK_MAIL_PREFIX='mcp__workmail__'
WORK_MAIL_WRITES='mail_draft,mail_archive,mail_flag,mail_mark_read'
# WORK_DIR_RE         Regex for the work source tree (writes ask); WORK_STAGING_RE for the
#                     normalised-path staging dir inside it (writes allowed).
WORK_DIR_RE='[\\/]source[\\/]WORK([\\/]|$)'
WORK_STAGING_RE='/source/WORK/(.+/)?_work/'
# ======================================================================================

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && (pwd -W 2>/dev/null || pwd))"
export HOOK_DIR WORK_PROD_RE WORK_DEV_HOST WORK_TRACKER_PREFIX WORK_TRACKER_EXTRA \
       WORK_MAIL_PREFIX WORK_MAIL_WRITES WORK_DIR_RE WORK_STAGING_RE
PY=$(command -v python || command -v python3)

payload=$(cat)

printf '%s' "$payload" | "$PY" -c '
import json, sys, re, os

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)

E = os.environ
tool = d.get("tool_name") or ""
ti = d.get("tool_input") or {}
if not isinstance(ti, dict):
    ti = {}


def emit(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason}}))
    sys.exit(0)


# --- 1. Work PRODUCTION host -- absolute deny -------------------------------
PROD = re.compile(E["WORK_PROD_RE"], re.I)

NETWORKY = re.compile(
    r"WebFetch|claude-in-chrome|Claude_Browser|playwright|computer-use|"
    r"navigate|browser_|preview_start", re.I)

if NETWORKY.search(tool):
    # A browser tool can carry the host in a url, a typed string, or a script,
    # so the whole input is in scope.
    hay = json.dumps(ti)
else:
    # Elsewhere only the action-carrying fields count, so that writing docs
    # that merely mention the prod host is not blocked.
    hay = " ".join(str(ti.get(k) or "") for k in ("url", "command"))

if PROD.search(hay):
    emit("deny",
         "Blocked: " + E["WORK_PROD_RE"].replace("\\", "") + " is the work PRODUCTION "
         "system, which is off limits for every action including reads -- no exceptions. "
         "All work goes to DEV: swap the host to " + E["WORK_DEV_HOST"] + " and retry. "
         "URLs pasted out of tickets almost always point at the production host, which "
         "is exactly the mistake this catches.")

# --- 2. Work tracker writes -- ask -----------------------------------------
TRACKER = E["WORK_TRACKER_PREFIX"]
EXTRA = set(x for x in E["WORK_TRACKER_EXTRA"].split(",") if x)

if TRACKER and tool.startswith(TRACKER):
    name = tool[len(TRACKER):]
    if name.endswith("_write") or name in EXTRA:
        emit("ask",
             "The work tracker is an employer/client system and this call WRITES "
             "to it (" + name + "). The standing rule is an explicit OK before "
             "acting on work systems, every time -- confirm to proceed. Tracker reads "
             "are not gated.")

# --- 3. File writes under the work checkout -- ask -------------------------
if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
    p = str(ti.get("file_path") or ti.get("notebook_path") or "")
    # A _work directory anywhere in the tree is the staging area for intermediate
    # files -- notes and drafts that feed a document -- and is allowed without a
    # prompt. Normalised first so _work/../x does not slip out of it. The content
    # still stays inside the work tree.
    np = os.path.normpath(p.replace("\\", "/")).replace("\\", "/")
    if re.search(E["WORK_STAGING_RE"], np, re.I):
        emit("allow",
             "Work-tree _work staging directory: writes allowed without a prompt.")
    if re.search(E["WORK_DIR_RE"], p, re.I):
        emit("ask",
             "This writes to employer/client work under the work checkout, which "
             "needs an explicit OK first, every time -- confirm to proceed. "
             "Reading that tree is not gated. Keep the content in that tree: it "
             "must never be copied into your personal repos or a scratch folder.")

# --- 4. Mailbox mutations -- ask -------------------------------------------
# Belt and braces: the mail MCP should already gate writes behind a flag that is off by
# default. This holds the line on the day that flag is turned on.
MAIL = E["WORK_MAIL_PREFIX"]
MAIL_WRITES = set(x for x in E["WORK_MAIL_WRITES"].split(",") if x)

if MAIL and tool.startswith(MAIL) and tool.split("__")[-1] in MAIL_WRITES:
    emit("ask",
         "This mutates the work mailbox (" + tool.split("__")[-1] + "), a "
         "work system -- explicit OK required every time. Confirm to proceed. "
         "Reads are not gated.")
' 2>/dev/null

exit 0
