# Examples

Sanitized, generic, working copies of a Claude Code setup. Everything employer- or
machine-specific has been replaced with a clearly marked `CONFIG` section holding
placeholders (`work.example.com`, `~/source/WORK`, `mcp__worktracker__`). Read each file's
header comment first: it says what the file enforces and why.

## Index

| Path | What it does |
|---|---|
| `CLAUDE.md.example` | A short global `~/.claude/CLAUDE.md`: hard rules that point at hooks, response conventions, git and tracker rules, the memory format. |
| `settings/settings.example.json` | The `hooks` wiring (and one `permissions.allow` line) that connects the hooks and scripts below to Claude Code events. |
| `hooks/block-file-delete.sh` | Delete becomes archive: bulk or forced removal is denied, a single `rm` asks, `git rm`, scratch, caches and worktrees are exempt. |
| `hooks/block-cd-git.sh` | Refuses `cd <dir> && git ...`, which defeats the permission allowlist; points at `git-in.sh`. |
| `hooks/block-heredoc.sh` | Refuses shell heredocs and PowerShell here-strings for file content; points at Write/Edit. |
| `hooks/block-unbounded-find.sh` | Refuses `find` rooted at `/`, `~`, a drive root, without `-maxdepth`. |
| `hooks/block-long-sleep.sh` | Refuses a foreground `sleep` over a limit (default 30 s) used as a timer; points at background jobs and Monitor. |
| `hooks/block-work-systems.sh` | Work systems need an explicit OK: production host is denied outright, tracker/mail writes and writes under the work tree ask. |
| `hooks/block-work-to-third-party.py` | Work content goes to Anthropic models only: taints a session that touched work, then denies every route to a third-party AI. Runs on Pre and PostToolUse. |
| `hooks/orchestrator-only.py` | The main thread may not edit code; it must dispatch to a subagent, unless a dispatched agent failed or you said "do it yourself". |
| `hooks/shell_vars.py` | Helper module: a quote-aware shell tokenizer all the shell guards use, so quoted text is never read as a command and `VAR=x; rm $VAR/f` is judged by the real path. |
| `hooks/work_markers.py` | Helper module: the work-content markers (`CONFIG` block), shared by the third-party hook and any tool that must withhold work content. |
| `hooks/tests/` | pytest suite: feeds sample hook JSON to each hook and asserts allow/ask/deny; plus `test_commit_msg.py` for the git hook. |
| `git/commit-msg` | Global git hook: blocks AI co-author trailers and issue-closing keywords (`closes #N`), suggests `re #N`. |
| `scripts/git-in.sh` | `git -C <dir> ...` wrapper so one stable command prefix can be allowlisted. |
| `scripts/okf.py` | Keeps memory directories valid Open Knowledge Format (OKF v0.2) bundles: `check`, `index`, `convert`, and the SessionStart / PostToolUse hooks. |
| `agents/` | Six subagent definitions (`coder`, `doc-analyst`, `drafter`, `hard-problem`, `quick-fix`, `researcher`) with model routing by task weight. |
| `skills/` | `work-ready-issues`, `groom`, `ask-the-board`, `delegate`. |
| `memory/` | A sample memory bundle (fictional content) in the format `okf.py` validates. |

## Install

Everything below assumes Claude Code on Linux, macOS or Windows with Git Bash, `bash`,
`python` (3.9+) on the PATH, and `git`. The shell hooks look for `python`, then `python3`.

1. **Hooks and helpers.** Copy the hook files, plus the two helper modules, into
   `~/.claude/hooks/`:

   ```
   mkdir -p ~/.claude/hooks ~/.claude/scripts
   cp examples/hooks/*.sh examples/hooks/*.py ~/.claude/hooks/
   cp examples/scripts/git-in.sh examples/scripts/okf.py ~/.claude/scripts/
   ```

   All hooks find `shell_vars.py` and `work_markers.py` next to themselves, so they must
   stay in the same directory.

2. **Edit the CONFIG sections.** `block-work-systems.sh`, `block-work-to-third-party.py`
   and `work_markers.py` ship with placeholders for a fictional employer. Replace the
   hostnames, MCP prefixes, work-tree path and company name with your own, or delete the
   hook entries from settings if you have no work/personal split. `orchestrator-only.py`
   has a `PROTECTED` list of directories under `~/source`; set it to your own.

3. **Merge the settings block.** Do not overwrite your `~/.claude/settings.json`. Merge the
   `hooks` object from `examples/settings/settings.example.json` into it (and the
   `permissions.allow` line, if you want `git-in.sh` to run without a prompt). Hooks are
   re-read on every tool call, so a mistake is live immediately: keep a backup, and run the
   tests below after any edit.

4. **Git hook (global).**

   ```
   mkdir -p ~/.githooks
   cp examples/git/commit-msg ~/.githooks/commit-msg
   chmod +x ~/.githooks/commit-msg
   git config --global core.hooksPath ~/.githooks
   ```

   The closing-keyword check only runs in repos whose remote URL matches
   `CLOSING_REMOTES` (default `gitlab|github`); set it in your shell profile to add a
   self-hosted forge. `ALLOW_CLOSING_KEYWORD=1 git commit ...` overrides it for one commit.

5. **Agents, skills, CLAUDE.md.**

   ```
   cp examples/agents/*.md ~/.claude/agents/
   cp -r examples/skills/* ~/.claude/skills/
   cp examples/CLAUDE.md.example ~/.claude/CLAUDE.md      # then edit it
   ```

   The `groom`, `work-ready-issues` and `delegate` skills describe tools you supply (a
   GitLab MCP server, a `delegate.py` wrapper); they are the workflow, not the plumbing.

6. **Memory.** A bundle lives at `~/.claude/projects/<key>/memory/`. Copy `examples/memory/`
   there to start from the sample, delete the fictional files, and validate any time with:

   ```
   python ~/.claude/scripts/okf.py check ~/.claude/projects/<key>/memory
   ```

## Test

```
python -m pytest examples/hooks/tests -q
```

The suite runs every hook with `HOME` and `USERPROFILE` pointed at a temporary directory, so
the taint state and override markers never touch your real `~/.claude`. It needs `pytest`
(`pip install pytest`) and, on Windows, Git for Windows (the tests look for
`C:\Program Files\Git\bin\bash.exe` first so they do not pick up the WSL launcher).

## Notes

- The hooks are drift guards, not security boundaries. They catch the mistake an agent makes
  by habit; they do not stop a determined bypass.
- Hooks fail open on their own bugs: a broken hook must not wedge every session. Errors from
  the third-party and orchestrator hooks are logged under `~/.claude/state` and
  `~/.claude/tracking`.
- `orchestrator-only.py` has an optional unlock that reads a SQLite table
  `runs(session_id, outcome)`; without that database the unlock is simply never taken, and
  saying "do it yourself" still works.
