# work_queue

[Back to index](../README.md)

## Signature

```python
work_queue(project='', format='text', full=False, repo='', instance='')
```

The dispatch queue: what is READY to pick up, in the order to pick it up, and what is STRANDED in status::in-progress. The read a 'work the ready issues' run opens with, and the only tool in the loop that writes nothing. READY is ordered priority::high, medium, low, unprioritised, then iid — an order, not a set, so a run taking the first N agrees with the next run about which N those are.

STRANDED is every status::in-progress issue with the age since that label was APPLIED (from the resource label events, not from updated_at — a comment must not reset it). Stranded issues are strays and are NEVER offered for dispatch: status::in-progress is the dispatch lock, so an issue wearing it is either a run happening right now or a run that died and left the label, and nothing in the issue tells those apart.

An issue carrying BOTH labels is listed as stranded and flagged, never dispatched. A third list, IN REVIEW, shows every status::review issue with its MERGE REQUEST and that MR's state — because status::review means an MR is open, not that a branch exists somewhere. A review row reading `no MR` is a stray of the same kind as a stranded one, visible in the read that already exists to find strays; `?` means the lookup did not run, which is a different answer.

The MR for each row is read out of ONE listing per project (a second only when a row is unmatched, to tell 'merged and never closed' from 'never had one'), never one request per row. A fourth list, BLOCKED, shows every status::blocked issue with WHAT IT IS WAITING FOR — the unanswered question numbers, or the reason recorded in the description's '## Blocked' section. status::blocked asserts a stated reason the issue cannot proceed (#109), so the two states that contradict that are flagged and sorted to the top: `no_reason` (nothing on the issue says why) and `all_answered` (every question answered and nobody moved it — a block that reads as live work while the answer it was waiting for already arrived).

The check is free: the listing payload already carries the description. READY is split on the issue's '## Depends on' section AND any inline '**Depends on:** #N' marker, which ends at the first ' · ' or next '**Label:**' (#195, #198): DISPATCHABLE when every dependency it names is satisfied — closed status::done, or has a merged MR — and HELD, with the reason, when one is not (`#4 status::review (MR !7 open)`).

`#N` and `namespace/project#N` both parse; `None.` or no section means none. Three problems are flagged and sorted to the top of held: `dep_unresolvable` (a dependency that does not exist, or could not be read), `dep_dead` (closed wontfix/moved with no merged MR — it will never be satisfied) and `dep_cycle` (ready issues depending on each other). A lookup that failed holds the issue; it is never dispatchable on a guess.

Cost: one issues listing per referenced project plus at most one MR listing (all states) per project, never per dependency. PROJECT-SCOPED: `project` is a project ref, or '*' for every project the token can see. There is no implicit instance-wide read — an omitted project is refused rather than swept, because a dispatcher that swept the instance by accident would pick up work nobody asked it to do.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins. All four lists state their zero out loud — an empty queue is 'nothing to dispatch', which is an answer. Listings are capped and say what they withheld; full=True returns the rest. Four requests plus one per stranded issue for its age and one or two per project holding a review row, all bounded — past a bound a row shows `?` rather than an answer read off the wrong field.

`format=text|toon|json`.

## Convention

The read a dispatch run opens with, and the only one of these that writes nothing. THREE lists: `ready` in dispatch order, `stranded` — every status::in-progress issue, aged from the LABEL EVENT so a comment cannot reset the clock — and `in review`, with the MERGE REQUEST each row is waiting on and that MR's state. Stranded issues are strays and are never offered: in-progress is the dispatch lock, so one wearing it is a live run or a dead one and the issue does not say which.

A review row reading `no MR` is a stray of the same kind — status::review means an MR is OPEN. Project-scoped; '*' is asked for, never assumed.
