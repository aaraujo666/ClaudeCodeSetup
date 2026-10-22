---
name: groom
description: >
  Pre-triage a GitLab backlog against the definition of ready — read the backlog,
  judge each issue with `issue_ready(check=True)`, draft acceptance criteria FROM
  THE CODE for the ones that fall short, and promote only the issues the user
  names in a batch reply. Use when the user says "groom the backlog", runs
  `/groom <project>`, `/groom all` or `/groom *`, or asks to triage, pre-review
  or work through a backlog against readiness. Grooming NEVER promotes an issue
  on its own initiative and never closes one.
---

# Groom a backlog

The human-facing half of the review -> ready -> work -> review loop. `work-ready-issues`
runs the dispatch end; this runs the end that feeds it.

The tool names below (`issue_ready`, `issue_answers`, `issue_criteria`, ...) belong to a
GitLab MCP server that encodes the workflow rules: the label state machine and the
definition of ready. Substitute your own server's tools; keep the invariants.

The problem it exists for: a backlog of hundreds of open issues, every one of them
`status::backlog`. The human review step is the bottleneck in the whole loop, and at that
volume it never happens. The fix is **not** to automate the judgement — it is to make the
judgement cheap. Grooming reads a backlog and, for each issue, either shows it as already
sufficient or drafts acceptance criteria **from the actual code**, so the user is
confirming a judgement rather than authoring one.

## The invariants, before anything else

**Nothing is promoted that the user did not name.** Grooming produces a draft; the
user's reply is the promotion. Until that reply arrives, every readiness call is
`issue_ready(..., check=True)` — the dry run, which writes nothing. A grooming pass that
promoted what it approved of would be a dispatcher wearing a review step's clothes.

Four more:

- **One rule, not two.** The judgement is `issue_ready(check=True)` — the same code the
  gate runs. Never re-implement "is this ready" by reading the issue and applying the
  checks yourself: a second copy of the definition drifts, and the copy that drifts is
  always the one nobody tests.
- **Criteria come from the code, never from the title.** No checkout, no drafting. A
  criterion paraphrased from the title reads exactly like a real one and certifies an
  issue as implementable that nobody has checked is implementable — which is worse than
  leaving it in the backlog, because the next reader is an agent that will build it.
- **Grooming reads answers; it does not author them.** The decisions an issue needs are
  asked when the issue is WRITTEN, with `issue_ask`, not discovered at grooming time.
  By the time the user types `/groom`, the questions should already be there and
  answered. So grooming's job at this step is `issue_answers` — read what was decided,
  and judge whether it actually settles the thing it was asked about.
- **Grooming never closes, and never promotes on its own initiative.** A dropped issue
  goes to `status::wontfix` and stays open for the user to close.
- **An unanswered question is asked LIVE, in the round.** The user is sitting there —
  `/groom <project> 20` is a long sitting they opted into — so do not park the issue and
  move on. Ask in the round, take the answer in chat, record it on the issue, groom it,
  and carry on. See "Recording a live answer" below — `issue_answer` is the write, and
  it is the only safe one.

## Invocation

```
/groom <project>            one project ref — <group>/<project>
/groom all      /groom *    every project the token can see
/groom <project> --priority high --type feature
```

`--priority` takes `high|medium|low|none`, `--type` takes `feature|bug|chore|story`.
Both compose into the `labels` filter of the backlog read; `--priority none` is not a
label and is applied by filtering the rows.

`all` and `*` are the same thing and both go through `issue_list(project='*')`. Say the
scope back before reading — an instance-wide groom is a long sitting and the user should
see that is what they asked for.

## One round is 10 issues

Batch approval in one reply only works if the user can read the whole batch in one
sitting. Drafting criteria from code costs real reading per issue — the issue, then the
part of the repo it names — and ten of those is a page of output worth reviewing. A
backlog of hundreds is not a sitting.

So a round is **10 issues**, and the rest of the backlog is reported as waiting with its
count. If the user names a number, that number wins. Offer the next round when the
current one is answered; never start it unasked.

## The protocol

### 1. Read the backlog

```
issue_list(project='<group>/<project>', labels='status::backlog', state='opened')
```

Add `type::` / `priority::` to `labels` for the filters. The rows come back as
`#iid state title [labels]`.

**Sort them yourself**, into the order `work_queue` dispatches in: `priority::high`,
`medium`, `low`, unprioritised, then iid. `issue_list` does not sort, and grooming the
top of the backlog in dispatch order is what makes the top of the ready queue worth
having. Take the round from the top.

