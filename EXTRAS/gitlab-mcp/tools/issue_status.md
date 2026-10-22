# issue_status

[Back to index](../README.md)

## Signature

```python
issue_status(project, iid, status, allow_new=False, force=False, reason='', instance='')
```

Move an issue to a workflow status in ONE call — the correct way to change status on this CE instance, which has no scoped-label auto-exclusion. Adds status::<status> and removes every other status:: label in a single request (so an issue can never end up carrying two). `status` may be bare ('in-progress') or qualified ('status::in-progress'). Valid: backlog, ready, in-progress, review, blocked, done, wontfix, moved.

Rejects values outside the scheme instead of letting GitLab silently create a typo'd label; allow_new=True overrides. Idempotent — a no-op move reports 'no change' and writes nothing. ILLEGAL MOVES ARE REFUSED (backlog->review, ready->done, blocked->in-progress and the rest), naming the legal moves from the current state and the tool that owns the one you asked for — `done` is reached through issue_close, which logs the time, and `in-progress` through issue_start, which sets the estimate. force=True moves it anyway, for repairing an issue already in a wrong state.

An issue carrying no status:: label, or two, is REPAIRED rather than refused. BLOCKED -> BACKLOG (#192) is the way back for an issue its author blocked with issue_ask at write time: legal only once every question is answered — an unanswered, contradictory or unreadable questions block is refused with the code issue_ready would give (open_questions / contradictory_answer / unreadable_questions).

A block held up only by a reason passes. force=True skips it. MOVING TO `blocked` REQUIRES A REASON (#109). status::blocked means the issue carries a STATED reason it cannot proceed — that is what the label asserts, and it is why `-> blocked` is legal from backlog and ready as well as in-progress. Pass `reason` ('waiting on the staging-host rebuild'); it is appended to a '## Blocked' section in the description, append-only, so the block explains itself to the next reader.

An issue that already carries UNANSWERED QUESTIONS needs no reason — the questions are the reason — and `issue_ask` writes those and moves the issue in one call. Neither one is a refusal, and force=True does NOT bypass it: force is about the transition table, the reason is about what `blocked` means. `reason` on any other target is refused.

## Convention

One call. On CE, adding status::in-progress does NOT remove status::backlog — this does both. Idempotent: a no-op reports 'no change' and writes nothing. ILLEGAL moves are refused (ready->done, backlog->review, blocked->in-progress, …) with the legal ones named; force=True repairs a wrong state. An issue carrying no status:: label, or two, is repaired rather than refused.

## Example

```python
issue_status('root/gitlab-mcp', 42, 'in-progress')
```

## Required

`project`, `iid`, `status`
