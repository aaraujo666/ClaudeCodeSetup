"""Regression suite for the example PreToolUse guard hooks.

Feeds each hook a fake tool call as JSON on stdin, exactly as Claude Code does, and
asserts the decision it prints: allow (no output), ask, or deny. Covers
block-file-delete.sh, block-cd-git.sh, block-heredoc.sh, block-unbounded-find.sh,
block-long-sleep.sh, block-work-systems.sh, block-work-to-third-party.py and
orchestrator-only.py, including the cases shell_vars.parse() exists for: variables set
earlier in the line (`W=...; rm $W/f`) and words inside a quoted argument
(`git commit -m "find x -delete"`) that are not commands.

    python -m pytest examples/hooks/tests -q

Every hook runs with HOME / USERPROFILE pointed at a temp dir, so the taint state and
override markers the hooks write never touch your real ~/.claude.
"""
import json
import os
import shutil
import subprocess
import sys

import pytest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)
from work_markers import WORK_PATH_NAME  # noqa: E402  (the CONFIG placeholder)

_GIT_BASH = r"C:\Program Files\Git\bin\bash.exe"
BASH = _GIT_BASH if os.path.exists(_GIT_BASH) else shutil.which("bash")

# A work identifier matching the placeholder CONFIG in work_markers.py.
WORK_HOST = "tracker.example.net"


@pytest.fixture
def home(tmp_path):
    return tmp_path


def run_hook(hook, payload, home, extra_args=(), extra_env=None):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
    env.update(extra_env or {})
    argv = ([sys.executable] if hook.endswith(".py") else [BASH]) + [os.path.join(HOOKS, hook)]
    r = subprocess.run(argv + list(extra_args), input=json.dumps(payload), capture_output=True,
                       text=True, encoding="utf-8", env=env, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def decision(out):
    if not out:
        return "allow"
    # A bare {"systemMessage": ...} (a notice to the user) is not a decision: allow.
    return json.loads(out).get("hookSpecificOutput", {}).get("permissionDecision", "allow")


def bash_call(command, tool="Bash", cwd="/work", sid="clean-session"):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "session_id": sid,
            "cwd": cwd, "tool_input": {"command": command}}


# --------------------------------------------------------------------------- shell guards

DEL, CDG, HD, FIND, SLP = ("block-file-delete.sh", "block-cd-git.sh", "block-heredoc.sh",
                           "block-unbounded-find.sh", "block-long-sleep.sh")
WT = "/home/u/source/worktrees/x"
REPO = "/home/u/source/repos/foo"

