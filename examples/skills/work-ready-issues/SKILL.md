---
name: work-ready-issues
description: >
  Dispatch a subagent per GitLab issue sitting in status::ready — read the queue,
  work each issue in three dispatched phases (validate and lock with issue_start on the
  session's model, implement on the Sonnet coder agent, review on the session's model)
  in its own git worktree, open a merge request and
  hand it back to status::review. Use when the user says "work the ready issues",
  asks to dispatch, pick up or run the ready queue, or names a project and asks for
  its ready work to be started. Agents NEVER close or merge.
---

# Work the ready issues

The agent-facing half of the review -> ready -> work -> review loop. A human decides what
is ready and a human decides what is done; this skill owns only the middle.

The tool names below (`work_queue`, `issue_ready`, `issue_start`, `issue_handoff`,
`mr_create`, ...) belong to a GitLab MCP server that encodes the workflow rules: the
label state machine, the definition of ready, the close protocol. They are named here
because the skill is only as good as those tools. Substitute your own server's tools; keep
the invariants.

## The invariant, before anything else

**Agents never close an issue, never merge one, and never approve one.** Not with
`issue_close`, not with `mr_merge`, not with `mr_approve`, not with a `closes #N` in a
commit message or an MR description, not "because it is obviously finished". The close is
the human's word, in a later session, through the close protocol; the merge is the same
word said with a different tool. Work that is finished goes to `status::review` — an
**open merge request** — and stops there.

**`mr_approve` is the one that will look harmless, and is not.** GitLab CE does not
enforce approvals, so `mr_merge` does — which makes a human approval the only
machine-readable evidence that somebody other than the agent that wrote the branch
actually read it. An agent approving its own work destroys the single signal the gate
exists to carry, and leaves a merge that looks reviewed and was not.

Three more that this whole loop exists to hold:

- **`ready` is a promise, not a fact.** It means "implementable by a session with no
  conversation history". A human can flip the label early or by hand, so it is
  **checked, not trusted** — re-validation is not a formality.
- **Questions are asked, never guessed.** An issue that turns out to be underspecified
  stops and moves to `status::blocked`. Guessing is the failure this loop was built to
  prevent, and a plausible wrong guess costs more than a day of waiting.
- **Time is proposed at handoff, logged only by `issue_close`.** `issue_spend` is
  additive and GitLab exposes no timelog list, so a double log cannot be detected
  afterwards. Never call `issue_spend` here.

## Two layers: the run, and one agent per issue

**One issue, one subagent.** The run reads the queue and dispatches; each issue is
re-validated, locked, worked and handed back inside its own agent, which returns a few
lines. The run never reads an issue body, never opens a worktree, never edits a file.

This is not tidiness, it is the only thing that keeps the run affordable. A worktree
isolates the filesystem and nothing else — eight issues worked in one conversation
means issue one's diffs, test output and dead ends are still being re-sent on every
request when issue eight closes. One conversation grows quadratically with the number of
issues; dispatch grows linearly. A lone agent pays a cold-start cost the parent had
already amortised, so the split only pays for itself from about two issues up, and the gap
widens from there.

**Invoking this skill is the standing request to dispatch.** The usual "do not spawn
agents unless the user asks" does not apply inside this run — asking for the ready
queue *is* the ask.

## At most 3 issues per run

Three agents, concurrent, and it is a cap on *dispatch*, not on the queue: a run that
finds nine dispatchable issues starts the first three and reports the other six as
waiting. The cap counts `dispatchable` only. A `held` issue is not "waiting (cap)" — it is
waiting on a dependency, a different reason with its own list in the report, and it never
occupies one of the three slots.

The bottleneck is the review end, not the working end. Everything an agent finishes
lands in `status::review` as an open merge request for one human to read, and a run that
starts nine issues has built a nine-deep queue for a person, plus nine MRs, nine
worktrees and nine branches to keep straight. Three is what one person can actually
review in a sitting.

If the user names a number, that number wins — they are allowed to say "start six", and
naming a list (`do #45 -> #47 -> #48`) names its length. Dispatch is still one agent per
issue however long the list runs.

