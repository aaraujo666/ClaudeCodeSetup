# Glossary

**Acceptance criteria.** The checkable statements in an issue that define done. A ready
issue must have a non-empty section; the gate reads it.

**Agent (subagent).** A separate Claude instance, defined by a markdown file (name,
model, optional tool list, prompt), dispatched by the main thread to do a bounded piece
of work and return a short report. See [05](05-agents-and-model-routing.md).

**Archive, never delete.** Moving a file into an `_archive/` folder instead of removing
it. Enforced by a hook. See [03](03-hooks.md).

**Break-even (Jev).** The pile size above which using the cheap decision model costs
fewer orchestrator tokens than reading the pile directly. Measured at about 45 to 60
issues. See [06](06-jev-decision-model.md).

**Closing keyword.** A word such as `closes`, `fixes`, `resolves` or `implementing`
followed by an issue reference. Auto-closes the issue on push or merge and bypasses the
closing protocol. Write `re #N` instead. See [04](04-issue-workflow.md).

**Closing protocol.** The five steps `issue_close` runs: cross-reference the merge
request, log time, set a terminal status, close, sync the wiki.

**CLAUDE.md.** A markdown file Claude Code reads at the start of a session. Here it is
kept short: hard rules plus pointers to detail.

**Dispatch lock.** The `status::in-progress` label, taken by an agent before it writes a
line. An issue wearing it is either a run in flight or a run that died.

**Definition of ready.** The conditions `issue_ready` checks before promoting an issue:
not a story, no unanswered or contradictory questions, no prose decisions, non-empty
acceptance criteria. "Implementable by a session with no conversation history."

**Delegate helper.** Another vendor's coding agent, run headless in a disposable git
worktree for a second opinion. Claude reviews its output; it never writes to the real
repository.

**Drift guard.** A hook that stops an agent forgetting a rule. Distinct from a security
boundary, which must hold against something trying to get around it.

**Effort (estimated skilled-developer).** What the work would reasonably cost a competent
developer who knows the codebase, including tests and docs. The unit of logged time. Not
clock hours.

**Fail open.** A hook that exits successfully and allows the call if its own logic
crashes, so a bug in a hook cannot wedge every session.

**Handoff.** The structured comment `issue_handoff` writes (repo, branch, commit, merge
request, proposed spend, summary, verified and not verified) while moving an issue to
review. The later close reads it.

**Hook.** A command Claude Code runs at an event (`PreToolUse`, `PostToolUse`,
`UserPromptSubmit`, `SessionStart`, `Stop`, and others), receiving JSON on stdin and
optionally returning a decision.

**`help()` catalogue.** A tool on every MCP server that lists its tools, generated from
registered metadata so it cannot drift.

**Jev.** TypeSafe's "System One" model: returns typed judgments only. "Jev decides,
Claude writes."

**Lane.** The unit of branch, merge request, delivery and merge within a milestone run.

**Ledger.** An append-only file recording a long run's events; its memory and resume
point.

**MCP (Model Context Protocol).** The protocol Claude Code uses to talk to external tool
servers.

**Memory bundle.** A directory of small typed markdown files with an index, a change log
and a validator hook. Follows the Open Knowledge Format.

**Orchestrator.** The main session, which plans and dispatches but does not edit code.

**Open Knowledge Format (OKF).** A small spec for knowledge bundles: concept files with
typed frontmatter, an index and a log.

**Pre-sort.** Using a cheap model to score a whole backlog so the expensive model reads
only the borderline items.

**`restart_self`.** A tool that makes an MCP server exit so the client restarts it
after an edit to an existing tool.

**Scoped label.** A label of the form `scope::value`. On GitLab's free edition, scopes are
not mutually exclusive, so status moves use a tool that swaps atomically.

**Skill.** A `SKILL.md` that packages a repeated procedure and loads when its description
matches.

**Stale (`stale_after`).** A memory frontmatter date after which a fact must be
re-verified before it is relied on.

**Taint.** A session-level flag recording that work content was seen, after which routes to
third-party AI are denied.

**TRAP.** A memory entry for something that cost real time: what it appears to do, what it
actually does, how it was found, and how to apply the safe alternative.

**Verified (`verified`).** Frontmatter recording that a human confirmed a fact. Outranks
an inferred one.

**Worktree.** A second working directory for the same git repository on its own branch.
One per issue keeps parallel work and delegate helpers away from the real checkout.

Back to the [README](../README.md).
