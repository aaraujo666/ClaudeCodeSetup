---
name: delegate
description: Hand a coding task, a code review or a question about code to another AI agent — OpenAI Codex CLI (`codex`), Google Antigravity CLI (`agy`, Gemini), or an OpenRouter model (`openrouter`, free models driven by the Codex harness) — running headless in a disposable git worktree, then review what comes back and apply it or reject it. Use when the user says "ask Codex", "have Gemini/Antigravity look at this", "use OpenRouter", "get a second opinion", "delegate this to Codex/agy", "let another AI review this", or asks to farm work out to another model. Claude stays the reviewer; a helper never writes to the real repo.
---

# Delegate: another AI does the work, you review it

Three helper agents can be wired in. Fill in the table with your own accounts and limits;
the numbers below are placeholders.

| Helper | Model | Account | Budget |
|---|---|---|---|
| `codex` | an OpenAI model | your ChatGPT account (plan: `<plan>`) | `<allowance>` |
| `agy` | a Gemini model | your Google account (tier: `<tier>`) | `<requests per day>` |
| `openrouter` | any OpenRouter model (a `:free` one by default) | `OPENROUTER_API_KEY` | `<free-tier request cap>`; paid models fail without credits |

`openrouter` is not its own CLI. It is `codex exec` with a custom model provider pointed
at OpenRouter's Responses API, so it gets Codex's tools, sandbox, sessions and JSON
output. The wrapper script injects the provider config and reads the key from the
environment; nothing in `~/.codex` changes. One agent turn is several requests (every
tool call is one), so a small edit costs a handful of requests and a real task can cost
20 or more.

This skill assumes a small wrapper script, `delegate.py` (stdlib only), that creates the
worktree, runs the helper headless, and records the result. Its contract is described under
"The tool". Write it for your own machine; the hook `block-work-to-third-party.py`
recognises it as an egress route through its `EGRESS_SCRIPTS` setting.

## Standing rules

1. **You stay the reviewer.** A helper's diff is a proposal. Read every line
   before `apply`, run the repo's own checks after applying, and reject
   anything you wouldn't have written yourself. Say what you rejected and why.
2. **Everything sent to a helper leaves the computer.** Personal and open-source repos are
   fine. **Work content NEVER goes. There is no override.** That means anything from your
   employer or a client: their source tree, tracker, mail, wiki. The wrapper refuses the
   work tree outright, and the PreToolUse hook `block-work-to-third-party.py` denies every
   helper call from a session that has touched work content, and any task carrying work
   markers. Work goes to Claude subagents (coder, doc-analyst) instead. Never put
   credentials, tokens or `.env` contents in a task.
3. **A helper works only in its worktree.** The script handles this. Never
   point a helper at the real checkout, and never let it commit, push or merge.
   Some helpers run with all permissions and no sandbox, so the worktree is the only
   thing fencing them in. Keep the tasks you give them to code work.
4. **Watch the free budgets.** Each run and follow-up uses requests from a small daily
   allowance. Prefer `codex` for iterative work, `agy` for a second opinion or a very
   large context, and `openrouter` for a third, independent opinion or for small,
   well-specified edits. Free OpenRouter models are weaker than the other two; read their
   diffs with that in mind.
5. **Every turn that runs a helper ends with a usage line**, next to the file links:
   `Delegate: codex 1 run, 88,888 input / 819 output tokens (subscription, no USD)`
   Take the numbers from the run's usage totals. Report tokens, not dollars, when the
   helper runs on a subscription or free tier.

## The tool

`~/source/tools/helpers/delegate.py` (a wrapper you provide). Every command prints JSON.
Write long tasks to a file in the scratchpad and pass `--task`; short ones can go in
`--task-text`.

```
python delegate.py run --helper codex|agy|openrouter --repo <dir> --mode edit|review|ask --task <file>
python delegate.py followup <id> --task-text "..."    # same session, same worktree
python delegate.py apply <id> [--check]               # diff -> repo working tree, uncommitted
python delegate.py discard <id>                       # remove the worktree, keep the record
python delegate.py list | show <id>
```