---

# The run's protocol

## 1. Read the queue

```
work_queue(project='<group>/<project>')
```

`project` is required — there is no implicit instance-wide read, and `'*'` has to be
asked for. If the user did not name a project, use the checkout you are standing in
(`work_queue(repo='.')`) or ask which one; never sweep the instance to find out.

**Report the strays and never pick one up.** The `stranded` list is every
`status::in-progress` issue. That label is the dispatch lock — an agent takes it before
writing a line — so an issue wearing it is either a run happening right now or a run
that died and left it behind, and nothing in the issue says which. Both are the user's
decision between resuming and resetting. Print them with their ages; do not touch them.

**Dispatch from `dispatchable` only.** It comes back in dispatch order (`priority::high`,
`medium`, `low`, unprioritised, then iid). Take them from the top.

**Name `held` explicitly, and never start it.** `held` is ready work waiting on a
dependency declared under `## Depends on`. Print each held row with its unmet dependencies,
quoted verbatim from `work_queue`. Rows carrying a `dep_unresolvable`, `dep_dead` or
`dep_cycle` flag come first: that flag means the dependency will never clear by itself and
a human has to act — fix the reference, re-plan, or break the cycle. A held issue is never
dispatched, never given a Phase A, and never receives `issue_start`. Merging is the human's,
so a run never waits for a dependency to land: it reports the held issues and ends, and the
next run after the merge picks them up.

Resolve the **main checkout path** once, here, and pass it to every agent — they each
start cold and cannot be expected to find it.

## 2. Dispatch: three phases per issue, each a wave

Each issue is worked in three phases, each its own subagent. Subagents cannot start
subagents, so the run dispatches all three. Each phase goes out as a **wave**: one agent per
issue, all in **one message**, so they run concurrently. They touch disjoint worktrees and
disjoint issues, so there is nothing to serialise.

| phase | `subagent_type` | model | runs the issue agent's protocol… |
|---|---|---|---|
| **A, validate** | `general-purpose` | inherited | steps 1–4, then writes the implementation brief |
| **B, implement** | `coder` | Sonnet | phase B: implement, full check command, commit |
| **C, review** | `general-purpose` | inherited | phase C: review B's commit, then steps 5–6 |

1. **Wave A** for every issue being started. `validated` issues go on to B; `parked` and
   `refused` are final.
2. **Wave B** for every `validated` issue, `corrections: -`.
3. **Wave C** for every B that returned, `round: 1`, with B's lines pasted verbatim.
   - `fix` -> B again for that issue with C's `corrections` (B amends its commit), then C
     with `round: 2`.
   - `take-over` -> C again with `round: take-over`; it finishes the work itself.
   - `started` / `parked` -> final.

Leave `model` unset on A and C: they inherit the session's model and effort. B's model comes
from the `coder` agent definition. Set either only when the user asked for it.

**Why the split.** The risk of a cheaper model is concentrated in **re-validation**,
reading the issue against the code and judging whether it is really implementable. That
step fails quietly on a smaller model, with confident nonsense in a handoff that reads as
competent. But one inherited-model agent doing the whole job burns most of the usage on the
long edit-and-test loop in the middle. So the judgement stays on the session's model at
both ends (A decides what to build, C decides whether it was built), and the loop in the
middle runs on the cheaper model.

**Tracking (optional).** If you log agent runs (a SubagentStop hook writing one row per
phase), link each issue's B and C rows to its A row so the issue counts as one task with its
tokens summed, and record the outcome. A `fix` round is a `retry` of the first B row, and a
take-over is an `escalation`.

Every brief has to stand alone. The agent has no conversation history, cannot see the queue,
and cannot ask the user anything. `~` is the home directory: fill every path in a brief in
absolute form, because the Read tool and MCP arguments do not expand it.

**Wave A brief:**