SHELL_CASES = [
    # --- delete: archive, never delete; worktrees, temp and caches exempt ---
    (DEL, "plain rm of a real file", f"rm {REPO}/a.ts", "ask"),
    (DEL, "rm -rf", f"rm -rf {REPO}", "deny"),
    (DEL, "rm with a glob", f"rm {REPO}/*.ts", "deny"),
    (DEL, "rm in /tmp", "rm /tmp/x/a.txt", "allow"),
    (DEL, "rm in a worktree", f"rm {WT}/a.ts", "allow"),
    (DEL, "rm -rf in node_modules", f"rm -rf {REPO}/node_modules", "allow"),
    (DEL, "variable to a worktree", f"W={WT}; rm $W/a.ts", "allow"),
    (DEL, "variable to a real repo", f"W={REPO}; rm $W/a.ts", "ask"),
    (DEL, "reassigned away from worktree", f"W={WT}; W={REPO}; rm $W/a.ts", "ask"),
    (DEL, "rm -rf via variable", f"W={REPO}; rm -rf $W", "deny"),
    (DEL, "cd into worktree then relative rm", f"cd {WT} && rm src/x.tmp.ts", "allow"),
    (DEL, "git rm is versioned", "git rm src/a.ts", "allow"),
    (DEL, "find -delete", f"find {REPO} -name '*.log' -delete", "deny"),
    (DEL, "find -exec rm", f"find {REPO} -name x -exec rm {{}} \\;", "deny"),
    (DEL, "find -delete inside a worktree", f"find {WT} -name x -delete", "allow"),
    (DEL, "git clean -f", f"git -C {REPO} clean -fd", "deny"),
    (DEL, "git clean -n is a dry run", f"git -C {REPO} clean -n", "allow"),
    (DEL, "grep for rm", 'grep "rm -rf" notes.txt', "allow"),
    (DEL, "words in a commit message", 'git commit -m "file-delete guard: find -delete"', "allow"),
    (DEL, "ps: Remove-Item -Recurse", "Remove-Item -Recurse C:\\data", "deny", "PowerShell"),
    # --- cd + git ---
    (CDG, "cd then git", f"cd {REPO} && git status", "deny"),
    (CDG, "cd then make then git", f"cd {REPO} && make && git commit -m x", "deny"),
    (CDG, "git clone then cd is fine", "git clone x && cd x", "allow"),
    (CDG, "git -C needs no cd", f"git -C {REPO} status", "allow"),
    (CDG, "ls .git after cd", f"cd {REPO} && ls .git", "allow"),
    (CDG, "git-in.sh wrapper", f"bash ~/.claude/scripts/git-in.sh {REPO} status", "allow"),
    (CDG, "ps: Set-Location then git", f"Set-Location {REPO}; git status", "deny", "PowerShell"),
    # --- heredocs ---
    (HD, "cat heredoc", "cat > f.txt <<EOF\nhello\nEOF", "deny"),
    (HD, "quoted heredoc", "cat > f.txt <<'EOF'\nhello\nEOF", "deny"),
    (HD, "<<- heredoc", "cat <<-EOF\nx\nEOF", "deny"),
    (HD, "here-string <<< is fine", "grep a <<< abc", "allow"),
    (HD, "shift on digits", "echo $((1 << 2))", "allow"),
    (HD, "<<EOF inside a quoted message", 'git commit -m "no <<EOF here"', "allow"),
    (HD, "ps here-string", "$x = @'\nabc\n'@", "deny", "PowerShell"),
    (HD, "plain command", "ls -la", "allow"),
    # --- unbounded find ---
    (FIND, "find from /", "find / -name x", "deny"),
    (FIND, "find from ~", "find ~ -name x", "deny"),
    (FIND, "find from $HOME", "find $HOME -name x", "deny"),
    (FIND, "find from a drive root", "find /c -name x", "deny"),
    (FIND, "root via variable", "R=/; find $R -name x", "deny"),
    (FIND, "bounded by -maxdepth", "find / -maxdepth 2 -name x", "allow"),
    (FIND, "real subdirectory", f"find {REPO} -name x", "allow"),
    (FIND, "maxdepth on a different find", "find / -name x; find . -maxdepth 1", "deny"),
    (FIND, "word find in a message", 'git commit -m "find / is slow"', "allow"),
    # --- long sleep ---
    (SLP, "sleep 590 then grep", "sleep 590; grep done build.log", "deny"),
    (SLP, "sleep 5m", "sleep 5m", "deny"),
    (SLP, "sleep 31", "sleep 31", "deny"),
    (SLP, "sleep via variable set earlier in the line", "N=300; sleep $N", "deny"),
    (SLP, "sleep via unresolved variable", "sleep $N", "allow"),
    (SLP, "sleep 5", "sleep 5", "allow"),
    (SLP, "short sleep in a poll loop", "until grep -q ok x.log; do sleep 5; done", "allow"),
    (SLP, "Start-Sleep 120", "Start-Sleep -Seconds 120", "deny", "PowerShell"),
    (SLP, "Start-Sleep 500 ms", "Start-Sleep -Milliseconds 500", "allow", "PowerShell"),
]


@pytest.mark.parametrize("case", SHELL_CASES, ids=[f"{c[0]}:{c[1]}" for c in SHELL_CASES])
def test_shell_guard(case, home):
    hook, _name, cmd, want = case[:4]
    tool = case[4] if len(case) > 4 else "Bash"
    assert decision(run_hook(hook, bash_call(cmd, tool), home)) == want