### 2. Find the checkout — or refuse

The criteria come from the repo, so the repo has to be in hand. The checkout is the
directory under your repo roots whose project config names the project — the same map
`issue_handoff` uses:

```bash
grep -l "<project-name>" ~/source/repos/*/.gitlab-tools.json
```

No checkout is a **refusal**, per project, said out loud: grooming that project would
have to draft from titles, which is the one thing this skill must not do. Report it and
groom the projects that do have one. This is the common case on `/groom *`.

### 3. Judge each issue — with the gate, not by eye

Per issue in the round:

```
issue_ready(project, iid, check=True)
```

Writes nothing, reports what the promotion would report, and carries the same `code:`.
Outcomes, and only one of them is grooming's own work:

| `check` says | What it means | What grooming does |
|---|---|---|
| `PASSES` | already sufficient | offer it for promotion as-is — it needs no drafting |
| `code: no_acceptance_criteria` | the issue grooming exists for | **draft** (step 4) |
| `code: not_delegable` | `type::story` — a decision, not work | report; splitting a story is the user's call, not a draft |
| `code: open_questions` / `contradictory_answer` | the user has not answered yet | **ask it live** in the round (step 4a) |
| `code: illegal_transition` | the issue is in a state `ready` cannot be reached from | report, with `issue_status(force=True)` named as the repair |

**Then read the answers, on any issue that carries questions:**

```
issue_answers(project, iid)
```

One row per question: number, text, kind, state. `yes` / `no` / `answered` /
`unanswered` / `contradictory`. This is the read the whole skill turns on — the decisions
were made when the issue was written, and grooming's job is to carry them into criteria.

**Two judgements the tools cannot make for you**, and both get said out loud in the
round rather than quietly absorbed:

- **An answer that does not settle its question.** `issue_answers` reports
  `contradictory` when both boxes are ticked, but it cannot tell you that a ticked box
  or a paragraph fails to actually resolve the decision. If it does not, treat the
  question as unanswered and ask again (step 4a) — do not draft criteria around half an
  answer.
- **An issue that passes all the checks and still does not say what to build.** Offer
  it with that noted, never waved through.

Read the issue in full (`issue_show(project, iid, full=True)`) for anything you are
going to draft for.

*Optional pre-sort.* On a very large backlog you can have a cheap classifier score every
issue for "implementable cold" so you know which ones deserve a full read. It decides what
you **read**, never what is promoted: `issue_ready(check=True)` still runs on every issue
in the round. If you do this, never send issue text that carries work content to a
third-party model (see the `block-work-to-third-party.py` hook), and only send text from
projects that opted in.

### 4. Draft the criteria from the code

For each issue in the draft set, in this order: read the issue, **then** read the code it
names — the file, the tool, the function, the behaviour. Grep the checkout. The draft is
worth nothing if it was written before that read, and a user who spots one paraphrased
from the title stops trusting the whole round.

A criterion is worth writing when it:

- **names the artefact** it lands in — a file, a tool, a doc, a rendered line — not a
  feeling about the code;
- **is checkable cold**: a session with no conversation history can say passed or failed
  without asking anyone;
- **matches the repo's own conventions**. Read the repo's contribution or tool-contract
  document: a new read takes a `format=` option, a listing states its zero, a mutation
  converges on a second call. A drafted criterion that ignores the conventions drafts work
  that will be sent back at review.

Three to six of them. Fewer says nothing; more is a design document and the user did not
ask for one.

**Never invent scope.** If the issue asks for X, the criteria are about X. A criterion
for something the issue does not ask for is scope nobody agreed to, and an agent will
build it.

**Decide what you can.** Anything answerable from the code, the conventions, or a
decision already recorded is yours: make the call, draft the criteria around it, and say
in the round what you decided and **which alternatives you discarded and why**. Do not
manufacture a question out of a decision you are equipped to make — that is the failure
mode on the other side of guessing.

What is genuinely NOT yours — priority, whether the thing is worth building at all,
anything spending the user's time or money, anything committing them to an ongoing
operational burden — goes to step 4a.

### 4a. Ask the live question

The issue reached grooming with a decision still open. That is a defect in how it was
written (the question belonged in `issue_ask` at authoring time), but the round does not
stop for it:

1. **Ask in the round**, next to the issue, with the reasoning in the question — the
   user is deciding, not re-deriving what you already read in the code. A two-option
   choice is put as a yes/no on your recommendation ("Should X survive? no = Y"), never
   as an open "X or Y?".