```
Validate GitLab issue #<iid> in project <project>. Follow the issue agent's protocol in
the work-ready-issues skill at <abs ~>/.claude/skills/work-ready-issues/SKILL.md — read it
first, and run only "Phase A" under "The issue agent's protocol". Do NOT dispatch
subagents. Make no code edits.

  project:        <project slug>
  iid:            <iid>
  main checkout:  <absolute path>
  worktree:       <abs ~>/source/worktrees/<project>-<iid>
  branch:         issue/<iid>-<slug>
  brief:          <abs ~>/source/worktrees/<project>-<iid>.brief.md

Return exactly these lines and nothing else:
  verdict:  validated | parked | refused
  brief:    <path, or - >
  estimate: <est, or - >
  note:     <one line>
```

**Wave B brief** (`subagent_type='coder'`):

```
Implement GitLab issue #<iid> in project <project>. Follow "Phase B" under "The issue
agent's protocol" in <abs ~>/.claude/skills/work-ready-issues/SKILL.md — read that section
first. Your spec is the brief file. Do NOT push, open an MR or call any issue_* tool except
issue_show. Do NOT dispatch subagents.

  project:      <project slug>
  iid:          <iid>
  worktree:     <absolute path>
  branch:       issue/<iid>-<slug>
  brief:        <absolute path>
  corrections:  <C's corrections, on a fix round>   or -

Return exactly these lines and nothing else:
  verdict:  implemented | blocked
  commit:   <sha, or - >
  checks:   <the full check command's results, one line: tests and lint named>
  note:     <one line — what landed, or the decision that is missing>
```

**Wave C brief:**

```
Review and hand off GitLab issue #<iid> in project <project>. Follow "Phase C" under "The
issue agent's protocol" in <abs ~>/.claude/skills/work-ready-issues/SKILL.md — read it
first. Do NOT dispatch subagents.

  project:        <project slug>
  iid:            <iid>
  main checkout:  <absolute path>
  worktree:       <absolute path>
  branch:         issue/<iid>-<slug>
  brief:          <absolute path>
  round:          1 | 2 | take-over
  phase B said:   <B's four lines, verbatim>

You never close the issue, never merge it, never approve it, and never call
issue_spend. Finish at status::review — pushed, MR open, issue_handoff posted —
then stop.

Return exactly these lines and nothing else:
  verdict:     started | fix | take-over | parked
  branch:      <branch, or - >
  mr:          <!iid, or - >
  worktree:    <path, or - >
  estimate:    <est, or - >
  corrections: <on fix: the corrections, separated by " ; ">   or -
  note:        <one line — what landed, or why it parked>
```

Each issue's phase A re-validates its own issue. A run does not pre-screen for them: reading
nine issue bodies in the parent to decide what to dispatch puts back exactly the context the
split exists to remove.

## 3. Collect and report

The last wave returns; the run assembles the five lists below from each issue's final
verdict (A's `parked`/`refused`, or C's `started`/`parked`), plus the `held` rows it read
at step 1. A Phase A that parked on an unmet dependency appears under *parked* (the issue
is now blocked), which is distinct from *held*: held issues were never dispatched at all.
If an agent comes back with anything other than the lines it was asked for, take its
`verdict` and summarise the rest in one line — do not paste its transcript into the report.

A `started` row with no `mr` is worth saying out loud rather than smoothing over: the
work is on a branch nobody proposed, which is the one state `status::review` is defined
to exclude.

An agent that dies leaves a locked issue and an orphan worktree, which is what the
step-3 comment inside the agent exists to make recoverable. Report it as **refused**
with the iid and say the lock is still held.

---

# The issue agent's protocol

Everything below runs **inside a dispatched agent**, against one issue. If you are the
run, you are not doing any of this. Your brief names your phase; run only that part:

- **Phase A** (validate, inherited model): steps 1–4, then *Phase A ends: the
  implementation brief*. No code edits.
- **Phase B** (implement, `coder`): the *Phase B* section only.
- **Phase C** (review, inherited model): *Phase C* section, then steps 5–6.

## 1. Re-validate, before touching any code

```
issue_ready(project, iid)          # idempotent: re-runs the checks, writes nothing new
issue_show(project, iid, full=True)
```

