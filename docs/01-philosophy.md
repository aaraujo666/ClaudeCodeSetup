# 01. Philosophy

The setup in this repository rests on one idea: a model is a capable but forgetful
colleague, and you manage a forgetful colleague with process, not with reminders.
Everything else follows from taking that seriously.

## What most people get wrong

### 1. Rules written as prose and expected to stick

Everyone writes a `CLAUDE.md` full of rules, and the model drifts from them anyway.
Not out of malice. Instructions compete for attention with the task, with the last
tool output, and with the habits baked into the model. A rule that appears once at
the top of a long session is weaker at turn 200 than at turn 2.

My rule of thumb: if I have corrected the same behaviour twice, it stops being a
sentence in `CLAUDE.md` and becomes a `PreToolUse` hook that denies the call. The
hook fires every time, costs no context, and teaches the model in the moment, because
the deny message says what to do instead. See [Hooks](03-hooks.md).

### 2. No system of record

If the AI decides when work is "done", you will get work that is "done". A tracker
with a state machine, where only a human can move an issue to `ready` and only a
human can move it to `done`, takes that decision away from the model on purpose. See
[Issue workflow](04-issue-workflow.md).

### 3. One model for everything

Using the strongest model for a typo fix is waste. Using the cheapest model for a
subtle concurrency bug is a different waste. Route by difficulty, and keep the
orchestrating session's context clean by pushing the noisy work into subagents that
return a few lines. See [Agents and model routing](05-agents-and-model-routing.md).

### 4. Memory as a dumping ground

A flat file of notes grows until it is noise. Memory that works is one fact per file,
typed, dated, marked with what a human confirmed, and honest about what has gone
stale. The most valuable entries are the traps: the thing that cost an afternoon
once and must never cost one again. See [Memory](08-memory.md).

### 5. Only generic MCP servers

Off-the-shelf servers expose an API. The best servers are the ones you write for your
own domain, with your rules built into the tool surface so that the wrong move is not
available. See [MCP servers](09-mcp-servers.md).

### 6. Trusting "done"

"Done" from a model means "I stopped". Make verification part of the workflow:
measure, hash, render, compile, run. See [Verification](11-verification.md).

### 7. An expensive model for every decision

A large share of the work in a setup like this is judging, not writing: is this issue
ready, is this alert noise, does this description match its diff. A cheap classifier
under the expensive model handles that, but only above a break-even size that I
measured and that most people will not guess. See
[Jev decision model](06-jev-decision-model.md).

## Principles

**Enforce, do not remind.** If a rule matters, it is code. `CLAUDE.md` stays short and
points to the detail; the hooks do the enforcing.

**The human owns the two decisions that matter.** What is ready, and what is done.
An agent may decide that it has started, that it is stuck, or that it has finished.
Those sets never overlap.

**Stop and ask, never guess.** Underspecified work moves to `blocked` with a written
question. A plausible wrong guess costs more than a day of waiting.

**Shape the tool so the wrong move does not exist.** A mailbox server with no send or
delete verb cannot send or delete. The safest permission is a capability that does not
exist.

**Keep the orchestrator's context clean.** Every extra request in a long session
re-sends the whole conversation. Isolating work in subagents is not tidiness, it is
what keeps the run affordable.

**Archive, never delete.** A move into `_archive/` is reversible. A delete is not.
This one rule has paid for itself many times over.

**Verify before asking or asserting.** Look for the answer first. Asking is the last
resort, and "you may be right" is not an answer; going to check is.

**Measure the thing you are optimising.** Cost claims, accuracy claims, and
break-even points get measured. Several of the surprises in this repository (a cheap
model costing more tokens, not fewer) came from measuring a belief.

**Record the trap.** When something costs hours, write it down in a form the next
session will actually read.

## What this costs

Setup effort. Hooks need writing and testing; a tracker needs a server; skills need
refining. The adoption path in [Getting started](13-getting-started.md) is ordered so
that each step pays back before the next begins.

It also costs some friction. A hook will deny a call that would have been fine. That
is the trade: occasional false positives against occasional silent disasters. When a
hook is wrong, fix the hook (the [examples](../examples/hooks/) ship with tests for
this reason), and prefer `ask` over `deny` where a human judgment is the right gate.

Next: [02 Architecture](02-architecture.md)