2. **Take the answer in chat**, in the same batch reply as the promotions.
3. **Record it on the issue**, then draft criteria around it and groom it. Carry on
   through the rest of the round.

**Recording a live answer** is `issue_answer(project, iid, answers)` — one answer per
line, keyed by question number:

```
issue_answer(project, iid, answers="Q1: yes\nQ2: it falls back to the default and logs once")
```

A yes/no question takes `yes` / `no`; a long-form one takes the paragraph, which is
posted as a comment and then ticked. It ticks and never unticks, so a question that was
already answered is reported and skipped rather than overwritten — say so in the round
and move on rather than trying to force it.

**`issue_update(description=…)` is still forbidden as a way to answer.** It is the
whole-description replace that silently eats the `<!-- asked: -->` / `<!-- next: -->`
markers, and the next `issue_ask` then reuses a question number. `issue_answer` is a
one-character splice for exactly that reason.

Only when the answer is not available — the user has not given one — does the issue stay
put:

> Report the issue in the round as needing an answer, leave it `blocked`, and groom the
> rest. It is picked up on the next round.

### 5. Present the round, then stop

One block per issue. The drafted criteria go in **in full** — they are the thing being
reviewed, and a summary of them is not reviewable.

```
#41  priority::low   type::feature   export_icon: --transparent
     no acceptance criteria — drafted from tools/export.py:88
     ## Acceptance criteria
     - [ ] `export_icon` takes `transparent: bool = False`
     - [ ] with it set, the film is transparent and the PNG keeps its alpha
     - [ ] the default render is byte-identical to today's
     - [ ] the report names which of the two it produced

#46  priority::medium type::bug     wiki_sync drops a trailing newline
     PASSES as it stands — offered unchanged

#53  priority::medium type::feature  issue_digest: what changed since a date
     Q1 answered yes, Q2 answered no — both settle. Criteria drafted from
     tools/reports.py:210.
     ## Acceptance criteria
     - [ ] ...

#58  priority::low   type::chore    validate_widget storage-key collision
     ANSWER NEEDED — is a colliding storage key an error or a warning?
     Error is consistent with validate_widget's other collisions (widgets.py:311) and
     an agent cannot pick this without setting a precedent. I'd say error.
     yes = error, no = warning.

#62  priority::high  type::story    The v2 logistics core
     type::story — not delegable, and grooming does not split stories.
```

Then the reply menu, every round, **built from this round's iids**. The verbs and
their explanations are fixed; the numbers are not. The `ready:` line lists every iid
offered for promotion this round, comma-separated, so the user can copy it and send it
unchanged. Print the `<iid>: yes` line only when a live question was asked, once per
such issue, with its iid. `edit` / `drop` / `skip` carry a real iid from the round, or
`<iid>` when no particular issue suggests itself. Never print an iid that is not in the
round: a copied menu that names someone else's issues promotes the wrong work.

For the example round above, which offers #41, #46 and #53, asks on #58, and reports
#62 as a story, the menu reads as follows. The numbers are illustrative; they come
from that example, not from any real backlog:

```
ready: 41,46,53     write the criteria and promote
58: yes             answer the live question, then groom and promote it
edit 41: <text>     reword first — nothing is written until you say ready
drop: <iid>         -> status::wontfix, left OPEN for you to close
skip: 62            leave it as it is, no comment
```

And **stop**. No promotion, no description write, nothing. An unanswered round leaves the
backlog exactly as it was found.

### 6. Act on the reply, and only on it

For each iid the user named in `ready:`, in this order:

**a. Write the criteria — append-only.**

```
issue_criteria(project, iid, criteria='<one criterion per line>')
```

One call. It reads the issue itself, so there is no copy to go stale, and the rest of
the description comes back byte-identical — including the `<!-- asked: -->` and
`<!-- next: -->` markers an `## Open questions` block carries, which render as nothing
and which a description round-tripped through a paraphrase loses silently. Never
`issue_update(description=…)` for this; it replaces the whole description.

It handles the three shapes itself: no section, and one is appended at the end; an
**empty** section (what a template leaves behind, and what the gate reads as absent),
and it is filled rather than joined by a second one the gate would never look at; a
**non-empty** section, which it leaves alone and reports. Read that report — criteria
already there are somebody's judgement, and the drafted ones were not written.

**Revising criteria that are already there is a replace, never a comment.** When the
existing section has gone stale against the code, a comment carrying the revision is
invisible to `issue_ready` — the gate reads the description, so the issue gets promoted
on the stale criteria. Read the section, then replace it with the full revised set:

```
issue_criteria_list(project, iid=iid)          # rows + the digest
issue_criteria_replace(project, iid, criteria='<the FULL revised set>', digest='<from the read>')
```

The replace runs only on `status::backlog` or `status::blocked`, which is where grooming
works. A `stale_digest` refusal means the section changed since the read — re-read it,
never retry the old digest. Read its report: a ticked criterion the new set removed is
somebody's verification being dropped, and the user should hear about it.

**b. Promote it.**

```
issue_ready(project, iid)
```

The real call, not the check. It re-validates — the label is checked, not trusted — so a
criteria write that came out wrong is caught here rather than at dispatch. Report the
refusal verbatim if one comes back; do not repair it by forcing.

**For `drop:`** — `issue_status(project, iid, 'wontfix')`. `wontfix` is legal from every
state, so no force is needed. It leaves the issue **open** and labelled: dropping is
visible and reversible, and the close is the user's word through
`issue_close(project, iid, spend='0', status='wontfix', summary=<why>, repo=<checkout>)`
— which posts that `summary` as a comment, since a close with no timelog has nowhere
else to put it. Grooming never closes.

**For `edit N: …`** — apply the wording, show the revised block, wait. An edit is not an
approval.

### 7. Report the round

Five lists, every round, even the empty ones. An empty list is an answer; a missing one
reads as a step that did not run.

```
promoted (2)
  #41  criteria written, status::backlog -> status::ready
  #46  already sufficient — promoted unchanged

dropped (1)
  #58  -> status::wontfix, still open; close it with issue_close(spend='0', status='wontfix', repo=…)

answered live (1)
  #58  error, not warning — recorded on the issue, criteria drafted, promoted

not groomable (2)
  #71  type::story — a decision, not delegable work
  #77  Q2 answered but the answer does not settle it — re-asked, see above

refused (1)
  <group>/other-project — no checkout under the scanned roots; grooming it would mean
  drafting from titles

waiting (683)  — the round is 10
  next round starts at #83
```

**Refused** is anything the run declined to act on at all. Refusing is a correct
outcome and gets said out loud; the failure mode is a run that quietly worked around
something and reported a clean round.

## What grooming never does

- promote an issue the user did not name
- close anything — `wontfix` is a label here, not a state change to closed
- **manufacture a question out of a decision it is equipped to make.** Anything settled
  by the code, the conventions, or a recorded decision is grooming's to decide, stating
  what it discarded and why
- **`issue_ask` the issue it is grooming.** The questions belong at authoring time. The
  ONE exception is collateral: a live answer on issue A that destabilizes a *related*
  issue B may be asked on B
- pass `force=True` to anything. `issue_ask` on a collateral issue needs none:
  `-> blocked` is legal from `backlog` and `ready` as well as `in-progress`, because the
  entry condition is that the issue carries a stated reason it cannot proceed — and the
  questions are that reason
- draft a criterion without reading the code it is about
- **write an answer into a description.** `issue_answer` records one;
  `issue_update(description=…)` eats the question markers. See step 4a
- **replace a description.** Grooming's description writes are `issue_criteria` and
  `issue_criteria_replace`, which touch the criteria section and return the rest byte
  for byte. `issue_update(description=…)` is not a way to reach that section
- **post revised criteria as a comment.** The gate never reads it; revise with
  `issue_criteria_replace`

## Tools this skill uses

All tracker MCP tools, all allowlisted, so none of them prompts. Never hand-roll a
`curl` against the GitLab API — the workflow rules live in the tools.

| Step | Tool |
|------|------|
| read the backlog | `issue_list(project, labels, state, limit)` |
| judge | `issue_ready(project, iid, check=True)` — writes nothing |
| **read the answers** | `issue_answers(project, iid)` — the read this skill turns on |
| read in full | `issue_show(project, iid, full=True)` |
| write the criteria | `issue_criteria(project, iid, criteria)` — append-only; NEVER `issue_update(description=…)` |
| revise criteria already there | `issue_criteria_list(project, iid)` then `issue_criteria_replace(project, iid, criteria, digest)` — NEVER a comment |
| promote | `issue_ready(project, iid)` |
| drop | `issue_status(project, iid, 'wontfix')` |
| ask on a COLLATERAL issue | `issue_ask(project, iid, questions)` — never on the issue being groomed |
| record a live answer | `issue_answer(project, iid, answers)` — `'Q1: yes'` / `'Q2: <a paragraph>'`; NEVER `issue_update(description=…)` |
| never | `issue_close`, `issue_start`, `force=True`, `issue_ask` on the groomed issue |