`issue_ready` re-runs the mechanical checks — not a story, no unanswered or
contradictory question, an acceptance-criteria section that is not empty — and reports
every failure at once. Then **read the issue yourself**, because the mechanical checks
cannot see the failure that actually matters: an issue that passes them and still does
not say what to build.

**Then re-check its dependencies against live state, before `issue_start`.** The run's
queue read can be minutes old, and a dependency's state moves:

```
work_queue(project, format='json')     # find this iid
```

- In `dispatchable` -> proceed.
- In `held` -> **park, do not build.** Do **not** call `issue_start`: a held issue never
  gets the lock, because it is not being picked up, it is waiting. Call `issue_ask`
  directly (legal from `ready`) with an `open:` line naming the unmet dependency and
  its reason as `work_queue` printed it. Return `verdict: parked`, brief `-`, estimate
  `-`, and a note naming the dependency.
- In neither (no longer `status::ready`, e.g. another run took it) -> return `refused` and
  touch nothing.

Two outcomes for the issue itself, and neither is "have a go anyway":

- **It holds up** -> step 2.
- **It does not** -> take the lock first, then ask (this is the underspecified path; the
  dependency park above deliberately skips `issue_start`):
  ```
  issue_start(project, iid, estimate='…')
  issue_ask(project, iid, questions='...one per line...')
  ```
  `issue_start` before `issue_ask` on purpose, even though `ready -> blocked` is
  legal: taking the lock first stops a second run discovering the same broken issue and
  writing the same questions, and it leaves a truthful trail (picked up, then blocked).
  Prefix a line `open:` for a question that needs a paragraph rather than a yes/no.
  Return `verdict: parked` and stop.

## 2. `issue_start` — the dispatch lock

```
issue_start(project, iid, estimate='2h')
```

This is what makes the queue safe to run twice: the issue leaves `ready` before a single
line is written, so nothing can be picked up by two agents. Take the lock **before** the
worktree, the branch and the first edit.

`estimate` is your honest estimate of **skilled-dev effort** for the work — the same
unit `issue_close` eventually logs, never clock time or session length.

## 3. Comment the branch and the worktree, immediately

Before the first edit, not after the last:

```
issue_comment(project, iid, body='Working on `issue/12-work-queue` in `~/source/worktrees/<project>-12`')
```

An agent that dies between here and the handoff leaves an orphan worktree and a locked
issue. With this comment that is a two-minute recovery; without it, it is archaeology.
This is also the only record `work_queue`'s stranded list can point a human at, and the
run that dispatched you cannot write it for you — it does not know the branch until you
have made it.

## 4. One worktree per issue

Agents never share a checkout. Two agents editing one working tree is the fastest way to
lose work that has not been committed yet — and under concurrent dispatch that is not
hypothetical, there really are three of you.

```bash
bash ~/.claude/scripts/git-in.sh <main-checkout> worktree add -b issue/<iid>-<slug> ~/source/worktrees/<project>-<iid>
```

Every git call goes through `git-in.sh` — never `cd <dir> && git`.

**Worktrees live outside your repo roots.** If your tooling scans `~/source/repos` for
checkouts (a registry mapping projects to directories), a worktree parked inside it carries
a copy of the project config and makes the registry see two checkouts for one project.
`~/source/worktrees/` is a sibling of the scanned roots and is the place for them.

**Leave the worktree standing when you finish, and never remove it yourself.** A review
that comes back as "change this" continues in this worktree (see *Rework*, below), so an
agent that tore it down on the way out would have thrown away the checkout the next
round needs.

**Teardown belongs to whoever merges, at the merge.** Not to you, not to the run, and
not to a later dispatch. `mr_merge` deletes the *remote* source branch; the local
worktree and the local branch survive it, and the person who merged removes both in the
same sitting:

```bash
bash ~/.claude/scripts/git-in.sh <main-checkout> worktree remove ~/source/worktrees/<project>-<iid>
bash ~/.claude/scripts/git-in.sh <main-checkout> branch -d issue/<iid>-<slug>
```