def test_long_sleep_in_background_is_allowed(home):
    payload = bash_call("sleep 590")
    payload["tool_input"]["run_in_background"] = True
    assert decision(run_hook(SLP, payload, home)) == "allow"


def test_deny_messages_name_the_way_out(home):
    out = run_hook(DEL, bash_call(f"rm -rf {REPO}"), home)
    assert "_archive" in out
    out = run_hook(CDG, bash_call(f"cd {REPO} && git status"), home)
    assert "git-in.sh" in out
    out = run_hook(HD, bash_call("cat <<EOF\nx\nEOF"), home)
    assert "Write tool" in out
    out = run_hook(SLP, bash_call("sleep 590"), home)
    assert "completion notification" in out
    out = run_hook(FIND, bash_call("find / -name x"), home)
    assert "-maxdepth" in out


def test_garbage_stdin_fails_open(home):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
    for hook in (DEL, CDG, HD, FIND, SLP, "block-work-systems.sh"):
        r = subprocess.run([BASH, os.path.join(HOOKS, hook)], input="not json", capture_output=True,
                           text=True, env=env, timeout=60)
        assert r.returncode == 0 and r.stdout.strip() == ""


# --------------------------------------------------------------------------- work systems

WS = "block-work-systems.sh"


def tool_call(tool, **ti):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "session_id": "s", "tool_input": ti}


WORK_CASES = [
    ("prod host in WebFetch", tool_call("WebFetch", url="https://work-prod.example.com/list"), "deny"),
    ("prod host in a browser script", tool_call("mcp__playwright__browser_evaluate",
                                               function="fetch('https://work-prod.example.com/x')"), "deny"),
    ("prod host in a curl command", tool_call("Bash", command="curl https://work-prod.example.com/x"), "deny"),
    ("dev host is allowed", tool_call("WebFetch", url="https://work-dev.example.com/list"), "allow"),
    ("doc that merely mentions prod", tool_call("Write", file_path="/tmp/n.md",
                                                content="never use work-prod.example.com"), "allow"),
    ("tracker write asks", tool_call("mcp__worktracker__wit_work_item_write", id=1), "ask"),
    ("tracker odd write verb asks", tool_call("mcp__worktracker__pipelines_run", id=1), "ask"),
    ("tracker read is open", tool_call("mcp__worktracker__wit_query", q="x"), "allow"),
    ("write under the work tree asks", tool_call("Write", file_path=f"/home/u/source/{WORK_PATH_NAME}/proj/a.py"), "ask"),
    ("edit under the work tree asks", tool_call("Edit", file_path=f"C:\\Users\\u\\source\\{WORK_PATH_NAME}\\proj\\a.py"), "ask"),
    ("_work staging dir is allowed", tool_call("Write", file_path=f"/home/u/source/{WORK_PATH_NAME}/proj/_work/n.md"), "allow"),
    ("_work escape does not count", tool_call("Write", file_path=f"/home/u/source/{WORK_PATH_NAME}/proj/_work/../a.py"), "ask"),
    ("write elsewhere is open", tool_call("Write", file_path="/home/u/source/repos/foo/a.py"), "allow"),
    ("mail draft asks", tool_call("mcp__workmail__mail_draft", to="x"), "ask"),
    ("mail read is open", tool_call("mcp__workmail__mail_triage"), "allow"),
]


@pytest.mark.parametrize("case", WORK_CASES, ids=[c[0] for c in WORK_CASES])
def test_work_systems(case, home):
    _name, payload, want = case
    out = run_hook(WS, payload, home)
    assert decision(out) == want
    if want == "deny":
        assert "work-dev.example.com" in out


# --------------------------------------------------------------------------- work -> third party

TP = "block-work-to-third-party.py"


def egress(command, sid="tp-session", tool="Bash"):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "session_id": sid,
            "tool_input": {"command": command}}


def test_tp_clean_session_allows_ordinary_egress(home):
    assert decision(run_hook(TP, egress('codex exec "refactor this function"'), home)) == "allow"


