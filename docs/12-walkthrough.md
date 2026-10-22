# 12. Walkthrough: one issue, idea to closed

A worked example on a fictional project, `acme-widgets`: a small service that syncs
widget definitions from a remote catalogue. Everything below is invented, but the tool
names, the states and the refusals are the real shape of the workflow from
[doc 04](04-issue-workflow.md). Output is abbreviated.

```mermaid
flowchart LR
    A["1 Idea"] --> B["2 issue_create"]
    B --> C["3 issue_ask at write time"]
    C --> D["4 Human answers"]
    D --> E["5 Groom: criteria from code"]
    E --> F["6 Human promotes to ready"]
    F --> G["7 Run: lock + worktree"]
    G --> H["8 Blocked: new question"]
    H --> I["9 Human answers, re-ready"]
    I --> J["10 Implement + review"]
    J --> K["11 MR + handoff"]
    K --> L["12 Human closes"]
```

## 1. The idea

While debugging, I notice the sync client gives up on the first HTTP 503. I tell Claude:
"the sync client should retry on transient errors; file it."

## 2. The issue is filed, with the decision asked at write time

Claude searches first, so it does not duplicate, then creates the issue:

```text
> issue_search(project="root/acme-widgets", query="retry")
nothing matched: "retry" in 41 issues (open and closed)

> issue_create(project="root/acme-widgets",
               title="Sync client: retry transient HTTP errors with backoff",
               labels="type::feature", template="feature",
               description="""
The sync client (src/sync/client.py) aborts the whole run on the first 503
or connection reset. Retry transient failures with exponential backoff.
""")
created root/acme-widgets#42  status::backlog  type::feature
```

While writing it, Claude hit two choices it cannot make: should the retry count be
configurable, and what counts as transient? It does not leave those as a heading. A
heading like "What has to be decided" would be refused anyway (`prose_decision`), because
the ready gate cannot see prose. It asks:

```text
> issue_ask(project="root/acme-widgets", iid=42, questions="""
Q1: Should the retry count be configurable via settings?  (yes/no)
Q2: Which status codes are transient? open: list them
""")
Wrote 2 questions to #42 description (round 1).
status: backlog -> blocked  (reason: 2 unanswered questions)
```

The description now carries:

```markdown
## Open questions

### Q1 - Should the retry count be configurable via settings?
<!-- asked: 2026-10-14T10:02:11Z -->
- [ ] Yes
- [ ] No

### Q2 - open: Which status codes are transient?
<!-- asked: 2026-10-14T10:02:11Z -->
- [ ] Answered below
<!-- next: 3 -->
```

## 3. I answer

I answer in the conversation, and Claude records it with the tool, not a comment and not
a hand-edit of the description (which would drop the invisible round markers):

```text
> issue_answer(project="root/acme-widgets", iid=42,
               answers="Q1: yes\nQ2: 429, 502, 503, 504, and connection resets")
Q1: ticked Yes
Q2: comment posted, then ticked
all 2 questions answered. #42 still status::blocked.

> issue_status(project="root/acme-widgets", iid=42, status="backlog")
#42: blocked -> backlog  (answered, and asked at write time)
```

Answering does not move the status. The last answer only makes the issue *eligible* for
the ready gate.

## 4. Grooming drafts the acceptance criteria from the code

Later I run `/groom acme-widgets`. The skill finds the local checkout (it refuses
without one), pre-sorts the backlog, and runs the gate's dry run on each issue.

```text
> issue_ready(project="root/acme-widgets", iid=42, check=True)
FAILS: code: no_acceptance_criteria
  The description has no acceptance-criteria section.
```

Grooming reads `src/sync/client.py` and `tests/test_sync.py`, then drafts criteria that
refer to real names, append-only:

```text
> issue_criteria(project="root/acme-widgets", iid=42, criteria="""
SyncClient.fetch retries on 429, 502, 503, 504 and ConnectionResetError
Wait between attempts is base * 2**attempt, with jitter, capped at 30s
Retry count comes from settings.SYNC_MAX_RETRIES, default 3
After the last attempt the original exception propagates unchanged
Non-transient errors (400, 401, 404) are not retried
tests/test_sync.py covers each of the above
""")
Appended 6 criteria to #42. Rest of description byte-identical.
```

Then it presents the round and stops:

```text
#42  priority::medium  type::feature  Sync client: retry transient HTTP errors
     gate: would PASS    criteria drafted from src/sync/client.py:88-131
Promote which? (e.g. "42", "42,45", "none")
```

## 5. I promote it

This is the human-only transition:

```text
Me: promote 42

> issue_ready(project="root/acme-widgets", iid=42)
#42: backlog -> ready  (gate passed: criteria present, questions answered, type::feature)
```

## 6. The ready queue is worked

I say "work the ready issues for acme-widgets". The `work-ready-issues` skill reads the
queue:

```text
> work_queue(project="root/acme-widgets")
READY - dispatch in this order (1):
  #42  priority::medium  Sync client: retry transient HTTP errors
HELD (0)    STRANDED in-progress (0)    REVIEW (1): #39 MR !15 open
BLOCKED (0)
```

One dispatchable issue, so one subagent. It starts cold and re-validates before touching
anything, because a label can be flipped by hand:

```text
> issue_ready(project="root/acme-widgets", iid=42, check=True)
PASSES
> issue_start(project="root/acme-widgets", iid=42, estimate="2h")
#42: ready -> in-progress  estimate 2h  (dispatch lock taken)
> issue_comment(project="root/acme-widgets", iid=42,
                body="Working on branch issue/42-sync-retry, worktree ~/worktrees/acme-widgets-42")
```

It creates the worktree through the git wrapper (a direct `cd && git` would be denied):

```text
$ bash ~/tools/git-in.sh ~/projects/acme-widgets worktree add \
      ~/worktrees/acme-widgets-42 -b issue/42-sync-retry
```

## 7. Blocked: a question the issue did not answer

The agent writes the brief, then notices something the criteria do not cover: the
catalogue sends a `Retry-After` header on 429. Should the client honour it, or use its own
backoff? That is a design choice and the issue does not make it. The agent does not guess:

```text
> issue_ask(project="root/acme-widgets", iid=42, questions="""
Q3: On a 429 with a Retry-After header, honour the header or use computed backoff?
    (honour / ignore)
""")
Wrote 1 question to #42 (round 2, Q3).
status: in-progress -> blocked  (reason: 1 unanswered question)
```

The agent returns to the orchestrator in two lines: `#42 blocked on Q3; worktree kept at
~/worktrees/acme-widgets-42`. The run reports it and finishes. Nothing was guessed and no
code was written on a coin flip.

## 8. I answer, and re-ready it

```text
> issue_answers(project="root/acme-widgets", iid=42)
Q1 yes   Q2 answered   Q3 unanswered

Me: honour the header, but cap it at 30 seconds.

> issue_answer(project="root/acme-widgets", iid=42,
               answers="Q3: honour, capped at 30s")
Q3: comment posted, then ticked.

```

The answer changes the definition of done, so the criteria are amended *before*
re-readying. Criteria are locked once an issue is ready, in progress or in review, and
editable only on backlog or blocked issues. The revision reads the section and its digest
first, so a stale edit is refused:

```text
> issue_criteria_list(project="root/acme-widgets", iid=42)
6 criteria, digest 3fa91c

> issue_criteria_replace(project="root/acme-widgets", iid=42, digest="3fa91c",
      criteria="""...the six existing lines...
A 429 with Retry-After waits that many seconds, capped at 30s""")
7 criteria; 0 ticks dropped.

> issue_ready(project="root/acme-widgets", iid=42)
#42: blocked -> ready
```

## 9. The run again: implement and review

`work-ready-issues` runs again. The queue shows #42 ready; a new agent validates, takes
the lock, and finds the existing worktree. Phase B hands the brief to `coder`:

```text
coder -> report
Changed: src/sync/client.py (+54 -9), src/settings.py (+3), tests/test_sync.py (+118)
Verified: pytest tests/test_sync.py -q -> 31 passed in 2.4s
          pytest -q -> 214 passed
Unsure: jitter uses random.uniform; the existing tests seed nothing global, so I
        injected a rng parameter instead of patching.
```

Phase C is the review, on the session's own model. The reviewer reads the diff against
each acceptance criterion and re-runs the suite itself rather than trusting the report.
It finds one miss: the cap applies to computed backoff but not to a `Retry-After` value.
It sends that back to `coder` as a precise correction, re-reads the diff, and the suite is
green.

## 10. Merge request and handoff

```text
> mr_create(project="root/acme-widgets", source_branch="issue/42-sync-retry",
            title="Sync client: retry transient errors with capped backoff",
            description="Related to #42. Retries 429/502/503/504/reset...")
created !17  target main  squash on  delete-source on

> issue_handoff(project="root/acme-widgets", iid=42, commit="9e26896", mr="17",
                spend="3h", summary="exponential backoff + Retry-After, capped 30s")
#42: in-progress -> review
handoff comment written (spend 3h PROPOSED, not logged)
```

Note the merge request description says `Related to #42`. Writing "closes #42" would have
been refused by `mr_create`. Note also that the agent proposed 3h, against a 2h estimate,
and said so; the number is effort, not clock time.

The agent has not closed, merged or approved anything. It returns:
`#42 -> review, MR !17. Verified: 214 passed. Not verified: live run against the catalogue.`

## 11. I review and close

Days later, in a fresh session with no memory of any of this, I read !17 and approve it
myself. Then:

```text
Me: close 42, the estimate is right

> mr_merge(project="root/acme-widgets", mr=17)
merged !17 into main (squash)

> issue_close(project="root/acme-widgets", iid=42, spend="3h")
from handoff: repo ~/projects/acme-widgets, commit 9e26896, mr 17, summary ...
1 cross-reference: !17 + 9e26896 noted on #42
2 time: logged 3h (prior total 0)
3 status: review -> done
4 closed
5 wiki: docs/sync.md changed -> 1 page updated, 4 same
#42 closed.
```

`issue_close` was legal cold because the handoff had already written the repo, branch,
commit, merge request and proposed spend onto the issue. If it had been closed from the
web UI instead, `close_audit` would flag it.

## What the example shows

- The model decided three things: that it had started, that it was stuck, and that it was
  finished. I decided the other two: that the issue was ready, and that it was done.
- Both unmade decisions (Q1 and Q2 at write time, Q3 mid-flight) became written questions
  with tickable boxes, not guesses.
- The main thread never edited code. The work happened in a worktree, by `coder`, and was
  re-read by a second pass before it reached me.
- The effort number came from estimated skilled-developer effort, logged once, by the
  closing tool.

Next: [13 Getting started](13-getting-started.md)