That is the only thing that ever removes one, so a worktree still standing means one of
exactly two things: an MR waiting on review, or an agent that died. The step-3 comment
is what tells them apart.

## Phase A ends: the implementation brief

Write the brief to the `brief:` path from your dispatch: beside the worktree, never inside
it, so it is never committed. Phase B has no history. It reads this file and the code, and
nothing else about the issue, so the brief must stand alone:

```
# #<iid> — <title>
goal:         <what to build, 2–4 lines, in your words, not the issue's>
criteria:     <each acceptance criterion, one per line, as written on the issue>
files:        <the files you expect to change, and why — from reading the code>
approach:     <the approach, and any trap you saw in the code>
not-in-scope: <what another issue owns>
checks:       <the repo's FULL check command — tests AND lint, each named>
```

Return `validated` with the brief path. That is the end of phase A.

# Phase B — implement (`coder`)

You are working from a brief that a phase A agent wrote after re-validating the issue and
taking the lock. The issue is `status::in-progress`, the worktree exists and is on the
issue branch.

1. Read the brief, then the files it names. The brief is your spec. Where it and the code
   disagree, or it does not say what to build, **do not guess**: restore the worktree
   (`git-in.sh <worktree> checkout -- .`, plus removing any new untracked files you created,
   by name) and return `blocked` with the missing decision in `note`. Phase C asks the
   question.
2. Implement inside the brief's `criteria` and `not-in-scope`.
3. Run the brief's `checks`, the full check command, tests **and** lint. Fix until green, or
   report exactly what is still red.
4. Commit with `re #<iid>` in the message, never a closing keyword (closes/fixes/resolves/
   implementing). On a `corrections` round, address every correction and amend
   (`commit --amend`), so the issue stays one commit until review.
5. Never push, never open an MR, never call an `issue_*` tool other than `issue_show`. Every
   git call goes through `git-in.sh`.

Return the lines your brief asked for: `checks` names the commands you ran and their results.

# Phase C — review, then hand off

You run on the inherited model because this is the judgement the split keeps there: **does
the commit actually do what the issue asks, or does it only look finished?**

**B returned `blocked`.** If the missing decision is real, `issue_ask(project, iid,
questions=...)` and return `parked`. The lock is already held by phase A, so `in-progress ->
blocked` is legal. If the brief simply failed to say something you can answer from the issue
and the code, fix the brief and return `fix` with that as the correction.

**B returned `implemented`.** Read `issue_show(project, iid, full=True)`, the brief, and the
commit (`git-in.sh <worktree> show <sha>`). Re-run the full check command yourself. Check it
against the **issue**, not just the brief:

- every acceptance criterion is met by the diff, not merely claimed;
- tests and lint both ran and passed;
- nothing outside the issue's scope changed;
- the commit message carries `re #<iid>` and no closing keyword.

Then:

- **Meets it** -> steps 5–6 below.
- **Falls short, round 1** -> return `fix` with specific corrections: which criterion, what is
  wrong, what to change. Not "improve tests". The run sends them to B once.
- **Falls short, round 2** -> return `take-over`. A tier that failed twice is not tried a
  third time.
- **`round: take-over`** -> finish the work yourself in the worktree (amend B's commit or
  redo it), then steps 5–6, and say in the handoff's `verified` that it was taken over.

## 5. Hand it back: push, open the MR, hand off

`status::review` means **a merge request is open**, not that a branch exists somewhere.
A branch nobody proposed has no diff to read and nowhere to leave a comment, so these
are one step and the handoff is the last of the three — never the only one.

```bash
bash ~/.claude/scripts/git-in.sh <worktree> push -u origin issue/<iid>-<slug>
```

```
mr_create(project, source='issue/12-work-queue', issue=12,
          title='Work queue — the dispatch read',
          description='<the same summary the handoff carries>')
```

- **`target` is omitted on purpose.** `mr_create` reads the project's default branch from
  the API rather than guessing between `main` and `master`.
- `squash=True` and `delete_source=True` are the defaults — a per-issue branch has no life
  after the merge. Do not pass them.