Useful `run` options:
- `--with-uncommitted` carries the repo's current uncommitted and untracked
  changes into the worktree as a commit. In `review` mode the helper is told
  to look at them with `git show HEAD`. This is how to get your own
  in-progress work reviewed.
- `--model`, `--effort` pass through to the CLI. For `openrouter`, `--model`
  takes any OpenRouter model id. Only `:free` ids work until credits are
  bought, and the model must list `tools` in its `supported_parameters`.
- `--timeout` is in seconds (default 1200). On timeout the process tree is
  killed.

Runs live in `~/.delegate/runs/<id>/`: `wt/` (the worktree, detached HEAD),
`TASK.md`, `turnN.log` (raw CLI output), `changes.diff` and `run.json`.

## Modes

- **edit**: the helper changes code. You get back `files_changed`,
  `diff_stat`, `diff_path` and its summary in `response`.
- **review**: the helper reports findings and should change nothing. If
  `files_changed` isn't empty, it ignored that; discard the run.
- **ask**: a question about the code, answered in `response`.

## Workflow

1. **Write the task cold.** The helper knows nothing about this conversation.
   Name the files, the goal, the constraints (style, what not to touch) and how
   to verify (the test or build command). The worktree has no `node_modules`,
   `vendor` or build output. If the check needs them, say so in the task, or
   run the check yourself after applying.
2. **Run** it. For a big job, run it in the background and carry on.
3. **Read the diff** (`diff_path`) in full, not just the summary. Helpers
   claim things they didn't do.
4. **Decide:**
   - Good: `apply <id>`, then run the repo's tests or build in the real
     checkout.
   - Close but not right: `followup <id>` with specific corrections, then read
     the diff again.
   - Wrong: `discard <id>`, then do it yourself or reword the task.
5. **Report**: what was delegated, to which helper, what you kept,
   changed or rejected, and the usage line.

`apply` refuses a run built with `--with-uncommitted`, because its diff sits on
top of changes the repo already has. Apply those by hand after review. When
`apply --check` fails because the repo moved on, re-run the task on the new
HEAD rather than forcing the patch.

Discard every run you don't apply. `list` shows open ones.

## Good uses and poor ones

- **Good:**
  - a second-opinion review of your own diff before a merge request
  - independent attempts from two helpers at a hard bug, then compare
  - bulk mechanical edits that follow a pattern
  - a read-the-whole-repo question
- **Poor:** a small edit you could make faster yourself. Writing the task and
  reviewing the diff costs more than the edit.

## Traps

- `codex exec` waits on stdin. The wrapper feeds the prompt through stdin, so
  don't call it by hand without `< /dev/null` or `-`.
- Codex loads the MCP servers in its own config. Turn them off for helper runs; a
  dead server entry spams errors.
- Some CLIs' `--sandbox` flag misbehaves on Windows (a restricted child process that hangs
  and cannot be killed). Test it before relying on it.
- A CLI installed after a shell started is not on that shell's PATH. Have the wrapper
  locate it explicitly.
- Per-user app-data directories can be virtualized for processes a desktop app starts,
  which is why runs live under `~/.delegate`.
- Headless runs without a permissions-skip flag may auto-deny shell commands and return an
  empty response.
- `openrouter` runs under its own `CODEX_HOME` (for example `~/.delegate/codex-openrouter`).
  Under the real `~/.codex` it overwrote the model cache with OpenRouter's catalogue, which
  broke the ChatGPT-plan model list. Never point it back at the real home.
- `openrouter`: Codex tries to refresh its model list from OpenRouter's `/models`, cannot
  parse it, and logs the whole multi-megabyte body to stderr. Set
  `RUST_LOG=error,codex_models_manager=off` to stop it. A "Model metadata not found,
  defaulting to fallback" item in the JSON is harmless.
- `openrouter`: free models often return 429 because the upstream provider is
  rate-limited, not your key. Codex retries; if the run still fails, re-run with a
  different `:free` model. The key-info endpoint's usage counter is not a reliable budget
  gauge; count by hand, or watch for 429s.