def test_tp_request_carrying_a_work_marker_is_denied(home):
    out = run_hook(TP, egress(f'codex exec "summarise the ticket on {WORK_HOST}"'), home)
    assert decision(out) == "deny"
    assert "Anthropic" in out


def test_tp_task_file_carrying_a_work_marker_is_denied(home, tmp_path):
    task = tmp_path / "task.md"
    task.write_text(f"Fix the bug reported at {WORK_HOST}/issue/7", encoding="utf-8")
    assert decision(run_hook(TP, egress(f'codex exec "$(cat {task.as_posix()})"'), home)) == "deny"


def test_tp_clean_task_file_is_allowed(home, tmp_path):
    task = tmp_path / "task.md"
    task.write_text("Rename the helper and add a test.", encoding="utf-8")
    assert decision(run_hook(TP, egress(f'codex exec "$(cat {task.as_posix()})"'), home)) == "allow"


def test_tp_helper_script_counts_as_egress(home):
    cmd = f'python delegate.py run --task "see {WORK_HOST}"'
    assert decision(run_hook(TP, egress(cmd), home)) == "deny"


def test_tp_word_codex_in_a_commit_message_is_not_egress(home):
    assert decision(run_hook(TP, egress(f'git commit -m "codex notes for {WORK_HOST}"'), home)) == "allow"


def test_tp_non_egress_commands_are_allowed(home):
    assert decision(run_hook(TP, egress("ls -la"), home)) == "allow"


def test_tp_hard_taint_closes_every_route(home):
    sid = "tp-tainted"
    assert decision(run_hook(TP, tool_call("mcp__worktracker__wit_query", q="x") | {"session_id": sid}, home)) == "allow"
    assert os.path.exists(os.path.join(str(home), ".claude", "state", "work-taint", sid + ".taint"))
    out = run_hook(TP, egress('codex exec "an innocent prompt"', sid=sid), home)
    assert decision(out) == "deny"
    assert "touched work" in out
    assert "no override" in out.lower()


def test_tp_work_path_in_tool_input_taints(home):
    sid = "tp-path"
    run_hook(TP, tool_call("Read", file_path=f"/home/u/source/{WORK_PATH_NAME}/proj/a.py") | {"session_id": sid}, home)
    assert decision(run_hook(TP, egress('codex exec "x"', sid=sid), home)) == "deny"


def test_tp_work_output_makes_the_session_suspect_and_asks(home):
    sid = "tp-suspect"
    post = {"hook_event_name": "PostToolUse", "tool_name": "Bash", "session_id": sid,
            "tool_input": {"command": "cat notes.txt"},
            "tool_response": f"see https://{WORK_HOST}/ticket/9"}
    run_hook(TP, post, home)
    pre = egress('codex exec "an innocent prompt"', sid=sid) | {"permission_mode": "default"}
    out = run_hook(TP, pre, home)
    assert decision(out) == "ask"
    # In a mode where a prompt would not reach the user, the gate denies instead.
    pre["permission_mode"] = "dontAsk"
    assert decision(run_hook(TP, pre, home)) == "deny"


def test_tp_base64_noise_in_output_does_not_taint(home):
    sid = "tp-b64"
    blob = "A" * 120 + "tracker.example.net" + "B" * 120
    post = {"hook_event_name": "PostToolUse", "tool_name": "Read", "session_id": sid,
            "tool_input": {"file_path": "/tmp/x.png"}, "tool_response": blob}
    run_hook(TP, post, home)
    assert decision(run_hook(TP, egress('codex exec "x"', sid=sid), home)) == "allow"


def test_tp_claude_cannot_clear_the_guard(home):
    cmd = "python ~/.claude/hooks/block-work-to-third-party.py clear some-session"
    assert decision(run_hook(TP, egress(cmd), home)) == "deny"


def test_tp_deny_message_masks_the_marker(home):
    out = run_hook(TP, egress(f'codex exec "see {WORK_HOST}"'), home)
    assert WORK_HOST not in out