- **`issue=<iid>` is what posts the cross-reference.** It writes `Related to #N` into the
  description, and GitLab turns that mention into the note on the issue.
- It **converges**: a retry after a timeout returns the MR that is already open for that
  source -> target and says `existing`, rather than dying on GitLab's duplicate 409.

**Put the handoff summary in the description** — what was done, and what you verified,
did not verify and deferred. That is the first thing a reviewer reads, and you are
writing it anyway for `issue_handoff`; a description carrying only `Related to #12` sends
them back to the issue to find out what changed.

**Then look at the pipeline you just triggered, before you hand off.** Pushing fires CI
on `refs/merge-requests/<mr>/head` — **not** on your branch name, so
`pipeline_list(project, ref='issue/12-work-queue')` finds nothing and reads as "no CI on
this project". Call `pipeline_list(project)` and match the sha you pushed. Wait for it to
leave `running`/`pending`.

- **Green** -> hand off.
- **Red** -> that is your work, not the reviewer's. Fix it and push again, **once**.
- **Still red after that one round** -> hand off anyway, naming the failed job and the
  pipeline id in `not_verified`.

Both halves of that are load-bearing. An agent that exits quietly on a red pipeline hands
a reviewer a branch that cannot merge and is gone by the time anyone finds out — the
context that would have made the fix cheap died with it. An agent that grinds on CI until
it goes green is the runaway the per-issue dispatch split exists to bound. One round, then
say so out loud.

`mr_merge` gates on CI anyway, so this never lets a red branch merge. What it changes is
*where* the failure lands: on the agent that still has the context, rather than on the
human at the gate days later.

Then hand off, naming the MR:

```
issue_handoff(project, iid, repo='<MAIN checkout>', branch='issue/12-work-queue',
              commit='<sha>', mr='<the !iid mr_create returned>', spend='2h30m',
              summary='what was done',
              verified='pytest: 1432 passed · ruff: clean · pipeline #117 green',
              not_verified='…', deferred='…')
```

One comment, updated in place, carrying everything the close will need days later in a
session that was not here. It moves the issue to `status::review` in the same call.

- `repo` is the **main checkout**, not the worktree. The worktree is gone by the time
  anyone closes the issue, and `issue_close` syncs the wiki from this path — a recorded
  path that no longer exists makes the close fail. The close **refuses** when nothing tells
  it where the checkout is, and the handoff is what makes a cold close possible at all.
- `mr` is what makes the handoff complete: `issue_close` reads it back and
  cross-references it. A handoff with a `branch` and no `mr` is *warned* about rather
  than refused — that warning exists for the rework round, where the MR is already open
  and the field carries itself forward. On a first round, treat it as the bug it is.
- `spend` is **proposed** and is not logged. Never `issue_spend`.
- `verified` states the result of the repo's **full check command — tests *and* lint**,
  each named. If you did not run one of them, it goes in `not_verified` explicitly.
  "Tests pass" with no mention of lint is the handoff that gets merged and then refused at
  the gate: a pipeline can already be failing on lint errors in code the issue just wrote.
- Say what you did **not** verify, out loud, in `not_verified`. A handoff that lists only
  successes is what makes a reviewer trust the next one less.

## 6. Stop

No close. No merge. No `closes #N`, `fixes #N`, `resolves #N` or `implementing #N` — not
in a commit message, and **not in the MR title or description either**. All four are
GitLab closing keywords, and they perform one step of the close protocol and none of the
others: no cross-reference, no logged time, no terminal `status::` label. From a
commit they fire on push; from an MR they fire on merge, which is the same failure
through the second door. Write `re #N` in a commit and `Related to #N` in an MR — and
`issue=<iid>` writes that line for you.

`mr_create` **refuses** those keywords outright, quoting the phrase back. That refusal is
the rule working, not an obstacle to route around: reword and call it again. Watch
`implementing` in particular — it is a closing keyword that reads like ordinary prose,
and it is the one that gets written by accident.

