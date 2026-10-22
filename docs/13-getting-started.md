# 13. Getting started: adopt this incrementally

Do not copy all of this on day one. Each step below pays for itself before the next one
begins, and you can stop at any step with a better setup than you started with.

Everything referenced lives in [examples/](../examples/README.md).

## Week 1: three hooks and a short CLAUDE.md

**Goal:** stop the three or four recurring mistakes that cost you the most.

1. Copy the sample [CLAUDE.md](../examples/CLAUDE.md.example) to `~/.claude/CLAUDE.md`
   and cut it down to what is true for you. Aim for a page. A short file is read; a long
   one is skimmed.
2. Pick three hooks from [examples/hooks/](../examples/hooks/). My recommendation:
   - `block-file-delete.sh`: archive instead of delete. Best return of any hook.
   - `block-cd-git.sh` plus the [git wrapper](../examples/scripts/git-in.sh): stops the
     permission-prompt churn.
   - `block-heredoc.sh`: stops double-done edits.
3. Merge the sample [settings](../examples/settings/settings.example.json) into your
   `~/.claude/settings.json`. Wire each hook with the narrowest matcher that covers it.
4. Run the hook tests in [examples/hooks/tests/](../examples/hooks/tests/) so you know
   they deny what they should and allow what they should.
5. Install the [commit-msg hook](../examples/git/commit-msg) globally with
   `git config --global core.hooksPath`.

**You will know it is working when** the model is stopped, reads the deny message, and
does the right thing on its next call without you saying anything.

From then on, apply the rule of thumb: the second time you correct a behaviour, write
a hook.

## Week 2: subagents and a routing note

**Goal:** keep your main session's context clean and stop paying strongest-model rates
for trivial work.

1. Copy [examples/agents/](../examples/agents/) into `~/.claude/agents/`. Start with
   three: a cheap `quick-fix`, a mid-tier `coder`, and a strongest-tier `hard-problem`.
2. Add a routing note to your `CLAUDE.md`: the main thread orchestrates; edits go to
   `quick-fix` or `coder`; two failed attempts go to `hard-problem`.
3. Add the [orchestrator-only hook](../examples/hooks/orchestrator-only.py) once you
   trust the agents. It makes the routing stick. Keep the "do it yourself" escape.
4. Watch what the agents report. Tighten their prompts where they over-reach or
   under-verify.

## Week 3 to 4: a tracker

**Goal:** move the decision about what is "done" out of the model.

1. Run a self-hosted GitLab (or reuse one). A small VM is plenty.
2. Adopt the label scheme: one `type::`, one `status::`, optional `priority::`.
3. Write down the state machine from [doc 04](04-issue-workflow.md), including who owns
   each transition.
4. Start with the smallest enforcement that helps: an MCP server with `issue_create`,
   `issue_status` (refusing illegal moves), `issue_ready` and `issue_close`. Grow it as
   raw calls reveal missing tools.
5. Add the commit-msg hook's closing-keyword rule if you did not in week 1.
6. Add the [work-ready-issues skill](../examples/skills/) once issues are reliably
   groomed.

If you do not want a self-hosted server, the same state machine works with any tracker
that has an API and labels. The principle is that the model cannot move its own work to
done.

## Week 5 on: memory

**Goal:** stop re-explaining yourself, and stop re-learning traps.

1. Start a memory directory with the [sample bundle](../examples/memory/) as a template.
2. Write the first five entries from things you have already said to Claude more than
   once. Use the four types.
3. Add `stale_after` to anything that ages.
4. Add a PostToolUse hook to validate writes, and a SessionStart hook to report
   staleness. Keep the bundle in git.
5. Write a TRAP entry the next time something costs you more than half an hour.

## Later: the specialised pieces

Only when the need is clear:

- A **decision model** (Jev) for large piles of judgments. Measure the break-even first;
  below roughly 50 items it costs more than it saves. See [doc 06](06-jev-decision-model.md).
- **Delegate helpers** for second opinions, once your worktree discipline is solid.
- **Domain MCP servers** for the places you keep doing the same multi-step thing by
  hand. See [doc 09](09-mcp-servers.md).
- **Infrastructure rules** the day you have more than a couple of hosts. See
  [doc 10](10-infrastructure-rules.md).

## Pitfalls

- **Writing a hook before the second correction.** You will guess wrong about what the
  rule should be. Wait for the pattern.
- **Hooks that grep instead of parse.** They get false positives, you disable them, and
  the rule is gone. Parse commands.
- **Skipping the tests.** An untested hook is a source of random denials, which is how
  hooks get ripped out.
- **A `CLAUDE.md` that is a manual.** Keep it to hard rules and pointers.
- **Over-trusting `deny`.** These are drift guards. A permission boundary is something
  else, and you need one if the stakes are high.
- **Using a cheap model without measuring.** Check the break-even.

## Where to read next

If you want the one change with the highest return, read [Hooks](03-hooks.md) again. If
you want to see the whole loop in motion, read the [walkthrough](12-walkthrough.md). For
terms, the [glossary](glossary.md).

Next: [Glossary](glossary.md)