def test_tp_cli_status_and_clear(home):
    sid = "tp-cli"
    post = {"hook_event_name": "PostToolUse", "tool_name": "Bash", "session_id": sid,
            "tool_input": {"command": "cat n"}, "tool_response": f"https://{WORK_HOST}/x"}
    run_hook(TP, post, home)
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
    r = subprocess.run([sys.executable, os.path.join(HOOKS, TP), "status", sid], capture_output=True,
                       text=True, env=env)
    assert "(pending)" in r.stdout
    subprocess.run([sys.executable, os.path.join(HOOKS, TP), "clear", sid], env=env, capture_output=True)
    assert decision(run_hook(TP, egress('codex exec "x"', sid=sid), home)) == "allow"


# --------------------------------------------------------------------------- orchestrator-only

ORCH = "orchestrator-only.py"
SID = "orch-session"


@pytest.fixture
def orch_env(home):
    return {"ORCH_DB": str(home / "agents.db"), "ORCH_STATE_DIR": str(home / "state"),
            "ORCH_LOG_DIR": str(home / "logs"), "TRACK_HOST": "testhost"}


def edit(home, path, tool="Edit", **extra):
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "session_id": SID,
            "tool_input": {key: path}, **extra}


def test_orch_main_thread_edit_of_protected_code_is_denied(home, orch_env):
    path = str(home / "source" / "repos" / "demo" / "app.py")
    out = run_hook(ORCH, edit(home, path), home, ["pretool"], orch_env)
    assert decision(out) == "deny"
    assert "quick-fix" in out and "coder" in out


def test_orch_subagent_edit_is_allowed(home, orch_env):
    path = str(home / "source" / "repos" / "demo" / "app.py")
    assert decision(run_hook(ORCH, edit(home, path, agent_id="sub-1"), home, ["pretool"], orch_env)) == "allow"


@pytest.mark.parametrize("tool", ["Write", "MultiEdit", "NotebookEdit"])
def test_orch_other_edit_tools_are_covered(home, orch_env, tool):
    path = str(home / "source" / "tools" / "x" / "app.py")
    assert decision(run_hook(ORCH, edit(home, path, tool), home, ["pretool"], orch_env)) == "deny"


def test_orch_unprotected_paths_are_main_thread_work(home, orch_env):
    for p in (home / ".claude" / "memory" / "a.md", home / "notes" / "a.md"):
        assert decision(run_hook(ORCH, edit(home, str(p)), home, ["pretool"], orch_env)) == "allow"


def test_orch_staging_dir_is_not_code(home, orch_env):
    path = str(home / "source" / "work" / "proj" / "_work" / "n.md")
    assert decision(run_hook(ORCH, edit(home, path), home, ["pretool"], orch_env)) == "allow"


def test_orch_do_it_yourself_unlocks_the_session(home, orch_env):
    path = str(home / "source" / "repos" / "demo" / "app.py")
    prompt = {"hook_event_name": "UserPromptSubmit", "session_id": SID, "prompt": "Just do it yourself"}
    run_hook(ORCH, prompt, home, ["prompt"], orch_env)
    assert decision(run_hook(ORCH, edit(home, path), home, ["pretool"], orch_env)) == "allow"
    # ...and only that session.
    other = edit(home, path) | {"session_id": "another"}
    assert decision(run_hook(ORCH, other, home, ["pretool"], orch_env)) == "deny"


def test_orch_failed_agent_run_unlocks_the_session(home, orch_env):
    import sqlite3
    db = sqlite3.connect(orch_env["ORCH_DB"])
    db.execute("CREATE TABLE runs (id INTEGER PRIMARY KEY, session_id TEXT, outcome TEXT)")
    db.execute("INSERT INTO runs (session_id, outcome) VALUES (?, 'fail')", (SID,))
    db.commit()
    db.close()
    path = str(home / "source" / "repos" / "demo" / "app.py")
    assert decision(run_hook(ORCH, edit(home, path), home, ["pretool"], orch_env)) == "allow"


def test_orch_garbage_stdin_fails_open(home, orch_env):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), **orch_env)
    r = subprocess.run([sys.executable, os.path.join(HOOKS, ORCH), "pretool"], input="{{{", env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.strip() == ""