Return the lines the dispatch brief asked for. Do not summarise your working
history — the run does not want it, and everything a reviewer needs is already on the
issue.

## Rework: an issue that came back

An issue moving `review -> ready` is rework, not new work. It already has a branch and an
open merge request, and starting over throws away the work, the review, and the thread
the review happened in.

Before step 4, read the handoff comment (`issue_show`): it carries the `branch` and the
`mr` of the previous round. Continue **on that branch**, in a worktree pointing at it —
which, if the previous round's worktree is still standing, it already is, because nothing
removes one before the merge:

```bash
bash ~/.claude/scripts/git-in.sh <main-checkout> worktree add ~/source/worktrees/<project>-<iid> issue/<iid>-<slug>
```

Then read the review comments posted after the handoff before touching anything — the
rework is defined by those, not by the original description. This is phase A's job: the
brief it writes for a rework round lists the review comments as its `criteria`, and phase B
adds new commits on the branch (it does not amend a commit that has already been pushed).

**Re-use the open MR; never open a second.** At step 5 you push to the same branch, and
that is the whole of it: an MR tracks its source branch, so the new commits appear in the
MR the reviewer is already reading, under the comments they already left. A second MR for
one issue splits the review across two threads and leaves one of them to be closed by
hand.

Call `mr_create` again only if the handoff records **no** `mr`. It is safe either way: it
converges, returning the open MR for that source -> target and reporting it as existing.

At the end, call `issue_handoff` again with the same arguments plus what changed; it
updates the existing comment in place rather than posting a second, and a field you leave
out keeps the value already recorded — which is why a rework round need not re-state `mr`
at all.

---

# What the run reports

End every run with these five lists, even when one of them is empty. An empty list is an
answer; a missing one reads as a step that did not run.

```
started (2)
  #12  !7  issue/12-work-queue      ~/source/worktrees/proj-12   est 3h
  #14  !8  issue/14-grooming-skill  ~/source/worktrees/proj-14   est 2h

parked (1)
  #21  2 questions asked — now status::blocked

refused (1)
  #30  carries two status:: labels — left alone, repair with issue_status(force=True)

held (2) — waiting on a dependency
  #31  #12 status::review (MR !7 open)
  #33  !! dep_cycle — these issues depend on each other; break the cycle
  the next run after the merge picks these up

strays, not picked up (1)
  #7   held 3d 4h — a run in flight or a run that died; resume or reset by hand

waiting (6)  — the cap is 3 per run
  #9 #15 #16 #18 #22 #25
```

**Refused** is anything the run declined to act on at all: a failed re-validation an
agent could not turn into questions, a doubly-labelled issue, a project that would not
resolve, an agent that died holding a lock. Refusing is a correct outcome and gets said
out loud — the failure mode here is a run that quietly worked around something and
reported success.

# Tools this skill uses

All of them are tracker MCP tools and all should be allowlisted, so none of them prompts.
Never hand-roll a `curl` against the GitLab API: the workflow rules live in the tools.

| Layer | Step | Tool |
|-------|------|------|
| run | read the queue | `work_queue(project, format, full, repo)` |
| run | dispatch, phases A and C | `Agent(description, subagent_type='general-purpose', prompt)` |
| run | dispatch, phase B | `Agent(description, subagent_type='coder', prompt)` |
| issue agent | re-validate | `issue_ready(project, iid)`, `issue_show(project, iid, full)` |
| issue agent | ask | `issue_ask(project, iid, questions)` |
| issue agent | lock | `issue_start(project, iid, estimate)` |
| issue agent | record the branch | `issue_comment(project, iid, body)` |
| issue agent | open the MR | `mr_create(project, source, title, description, issue)` |
| issue agent | check CI | `pipeline_list(project)` — match the sha; CI runs on `refs/merge-requests/<mr>/head`, not the branch |
| issue agent | hand over | `issue_handoff(project, iid, repo, branch, commit, mr, spend, summary, verified, not_verified, deferred)` |
| never | | `issue_close`, `issue_spend`, `mr_merge`, `mr_approve` |
